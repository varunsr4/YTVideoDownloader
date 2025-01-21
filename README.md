# C-SPAN Videos featuring Trump on YouTube - Scraper & Processor

This project downloads and processes CSPAN videos from YouTube.com containing appearances of Donald Trump, automatically detecting and extracting segments where his face appears.

## Project Structure

- `scraper.py`: YouTube API scraper that searches CSPAN's channel for videos containing Trump and generates URL lists
- `downloader.py`: Downloads videos from the URL lists and processes them for Trump appearances
- `video_processor.py`: Contains face detection and video trimming functionality
- `trump_reference.jpg`: Reference image used for face detection

## Prerequisites

### API Key Setup
1. Obtain a YouTube Data API v3 key from Google Cloud Console
2. Create a file named `api-key.txt` in the project root
3. Paste your API key into this file

### Required Libraries
Install the following dependencies using pip:

```bash
pip install google-api-python-client
pip install yt-dlp
pip install face-recognition
pip install opencv-python
```

Note: For face_recognition installation on macOS/Linux:
```bash
# macOS prerequisites
brew install cmake

# Linux prerequisites
sudo apt-get install python3-dev
sudo apt-get install cmake
sudo apt-get install gcc g++
```

### Additional Requirements
- FFmpeg must be installed on your system:
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`
  - Windows: Download from FFmpeg website and add to PATH

## How It Works

1. `scraper.py`:
   - Searches CSPAN's YouTube channel for videos mentioning Trump
   - Collects videos up to 1000 minutes total duration
   - Splits URLs into 7 separate files for parallel processing
   - Uses YouTube Data API to fetch video metadata

2. `downloader.py`:
   - Downloads videos using yt-dlp
   - Processes each video for Trump appearances
   - Creates trimmed versions containing only Trump segments
   - Saves timestamp data to JSON file

3. `video_processor.py`:
   - Handles face detection using face_recognition library
   - Processes video frames at regular intervals
   - Identifies Trump appearances with adjustable tolerance
   - Handles video trimming using FFmpeg

## Usage

1. Set up API key:
```bash
echo "YOUR_API_KEY" > api-key.txt
```

2. Run the scraper:
```bash
python scraper.py
```

3. Run the downloader:
```bash
python downloader.py
```

The process will:
- Generate video URL lists in video_urls1.txt through video_urls7.txt
- Download videos to a 'downloads' directory
- Create trimmed versions containing only Trump segments
- Save timestamp data in trump_timestamps.json

## Performance Notes

- Face detection uses the 'hog' model for faster performance at the cost of accuracy
- Frame sampling rate is set to 1 second for faster performance at the cost of accuracy
- Video resolution is reduced by 25% during processing for faster performance at the cost of accuracy
- Face detection tolerance is set to 0.65 (default is 0.6) for slightly better accuracy
- FFmpeg uses h264_videotoolbox (MacOS) for hardware-accelerated encoding

## Troubleshooting

If face detection is failing:
   - Ensure trump_reference.jpg is a clear frontal face image
   - Adjust the face detection tolerance in video_processor.py
   - Try increasing the frame sampling rate

## Future Improvements

### Enhanced Face Detection
Several commercial APIs could provide more accurate face detection and recognition:

- **Amazon Rekognition**: Used in Prime Video's X-Ray feature, offers highly accurate celebrity recognition
  - Pros: Highly accurate, includes celebrity recognition out of the box
  - Cons: Approximately $0.10 per minute of video processed
  - Could significantly improve detection accuracy and reduce false positives

- **Google Cloud Vision API**: 
  - Similar pricing to Rekognition (around $0.10 per minute)
  - Includes person detection and face detection
  - Could be integrated with existing Google Cloud infrastructure

### Cloud Processing

Moving processing to a cloud platform could significantly improve performance:

1. **Cloud Server Benefits**:
   - GPU-accelerated processing (3-4x faster than CPU)
   - Parallel processing of multiple videos
   - No local storage constraints
   - Continuous operation without affecting local machine

2. **Estimated Performance**:
   - Current local processing: ~2x realtime (1 hour video takes 2 hours to process)
   - GPU-accelerated cloud: ~0.5x realtime (1 hour video takes 30 minutes)
   - With parallel processing: Could process all videos in 1/7th the time

3. **Cloud Platform Options**:
   - Google Cloud Compute Engine with Tesla T4 GPU: ~$0.50/hour
   - AWS EC2 g4dn.xlarge instance: ~$0.55/hour
   - Azure NC-series VM: ~$0.60/hour
