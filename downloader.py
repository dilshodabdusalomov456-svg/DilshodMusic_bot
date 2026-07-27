import yt_dlp
import os


def download_music(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    

    os.makedirs("downloads", exist_ok=True)

    options = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "quiet": False,
    "cookiefile": "cookies.txt",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    return filename.rsplit(".", 1)[0] + ".mp3"