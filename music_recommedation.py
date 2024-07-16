import webbrowser
import cv2
import spotipy
from fer import FER
from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
from PIL import Image, ImageTk
from ttkbootstrap import Style  
from tkinter import ttk
from dotenv import load_dotenv
from os import getenv

load_dotenv() # load environmental varible

class EmotionMusicRecommender:

    def __init__(self, root):
        self.root = root
        self.is_capturing = False
        self.root.title("Emotion Music Recommender")
        self.root.geometry("800x600")
        self.root.resizable(False,False)

        # Apply a modern theme
        style = Style(theme='darkly')  # You can choose different themes provided by ttkbootstrap
        
        # Load the background image
        self.bg_image = Image.open("assets/bg_image.jpeg")
        self.bg_image = self.bg_image.resize((800, 600))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a canvas and set the background image
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor=tk.NW)
        self.canvas.pack(fill="both", expand=True)

       # Set up the main frame with padding and style
        self.main_frame = ttk.Frame(self.canvas, padding="20 20 20 20", style="MainFrame.TFrame")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Emotion Detector Section
        self.emotion_detector_label = ttk.Label(self.main_frame, text="Emotion Detector", font=("Helvetica", 16, "bold"), style="TLabel")
        self.emotion_detector_label.grid(row=0, column=0, sticky=tk.N, pady=10)
        
        self.emotion_image_label = ttk.Label(self.main_frame, borderwidth=2, relief="solid", width=30)
        self.emotion_image_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.detected_emotion_label = ttk.Label(self.main_frame, text="Detected Emotion:", font=("Helvetica", 14), style="TLabel")
        self.detected_emotion_label.grid(row=2, column=0, pady=10)

        # Video Start/Stop
        self.video_button = ttk.Button(self.main_frame, text="Start Video", command=self.toggle_video_capture, style="TButton")
        self.video_button.grid(row=3, column=0, pady=10)

        self.yt_botton = ttk.Button(self.main_frame, text="YouTube video", command=self.open_youtube, style="TButton")
        self.yt_botton.grid(row=4, column=0, pady=10)

        # Song Recommendations Section
        self.song_recommendations_label = ttk.Label(self.main_frame, text="Song Recommendations", font=("Helvetica", 16, "bold"), style="TLabel")
        self.song_recommendations_label.grid(row=0, column=1, sticky=tk.N, pady=10)
        
        columns = ("Name", "Album", "Artist", "Link")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show='headings', style="Treeview")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=0, width=100)
        
        self.tree.grid(row=1, column=1, rowspan=3, padx=10, pady=10, sticky=(tk.N, tk.S, tk.W, tk.E))
        
    def toggle_video_capture(self):  
        self.is_capturing = not self.is_capturing  
        if self.is_capturing:
            self.video_button.config(text="Stop Video")  
            self.record()  
        else:
            self.video_button.config(text="Start Video")  
            self.spotify_song()
        
    def record(self):
        if not self.is_capturing:  
            return
        
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        self.detector = FER(mtcnn=True)

        if ret:
            result = self.detector.detect_emotions(frame)

            for face in result:
                (x, y, w, h) = face["box"]
                emotions = face["emotions"]               
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                dominant_emotion = max(emotions, key=emotions.get)
                music = f'{dominant_emotion}'
                cv2.putText(frame, music, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                self.detected_emotion_label.config(text=f'Detected Emotion: {music}')

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = frame.resize((300,300))
            img = ImageTk.PhotoImage(image=frame)
            self.emotion_image_label.img = img  
            self.emotion_image_label.config(image=img)

        self.root.after(15, self.record)

    def spotify_song(self):
        client_credentials_manager = SpotifyClientCredentials(client_id=getenv('CLIENT_ID'), client_secret=getenv('CLIENT_SECRET'))
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        results = sp.search(q=self.detected_emotion_label.cget('text').replace('Detected Emotion: ',''), type='track', limit=15)

        for i, track in enumerate(results['tracks']['items']):
            link = track['external_urls']['spotify']
            artist_name = track['artists'][0]['name']
            song_name = track['name']
            album_name = track['album']['name']
            self.tree.insert("", tk.END, values=(song_name, album_name, artist_name, 'link', link)) 
            self.tree.bind("<ButtonRelease-1>",self.open_link)
    
    def open_link(self, url):
        """Open a URL in the default web browser."""
        item_id = self.tree.focus()
        item = self.tree.item(item_id)
        url = item['values'][4]  
        webbrowser.open(url)

    def open_youtube(self):
        url=self.detected_emotion_label.cget('text').replace('Detected Emotion:','')
        url=url.replace(' ','+')

        if url:
            url=f'https://www.youtube.com/results?search_query={url}'
            webbrowser.open(url)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionMusicRecommender(root)
    root.mainloop()
