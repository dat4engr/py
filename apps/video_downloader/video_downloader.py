import tkinter
import customtkinter
from pytube import YouTube

def start_download():
    try:
        youtube_link = link.get()
        youtube_object = YouTube(youtube_link, on_progress_callback=download_progress)
        video = youtube_object.streams.get_highest_resolution()
        title.configure(text=youtube_object.title)
        finish_label.configure(text="")
        finish_label.configure(text="Downloading")
        video.download()
        finish_label.configure(text="Download complete.", text_color="white")
    except:
        finish_label.configure(text="Download error.", text_color="red")

def download_progress(stream, chunk, bytes_remaining):
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
app.title("YouTube Downloader")

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
