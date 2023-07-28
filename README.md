
Music Player README

Install instructions:

<a href="https://youtu.be/ifglzdPB1sY">
  <img src="https://img.youtube.com/vi/ifglzdPB1sY/hqdefault.jpg" alt="Watch the video" width="50%">
</a>

Setting up the bot in discord developer portal: https://www.youtube.com/watch?v=hoDLj0IzZMU&t=1s watch from 1:30 to 4:10
(Used to get your TOKEN variable, you need this to let the bot log into discord (explained in the video)

Wtahc this video to install the FFMpeg audio processor to your systems PATH variable: https://www.youtube.com/watch?v=IECI72XEox0.

**Usage instructions:**
In short: 
- **Download all 4 files**
- **Create discord bot in discord developers portal**
- **Download FFMpeg to your systems PATH variable**
- **Put in keys**
- **Install neccessary dependecies:** pip install discord.py
pip install discord.py
pip install yt-dlp
pip install spotipy
pip install aiohttp
pip install responses
pip install lyricsgenius
pip install langdetect

- **Run the files in an editor (Like PyCharm community edition)**
- **(optional) edit the bots non-music respones in the responses file**
- **Enjoy the bot!**

**Requirements**

  The code imports various libraries and modules for different functionalities. Here's the updated list:

- asyncio: A library for writing asynchronous code using coroutines, allowing the bot to perform multiple tasks concurrently without blocking the main execution.

- sqlite3: A lightweight database engine used for storing audio URLs in a cache. This enables the bot to efficiently manage and retrieve audio URLs when playing music.

- urllib.parse and urllib.request: Modules for handling URLs and making HTTP requests. These modules are used to interact with web resources, such as fetching song information from YouTube and making API calls to Genius.

- re: A module for regular expressions, which is used for parsing URLs and extracting relevant information from text, like video IDs or song names from YouTube and Spotify links.

- discord: A library for creating Discord bots. This library provides the necessary tools for the bot to connect to Discord servers, respond to messages, and interact with users.

- yt_dlp (YouTube DL): A library for downloading YouTube videos and extracting audio URLs. This library allows the bot to fetch audio URLs from YouTube videos, which are used for music playback.

- spotipy and spotipy.oauth2.SpotifyClientCredentials: Libraries for interacting with the Spotify Web API. With these libraries, the bot can fetch information about Spotify tracks and playlists, allowing users to play music from Spotify.

- config: A module for managing configuration variables like tokens and secrets. This module stores sensitive information, such as Discord bot token, Genius access token, Spotify client ID, and Spotify client secret, in a centralized location, making it easier to manage and maintain these values.

- aiohttp: A library for making HTTP requests in an asynchronous way. This library enables the bot to perform HTTP requests concurrently, without blocking other tasks, which is essential for responsiveness in a Discord bot.

- responses: A library for creating mock responses to HTTP requests, typically used for testing. It allows developers to simulate API responses during testing without making actual network calls.

- time: A module for handling time-related functions. The bot uses this module for various tasks, such as setting cooldowns between commands and handling audio playback durations.

- lyricsgenius: A library for interacting with the Genius API to fetch song lyrics. With this library, the bot can search for and retrieve song lyrics from Genius, which can be displayed or used as part of its features.

- typing, typing.Tuple, and typing.Optional: Modules for type hints and annotations. Type hints improve code readability and help developers understand the expected data types of function parameters and return values.

- langdetect: A library for detecting the language of a given text. This library assists the bot in identifying the language of fetched song lyrics to ensure it only displays lyrics in English, improving user experience and readability.
  

**You can install these dependencies using the following pip installs**

pip install discord.py
pip install yt-dlp
pip install spotipy
pip install aiohttp
pip install responses
pip install lyricsgenius
pip install langdetect

**Available Commands**

The Music Player supports the following commands when used in a Discord server where the bot is present:

    `!Music (YouTube/Spotify link or song name)`: Plays music from the provided YouTube link or adds it to the Queue.
     `!Pause`: Pauses the currently playing song.
     `!Resume`: Resumes playback of the paused song.
     `!Stop`: Stops the bot from playing music and makes it leave the voice channel.
     `!Qnext`: Skips to the next song in the queue.
     `!Force (YouTube/Spotify link or song name)`: Interrupts the current song and plays the specified song.
     `!Qforce (number) plays the song with the specified number in the queue.
     `!loop`: Loops the song that is currently playing.
     `!loop stop`: Stop looping the song that is currently playing.
     `!Q`: Shows the songs that are currently in the queue.
     `!np`: Shows the song that is currently playing.
     `!lyrics`: Shows the lyrics of the song that is currently playing.
     `!Reset`: Clears the bots queue and all it's other tasks (**Debug and crash functionality**).
     `!cc`: Clears the bots cache (**Debug and crash functionality**).

**How does the code function?**

 This code is a Discord bot that plays music from various sources like YouTube and Spotify. It also has features to fetch and display song lyrics. Here's a breakdown of the code:

- Imports: The script imports various libraries for asynchronous programming, database interactions, URL handling, regular expressions, Discord bot creation, YouTube video downloading, Spotify API interactions, HTTP requests, time handling, Genius API interactions for lyrics fetching, type hinting, and language detection.

- Class Definition: The MusicPlayer class is defined, which encapsulates all the functionality of the bot. It has several instance variables like voice_channel, current_audio, queue, audio_cache, command_timestamps, ydl, sp, loop, and conn.

- Initialization and Cleanup: The __init__ method initializes the instance variables, and the __del__ method ensures the database connection is closed when the object is deleted.

- Database Connection: The connect_to_database and disconnect_from_database methods are used to manage the connection to the SQLite database, which is used to cache audio URLs.

- Audio Playback: The play_audio method is used to play a given audio file or stream. It fetches the audio URL based on the type of link provided (Spotify track, Spotify playlist, or YouTube video), stores it in the cache if it's not already cached, and then plays the audio.

- Queue Management: The wait_for_audio_finish and play_next_song methods are used to manage the queue of songs to be played. When a song finishes playing, the bot either loops the same song or plays the next song in the queue, depending on the loop variable.

- Message Sending: The send_message method is used to send a message to a Discord channel or user.

- Voice Channel Management: The join_voice_channel and disconnect_voice_channel methods are used to manage the bot's connection to the voice channel.

- Now Playing: The now_playing method is used to send a message with the currently playing song.

- Spotify Track and Playlist Handling: The get_spotify_track_name and get_spotify_playlist_tracks methods are used to fetch information about Spotify tracks and playlists.

- Lyrics Handling: The clean_lyrics, extract_artist_and_song_from_title, and fetch_lyrics_from_genius methods are used to fetch and clean song lyrics from Genius.

- YouTube Video Handling: The get_youtube_video_title method is used to fetch the title of a YouTube video.

- Queue Display: The display_queue method is used to send a message with the current queue of songs.

- Bot Start: The start method is used to start the bot. It connects to the database, creates a Discord client, defines several event handlers for the client (such as on_ready, on_message, and on_voice_state_update), and starts the client.

- Main Execution: If the script is run as the main module, it creates a MusicPlayer instance and starts it in an asyncio task, then runs the asyncio event loop forever.
