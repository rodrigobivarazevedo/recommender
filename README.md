# HealthCast - AI-Powered Health Podcast Recommendation System

A modern FastAPI web application that provides content-based recommendations for health and wellness podcasts using pre-computed embeddings and machine learning.

## Features

- 🧠 **AI-Powered Recommendations**: Uses pre-computed embeddings (transcript and metadata) for superior content analysis
- 🎯 **Health-Focused**: Specifically designed for health and wellness podcast content
- 🚀 **Modern UI**: Beautiful, responsive design with Bootstrap 5 and custom CSS
- ⚡ **Fast Performance**: Built with FastAPI for high-performance async operations
- 📱 **Mobile Responsive**: Works perfectly on all devices
- 🔍 **Interactive Search**: Real-time podcast recommendations with loading states
- 📊 **Embedding-Based**: Leverages advanced NLP embeddings for better recommendations

## Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **ML Libraries**: scikit-learn, pandas, numpy
- **Embeddings**: Pre-computed transcript and metadata embeddings
- **Server**: Uvicorn

## Installation

1. **Navigate to the app directory**:
   ```bash
   cd app
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**:
   ```bash
   python run.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

3. **Get recommendations**:
   - Go to the "Get Recommendations" page
   - Enter a podcast title or topic you're interested in
   - Choose the number of recommendations (3, 5, or 10)
   - Click "Get Recommendations" to see AI-generated suggestions

## How It Works

### Embedding-Based Recommendation System
The system uses two types of pre-computed embeddings:

1. **Transcript Embeddings** (`transcript_embedding_mean`): 
   - Captures the semantic meaning of podcast content
   - Weight: 70% in final similarity calculation

2. **Metadata Embeddings** (`metadata_embedding`):
   - Captures information about titles, hosts, and other metadata
   - Weight: 30% in final similarity calculation

### Recommendation Process
1. **Data Loading**: Loads pre-computed embeddings from CSV
2. **Embedding Processing**: Converts string embeddings to numpy arrays
3. **Similarity Calculation**: Uses cosine similarity on combined embeddings
4. **Ranking**: Returns top-N most similar podcasts

## API Endpoints

- `GET /` - Landing page
- `GET /recommendations` - Recommendations form page
- `POST /get_recommendations` - API endpoint for getting recommendations
- `GET /health` - Health check endpoint

## Data Requirements

The application expects podcast data in CSV format with the following columns:
- `title`: Podcast title
- `host`: Podcast host name
- `transcript`: Full transcript text
- `transcript_embedding_mean`: Pre-computed transcript embeddings
- `metadata_embedding`: Pre-computed metadata embeddings
- `duration_min`: Duration in minutes
- `tags`: Comma-separated tags

The system automatically loads data from `../podcast_youtube_recommender/embedded_podcast_youtube_data.csv`.

## Project Structure

```
app/
├── main.py                 # FastAPI application with embedding-based recommendations
├── run.py                  # Easy startup script
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── landing.html       # Landing page
│   └── recommendations.html # Recommendations page
└── static/                # Static files
    ├── css/
    │   └── style.css      # Custom styles
    └── js/
        └── main.js        # JavaScript functionality
```

## Features in Detail

### Advanced Recommendation Algorithm
- **Dual Embedding Approach**: Combines transcript and metadata embeddings
- **Weighted Similarity**: Configurable weights for different embedding types
- **Cosine Similarity**: Industry-standard similarity metric
- **Real-time Processing**: Fast similarity calculations

### Modern User Interface
- Clean, health-themed design with green color scheme
- Responsive layout that works on all screen sizes
- Smooth animations and transitions
- Interactive elements with hover effects
- Loading states and error handling

### Enhanced User Experience
- Intuitive navigation between pages
- Form validation and user feedback
- Example podcast suggestions for easy testing
- Similarity scores to show recommendation confidence
- Host information and duration display
- Transcript previews for better context

## Customization

### Embedding Weights
Modify the weights in `main.py`:
```python
transcript_weight = 0.7  # Weight for transcript embeddings
metadata_weight = 0.3    # Weight for metadata embeddings
```

### Styling
- Modify `static/css/style.css` to change colors, fonts, and layout
- Update CSS variables in `:root` for consistent theming
- Add new animations in the CSS file

### Functionality
- Extend `main.py` with additional API endpoints
- Modify the recommendation algorithm in the `PodcastRecommendationSystem` class
- Add new features in `static/js/main.js`

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Testing
Test the health endpoint:
```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Common Issues

1. **Embeddings not loading**: Ensure the CSV file contains the required embedding columns
2. **Memory issues**: Large embedding files may require more RAM
3. **Dependencies not found**: Run `pip install -r requirements.txt`
4. **Port already in use**: Change the port in the uvicorn command

### Debug Mode
Enable debug logging by setting the log level:
```bash
uvicorn main:app --reload --log-level debug
```

## Performance Notes

- **Embedding Loading**: Initial startup may take longer with large embedding files
- **Memory Usage**: Embeddings are loaded into memory for fast similarity calculations
- **Scalability**: Consider using approximate nearest neighbor search for very large datasets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the excellent web framework
- Bootstrap for the responsive UI components
- Font Awesome for the beautiful icons
- scikit-learn for the machine learning capabilities
- The embedding model creators for the semantic understanding capabilities 