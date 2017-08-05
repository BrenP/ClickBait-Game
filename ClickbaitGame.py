import tkinter as tk
import tkinter.scrolledtext as tkst
from multiprocessing import Queue
from PIL import ImageTk, Image
import shutil
import requests
from bs4 import BeautifulSoup
import os


# The ClickbaitClient class will control the frames that are displayed for the user and initiate TKInter
class ClickbaitClient(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        # Change the title of the window
        tk.Tk.wm_title(self, "ClickBait Game")

        main_frame = tk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Initiate the frames that will be displayed in the client
        self.frames = {}
        for F in (MainPage, YouTubeChoice):
            frame = F(main_frame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start the program by showing the main page
        self.show_frame(MainPage)

    # Show Frame function is called when a frame needs to be displayed
    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


# Main page class will hold the main menu frame
class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Display title
        label = tk.Label(self,    text="ClickBait Game")
        label.pack(pady=10, padx=10)

        # Allow user to enter starting video
        entry_url = tk.Entry(self)
        entry_url.pack()

        # Button to start the game
        button1 = tk.Button(self, text="Start",
                            command=lambda: controller.show_frame(YouTubeChoice))
        button1.pack()


# Youtube Choice class will display the game based on current video
class YouTubeChoice(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        link_url = 'https://www.youtube.com/watch?v=441ZGSk6A_8&t=0s'
        self.youtube_update(parent, link_url)

    # Update function will change the display of the frame depending on current youtube url
    def youtube_update(self, parent, link_url):

        # Clear frame will destroy all current widgets, allowing a clear state
        self.clear_frame()

        # Get the source code the current url
        source_code = requests.get(link_url)
        source_text = source_code.text
        # Beautiful Soup pulls data from HTML files, being our source code, into an organized state for later use
        soup = BeautifulSoup(source_text, 'html.parser')

        self.grid_columnconfigure(0, weight=1)

        # Download all the thumbnail images of recommended videos
        count = 0
        for links in soup.findAll('img', {'style': 'top: 0px'}):
            count = count + 1

            # gets the link to the image then attempts to get the best quality by changing the link text
            site = links.get('data-thumb')
            site = site.replace('168', '336')
            site = site.replace('94', '188')

            response = requests.get(site, stream=True)
            with open('img' + str(count) + '.jpg', 'wb') as out_file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, out_file)
            del response

        links = soup.findAll('a', {'class': 'content-link'})
        for row in range(1, 4):
            for col in range(1, 6):
                # Display the image for current link
                picture = Image.open('img' + str(col + (row-1)*5) + '.jpg')
                picture = picture.resize((320, 180), Image.ANTIALIAS)
                render = ImageTk.PhotoImage(picture)
                img = tk.Button(self, image=render,
                                command=lambda ro=row, coll=col: self.youtube_update(parent, 'https://www.youtube.com' + links[coll + (row-1)*5 - 1].get('href')))
                img.image = render
                img.grid(row=row*2-1, column=col, padx=5, pady=1)

                # Display the title of the video under the image
                text = tkst.ScrolledText(self, wrap=tk.WORD, font=('', 12), width=35, height=2)
                text.grid(row=row*2, column=col, padx=5, pady=10)
                text.insert(tk.INSERT, links[col + (row-1)*5 - 1].get('title'))

        self.grid_columnconfigure(100, weight=1)

    # Clear Frame function destroys all widgets on a frame
    def clear_frame(self):
        for widget in tk.Frame.winfo_children(self):
            widget.destroy()

# Start the client
app = ClickbaitClient()
app.mainloop()

# Delete Images on Close
for item in range(1, 21):
    try:
        os.remove("img" + str(item) + ".jpg")
    except OSError:
        break

