from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def add_watermark_to_video(input_video, output_video="", watermark_text="Watermark", position="top", margin=20) -> str | None:
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

        # Check if the input video is landscape.
        is_landscape = video_clip.size[0] > video_clip.size[1]

        if is_landscape:
            # Calculate target dimensions for portrait orientation with 9:16 aspect ratio.
            target_height = min(video_clip.size)
            target_width = target_height * 9 // 16
            target_size = (target_width, target_height)

            # Resize video with black bars to maintain aspect ratio
            resized_video = video_clip.resize(target_size).on_color(size=target_size, color=(0, 0, 0))
        else:
            # If the input video is already portrait and at least 1:1 aspect ratio, no modifications needed.
            resized_video = video_clip

        # Create watermark
        font_size = min(resized_video.size[0], resized_video.size[1]) / 10
        font_color = "blue2"
        font = "Kalam"
        watermark = (TextClip(watermark_text, fontsize=font_size, color=font_color, font=font)
                        .set_position(("center", resized_video.size[1] - margin - font_size) if position == "bottom" else ("center", margin))
                        .set_duration(resized_video.duration))

        # Composite video with watermark.
        watermarked_video = CompositeVideoClip([resized_video.set_audio(None), watermark.set_audio(None)])
        watermarked_video = watermarked_video.set_audio(audio_clip)

        # Set max duration to 1 minute.
        if watermarked_video.duration > 60:
            watermarked_video = watermarked_video.subclip(0, 59.9)

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
    position = input("Enter position of watermark ('top' or 'bottom'): ").lower()
    margin = int(input("Enter margin for watermark: "))

    add_watermark_to_video(input_video, output_video, watermark_text, position, margin)
