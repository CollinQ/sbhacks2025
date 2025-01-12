import cv2
import os
import json
from tqdm import tqdm  # For progress bar
from dotenv import load_dotenv
from supabase import create_client, Client
def timestamp_to_frame(timestamp, fps):
    print(f"[DEBUG] Timestamp: {timestamp}")
    timestamp_parts = timestamp.split(":")
    seconds = int(timestamp_parts[0]) * 60 + int(timestamp_parts[1]) + 2
    print(f"[DEBUG] Seconds: {int(seconds)}")
    return int(seconds * fps)


def save_frames(df_final_json):
    # Load environment variables
    load_dotenv()
    
    video_path = os.getenv('PATH_TO_VIDEO_FILE')
    if not video_path:
        raise ValueError("PATH_TO_VIDEO_FILE environment variable is not set")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at path: {video_path}")
        
    # Create a directory to save frames
    output_dir = "saved_frames"
    os.makedirs(output_dir, exist_ok=True)


    # Load video
    video_capture = cv2.VideoCapture(video_path)

    # Go through video and upload individual frames to Supabase
    if not video_capture.isOpened():
        print("[INFO] Error: Could not open video.")
        return []
    else:
        # Set up Supabase client
        url = os.getenv("SUPABASE_PROJECT_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        supabase = create_client(url, key)

        fps = video_capture.get(cv2.CAP_PROP_FPS)  # Video frames per second
        print(f"[INFO] Video FPS: {fps}")

        image_urls = []

        # Iterate through the JSON data with a progress bar
        for item in tqdm(df_final_json, total=len(df_final_json), desc="Processing frames"):
            try:
                # Get frame number from timestamp
                frame_number = timestamp_to_frame(item["timestamp"], fps)
                print(f"[DEBUG] Frame number: {frame_number}")
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                success, frame = video_capture.read()

                if not success:
                    print(f"Warning: Could not read frame at timestamp {item['timestamp']} (frame {frame_number}).")
                    image_urls.append(None)
                    continue

                # Convert frame to jpg bytes
                _, buffer = cv2.imencode('.jpg', frame)
                image_bytes = buffer.tobytes()

                # Upload to Supabase storage
                file_name = f"frame_{item['item_number']}.jpg"
                bucket_name = "item-images"
                try:
                    response = supabase.storage.from_(bucket_name).upload(
                        f"frame_{item['id']}.jpg",
                        image_bytes,
                        {"content-type": "image/jpeg"}
                    )
                    
                    # Get public URL
                    image_url = supabase.storage.from_(bucket_name).get_public_url(f"frame_{item['id']}.jpg")
                    image_urls.append(image_url)
                    print(f"[INFO] Uploaded frame {item['id']} to Supabase")

                except Exception as e:
                    print(f"Error uploading to Supabase: {e}")
                    image_urls.append(None)

            except Exception as e:
                print(f"Error processing item {item['item_number']}: {e}")
                print(f"[DEBUG] Item: {item}")
                print(f"[DEBUG] Timestamp: {item['timestamp']}")
                image_urls.append(None)
                continue

        print(f"\n[INFO] Uploaded {len([url for url in image_urls if url is not None])} frames to Supabase")
        return image_urls

