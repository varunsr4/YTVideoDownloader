from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import re
import os


def parse_duration(duration_str):
    """
    Convert ISO 8601 duration format to seconds
    Examples:
        PT1H2M10S -> 3730 seconds
        PT5M -> 300 seconds
        PT30S -> 30 seconds
        PT1H -> 3600 seconds
    """
    duration_str = duration_str.replace('PT', '')
    seconds = 0
    hours = re.search(r'(\d+)H', duration_str)
    minutes = re.search(r'(\d+)M', duration_str)
    secs = re.search(r'(\d+)S', duration_str)

    if hours:
        seconds += int(hours.group(1)) * 3600
    if minutes:
        seconds += int(minutes.group(1)) * 60
    if secs:
        seconds += int(secs.group(1))

    return seconds


def get_videos_up_to_duration(api_key, channel_id, query, target_duration_minutes):
    youtube = build('youtube', 'v3', developerKey=api_key)
    total_duration = 0
    videos = []
    next_page_token = None

    print(f"Starting search for videos up to {target_duration_minutes} minutes...")

    while total_duration < (target_duration_minutes * 60):
        print(f"Current total duration: {total_duration} seconds")

        try:
            request = youtube.search().list(
                part='id,snippet',
                channelId=channel_id,
                q=query,
                type='video',
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            if not response.get('items'):
                print("No videos found in response")
                break

            print(f"Found {len(response['items'])} videos in this page")
            video_ids = [item['id']['videoId'] for item in response['items']]

            # Get video details including duration
            video_request = youtube.videos().list(
                part='contentDetails,snippet',
                id=','.join(video_ids)
            )
            video_response = video_request.execute()

            for video in video_response['items']:
                duration_str = video['contentDetails']['duration']
                duration = parse_duration(duration_str)
                title = video['snippet']['title']

                print(f"Processing: {title} ({duration} seconds)")

                if total_duration + duration <= (target_duration_minutes * 60):
                    total_duration += duration
                    videos.append({
                        'url': f"https://youtube.com/watch?v={video['id']}",
                        'duration': duration,
                        'title': title
                    })
                    print(f"Added video. New total: {total_duration} seconds")
                else:
                    print(f"Reached duration limit at {total_duration} seconds")
                    return videos

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                print("No more pages to fetch")
                break

        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

    print(f"Final video count: {len(videos)}")
    return videos


def main():
    # Read API Key from file
    try:
        with open('api-key.txt', 'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("Error: api-key.txt not found. Please create this file with your YouTube API key.")
        return
    except Exception as e:
        print(f"Error reading API key: {e}")
        return

    if not api_key:
        print("Error: API key is empty. Please add your YouTube API key to api-key.txt")
        return
    
    cspan_channel_id = 'UCb--64Gl51jIEVE-GLDAVTg'  # C-SPAN's channel ID

    try:
        # Test the API connection first
        youtube = build('youtube', 'v3', developerKey=api_key)
        test_request = youtube.search().list(
            part='snippet',
            channelId=cspan_channel_id,
            q='trump',
            type='video',
            maxResults=1
        )
        test_response = test_request.execute()
        print("API connection test successful")

        # Get the videos
        videos = get_videos_up_to_duration(api_key, cspan_channel_id, 'trump', 1000)

        # Save URLs to a file
        if videos:
            with open('video_urls.txt', 'w', encoding='utf-8') as f:
                for video in videos:
                    f.write(f"{video['url']}\n")
            print(f"Successfully wrote {len(videos)} URLs to video_urls.txt")
        else:
            print("No videos were found to write to file")

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()