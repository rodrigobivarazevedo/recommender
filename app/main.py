from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
import ast

app = FastAPI(
    title="Health Podcast Recommendation System",
    description="A content-based recommendation system for health and wellness podcasts",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Global variables for recommendation system
podcast_data = None
tfidf_matrix = None
cosine_sim = None
vectorizer = None

class PodcastRecommendationSystem:
    def __init__(self, transcript_weight=0.7, metadata_weight = 0.3):
        self.podcast_data = None
        self.vectorizer_podcast_data = None
        self.transcript_weight = transcript_weight
        self.metadata_weight = metadata_weight
        self.transcript_embeddings = None
        self.metadata_embeddings = None
        self.combined_embeddings = None
        self.cosine_sim = None
        self.embedding_model = None
        
    def load_data(self, data_path: str):
        """Load podcast data from CSV file"""
        try:
            with open(data_path, "rb") as f:
                self.podcast_data = pickle.load(f)
            
            print(f"Loaded {len(self.podcast_data)} podcasts")
            
            # Load embedding model if available
            model_path = "../podcast_youtube_recommender/models/embedding_model"
            if os.path.exists(model_path):
                try:
                    self.embedding_model = SentenceTransformer(model_path)
                    print("Embedding model loaded successfully")
                except Exception as e:
                    print(f"Warning: Could not load embedding model: {e}")
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
        
              
    def clean_embedding_column(self, column_name):
        """
        Convert stringified lists in a column to real float lists.
        Drop rows with malformed or empty embeddings.
        """
        def safe_parse(x):
            if isinstance(x, str):
                try:
                    arr = ast.literal_eval(x) if isinstance(x, str) else x
                    return arr if isinstance(arr, list) and all(isinstance(i, (float, int)) for i in arr) else None
                except Exception:
                    return None
                
            if isinstance(x, list):
                return np.array(x)
            if isinstance(x, np.ndarray):
                return x
            return None
        
        self.podcast_data[column_name] = self.podcast_data[column_name].apply(safe_parse)
        before = len(self.podcast_data)
        self.podcast_data = self.podcast_data[self.podcast_data[column_name].notnull()]
        after = len(self.podcast_data)
        print(f"Cleaned {column_name}: {before - after} rows removed")
        
        
    def prepare_recommendations(self):
        
        """Prepare embeddings and similarity matrix from cleaned DataFrame"""
        if self.podcast_data is None:
            print("No podcast data found.")
            return False

        try:
            print("Cleaning embedding columns...")
            self.clean_embedding_column("transcript_embedding_mean")
            self.clean_embedding_column("metadata_embedding")

            # Drop rows with missing or malformed embeddings
            self.podcast_data = self.podcast_data[
                self.podcast_data["transcript_embedding_mean"].apply(lambda x: isinstance(x, np.ndarray) and x.ndim == 1) &
                self.podcast_data["metadata_embedding"].apply(lambda x: isinstance(x, np.ndarray) and x.ndim == 1)
            ].reset_index(drop=True)

            # Check vector dimensions
            transcript_dims = self.podcast_data["transcript_embedding_mean"].apply(lambda x: x.shape[0])
            metadata_dims = self.podcast_data["metadata_embedding"].apply(lambda x: x.shape[0])
            common_dim = transcript_dims.mode()[0]

            # Keep only embeddings with matching dimensions
            self.podcast_data = self.podcast_data[
                (transcript_dims == common_dim) & (metadata_dims == common_dim)
            ].reset_index(drop=True)

            # Now safely convert to arrays
            self.transcript_embeddings = np.vstack(self.podcast_data["transcript_embedding_mean"].to_numpy())
            self.metadata_embeddings = np.vstack(self.podcast_data["metadata_embedding"].to_numpy())

            print(f"Transcript embeddings shape: {self.transcript_embeddings.shape}")
            print(f"Metadata embeddings shape: {self.metadata_embeddings.shape}")

            if self.transcript_embeddings.ndim != 2 or self.metadata_embeddings.ndim != 2:
                raise ValueError("Embeddings must be 2D arrays")

            # Weighted combination
            self.combined_embeddings = (
                self.transcript_weight * self.transcript_embeddings +
                self.metadata_weight * self.metadata_embeddings
            )
            
            # Normalize combined embeddings row-wise to unit length
            self.combined_embeddings = normalize(self.combined_embeddings, norm='l2', axis=1)

            print("Calculating similarity matrix...")
            self.cosine_sim = cosine_similarity(self.combined_embeddings, self.combined_embeddings)

            print("✅ Recommendation system prepared successfully!")
            return True

        except Exception as e:
            print(f"❌ Error preparing recommendations: {e}")
            return False
        
     
    def get_random_playlist(self, n_recommendations: int = 5):
        
        random_idx = np.random.randint(0, len(self.podcast_data))

        # Get similarity scores
        sim_scores = list(enumerate(self.cosine_sim[random_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get top N recommendations (excluding the podcast itself)
        sim_scores = sim_scores[1:n_recommendations+1]
        podcast_indices = [i[0] for i in sim_scores]

        # Get the recommended podcasts with similarity scores
        recommendations = self.podcast_data.iloc[podcast_indices].copy()
        recommendations["similarity"] = [score[1] for score in sim_scores]

        return recommendations
    
    
    def cosine_similarity_matrix(self, vec, matrix, normalized=True):
        """
        Compute cosine similarity between a single vector `vec` and each row vector in `matrix`.
        vec: 1D numpy array, shape (d,)
        matrix: 2D numpy array, shape (n, d)
        Returns:
            similarities: 1D numpy array, shape (n,)
        """
        
        if normalized:
            return np.dot(matrix, vec)
            
        else:
            # Normalize the input vector and matrix row-wise
            vec_norm = vec / np.linalg.norm(vec)
            matrix_norm = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
            
            # Dot product between vec and each row in matrix (broadcasting)
            similarities = np.dot(matrix_norm, vec_norm)
            return similarities
    
    def item_based_filtering(self, podcast_title: str, n_recommendations: int = 5):
        """Get recommendations based on podcast title"""
        if self.podcast_data is None or self.cosine_sim is None:
            return []
            
        # Encode user input
        user_emb = self.embedding_model.encode(podcast_title)
        
        # Normlaize input
        user_emb_norm = normalize(user_emb.reshape(1, -1))[0]
        
        df = self.podcast_data.copy()

        # Stack embeddings into a numpy matrix
        normalized_embeddings_matrix = np.vstack(df['metadata_embedding'].values)

        # Compute all cosine similarities at once
        similarities = self.cosine_similarity_matrix(user_emb_norm, normalized_embeddings_matrix)

        # Add similarity scores
        df = df.assign(similarity=similarities)
        
        try:
            # Get top_n most similar rows
            top_match_idx = df.sort_values(by="similarity", ascending=False).index[0]
        except IndexError:
            # If exact match not found, return none
            return None
                
        # Get similarity scores
        sim_scores = list(enumerate(self.cosine_sim[top_match_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N recommendations (excluding the podcast itself)
        sim_scores = sim_scores[1:n_recommendations+1]
        podcast_indices = [i[0] for i in sim_scores]
        
        # Get the recommended podcasts with similarity scores
        recommendations = self.podcast_data.iloc[podcast_indices].copy()
        recommendations["similarity"] = [score[1] for score in sim_scores]
        
        print(recommendations)
        
        return recommendations
    
     
    def content_filtering(self, user_input, top_n=100, max_min=None, column='transcript_embedding_mean'):
        """
        Filter DataFrame based on user input about health goal or concern using transcripts.
        """
        df = self.podcast_data.copy()
        
        if max_min is not None:
            df = df[df['duration_min'] <= max_min]
        
        # Encode user input
        user_emb = self.embedding_model.encode(user_input)
        
        # Normalize User Input
        user_emb_norm = normalize(user_emb.reshape(1, -1))[0]

        # Stack embeddings into a numpy matrix
        normalized_embeddings_matrix = np.vstack(df[column].values)

        # Compute all cosine similarities at once
        similarities = self.cosine_similarity_matrix(user_emb_norm, normalized_embeddings_matrix)

        # Add similarity scores
        df = df.assign(similarity=similarities)

        # Get top_n most similar rows
        top = df.sort_values(by="similarity", ascending=False).head(top_n)
        
        print(top)
        
        return top
    
    
# Initialize recommendation system
recommendation_system = PodcastRecommendationSystem()

@app.on_event("startup")
async def startup_event():
    """Initialize the recommendation system on startup"""
    # Try to load data from the podcast_youtube_recommender directory
    data_path = "../podcast_youtube_recommender/transformers_embedded_podcast_data.pkl"
    if os.path.exists(data_path):
        if recommendation_system.load_data(data_path):
            recommendation_system.prepare_recommendations()
            print("Recommendation system initialized successfully!")
        else:
            print("Failed to initialize recommendation system")
    else:
        print(f"Data file not found at {data_path}")

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page for the health podcast recommendation system"""
    return templates.TemplateResponse(
        "landing.html",
        {"request": request}
    )

@app.get("/recommendations", response_class=HTMLResponse)
async def recommendations_page(request: Request):
    """Page to get podcast recommendations"""
    return templates.TemplateResponse(
        "recommendations.html",
        {"request": request}
    )

@app.post("/get_recommendations")
async def get_recommendations(podcast_title: str = Form(...), num_recommendations: int = Form(5)):
    """API endpoint to get podcast recommendations based on title"""
    try:
        recommendations = recommendation_system.item_based_filtering(podcast_title, num_recommendations)
        
        if recommendations is None:
            return {"recommendations": []}
            
        # Convert to list of dictionaries for JSON response
        recommendations_list = []
        for _, row in recommendations.iterrows():
            
            recommendations_list.append({
                'title': row.get('title', 'Unknown'),
                'host': row.get('host', 'Unknown Host'),
                'duration_min': row.get('duration_min', 0),
                'similarity_score': float(row.get("similarity", 0.0))
            })
        
        return {"recommendations": recommendations_list}
    except Exception as e:
        print(f"Error in get_recommendations endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")
    

@app.post("/get_random_playlist")
async def get_random_playlist(num_recommendations: int = Form(5)):
    """API endpoint to get a random playlist of podcast recommendations"""
    try:
        # Pass max_duration as max_min to the method
        recommendations = recommendation_system.get_random_playlist(num_recommendations)
        
        # Convert to list of dictionaries for JSON response
        recommendations_list = []
        for _, row in recommendations.iterrows():
           
            recommendations_list.append({
                'title': row.get('title', 'Unknown'),
                'host': row.get('host', 'Unknown Host'),
                'duration_min': row.get('duration_min', 0),
                'similarity_score': float(row.get("similarity", 0.0))
            })
        
        return {"recommendations": recommendations_list}
    except Exception as e:
        print(f"Error in get_random_playlist endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting random playlist: {str(e)}")

@app.post("/get_content_recommendations")
async def get_content_recommendations(user_input: str = Form(...), num_recommendations: int = Form(5), max_duration: int = Form(None)):
    """API endpoint to get recommendations based on user's health goals or concerns"""
    try:
        recommendations = recommendation_system.content_filtering(
            user_input, 
            top_n=num_recommendations, 
            max_min=max_duration
        )
        
        # Convert to list of dictionaries for JSON response
        recommendations_list = []
        for _, row in recommendations.iterrows():
            
            recommendations_list.append({
                'title': row.get('title', 'Unknown'),
                'host': row.get('host', 'Unknown Host'),
                'duration_min': row.get('duration_min', 0),
                'similarity_score': float(row.get("similarity", 0.0))
            })
        
        return {"recommendations": recommendations_list}
    except Exception as e:
        print(f"Error in get_content_recommendations endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting content recommendations: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "recommendation_system_loaded": recommendation_system.podcast_data is not None}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 