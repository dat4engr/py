import tkinter
import customtkinter
from pytube import YouTube
from tkinter import filedialog
import re

# Functions for start downloading
def startDownload():
    try:
        youtube_link = link.get()
        
        # Validate YouTube URL
        if not validateYouTubeUrl(youtube_link):
            finish_label.configure(text="Invalid YouTube URL.", text_color="red")
            return
        
        youtube_object = YouTube(youtube_link, on_progress_callback=downloadProgress)
        video = youtube_object.streams.get_highest_resolution()
        title.configure(text=youtube_object.title)
        finish_label.configure(text="")
        finish_label.configure(text="Downloading")
        save_location = filedialog.asksaveasfilename(defaultextension=".mp4")
        video.download(output_path=save_location)
        finish_label.configure(text="Download complete.", text_color="white")
    except Exception as e:
        finish_label.configure(text="Download error.", text_color="red")
        print(e)

def downloadProgress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f"Current downloading: {percentage_of_completion}%")
    
    # Updating progress percentage
    per = str(int(percentage_of_completion))
    progress_percentage.configure(text=per + '%')
    progress_percentage.update()

    # Updating progress bar
    progress_bar.set(float(percentage_of_completion) / 100)

def validateYouTubeUrl(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    match = re.match(youtube_regex, url)
    return match is not None

# Replicate system theme settings and color scheme
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# App framing, resolution, and title
app = customtkinter.CTk()
app.geometry("720x480")
app.title("YouTube Downloader")

# Adding UI elements
title = customtkinter.CTkLabel(app, text="Insert a YouTube link")
title.pack(padx=10, pady=10)

# Link input
url_variable = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_variable)
link.pack()

# Finished downloading
finish_label = customtkinter.CTkLabel(app, text="")
finish_label.pack()

# Progress percentage and bar
progress_percentage = customtkinter.CTkLabel(app, text="0%")
progress_percentage.pack()

progress_bar = customtkinter.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(padx=10, pady=10)

# Download button
download = customtkinter.CTkButton(app, text="Download", command=startDownload)
download.pack(padx=10, pady=10)

# App run
app.mainloop()