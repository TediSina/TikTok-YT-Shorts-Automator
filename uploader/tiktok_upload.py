import os
from tiktok_uploader.upload import upload_videos, FailedToUpload
from tiktok_uploader.auth import AuthBackend

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def upload_tiktok(video_path, description, cookies) -> bool | None:
    """
    Uploads a TikTok video to the user's account.

    Args:
        video_path (str): The path to the video file to upload.
        description (str): The description for the uploaded video.
        cookies (str, optional): The path to the cookies file. If not provided, the default cookies file path will be used.

    Returns:
        bool | None: True if the video is uploaded successfully, None if an exception occurs.
    """
    try:
        if not cookies:
            cookies = BASE_DIR + r"\cookies.txt"

        videos = [
            {
                "path": video_path,
                "description": description
            }
        ]

        auth = AuthBackend(cookies=cookies)

        failed_list = upload_videos(videos=videos, auth=auth)
    except FailedToUpload as e:
        print(e)
        return None
    except Exception as e:
        print(e)
        return None
    else:
        if len(failed_list) == 0 or not failed_list:
            return True
        else:
            return None

if __name__ == "__main__":
    video_path = input("Enter the path to your video file (e.g., path_to_your_video_file.mp4): ").strip('"')
    description = input("Enter the description for your short video: ")
    cookies = input("Enter the cookies for your account (leave empty for default cookies.txt): ")

    upload_tiktok(video_path, description, cookies)
