
import os
from ytmusicapi import YTMusic
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# ------------------------------------------
# 1. Spotify Authentication
#    (Create your credentials at https://developer.spotify.com)
# ------------------------------------------

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
)

# ------------------------------------------
# 2. Get Songs from a Spotify Playlist
# ------------------------------------------

playlist_url = input("Playlist URL: ")
playlist_id = playlist_url.split("/")[-1].split("?")[0]

results = sp.playlist_tracks(playlist_id)

songs = []

for item in results["items"]:
    track = item["track"]
    name = track["name"]
    artist = track["artists"][0]["name"]
    songs.append(f"{name} {artist}")

print("Songs found:")

for song in songs:
    print("-", song)


OUTPUT_FILE = "songs.txt"

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    for song in songs:
        file.write(f"{song}.\n")

print(f"Successfully saved to '{OUTPUT_FILE}'.")


OUTPUT_FOLDER = "PATH_FOLDER"

ytm = YTMusic()
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

options = {
    "format": "bestaudio/best",
    "outtmpl": f"{OUTPUT_FOLDER}/%(artist,uploader)s - %(title)s.%(ext)s",
    "postprocessors": [
        {
            # Convert audio to MP3
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        },
        {
            # Add metadata (title, artist, etc.)
            "key": "FFmpegMetadata",
        },
        {
            # Remove non-music segments
            "key": "SponsorBlock",
            "categories": ["music_offtopic"],
        },
        {
            "key": "ModifyChapters",
            "remove_sponsor_segments": ["music_offtopic"],
        },
    ],
    "quiet": True,
    "noplaylist": True,
}

with open(OUTPUT_FILE, encoding="utf-8") as file:
    songs_to_download = [
        line.strip() for line in file if line.strip()
    ]

with yt_dlp.YoutubeDL(options) as ydl:
    for query in songs_to_download:
        results = ytm.search(query, filter="songs", limit=1)

        if not results:
            print(f"❌ Not found: {query}")
            continue

        result = results[0]
        artist = result["artists"][0]["name"]

        print(f"⬇️  {artist} - {result['title']}")

        try:
            video_url = (
                f"https://music.youtube.com/watch?v={result['videoId']}"
            )
            ydl.download([video_url])

        except Exception as error:
            print(f"⚠️ Error with {query}: {error}")

print("✅ Done!")
