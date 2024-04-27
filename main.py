import sqlite3
import os

from downloader.tiktok_downloader import download_tiktok, validate_tiktok_url
from editor.video_editor import add_watermark_to_video
from uploader.tiktok_upload import upload_tiktok
from uploader.youtube_uploader import YouTubeUploader

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Connect to SQLite database
conn = sqlite3.connect(BASE_DIR + r'\video_info.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS video_info
             (tiktok_url TEXT, video_description TEXT, watermark_position TEXT,
             downloaded_tiktok TEXT, edited_video TEXT, tiktok_is_uploaded TEXT, youtube_video_id TEXT)''')
conn.commit()


def save_video_info(tiktok_url, video_description, watermark_position, downloaded_tiktok,
                    edited_video, tiktok_is_uploaded, youtube_video_id) -> None:
    """
    Save video download info to SQLite3 database.
    """
    c.execute("INSERT INTO video_info VALUES (?, ?, ?, ?, ?, ?, ?)",
              (tiktok_url, video_description, watermark_position, downloaded_tiktok,
               edited_video, tiktok_is_uploaded, youtube_video_id))
    conn.commit()


def upload_new_video() -> bool:
    """
    Uploads a new video to TikTok and YouTube.

    This function prompts the user to enter the TikTok video URL, video description, and watermark position. It then validates the TikTok URL, checks the length of the video description, and ensures the watermark position is either "top" or "bottom".

    The function downloads the TikTok video using the `download_tiktok` function from the `downloader.tiktok_downloader` module. It adds a watermark to the downloaded video using the `add_watermark_to_video` function from the `editor.video_editor` module.

    The edited video is then uploaded to TikTok using the `upload_tiktok` function from the `uploader.tiktok_upload` module. After that, the video is uploaded to YouTube using the `upload_video` method of the `YouTubeUploader` class from the `uploader.youtube_uploader` module.

    If any exception occurs during the process, an error message is printed and the function returns `False`. Otherwise, it returns `True`.

    Returns:
        bool: `True` if the video is successfully uploaded, `False` otherwise.
    """
    tiktok_url = None
    video_description = None
    watermark_position = None
    downloaded_tiktok = None
    edited_video = None
    tiktok_is_uploaded = None
    youtube_video_id = None
    
    while True:
        tiktok_url = input("Enter the TikTok video URL: ")
        if validate_tiktok_url(tiktok_url):
            break

    while True:
        video_description = input("Enter the video description (max. 100 characters): ")
        if len(video_description) <= 100:
            break

    while True:
        watermark_position = input("Enter the watermark position ('top' or 'bottom'): ").lower()
        if watermark_position in ["top", "bottom"]:
            break

    try:
        downloaded_tiktok = download_tiktok(tiktok_url)

        edited_video = add_watermark_to_video(downloaded_tiktok, watermark_text=os.getenv("WATERMARK_TEXT"), position=watermark_position, margin=20)

        tiktok_is_uploaded = upload_tiktok(edited_video, video_description, BASE_DIR + r"\uploader\cookies.txt")

        youtube_uploader = YouTubeUploader()
        youtube_video_id = youtube_uploader.upload_video(edited_video, title=video_description, description=video_description)
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        save_video_info(tiktok_url, video_description, watermark_position, downloaded_tiktok,
                        edited_video, tiktok_is_uploaded, youtube_video_id)
    return True


def upload_failed_video() -> bool:
    """
    Uploads failed videos from the database.
    
    This function retrieves failed videos from the 'video_info' table in the database. The failed videos are selected based on the following conditions:
    - 'downloaded_tiktok' is NULL
    - 'edited_video' is NULL and 'downloaded_tiktok' is not NULL
    - 'tiktok_is_uploaded' is 0 and 'edited_video' is not NULL
    - 'youtube_video_id' is NULL or 'tiktok_is_uploaded' is NULL
    
    For each failed video, the function performs the following steps:
    - If 'downloaded_tiktok' is None, it downloads the TikTok video using the 'download_tiktok' function. If the download is successful, it updates the 'video_info' table with the downloaded TikTok video.
    - If 'edited_video' is None, it adds a watermark to the downloaded TikTok video using the 'add_watermark_to_video' function. If the watermarking is successful, it updates the 'video_info' table with the edited video.
    - If 'tiktok_is_uploaded' is None, it uploads the edited video to TikTok using the 'upload_tiktok' function. If the upload is successful, it updates the 'video_info' table with the upload status.
    - If 'youtube_video_id' is None, it uploads the edited video to YouTube using the 'YouTubeUploader' class. If the upload is successful, it updates the 'video_info' table with the YouTube video ID.
    
    If all failed videos are successfully processed, the function returns True. If any error occurs during the process, the function prints the error message and returns False.
    
    Returns:
        bool: True if all failed videos are successfully processed, False otherwise.
    """
    try:
        # Get failed videos from the database in priority order
        c.execute("SELECT * FROM video_info WHERE downloaded_tiktok IS NULL OR edited_video IS NULL OR tiktok_is_uploaded IS NULL OR youtube_video_id IS NULL")
        failed_videos = c.fetchall()

        if len(failed_videos) == 0:
            print("No failed videos found.")
            return True
        
        for video_info in failed_videos:
            tiktok_url, video_description, watermark_position, downloaded_tiktok, edited_video, tiktok_is_uploaded, youtube_video_id = video_info

            if downloaded_tiktok is None:
                downloaded_tiktok = download_tiktok(tiktok_url)
                
                if downloaded_tiktok is not None:
                    c.execute("UPDATE video_info SET downloaded_tiktok=? WHERE tiktok_url=?", (downloaded_tiktok, tiktok_url))
                    conn.commit()

            if edited_video is None:
                edited_video = add_watermark_to_video(downloaded_tiktok, watermark_text="SportsFirm", position=watermark_position, margin=20)

                if edited_video is not None:
                    c.execute("UPDATE video_info SET edited_video=? WHERE tiktok_url=?", (edited_video, tiktok_url))
                    conn.commit()

            if tiktok_is_uploaded is None:
                tiktok_is_uploaded = upload_tiktok(edited_video, video_description, BASE_DIR + r"\uploader\cookies.txt")
                
                if tiktok_is_uploaded is not None:
                    c.execute("UPDATE video_info SET tiktok_is_uploaded=? WHERE tiktok_url=?", (tiktok_is_uploaded, tiktok_url))
                    conn.commit()

            if youtube_video_id is None:
                youtube_uploader = YouTubeUploader()
                youtube_video_id = youtube_uploader.upload_video(edited_video, title=video_description, description=video_description)

                if youtube_video_id is not None:
                    c.execute("UPDATE video_info SET youtube_video_id=? WHERE tiktok_url=?", (youtube_video_id, tiktok_url))
                    conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    else:
        return True


if __name__ == "__main__":
    new_video = input("Do you want to upload a new video? (Type 'yes' or 'y' to proceed): ")

    if new_video.lower() == "yes" or new_video.lower() == "y":
        upload_new_video() # Upload new video

    failed_video = input("Do you want to upload a failed video? (Type 'yes' or 'y' to proceed): ")

    if failed_video.lower() == "yes" or failed_video.lower() == "y":
        upload_failed_video() # Upload failed video

    print("Goodbye!")
    conn.close()
