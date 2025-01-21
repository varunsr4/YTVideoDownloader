import face_recognition
import cv2
import os
from datetime import timedelta


def load_trump_encoding():
    print("Loading Trump reference image...")
    try:
        trump_image = face_recognition.load_image_file("trump_reference.jpg")
        trump_encoding = face_recognition.face_encodings(trump_image)[0]
        print("Successfully loaded and encoded reference image")
        return trump_encoding
    except Exception as e:
        print(f"Error loading reference image: {e}")
        raise


def detect_trump_timestamps(video_path, trump_encoding):
    print(f"Starting face detection on {video_path}")
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        print(f"Error: Could not open video {video_path}")
        return []

    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video info: {total_frames} frames at {fps} fps")
    sample_rate = 1  # Sample every 1 second
    print(f"Will sample every {sample_rate} seconds")

    timestamps = []
    frame_number = 0
    frames_processed = 0

    while frame_number < total_frames:
        ret, frame = video.read()
        if not ret:
            print(f"Failed to read frame at position {frame_number}")
            break

        if frame_number % int(fps * sample_rate) != 0:
            frame_number += 1
            continue

        frames_processed += 1
        rgb_frame = frame[:, :, ::-1]
        # Reduce frame size by 25%
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.75, fy=0.75)

        try:
            # Use 'hog' model for better performance at cost of accuracy
            face_locations = face_recognition.face_locations(small_frame, model="hog")
            if face_locations:
                print(f"Found {len(face_locations)} faces in frame {frame_number}")
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)

                for encoding in face_encodings:
                    # Slightly increase tolerance for better performance (standard 0.7)
                    matches = face_recognition.compare_faces([trump_encoding], encoding, tolerance=0.65)
                    if matches[0]:
                        timestamp = frame_number / fps
                        timestamps.append(timestamp)
                        print(f"Found Trump at {timestamp:.2f} seconds")
                        break
        except Exception as e:
            print(f"Error processing frame {frame_number}: {e}")

        frame_number += 1
        if frame_number % int(fps * sample_rate * 5) == 0:
            print(f"Progress: {frame_number / total_frames * 100:.1f}% ({len(timestamps)} Trump appearances)")

    video.release()
    print(f"Finished processing {frames_processed} frames, found Trump in {len(timestamps)} frames")
    return timestamps


def trim_video(input_path, output_path, ranges):
    """Trim video to only keep ranges where Trump appears"""
    if not ranges:
        return False

    print(f"Starting video trimming for {len(ranges)} segments")
    try:
        # Create a filter complex for direct concatenation
        filter_complex = ""
        inputs = ""
        
        for i, (start, end) in enumerate(ranges):
            inputs += f" -ss {start} -t {end-start} -i \"{input_path}\""
            filter_complex += f"[{i}:v][{i}:a]"

        # Single FFmpeg command that handles all segments at once
        # Handle both video and audio streams properly in the filter complex
        filter_complex += f"concat=n={len(ranges)}:v=1:a=1[outv][outa];[outv]scale=-2:720[vout]"
        concat_str = f"ffmpeg {inputs} -filter_complex \"{filter_complex}\" "
        concat_str += f"-map \"[vout]\" -map \"[outa]\" -c:v h264_videotoolbox -b:v 2M -c:a aac \"{output_path}\" -loglevel error"
        
        print("Processing segments...")
        os.system(concat_str)
        return True
    except Exception as e:
        print(f"Error during video trimming: {e}")
        return False