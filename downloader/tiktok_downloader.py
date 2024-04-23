import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def validate_tiktok_url(url) -> bool:
    """
    Validates a TikTok video URL.

    Args:
        url (str): The URL to be validated.

    Returns:
        bool: True if the URL matches the pattern for a TikTok video URL, False otherwise.
    """
    # Regular expression pattern for TikTok video URL
    pattern = r'^https?://(?:www\.)?tiktok\.com/.+'
    return re.match(pattern, url) is not None

def download_tiktok(video_url) -> str | None:
    """
    Validates a TikTok video URL and downloads the video using a Chrome WebDriver session.

    Args:
        video_url (str): The URL of the TikTok video to be downloaded.

    Returns:
        str | None: The URL of the downloaded video if successful, None otherwise.
    """
    # Validate the TikTok video URL
    if not validate_tiktok_url(video_url):
        print("Invalid TikTok video URL.")
        return

    path_to_extension = BASE_DIR + r"\3.25_0"

    chrome_options = Options()
    chrome_options.add_argument("load-extension=" + path_to_extension)

    # Set the default download directory.
    download_dir = BASE_DIR + r"\Downloaded-TikToks"
    prefs = {"download.default_directory": download_dir}
    chrome_options.add_experimental_option("prefs", prefs)

    # Launch a browser session.
    with webdriver.Chrome(options=chrome_options) as driver: # You need to have Chrome WebDriver installed.
        # Ensure that window size is correct (needed to click the HD download button).
        driver.set_window_size(1705, 1372)
        # Open the target URL.
        driver.get("https://tikdownloader.io/en")

        time.sleep(5)

        driver.get("https://tikdownloader.io/en")

        # Find the input field by ID "s_input" and paste the video URL.
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "s_input"))
        )
        input_element.clear()
        input_element.send_keys(video_url)

        time.sleep(3)

        # Execute JavaScript to click the download button.
        driver.execute_script("ksearchvideo();")

        time.sleep(3)

        # Wait for the new page to load after the button click.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "search-result"))
        )

        # Execute JavaScript to simulate a click at specific coordinates (e.g., x=1200, y=225).
        driver.execute_script("document.elementFromPoint(1200, 225).click();")

        # Wait for the download to complete.
        download_complete = False
        timeout = 300  # Timeout in seconds.
        start_time = time.time()

        # Get the initial list of files in the download directory.
        initial_files = os.listdir(download_dir)

        while not download_complete and time.time() - start_time < timeout:
            # Wait for a short duration before checking again.
            time.sleep(5)

            # Get the current list of files in the download directory.
            current_files = os.listdir(download_dir)

            # Check if any new MP4 file has been added since the start of the download.
            new_files = [file for file in current_files if file not in initial_files]
            if any(file.endswith(".mp4") for file in new_files):
                download_complete = True

        if download_complete:
            downloaded_tiktok = [file for file in new_files if file.endswith(".mp4")]
            print("Download completed successfully.")
            return os.path.join(download_dir, downloaded_tiktok[0])
        else:
            print("Download did not complete within the specified timeout period.")
            return None

if __name__ == "__main__":
    video_url = input("TikTok Video URL: ")

    print(f"Downloaded video's path: {download_tiktok(video_url)}")
