import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class YouTubeUploader:
    def __init__(self, client_secrets_file=BASE_DIR + r"\client_secrets.json"):
        """
        Initializes the class with the given client secrets file.

        Parameters:
            client_secrets_file (str): The file containing client secrets.

        Returns:
            None
        """
        self.client_secrets_file = client_secrets_file
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.api_service_name = 'youtube'
        self.api_version = 'v3'
        self.youtube = self.get_authenticated_service()

    def get_authenticated_service(self):
        """
        Returns an authenticated Google API service using the provided client secrets file, scopes, service name, and version.
        """
        credentials = self.load_credentials()
        if credentials is None:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, self.scopes)
            credentials = flow.run_local_server(port=0)
            self.save_credentials(credentials)
        return googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials)

    def save_credentials(self, credentials):
        """
        Saves the provided credentials to a file.

        Parameters:
            credentials: The credentials to be saved.

        Returns:
            None
        """
        with open(BASE_DIR + r"\youtube_credentials.pkl", "wb") as token:
            pickle.dump(credentials, token)

    def load_credentials(self):
        """
        A function to load credentials. Checks if the credentials file exists, then loads and returns the credentials.
        Returns None if the file does not exist.
        """
        if os.path.exists(BASE_DIR + r"\youtube_credentials.pkl"):
            with open(BASE_DIR + r"\youtube_credentials.pkl", "rb") as token:
                return pickle.load(token)
        return None

    def upload_video(self, video_path, title, description, tags=None):
        """
        Uploads a video to YouTube using the provided video path, title, description, and optional tags.
        
        Parameters:
            video_path (str): The path to the video file.
            title (str): The title of the video.
            description (str): The description of the video.
            tags (list): Optional list of tags for the video. Default is an empty list.
        
        Returns:
            str: The video ID of the uploaded video if successful, None otherwise.
        """
        request_body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags if tags else []
            },
            "status": {
                "privacyStatus": "public"
            }
        }

        try:
            response = self.youtube.videos().insert(
                part="snippet,status",
                body=request_body,
                media_body=video_path
            ).execute()

            video_id = response["id"]
            print(f"Video uploaded successfully. Video ID: {video_id}")

            # Like the uploaded video
            self.like_video(video_id)

            return video_id

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def like_video(self, video_id):
        """
        Likes the video with the specified video ID.

        Parameters:
            video_id (str): The ID of the video to be liked.

        Returns:
            None
        """
        try:
            self.youtube.videos().rate(
                id=video_id,
                rating="like"
            ).execute()
            print("Video liked successfully.")
        except googleapiclient.errors.HttpError as e:
            print(f'An error occurred while liking the video: {e}')


if __name__ == '__main__':
    video_path = input("Enter the path to your video file (e.g., path_to_your_video_file.mp4): ").strip('"')
    title = input("Enter the title for your short video: ")
    description = input("Enter the description for your short video: ")
    tags = input("Enter tags for your short video (comma-separated, e.g., tag1,tag2,tag3): ").split(',')

    uploader = YouTubeUploader()
    uploader.upload_video(video_path, title, description, tags)
