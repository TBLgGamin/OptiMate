
Music Player README

Install instructions:

<a href="https://youtu.be/ifglzdPB1sY">
  <img src="https://img.youtube.com/vi/ifglzdPB1sY/hqdefault.jpg" alt="Watch the video" width="50%">
</a>

Setting up the bot in discord developer portal: https://www.youtube.com/watch?v=hoDLj0IzZMU&t=1s watch from 1:30 to 4:10
(Used to get your TOKEN variable, you need this to let the bot log into discord (explained in the video)

**Usage instructions:**
In short: 
- **Download all 4 files**
- **Put in keys**
- **Install neccessary dependecies:** pip install discord.py
pip install youtube_dl
pip install spotipy
pip install requests
pip install beautifulsoup4
pip install lyricsgenius
- **Run the files in an editor (Like PyCharm community edition)**
- **(optional) edit the bots non-music respones in the responses file**
- **Enjoy the bot!**

**Code explanation**

This code represents a MusicPlayer class that allows you to play audio in a voice channel on Discord. The player supports playing audio from various sources, such as YouTube and Spotify, and includes features like queuing songs, pausing and resuming playback, displaying the currently playing song, fetching lyrics, and more.

**Requirements**

To run this code, you need to have the following dependencies installed:

    asyncio: a library for writing asynchronous code using coroutines.
    sqlite3: a lightweight database engine for storing audio URLs in a cache.
    urllib: a module for handling URLs and making HTTP requests.
    re: a module for regular expressions, used for parsing URLs and extracting information.
    typing: a module for type hints and annotations.
    discord: a library for creating Discord bots.
    youtube_dl: a library for downloading YouTube videos and extracting audio URLs.
    spotipy: a library for interacting with the Spotify Web API.
    requests: a library for making HTTP requests to external APIs.
    bs4 (Beautiful Soup): a library for parsing HTML and XML documents.

**You can install these dependencies using the following pip installs**

pip install discord.py
pip install youtube_dl
pip install spotipy
pip install requests
pip install beautifulsoup4
pip install lyricsgenius

**Available Commands**

The Music Player supports the following commands when used in a Discord server where the bot is present:

    !music [song_link or name]: Adds a song to the queue and starts playing if not already playing.
    !force [song_link]: Stops the current song and starts playing the specified song immediately.
    !reset: Stops playing, clears the queue, and disconnects from the voice channel.
    !Qnext: Skips to the next song in the queue.
    !Q: Shows the current queue of songs.
    !stop: Stops playing and disconnects from the voice channel.
    !pause: Pauses the current song.
    !resume: Resumes the paused song.
    !np: Displays the currently playing song.
    !loop: Enables looping of the current song.
    !loop stop: Disables looping of the current song.
    !lyrics: Fetches and displays the lyrics of the currently playing song.

**Notes**

    The code uses asyncio to handle asynchronous operations, allowing the bot to handle multiple commands concurrently.
    The sqlite3 module is used to store audio URLs in a SQLite database for caching purposes.
    The youtube_dl library is used to extract audio URLs from YouTube videos.
    The spotipy library is used to interact with the Spotify Web API and retrieve information about tracks and playlists.
    The requests library is used to make HTTP requests to the Genius API and fetch song lyrics.
    The bs4 (Beautiful Soup) library is used to parse HTML documents and extract lyrics from Genius API responses.
