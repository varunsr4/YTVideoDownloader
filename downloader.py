from yt_dlp import YoutubeDL
import os
from video_processor import load_trump_encoding, detect_trump_timestamps, trim_video
import json


def process_video_after_download(video_path, trump_encoding):
    """Process video for Trump detection and trim"""
    print(f"\nDetecting Trump in {video_path}")

    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return None

    timestamps = detect_trump_timestamps(video_path, trump_encoding)
    print(f"Found {len(timestamps)} timestamps with Trump")

    # Convert timestamps to ranges
    ranges = []
    MIN_DURATION = 1.0  # Minimum segment duration in seconds

    if timestamps:
        start = timestamps[0]
        prev = timestamps[0]

        for t in timestamps[1:]:
            if t - prev > 4:  # Gap threshold adjusted for 2-second sampling
                if prev - start >= MIN_DURATION:  # Only add if duration meets minimum
                    ranges.append([start, prev])
                start = t
            prev = t

        # Add the final range if it's valid and meets minimum duration
        if prev - start >= MIN_DURATION:
            ranges.append([start, prev])

        # Filter out any remaining invalid ranges
        ranges = [r for r in ranges if r[1] - r[0] >= MIN_DURATION]

        print(f"Converted to {len(ranges)} valid ranges")
        for i, (start, end) in enumerate(ranges):
            print(f"Range {i + 1}: {start:.2f}s to {end:.2f}s (duration: {end - start:.2f}s)")
    else:
        print("No Trump detected in video")

    if ranges:
        trimmed_path = video_path.replace('.mp4', '_trimmed.mp4').replace('.webm', '_trimmed.mp4')
        print(f"Trimming video to Trump segments...")
        if trim_video(video_path, trimmed_path, ranges):
            os.remove(video_path)
            print(f"Created trimmed version: {trimmed_path}")
            return ranges
        else:
            print("Failed to trim video")

    return None


def download_videos(urls_file='video_urls.txt', output_dir='downloads'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.split(' - ')[0].strip() for line in f.readlines()]

    if not urls:
        print("No URLs found in file")
        return

    print(f"Found {len(urls)} videos to download")

    trump_encoding = load_trump_encoding()
    results = {}

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'ignoreerrors': True,
        'quiet': True,
        'progress': True,
        'writesubtitles': False,
        'writethumbnail': False,
        'writeinfojson': False,
        'writedescription': False,
        'writeautomaticsub': False,
    }

    for i, url in enumerate(urls, 1):
        try:
            print(f"\nProcessing video {i} of {len(urls)}")
            print(f"Downloading {url}")

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)

            ranges = process_video_after_download(video_path, trump_encoding)
            if ranges:
                results[os.path.basename(video_path)] = ranges

                with open('trump_timestamps.json', 'w') as f:
                    json.dump(results, f, indent=2)
            else:
                print(f"No Trump segments found in {video_path}")

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            continue


def main():
    try:
        # Test face detection
        print("Testing face detection...")
        try:
            encoding = load_trump_encoding()
            print("Successfully loaded Trump reference image")
        except Exception as e:
            print(f"Error loading Trump reference image: {e}")
            return

        download_videos()
        print("\nAll processing completed!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()