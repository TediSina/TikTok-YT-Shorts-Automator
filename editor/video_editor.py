from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def ensure_video_is_portrait(existing_clip: CompositeVideoClip) -> CompositeVideoClip:
    """
    Inserts an existing CompositeVideoClip into a centered empty black clip with a square 1:1 aspect ratio, only if the existing clip is landscape.

    Parameters:
        existing_clip (CompositeVideoClip): The existing CompositeVideoClip to be centered.

    Returns:
        CompositeVideoClip: The composite video clip with the existing clip centered on an empty black clip, or the original clip if it's portrait.
    """
    # Check if the existing clip is portrait or square.
    if existing_clip.size[0] <= existing_clip.size[1]:
        # Return the original clip if it's portrait or square.
        return existing_clip

    # Calculate the aspect ratio of the input clip.
    input_aspect_ratio = existing_clip.size[0] / existing_clip.size[1]

    # Calculate the height of the resized clip to fit the target aspect ratio.
    target_width = existing_clip.size[0]

    # Calculate the height of the resized clip to fit the target aspect ratio.
    target_height = existing_clip.size[1] * input_aspect_ratio

    # Create the empty black clip with the same duration and dimensions as the existing clip.
    empty_black_clip = ColorClip(size=(int(target_width), int(target_height)), color=(0, 0, 0), duration=existing_clip.duration)

    # Composite the existing clip onto the empty black clip, centering it vertically.
    centered_clip = CompositeVideoClip([empty_black_clip, existing_clip.set_position(("center"))])

    return centered_clip


def add_watermark_to_video(input_video: str, output_video="", watermark_text="Watermark", position="top", margin=20) -> str | None:
    """
    Adds a watermark to a video.

    Args:
        input_video (str): The path to the input video file.
        output_video (str, optional): The path to the output video file. If not provided, the output video file will be saved in the "Edited-Videos" directory with the same name as the input video file.
        watermark_text (str, optional): The text to be added as a watermark. Defaults to "Watermark".
        position (str, optional): The position of the watermark on the video. Can be "top" or "bottom". Defaults to "top".
        margin (int, optional): The margin between the watermark and the edges of the video. Defaults to 20.

    Returns:
        str | None: The path to the output video file if the watermark was successfully added, None otherwise.

    Raises:
        Exception: If an error occurs while adding the watermark to the video.
    """
    try:
        if not output_video:
            output_video = os.path.join(BASE_DIR + r"\Edited-Videos", os.path.basename(input_video))

        print(f"Output video path: {output_video}")

        video_clip = VideoFileClip(input_video)
        audio_clip = video_clip.audio

        # Create watermark
        font_size = min(video_clip.size[0], video_clip.size[1]) / 10
        font_color = "blue2"
        font = "Kalam"
        watermark = (TextClip(watermark_text, fontsize=font_size, color=font_color, font=font)
                        .set_position(("center", video_clip.size[1] - margin - font_size) if position == "bottom" else ("center", margin))
                        .set_duration(video_clip.duration))

        # Composite video with watermark.
        watermarked_video = CompositeVideoClip([video_clip.set_audio(None), watermark.set_audio(None)])
        watermarked_video = watermarked_video.set_audio(audio_clip)

        # Set max duration to 1 minute.
        if watermarked_video.duration > 60:
            watermarked_video = watermarked_video.subclip(0, 59.9)
        
        # Insert centered empty clip if video is portrait.
        watermarked_video = ensure_video_is_portrait(watermarked_video)

        # Write video with optimized codecs and multithreading.
        watermarked_video.write_videofile(output_video, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, threads=12)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    else:
        return output_video

if __name__ == "__main__":
    input_video = input("Enter input video file path: ").strip('"')
    output_video = input("Enter output video file path (leave empty for default): ").strip('"')
    watermark_text = input("Enter watermark text: ")
    while True:
        position = input("Enter the watermark position ('top' or 'bottom'): ").lower()
        if position in ["top", "bottom"]:
            break
    margin = int(input("Enter margin for watermark: "))

    add_watermark_to_video(input_video, output_video, watermark_text, position, margin)
