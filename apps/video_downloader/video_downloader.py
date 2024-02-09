import tkinter
import customtkinter
from pytube import YouTube

def start_download():
    # Starts the video download process when the 'Download' button is clicked.
    try:
        youtube_link = link.get()
        youtube_object = YouTube(youtube_link, on_progress_callback=download_progress)
        video = get_highest_resolution_video(youtube_object)
        set_title(youtube_object)
        set_finish_label("Downloading")
        download_video(video)
        set_finish_label("Download complete.", text_color="white")
    except:
        set_finish_label("Download error.", text_color="red")

def get_highest_resolution_video(youtube_object):
    # Returns the video stream with the highest resolution of the given YouTube object.
    return youtube_object.streams.get_highest_resolution()

def set_title(youtube_object):
    # Sets the title of the YouTube video in the GUI label.
    title.configure(text=youtube_object.title)

def set_finish_label(text, text_color=None):
    # Updates the finish_label with the given text and text color.
    finish_label.configure(text=text, text_color=text_color)

def download_video(video):
    # Downloads the given video stream.
    video.download()

def download_progress(stream, chunk, bytes_remaining):
    # Updates the GUI with the current progress of the video download.
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f"Current downloading: {percentage_of_completion}")

    per = str(int(percentage_of_completion))
    progress_percentage.configure(text=per + '%')
    progress_percentage.update()

    progress_bar.set(float(percentage_of_completion) / 100)

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x480")
app.title("Any Video Downloader")

title = customtkinter.CTkLabel(app, text="Insert a YouTube link")
title.pack(padx=10, pady=10)

url_variable = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_variable)
link.pack()

finish_label = customtkinter.CTkLabel(app, text="")
finish_label.pack()

progress_percentage = customtkinter.CTkLabel(app, text="0%")
progress_percentage.pack()

progress_bar = customtkinter.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(padx=10, pady=10)

download = customtkinter.CTkButton(app, text="Download", command=start_download)
download.pack(padx=10, pady=10)

app.mainloop()
