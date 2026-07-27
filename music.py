import re
import html

from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY

youtube = build(
    "youtube",
    "v3",
    developerKey=YOUTUBE_API_KEY
)


def format_duration(duration):
    duration = duration.replace("PT", "")

    hours = minutes = seconds = 0

    h = re.search(r"(\d+)H", duration)
    m = re.search(r"(\d+)M", duration)
    s = re.search(r"(\d+)S", duration)

    if h:
        hours = int(h.group(1))

    if m:
        minutes = int(m.group(1))

    if s:
        seconds = int(s.group(1))

    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"

    return f"{minutes}:{seconds:02}"


def clean_title(title):
    words = [
        "[Official Music Video]",
        "(Official Music Video)",
        "[Official Video]",
        "(Official Video)",
        "[Lyrics]",
        "(Lyrics)",
        "[HD]",
        "(HD)",
        "[4K]",
        "(4K)"
    ]

    for word in words:
        title = title.replace(word, "")

    return title.strip()


def search_music(query):

    request = youtube.search().list(
        part="snippet",
        q=query,
        maxResults=10,
        type="video"
    )

    response = request.execute()

    ids = []

    for item in response["items"]:
        ids.append(item["id"]["videoId"])

    details = youtube.videos().list(
        part="contentDetails",
        id=",".join(ids)
    ).execute()

    durations = {}

    for item in details["items"]:
        durations[item["id"]] = format_duration(
            item["contentDetails"]["duration"]
        )

    songs = []
    seen =set()
    

    for item in response["items"]:

        video_id = item["id"]["videoId"]

        title = clean_title(html.unescape(item["snippet"]["title"]))

        if title.lower() in seen:
            continue

        seen.add(title.lower())

        songs.append({
            "title": title,
            "channel": html.unescape(item["snippet"]["channelTitle"]),
            "videoId": video_id,
            "duration": durations.get(video_id, "--:--")
        })

    return songs