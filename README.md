
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
pip install langdetect
- **Run the files in an editor (Like PyCharm community edition)**
- **(optional) edit the bots non-music respones in the responses file**
- **Enjoy the bot!**

**Code explanation**

This code represents a MusicPlayer class that allows you to play audio in a voice channel on Discord. The player supports playing audio from various sources, such as YouTube and Spotify, and includes features like queuing songs, pausing and resuming playback, displaying the currently playing song, fetching lyrics, and more.

**Requirements**

To run this code, you need to have the following dependencies installed:

   Here's the updated list:

    asyncio: a library for writing asynchronous code using coroutines.
    sqlite3: a lightweight database engine for storing audio URLs in a cache.
    urllib.parse and urllib.request: modules for handling URLs and making HTTP requests.
    re: a module for regular expressions, used for parsing URLs and extracting information.
    discord: a library for creating Discord bots.
    youtube_dl: a library for downloading YouTube videos and extracting audio URLs.
    spotipy and spotipy.oauth2.SpotifyClientCredentials: libraries for interacting with the Spotify Web API.
    config: a module for managing configuration variables like tokens and secrets.
    aiohttp: a library for making HTTP requests in an asynchronous way.
    responses: a library for creating mock responses to HTTP requests (used for testing).
    time: a module for handling time-related functions.
    lyricsgenius: a library for interacting with the Genius API to fetch song lyrics.
    typing, typing.Tuple, and typing.Optional: modules for type hints and annotations.
    langdetect: a library for detecting the language of a given text.
  

**You can install these dependencies using the following pip installs**

pip install discord.py
pip install youtube_dl
pip install spotipy
pip install requests
pip install beautifulsoup4
pip install lyricsgenius
pip install langdetect
pip install aiohttp

**Available Commands**

The Music Player supports the following commands when used in a Discord server where the bot is present:

    `!Music (YouTube/Spotify link or song name)`: Plays music from the provided YouTube link or adds it to the Queue.
     `!Pause`: Pauses the currently playing song.
     `!Resume`: Resumes playback of the paused song.
     `!Stop`: Stops the bot from playing music and makes it leave the voice channel.
     `!Qnext`: Skips to the next song in the queue.
     `!Force (YouTube/Spotify link or song name)`: Interrupts the current song and plays the song from the provided link.
     `!loop`: Loops the song that is currently playing.
     `!loop stop`: Stop looping the song that is currently playing.
     `!Q`: Shows the songs that are currently in the queue.
     `!np`: Shows the song that is currently playing.
     `!lyrics`: Shows the lyrics of the song that is currently playing.
     `!Reset`: Clears the bots queue and all it's other tasks (**Debug and crash functionality**).
     `!cc`: Clears the bots cache (**Debug and crash functionality**).

**How does the code function?**

  This code is a Discord bot that plays music. It can play music from YouTube and Spotify, and it also has the ability to fetch song lyrics from Genius. Here's a breakdown of the code:

    Imports: The script starts by importing several libraries that it uses to perform its tasks. These include libraries for asynchronous programming (asyncio), database interactions (sqlite3), URL handling (urllib.parse and urllib.request), regular expressions (re), Discord bot creation (discord), YouTube video downloading (youtube_dl), Spotify API interactions (spotipy), HTTP requests (aiohttp and responses), time handling (time), Genius API interactions (lyricsgenius), type hinting (typing), and language detection (langdetect).

    Class Definition: The MusicPlayer class is defined, which encapsulates all the functionality of the bot. It has several class-level variables, such as FFMPEG_OPTIONS and COOLDOWN_TIME, and instance variables like voice_channel, current_audio, queue, audio_cache, command_timestamps, ydl, sp, loop, and conn.

    Initialization and Cleanup: The __init__ method initializes the instance variables, and the __del__ method ensures the database connection is closed when the object is deleted.

    Database Connection: The connect_to_database and disconnect_from_database methods are used to manage the connection to the SQLite database, which is used to cache audio URLs.

    Audio Playback: The play_audio method is used to play a given audio file or stream. It first checks if the audio URL is in the cache. If not, it fetches the URL based on the type of link provided (Spotify track, Spotify playlist, or YouTube video), stores it in the cache, and then plays the audio. If the audio URL is in the cache, it simply plays the audio. If an error occurs while playing the audio, it retries up to three times before skipping to the next song.

    Queue Management: The wait_for_audio_finish and play_next_song methods are used to manage the queue of songs to be played. When a song finishes playing, the bot either loops the same song or plays the next song in the queue, depending on the loop variable.

    Message Sending: The send_message method is used to send a message to a Discord channel or user.

    Voice Channel Management: The join_voice_channel and disconnect_voice_channel methods are used to manage the bot's connection to the voice channel.

    Now Playing: The now_playing method is used to send a message with the currently playing song.

    Spotify Track and Playlist Handling: The get_spotify_track_name and get_spotify_playlist_tracks methods are used to fetch information about Spotify tracks and playlists.

    Lyrics Handling: The clean_lyrics, extract_artist_and_song_from_title, and fetch_lyrics_from_genius methods are used to fetch and clean song lyrics from Genius.

    YouTube Video Handling: The get_youtube_video_title method is used to fetch the title of a YouTube video.

    Queue Display: The display_queue method is used to send a message with the current queue of songs.

    Bot Start: The start method is used to start the bot. It connects to the database, creates a Discord client, defines several event handlers for the client (such as on_ready, on_message, and on_voice_state_update), and starts the client.

    Main Execution: If the script is run as the main module, it creates a MusicPlayer instance and starts it in an asyncio task, then runs the asyncio event loop forever.
