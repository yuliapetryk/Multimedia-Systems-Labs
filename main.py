import os
from tkinter import *
import datetime
from tkinter import filedialog
import pygame
from PIL import Image, ImageTk
from tkVideoPlayer import TkinterVideo
from mutagen import File

# Initialize pygame mixer for audio
pygame.mixer.init()

# Constants for button size and colors
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50
PRIMARY_COLOR = "#4A90E2"
BACKGROUND_COLOR = "#FFFFFF"
TEXT_COLOR = "#333333"

# Initialize main application window
root = Tk()
root.title("MediaPlayer")
root.geometry("1200x700+200+10")
root.configure(bg=BACKGROUND_COLOR)

# Video player frame
player_frame = Frame(root, bg=BACKGROUND_COLOR)
player_frame.pack(expand=True, fill="both")

# Bottom control panel
control_panel = Frame(root, bg=BACKGROUND_COLOR, height=80)
control_panel.pack(fill="x", side=BOTTOM)

# Video player
player = TkinterVideo(player_frame, scaled=True)
player.pack(expand=True, fill="both")


# --- Functions ---
def update_duration(event):
    """Update the duration label and progress slider when video is loaded."""
    duration = player.video_info()["duration"]
    end_time_label.config(text=str(datetime.timedelta(seconds=duration)))
    progress_slider["to"] = duration


def update_audio_progress():
    """Update the progress slider and current time for audio playback."""
    if is_audio_playing:
        current_pos = pygame.mixer.music.get_pos() / 1000.0
        progress_value.set(int(current_pos))
        current_time_label.config(text=str(datetime.timedelta(seconds=int(current_pos))))
        root.after(100, update_audio_progress)


def update_progress(event):
    """Update the progress slider based on the current playback position."""
    progress_value.set(int(player.current_duration()))
    current_pos = int(progress_slider.get())
    current_time_label.config(text=str(datetime.timedelta(seconds=current_pos)))


# Flags to track if media is playing
is_video_playing = False
is_audio_playing = False


def open_file():
    """Open video or audio file"""
    global is_video_playing, is_audio_playing

    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv"),
                                                      ("Audio Files", "*.mp3;*.wav;*.flac;*.aac;*.ogg")])
    if file_path:
        _, file_extension = os.path.splitext(file_path)

        if is_video_playing:
            player.stop()
            player.pack_forget()
            play_pause_btn["text"] = "Play"
            is_video_playing = False
        elif is_audio_playing:
            pygame.mixer.music.stop()
            is_audio_playing = False
            play_pause_btn["text"] = "Play"

        if file_extension.lower() in ['.mp4', '.avi', '.mov', '.mkv']:
            player.load(file_path)
            player.play()
            play_pause_btn["text"] = "Pause"
            is_video_playing = True
        elif file_extension.lower() in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            play_pause_btn["text"] = "Pause"
            is_audio_playing = True

            audio_file = File(file_path)
            audio_duration = audio_file.info.length
            end_time_label.config(text=str(datetime.timedelta(seconds=audio_duration)))
            progress_slider["to"] = audio_duration

            update_audio_progress()


def seek(value):
    """Seek the video to a specific position."""
    if is_video_playing:
        player.seek(int(value))
    elif is_audio_playing:
        pygame.mixer.music.set_pos(int(value))


def skip(value):
    """Skip forward or backward by a specified number of seconds."""
    new_pos = int(progress_slider.get()) + value
    new_pos = max(0, min(new_pos, progress_slider["to"]))
    progress_value.set(new_pos)

    if is_video_playing:
        player.seek(new_pos)
    elif is_audio_playing:
        pygame.mixer.music.set_pos(new_pos)
        current_time_label.config(text=str(datetime.timedelta(seconds=new_pos)))

    progress_slider.set(new_pos)


def play_pause():
    """Toggle between play and pause for both video and audio."""
    if is_video_playing:
        if player.is_paused():
            player.play()
            play_pause_btn.config(text="Pause")
        else:
            player.pause()
            play_pause_btn.config(text="Play")
    elif is_audio_playing:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            play_pause_btn.config(text="Play")
        else:
            pygame.mixer.music.unpause()
            play_pause_btn.config(text="Pause")


def video_ended(event):
    """Handle video ending by resetting the player."""
    progress_slider.set(progress_slider["to"])
    play_pause_btn.config(text="Play")
    progress_slider.set(0)


def create_image_button(image_path, rotation=0, command=None):
    """Helper function to create image-based buttons with consistent styling."""
    img = Image.open(image_path).resize((BUTTON_WIDTH, BUTTON_HEIGHT), Image.Resampling.LANCZOS)
    if rotation:
        img = img.rotate(rotation, expand=True)
    photo_img = ImageTk.PhotoImage(img)
    btn = Button(control_panel, image=photo_img, bg=BACKGROUND_COLOR, activebackground=BACKGROUND_COLOR,
                 command=command, borderwidth=0)
    btn.image = photo_img
    return btn


# Time labels

current_time_label = Label(control_panel, text="0:00:00", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Arial", 12))
current_time_label.pack(side="left", padx=10)

end_time_label = Label(control_panel, text="0:00:00", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Arial", 12))
end_time_label.pack(side="right", padx=10)

# Buttons

# Forward button
forward_btn = create_image_button("resources/forward.png", command=lambda: skip(-5))
forward_btn.pack(side="left", padx=10)

# Progress slider
progress_value = IntVar()
progress_slider = Scale(
    control_panel,
    variable=progress_value,
    from_=0,
    to=0,
    orient="horizontal",
    command=seek,
    bg=BACKGROUND_COLOR,
    fg=PRIMARY_COLOR,
    highlightthickness=0,
    troughcolor="#DDDDDD",
    sliderrelief="flat",
)
progress_slider.pack(side="left", fill="x", expand=True, padx=10)

# Backward button
back_btn = create_image_button("resources/forward.png", rotation=180, command=lambda: skip(5))
back_btn.pack(side="left", padx=10)

# Container frame for the buttons
button_frame = Frame(root, bg="#FFFFFF")
button_frame.pack(side="top", anchor="nw", padx=10, pady=10)

# Video button
open_btn = Button(
    button_frame,
    text="Open",
    font=("Arial", 12),
    bg=PRIMARY_COLOR,
    fg=BACKGROUND_COLOR,
    activebackground="#357ABD",
    activeforeground=BACKGROUND_COLOR,
    command=open_file,
    width=10,
    height=1,
    borderwidth=0,
    relief="flat",
)
open_btn.pack(side="left", padx=10)

# Play/Pause button
play_pause_btn = Button(
    button_frame,
    text="Play",
    font=("Arial", 12),
    bg=PRIMARY_COLOR,
    fg=BACKGROUND_COLOR,
    activebackground="#357ABD",
    activeforeground=BACKGROUND_COLOR,
    command=play_pause,
    width=10,
    height=1,
    borderwidth=0,
    relief="flat",
)
play_pause_btn.pack(side="left", padx=10)

# --- Event Bindings ---
player.bind("<<Duration>>", update_duration)
player.bind("<<SecondChanged>>", update_progress)
player.bind("<<Ended>>", video_ended)

# Start the application
root.mainloop()
