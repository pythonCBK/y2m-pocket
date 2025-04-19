# KiVyMD import
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.app import App
from kivy.app import platform

# Main import
import webbrowser
from yt_dlp import YoutubeDL
import threading
import os
import yt_dlp

# Variables
format_choice = "audio"
last_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


### === Global definitions === ###

# Get duration
def duration(seconds):
    if seconds is None:
        return "Unknown"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}:{minutes:02}:{secs:02}" if hours else f"{minutes}:{secs:02}"


# Download function
def download(url, format_choice):
    print("Please wait...")
    if not url:
        print("No URL")
        return
    
    download_thread = threading.Thread(target=download_file, args=(url, format_choice))
    download_thread.start()

def download_file(url, format_choice):
    if platform == 'android':
        from kivy.app import App
        downloads_path = App.get_running_app().user_data_dir
    else:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    os.makedirs(downloads_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best' if format_choice == "audio" else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"File successfully saved in: {downloads_path}")
    except Exception as e:
        print(f"Error: {e}")


### === App === ###
class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.primary_palette = "Midnightblue"  # App color palette
        self.theme_cls.primary_hue = "100"
        self.theme_cls.theme_style = "Dark" # App theme
        return Builder.load_file('app_ui.kv')  # Load UI file

    def on_start(self):
        self.title = "Y2M Pocket" # App title




### === Functions === ###

    # GitHub btn
    def github(self):
        webbrowser.open("https://github.com/pythonCBK/y2m-pocket")

    # Proceed
    def result(self):
        global last_url
        url = self.root.ids.entry.text.strip()

        if not url:
            print("No URL!")
            return
        
        last_url = url

        self.root.ids.btn_download.disabled = True

        options = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': False,
            'no_warnings': True
        }

        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        if "entries" in info and info["entries"]:
            first_track = info["entries"][0]
        else:
            first_track = info


        ## If album/playlist
        if "entries" in info and info["entries"]:
            track_count = len(info["entries"])

            # If one tracks
            if track_count == 1:
                track_info = info["entries"][0]
                return {
                    "type": "track",
                    "title": track_info.get("title") or info.get("title"),
                    "artist": track_info.get("artist") or track_info.get("uploader") or "Unknown",
                    "duration": duration(track_info.get("duration")),
                    "thumbnail": track_info.get("thumbnail") or info.get("thumbnail")
                }
            
            # Album or playlist
            else:
                return {
                    "type": "playlist",
                    "title": info.get("title") or first_track.get("album") or "Unknow",
                    "artist": info.get("artist") or first_track.get("artist") or info.get("uploader") or "Unknown",
                    "track_count": track_count,
                    "thumbnail": info.get("thumbnail") or info["entries"][0].get("thumbnail")
                }
        
        else:
            return {
            "type": "track",
            "title": info.get("title"),
            "artist": info.get("artist") or info.get("uploader") or "Unknown",
            "duration": duration(info.get("duration")),
            "thumbnail": info.get("thumbnail")
        }
        

    def proceed(self):
        content = self.result()

        if content is None:
            print("Some problem kaput!")
            return
        
        print(last_url)
        self.root.ids.btn_download.disabled = False
        

        if content["type"] == "track":
            print("Type: song/video")
            print("Name:", content["title"])
            print("Artist:", content["artist"])
            print("Duration:", content["duration"])
            print("Cover:", content["thumbnail"])

            self.root.ids.song_info.text = f"{content["title"]}\nArtist: {content["artist"]}\nDuration: {content["duration"]}"
            self.root.ids.cover.source = content["thumbnail"]

        elif content["type"] == "playlist":
            print("Type: albom/playlist")
            print("Name:", content["title"])
            print("Artist:", content["artist"])
            print("Tracks amount:", content["track_count"])
            print("Cover:", content["thumbnail"])

            self.root.ids.song_info.text = f"{content["title"]}\nArtist: {content["artist"]}\nTracks amount: {content["track_count"]}"
            self.root.ids.cover.source = content["thumbnail"]



    def call_dwnl(self):
        print("Download button pressed")
        global last_url
        global format_choice

        format = format_choice
        url = last_url
        download(url, format)




### === System === ###

    ## Format update
    def format_upd(self, option):
        global format_choice
        format_choice = option
        print("Format updated:", format_choice)




MainApp().run()