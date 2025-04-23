from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import (
    MDSnackbar,
    MDSnackbarSupportingText,
    MDSnackbarText,
)

import json
import os
import threading
import webbrowser
import yt_dlp
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError

### ===== Load settings ===== ###
## Load settings
def load_settings():
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    return settings

## Save settings
def save_settings(settings):
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

### ===== Variables ===== ###
format = "audio"

### ===== App ===== ###
class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            selector='folder',
            search='dirs'
        )

    def build(self):
        settings = load_settings()

        self.theme_cls.primary_palette = "Midnightblue"  # App color palette
        self.theme_cls.theme_style = settings['theme'] # App theme
        return Builder.load_file('ui.kv')  # Load UI file

    def on_start(self):
        settings = load_settings()

        self.title = "Y2M Pocket" # App title
        self.root.ids.current_dir.text = settings['save_folder'] # Save folder path






    ### ===== File manager ===== ###

    def select_directory(self):
        self.file_manager.show(
            os.path.expanduser("~"))  # output manager to the screen
        self.manager_open = True

    def select_path(self, path: str):
        print("Chosen path:", path)

        settings = load_settings()
        settings['save_folder'] = path
        save_settings(settings)

        self.root.ids.current_dir.text = settings['save_folder']

        self.exit_manager()

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    ## CHeck if directory exists
    def directory_check(self):
        settings = load_settings()

        directory_to_check = settings['save_folder']

        if os.path.isdir(directory_to_check):
            print("Directory exists")
            return "dir.ok"
        else:
            print("Directory does not exist")

            notification = MDSnackbar(
                MDSnackbarText(
                    text = "Error!",
                ),
                MDSnackbarSupportingText(
                    text = "No such directory! Select new one and try again!",
                ),
                y=dp(10),
                orientation="horizontal",
                pos_hint={"center_x": 0.5},
                size_hint_x=0.8,
            )
            notification.open()



            return None
        





    ### ===== Buttons ===== ###

    ## Swicth app theme
    def switch_theme(self):
        settings = load_settings()
        current_theme = settings['theme']

        if current_theme == "Light":
            self.theme_cls.theme_style = "Dark"
            settings['theme'] = "Dark"
            save_settings(settings)

        else:
            self.theme_cls.theme_style = "Light"
            settings['theme'] = "Light"
            save_settings(settings)

    ## Format update
    def format_update(self, option):
        global format
        format = option
        print("Format updated:", format)
    
    # GitHub btn
    def github(self):
        webbrowser.open("https://github.com/pythonCBK/y2m-pocket")

























    ### ===== Information request ===== ###

    def download_file(self, url, format):
        settings = load_settings()

        downloads_path = settings['save_folder']

        os.makedirs(downloads_path, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best' if format == "audio" else 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            print(f"File successfully saved in: {downloads_path}")

            def notification_complete(dt):
                downloads_path = settings['save_folder']

                notification = MDSnackbar(
                            MDSnackbarText(
                                text = "Download completed",
                            ),
                            MDSnackbarSupportingText(
                                text = f"File successfully saved in {downloads_path}",
                            ),
                            y=dp(10),
                            orientation="horizontal",
                            pos_hint={"center_x": 0.5},
                            size_hint_x=0.8,
                        )
                notification.open()

                self.root.ids.progress.stop()
                self.root.ids.progress.opacity = 0
                
            Clock.schedule_once(notification_complete)


        except Exception as e:
            print(f"Error: {e}")



    def download(self, url, format):
        print("Please wait...")
        if not url:
            print("No URL")
            return
        
        dir_check = self.directory_check()

        if not dir_check:
            print("Please select another directory and try again.")
            return
        
        self.root.ids.progress.start()
        self.root.ids.progress.opacity = 1
        
        download_thread = threading.Thread(target=self.download_file, args=(url, format))
        download_thread.start()



    def call_download(self):
        global format
        url = self.root.ids.input_link.text.strip()

        self.download(url, format)



















    ### ===== Information request ===== ###
    def duration(self, time):
        if time is None:
            return "Unknown"

        hours = time // 3600 # Получаем ЦЕЛЫЕ часы без остатка
        minutes = (time % 3600) // 60 # От остатка часов получаем ЦЕЛЫЕ минуты
        seconds = time % 60 # Получаем ОСТАТОК от минут

        # If song duration is more than an hour
        if hours:
            return f"{hours}:{minutes:02}:{seconds:02}"
        # If duration is less than an hour
        else:
            return f"{minutes}:{seconds:02}"


    
    def information_request(self):

        # Get text from input field
        url = self.root.ids.input_link.text.strip()

        # Set options for yt_dlp request
        class QuietLogger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        request_options = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': False,
            'no_warnings': True,
            'logger': QuietLogger()
        }

        try:
            with YoutubeDL(request_options) as yt_dlp:
                information_request = yt_dlp.extract_info(url, download=False)

        except (DownloadError, ExtractorError) as e:
            print(f"Error extracting info: {e}")
            self.root.ids.information.text = "Error: some content requires age verification or login."
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.root.ids.information.text = "Unexpected error occurred."
            return None

        # Check - if there is entries in information then it is an album or playlist, else: single track
        if "entries" in information_request and information_request["entries"]:
            
            first_track = information_request["entries"][0]
        else:
            first_track = information_request
            


            # Count amount of tracks in album/playlist
        if "entries" in information_request and information_request["entries"]:
            track_amount = len(information_request["entries"])

            # If single track in playlist or album
            if track_amount == 1:
                track_info = information_request["entries"][0]
                return {
                    "type": "track",
                    "title": track_info.get("title") or information_request.get("title"),
                    "artist": track_info.get("artist") or track_info.get("uploader") or "Unknown",
                    "duration": self.duration(information_request.get("duration")),
                    "thumbnail": track_info.get("thumbnail") or information_request.get("thumbnail")
                }
            
            # If more than 1 track - album or playlist
            else:
                return {
                    "type": "playlist",
                    "title": information_request.get("title") or first_track.get("album") or "Unknow",
                    "artist": information_request.get("artist") or first_track.get("artist") or information_request.get("uploader") or "Unknown",
                    "track_count": track_amount,
                    "thumbnail": information_request.get("thumbnail") or information_request["entries"][0].get("thumbnail")
                }
        
        # If single track
        else:
            return{
            "type": "track",
            "title": information_request.get("title"),
            "artist": information_request.get("artist") or information_request.get("uploader") or "Unknown",
            "duration": self.duration(information_request.get("duration")),
            "thumbnail": information_request.get("thumbnail")
        }
    
    ## information_request call in thread
    def thread_request(self):
        
        # Check if there is save folder
        settings = load_settings()
        path = settings['save_folder']
        if not path:
            print("The save folder is not specified!")

            def ui_error(dt):
                self.root.ids.information.text = "Please specified the save folder in settings!"
                self.root.ids.cover.source = "https://litterbox.catbox.moe/resources/qts/1458602218407.png"

            Clock.schedule_once(ui_error)
            return


        # Check if URL was provided
        url = self.root.ids.input_link.text.strip()
        if not url:
            print("No URL provided!")

            def ui_error(dt):
                self.root.ids.information.text = "Please insert the link!"
                self.root.ids.cover.source = "https://litterbox.catbox.moe/resources/qts/1458602218407.png"

            Clock.schedule_once(ui_error)
            return
        
        # Check if we get response from request
        content = self.information_request()
        if not content:
            print("Some problem in content_request")

            def ui_error(dt):
                self.root.ids.information.text = "Something happened when we were collecting information!"
                self.root.ids.cover.source = "https://litterbox.catbox.moe/resources/qts/1458602218407.png"

            Clock.schedule_once(ui_error)
            return
        

        def update_ui(dt):
            # If requested media is a track
            if content["type"] == "track":
                self.root.ids.information.text = f"{content['title']}\nArtist: {content['artist']}\nDuration: {content['duration']}"
                self.root.ids.cover.source = content["thumbnail"]

            # If requested media is an album/playlist
            elif content["type"] == "playlist":
                self.root.ids.information.text = f"{content['title']}\nArtist: {content['artist']}\nTracks amount: {content['track_count']}"
                self.root.ids.cover.source = content["thumbnail"]

        self.root.ids.button_download.disabled = False

        Clock.schedule_once(update_ui)


    ## Proceed button
    def proceed(self):
        threading.Thread(target=self.thread_request, daemon=True).start()

        self.root.ids.button_download.disabled = True
        self.root.ids.information.text = "Please wait..."
        self.root.ids.cover.source = "https://litterbox.catbox.moe/resources/qts/1458602218407.png"






















MainApp().run()