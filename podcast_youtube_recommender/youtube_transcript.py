from youtube_transcript_api import YouTubeTranscriptApi
from pytube import Playlist
import os

from youtube_transcript_api.proxies import WebshareProxyConfig

ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username="yairiomm",
        proxy_password="928fk3ojwa9b",
    )
)

def get_video_ids_from_playlist(playlist_url):
    playlist = Playlist(playlist_url)
    video_ids = [video.video_id for video in playlist.videos]
    return video_ids

def fetch_transcript(video_id):
    try:
        transcript_list = ytt_api.get_transcript(video_id, languages=['en'])
        transcript_text = " ".join([t['text'] for t in transcript_list])
        return transcript_text
    except Exception as e:
        print(f"Could not get transcript for video {video_id}: {e}")
        return None

def save_transcript(video_id, transcript_text, save_dir='transcripts'):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{video_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(transcript_text)

if __name__ == "__main__":
    
    
    # Huberman Lab playlists
    playlist_url_1 = 'https://www.youtube.com/watch?v=h_1zlead9ZU&list=PLPNW_gerXa4Oge1tYt2NxOD23eMnUJxkO' # all guest episodes of huberman lab (140+ videos)
    
    
    playlist_url_5 =  'https://www.youtube.com/watch?v=In9Bq4EJMZw&list=PLPNW_gerXa4M58QbO_KM4aMLmSINuywh3' # Example Huberman Lab playlist for circadian rhythms
    playlist_url_2 = 'https://www.youtube.com/watch?v=h_1zlead9ZU&list=PLPNW_gerXa4Pc8S2qoUQc5e8Ir97RLuVW' # all episodes of huberman lab
    #playlist_url_7 = 'https://www.youtube.com/watch?v=HWcphoKlbxY&list=PLPNW_gerXa4OGNy1yE-W9IX-tPu-tJa7S' # huberman essentials playlist
    #playlist_url_8 = 'https://www.youtube.com/watch?v=RSnol_TVrzQ&list=PLPNW_gerXa4PSUFzfPS0rCNzuw5eFSEQE'  # Example Huberman Lab playlist for mental health
    #playlist_url_3 = 'https://www.youtube.com/watch?v=LYYyQcAJZfk&list=PLPNW_gerXa4O24l7ZHoJbMC2xOO7SpS7K' # Example Huberman Lab playlist for fitness and recovery
    #playlist_url_4 = 'https://www.youtube.com/watch?v=RSnol_TVrzQ&list=PLPNW_gerXa4PSUFzfPS0rCNzuw5eFSEQE'  # Example Huberman Lab playlist for mental health therapies
    #playlist_url_6 =  'https://www.youtube.com/watch?v=X8Hw8zeCDTA&list=PLPNW_gerXa4NKRk-x4U-Cuza8FPV8dx5x' # Example Huberman Lab playlist for behavioral change
    
    
    playlist_url_9 = "https://youtube.com/playlist?list=PLBC_rXxlVQZzpzL5yCFISrNiS6DDzcgRy&si=S2eFNJ5kl39huPlb"
    
    video_ids = get_video_ids_from_playlist(playlist_url_9)


    save_directory = 'all_transcripts_circadian_rhythms'

    for vid in video_ids:
        print(f"Processing video {vid}...")
        transcript = fetch_transcript(vid)
        if transcript:
            save_transcript(vid, transcript, save_dir=save_directory)
            print(f"Transcript saved for video {vid} in folder '{save_directory}'.")
        else:
            print(f"No transcript available for video {vid}.")




# github repos

# https://github.com/prakhar625/huberman-podcasts-transcripts/blob/main/youtube_extract_Andrew_Huberman.csv


# The drive podcast Peter Attia MD

# playlist_url_1 = https://www.youtube.com/watch?v=IQoHlEjJWKU&list=PLlFlZLYiJ88Px54CjCz4VRZW_c10T0IbW # Mental and Emotional Health

# playlist_url_2 = https://www.youtube.com/watch?v=9G3iLbQCIHI&list=PLlFlZLYiJ88MzCA5w2PtMKXnQCvY_czbU # Nutrition for Longevity

# playlist_url_3 = https://www.youtube.com/watch?v=sgJhPSFQ_Og&list=PLlFlZLYiJ88OTm8zInQB8K2POdjfTZlyI  # Exercise and Longevity

# playlist_url_4 = https://www.youtube.com/watch?v=8P46_vMn1II&list=PLlFlZLYiJ88PHIJn637lpW20tZRXhFn2U   # improve sleep

# playlist_url_5 = https://www.youtube.com/watch?v=mHjo3_ZtMZo&list=PLlFlZLYiJ88PHIJn637lpW20tZRXhFn2U&index=3 # full paylist



# from youtube_transcript_api import YouTubeTranscriptApi
# from pytube import Playlist, YouTube
# import os
# import json

# def get_videos_from_playlist(playlist_url):
#     playlist = Playlist(playlist_url)
#     videos_info = []
#     for url in playlist.video_urls:
#         try:
#             video = YouTube(url)
#             video_info = {
#                 'video_id': video.video_id,
#                 'title': video.title,
#                 'url': video.watch_url,
#                 'publish_date': video.publish_date.strftime("%Y-%m-%d") if video.publish_date else "Unknown"
#             }
#             videos_info.append(video_info)
#         except Exception as e:
#             print(f"Error fetching metadata for video {url}: {e}")
#     return videos_info

# def fetch_transcript(video_id):
#     try:
#         transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
#         transcript_text = " ".join([t['text'] for t in transcript_list])
#         return transcript_text
#     except Exception as e:
#         print(f"Could not get transcript for video {video_id}: {e}")
#         return None

# def save_transcript(video_info, transcript_text, save_dir='transcripts'):
#     os.makedirs(save_dir, exist_ok=True)
#     file_path = os.path.join(save_dir, f"{video_info['video_id']}.json")
    
#     full_data = {
#         'video_id': video_info['video_id'],
#         'title': video_info['title'],
#         'url': video_info['url'],
#         'publish_date': video_info['publish_date'],
#         'transcript': transcript_text
#     }

#     with open(file_path, "w", encoding="utf-8") as f:
#         json.dump(full_data, f, indent=2, ensure_ascii=False)

# if __name__ == "__main__":
#     # Use only the clean playlist URL
#     playlist_url = 'https://www.youtube.com/watch?v=RSnol_TVrzQ&list=PLPNW_gerXa4PSUFzfPS0rCNzuw5eFSEQE'

#     videos = get_videos_from_playlist(playlist_url)
#     save_directory = 'all_transcripts_mental_health_therapy'

#     for video in videos:
#         print(f"\nProcessing video {video['video_id']} - {video['title']}...")
#         transcript = fetch_transcript(video['video_id'])
#         if transcript:
#             save_transcript(video, transcript, save_dir=save_directory)
#             print(f"✅ Saved transcript for: {video['title']}")
#         else:
#             print(f"⚠️ No transcript available for: {video['title']}")
