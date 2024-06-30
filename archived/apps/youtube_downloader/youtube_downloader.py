import tkinter
import customtkinter
from pytube import YouTube
from pytube import Playlist
from tkinter import filedialog
import re

def start_download():
    try:
        video_link = link.get()
        
        if "playlist?list=" in video_link:
            playlist = Playlist(video_link)
            save_location = filedialog.askdirectory()
            playlist.download_all(output_path=save_location)
            finish_label.configure(text="Playlist download complete.", text_color="green")
        else:
            if validate_video_link(video_link):
                yt = YouTube(video_link)
                stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
                save_location = filedialog.asksaveasfilename(defaultextension=".mp4")
                stream.download(output_path=save_location)
                finish_label.configure(text="a download complete.", text_color="green")
            else:
                finish_label.configure(text="Invalid video URL.", text_color="red")
    except Exception as e:
        finish_label.configure(text="Download error.", text_color="red")
        print(e)

def validate_video_link(url):
    video_regex = r'(https?://)?(www\.)?.+\.(com|org|net)'
    match = re.match(video_regex, url)
    return match is not None

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("720x480")
app.title("Video Downloader")

title = customtkinter.CTkLabel(app, text="Insert a video link")
title.pack(padx=10, pady=10)

url_variable = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url_variable)
link.pack()

finish_label = customtkinter.CTkLabel(app, text="")
finish_label.pack()

download = customtkinter.CTkButton(app, text="Download", command=start_download)
download.pack(padx=10, pady=10)

app.mainloop()
