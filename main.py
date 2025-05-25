import os
import pickle
import argparse
import requests
import re

# Your TMDb API key
TMDB_API_KEY = '...'

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = '...'
TELEGRAM_CHAT_ID = '...'

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # Optional
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send message to Telegram: {response.text}")

# Set up argument parser
parser = argparse.ArgumentParser(description="Scan a folder and fetch TMDb info for media files.")
parser.add_argument("folder", help="Path to the folder to scan")
parser.add_argument("seen_file", help="Path to the file storing seen items (pickle format)")
parser.add_argument("--type", choices=['movie', 'serie'], required=True, help="Specify whether processing movies or series")
args = parser.parse_args()

SCAN_DIR = args.folder
SEEN_FILE_PATH = args.seen_file
MEDIA_TYPE = args.type  # 'movie' or 'serie'

# Load previously seen items if the file exists
if os.path.exists(SEEN_FILE_PATH):
    with open(SEEN_FILE_PATH, 'rb') as f:
        seen_items = pickle.load(f)
else:
    seen_items = set()

def extract_title_from_name(name):
    name = os.path.splitext(name)[0]
    name = re.sub(r'\b(?:en|jp|fr|de|it|es|zh|ru|ko|pt|th|vi|sv|da|no|fi|nl|tr)\b(?:\.[a-z]{2})?', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(s|season|episode|ep)\s?\d+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b\d{4}\b', '', name)
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'[\.\_\-]+', ' ', name)
    tags_pattern = r'\b(720p|1080p|2160p|HDR|WEB\-DL|BluRay|BRRip|DVDRip|x264|x265|HEVC|HEIC|HEVC|H264|AAC|DTS|DTS\-HD|AC3|5.1|6ch|7.1|10bit|WEB\-Rip|WEBRip|HDRip|PAL|NTSC|REMUX|Remux|PROPER|REPACK|YTS\.AG|YTS\.MX|YIFY|RARBG|PSA|SRT|sub|subs|internal|dub|dubbing|dual audio|multi audio)\b'
    name = re.sub(tags_pattern, '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def generate_fallback_titles(title):
    parts = title.strip().split()
    fallback_titles = []
    while len(parts) > 1:
        fallback_titles.append(' '.join(parts))
        parts.pop()
    if len(parts) == 1:
        fallback_titles.append(' '.join(parts))
    return fallback_titles

def search_tmdb(query, media_type):
    if media_type == 'movie':
        url = 'https://api.themoviedb.org/3/search/movie'
    else:
        url = 'https://api.themoviedb.org/3/search/tv'
    params = {
        'api_key': TMDB_API_KEY,
        'query': query,
        'include_adult': 'false'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]
        else:
            return None
    else:
        print(f"TMDb API error: {response.status_code}")
        return None

def search_with_fallbacks(title, media_type):
    fallback_titles = generate_fallback_titles(title)
    for attempt_title in fallback_titles:
        print(f"Trying fallback search: '{attempt_title}'")
        result = search_tmdb(attempt_title, media_type)
        if result:
            return result, attempt_title, media_type
    return None, None, None

def get_tmdb_url(media_item, media_type):
    tmdb_id = media_item.get('id')
    if media_type == 'movie':
        return f"https://www.themoviedb.org/movie/{tmdb_id}"
    elif media_type == 'serie':
        return f"https://www.themoviedb.org/tv/{tmdb_id}"
    elif media_type == 'person':
        return f"https://www.themoviedb.org/person/{tmdb_id}"
    else:
        return None

def extract_season_number(season_folder_name):
    """
    Extracts the season number from the folder name.
    Supports patterns like 'Season 1', 'Seizoen 2', 'S01', 'S02', etc.
    """
    patterns = [
        r'(?i)season\s?(\d+)',     # e.g., 'Season 1'
        r'(?i)seizoen\s?(\d+)',    # e.g., 'Seizoen 2'
        r'S(\d+)',                 # e.g., 'S01'
        r'(?i)Seizoen\s?(\d+)',    # uppercase 'Seizoen'
        r'(\d+)'                   # fallback: any number in name
    ]
    for pattern in patterns:
        match = re.search(pattern, season_folder_name)
        if match:
            return int(match.group(1))
    return None  # fallback if no pattern matches

def main():
    if MEDIA_TYPE == 'serie':
        # Process each series folder
        for root, dirs, files in os.walk(SCAN_DIR):
            for name in dirs:
                dir_path = os.path.join(root, name)
                if dir_path not in seen_items:
                    # Parse series name
                    series_name_raw = name
                    print(f"\nProcessing series folder: {dir_path}")
                    title = extract_title_from_name(series_name_raw)
                    print(f"Searching TMDb for series '{title}'...")
                    result, used_title, media_type_found = search_with_fallbacks(title, 'serie')
                    if result:
                        url = get_tmdb_url(result, 'serie')
                        series_name_found = result.get('name')
                        print(f"Found series: {series_name_found}")
                        
                        # Process season folders inside this series folder
                        for season_name in os.listdir(dir_path):
                            season_path = os.path.join(dir_path, season_name)
                            if os.path.isdir(season_path):
                                if season_path not in seen_items:
                                    seen_items.add(season_path)
                                    season_number = extract_season_number(season_name)
                                    season_text = f"Seizoen {season_number}" if season_number else "Seizoen"
                                    message = (f"{season_text} van \"{series_name_found}\" ({url}) is volledig toegevoegt aan de tv-lijst.\n\n"
                                               "Voor verdere wensen naar tv series kun je hier in Telegram of hier (https://forms.gle/xbEGtZYjVLdjatjQ9) een bericht achterlaten.\n"
                                               "Verder kun je ook altijd Jens een bericht sturen.")
                                    send_telegram_message(message)
                                # Else, season already processed
                        # Mark the series folder as processed
                        seen_items.add(dir_path)
                    else:
                        print(f"Geen resultaten gevonden voor serie '{title}'")
            # No need to recurse further if only processing top-level series folders
        # End of series processing
    else:
        # For movies, process files and folders as before
        for root, dirs, files in os.walk(SCAN_DIR):
            # Process directories (for movies)
            for name in dirs:
                dir_path = os.path.join(root, name)
                if dir_path not in seen_items:
                    seen_items.add(dir_path)
                    print(f"\nFound directory: {dir_path}")
                    # Search TMDb
                    title = extract_title_from_name(name)
                    print(f"Searching TMDb for '{title}'...")
                    result, used_title, media_type_found = search_with_fallbacks(title, MEDIA_TYPE)
                    if result:
                        url = get_tmdb_url(result, media_type_found)
                        name_found = result.get('title')
                        print(f"Match: {name_found}")
                        print(f"TMDb page: {url}")
                        if MEDIA_TYPE == 'movie':
                            message = f"De film {name_found} ({url}) is toegevoegt aan de filmlijst.\n\nVoor verdere wensen naar films kun je hier in Telegram of hier (https://forms.gle/xbEGtZYjVLdjatjQ9) een bericht achterlaten.\nVerder kun je ook altijd Jens een bericht sturen."
                            send_telegram_message(message)
                    else:
                        print(f"No results found for '{title}' after fallbacks.")
                        send_telegram_message(f"Geen resultaten gevonden voor '{title}' na zoeken.")
            # Process files (for movies)
            for name in files:
                file_path = os.path.join(root, name)
                if file_path not in seen_items:
                    seen_items.add(file_path)
                    print(f"\nFound file: {file_path}")
                    title = extract_title_from_name(name)
                    print(f"Searching TMDb for '{title}'...")
                    result, used_title, media_type_found = search_with_fallbacks(title, MEDIA_TYPE)
                    if result:
                        url = get_tmdb_url(result, media_type_found)
                        name_found = result.get('title')
                        print(f"Match: {name_found}")
                        print(f"TMDb page: {url}")
                        if MEDIA_TYPE == 'movie':
                            message = f"De film {name_found} ({url}) is toegevoegt aan de filmlijst.\n\nVoor verdere wensen naar films kun je hier in Telegram of hier (https://forms.gle/xbEGtZYjVLdjatjQ9) een bericht achterlaten.\nVerder kun je ook altijd Jens een bericht sturen."
                            send_telegram_message(message)
                    else:
                        print(f"No results found for '{title}' after fallbacks.")
                        send_telegram_message(f"Geen resultaten gevonden voor '{title}' na zoeken.")

    # Save the seen items
    with open(SEEN_FILE_PATH, 'wb') as f:
        pickle.dump(seen_items, f)
    print("\nScan complete. Seen items saved.")

if __name__ == "__main__":
    main()
