import logging
import sys
import requests
from config import config
import json
from pprint import pformat

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka import SerializingProducer

# Function to fetch a page of playlist items from YouTube API using a playlist ID
# and return the JSON response containing content details.
def fetch_playlist_items_page(google_api_key, youtube_playlist_id, page_token=None):
    response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems",
                            params={
                                "key": google_api_key,
                                "playlistId": youtube_playlist_id,
                                "part": "contentDetails",
                                "pageToken": page_token
                            })

    payload = json.loads(response.text)

    logging.debug("GOT %s", payload)

    return payload

# Function to fetch a page of video details from YouTube API using a video ID
# and return the JSON response containing snippet and statistics.
def fetch_videos_page(google_api_key, video_id, page_token=None):
    response = requests.get("https://www.googleapis.com/youtube/v3/videos",
                            params={
                                "key": google_api_key,
                                "id": video_id,
                                "part": "snippet,statistics",
                                "pageToken": page_token
                            })

    payload = json.loads(response.text)

    logging.debug("GOT %s", payload)

    return payload

# Generator function to fetch all playlist items from YouTube by handling pagination.
# It yields items from the playlist and automatically fetches subsequent pages if available.
def fetch_playlist_items(google_api_key, youtube_playlist_id, page_token=None):
    payload = fetch_playlist_items_page(google_api_key, youtube_playlist_id, page_token)

    yield from payload["items"]

    next_page_token = payload.get("nextPageToken")

    if next_page_token is not None:
        yield from fetch_playlist_items(google_api_key, youtube_playlist_id, next_page_token)

# Generator function to fetch all videos based on video IDs, handling pagination.
# It yields video details and fetches the next page if there is one.
def fetch_videos(google_api_key, youtube_playlist_id, page_token=None):
    payload = fetch_videos_page(google_api_key, youtube_playlist_id, page_token)

    yield from payload["items"]

    next_page_token = payload.get("nextPageToken")

    if next_page_token is not None:
        yield from fetch_videos(google_api_key, youtube_playlist_id, next_page_token)

# Function to extract and summarize relevant details from a video object.
# Returns a dictionary with video ID, title, view count, like count, and comment count.
def summarize_video(video):
    return {
        "video_id": video["id"],
        "title": video["snippet"]["title"],
        "views": int(video["statistics"].get("viewCount", 0)),
        "likes": int(video["statistics"].get("likeCount", 0)),
        "comments": int(video["statistics"].get("commentCount", 0)),
    }

# Callback function for Kafka delivery events. It handles potential errors during message delivery.
def on_delivery(err, record):
    pass

# Main function where the program starts execution.
# Initializes the schema registry, configures the Kafka producer, and fetches YouTube videos.
# Summarized video data is produced to a Kafka topic.
def main():
    logging.info("START")

    # Initialize Schema Registry client and fetch the latest schema version for the "youtube_videos-value" topic.
    schema_registry_client = SchemaRegistryClient(config["schema_registry"])
    youtube_videos_value_schema = schema_registry_client.get_latest_version("youtube_videos-value")

    # Configure Kafka producer with serializers and schema information.
    kafka_config = config["kafka"] | {
        "key.serializer": StringSerializer(),
        "value.serializer": AvroSerializer(
            schema_registry_client,
            youtube_videos_value_schema.schema.schema_str,
        ),
    }
    producer = SerializingProducer(kafka_config)

    # Read API key and playlist ID from the config file.
    google_api_key = config["google_api_key"]
    youtube_playlist_id = config["youtube_playlist_id"]

    # Fetch playlist items, then fetch video details for each video in the playlist.
    for video_item in fetch_playlist_items(google_api_key, youtube_playlist_id):
        video_id = video_item["contentDetails"]["videoId"]
        for video in fetch_videos(google_api_key, video_id):
            logging.info("GOT %s", pformat(summarize_video(video)))

            # Produce video data to the Kafka topic "youtube_videos".
            producer.produce(
                topic="youtube_videos",
                key=video_id,
                value={
                    "TITLE": video["snippet"]["title"],
                    "VIEWS": int(video["statistics"].get("viewCount", 0)),
                    "LIKES": int(video["statistics"].get("likeCount", 0)),
                    "COMMENTS": int(video["statistics"].get("commentCount", 0)),
                },
                on_delivery=on_delivery,
            )

    # Wait for all messages to be delivered to Kafka before exiting.
    producer.flush()

# Entry point of the script. Initializes logging and starts the main function.
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
