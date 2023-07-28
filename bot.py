import asyncio
import sqlite3
import urllib.parse
import urllib.request
import re
import discord
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import TOKEN, GENIUS_ACCESS_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
import aiohttp
import responses
import time
import lyricsgenius
from typing import Tuple, Optional
from langdetect import detect


class MusicPlayer:
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -af dynaudnorm'
    }
    COOLDOWN_TIME = 3  # Cooldown time in seconds

    def __init__(self):
        self.voice_channel = None
        self.current_audio = None
        self.queue = []
        self.audio_cache = {}
        self.command_timestamps = {}  # Stores the timestamp of the last command issued by each user
        self.ydl = yt_dlp.YoutubeDL({
            'format': 'bestaudio[abr<=96]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'Opus',
                'preferredquality': '192',
            }],
            'socket_timeout': 30,
        })
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))
        self.loop = False
        self.conn = None

    def __del__(self):
        if self.conn:
            self.conn.close()

    async def connect_to_database(self):
        self.conn = sqlite3.connect('audio_cache.db')
        cursor = self.conn.cursor()
        cursor.execute("""
                   CREATE TABLE IF NOT EXISTS audio_cache (
                       link_or_file_path TEXT PRIMARY KEY,
                       audio_url TEXT
                   )
               """)
        self.conn.commit()

    async def disconnect_from_database(self):
        if self.conn:
            self.conn.close()

    async def play_audio(self, link_or_file_path: str, retries: int = 3):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT audio_url FROM audio_cache WHERE link_or_file_path = ?",
                           (link_or_file_path,))
            result = cursor.fetchone()
            if result is None:
                audio_url = await self.get_audio_url(link_or_file_path, cursor)
            else:
                audio_url = result[0]

            if audio_url is not None:
                self.voice_channel.play(discord.FFmpegPCMAudio(audio_url, **self.FFMPEG_OPTIONS))
                self.current_audio = link_or_file_path
                await self.wait_for_audio_finish()
            else:
                await self.play_next_song()
        except Exception as e:
            print(f"Error playing audio: {e}")
            if retries > 0:
                print(f"Retrying... ({retries} retries left)")
                await self.play_audio(link_or_file_path, retries - 1)
            else:
                print("Failed after 3 retries, skipping to the next song.")
                await self.play_next_song()  # Skip to the next song in case of

    async def get_audio_url(self, link_or_file_path: str, cursor):
        if link_or_file_path.startswith('https://open.spotify.com/track/'):
            audio_url = await self.get_audio_url_from_spotify_track(link_or_file_path, cursor)
        elif link_or_file_path.startswith('https://open.spotify.com/playlist/'):
            audio_url = await self.get_audio_url_from_spotify_playlist(link_or_file_path)
        elif link_or_file_path.startswith('https://www.youtube.com/watch?v='):
            audio_url = await self.get_audio_url_from_youtube_video(link_or_file_path, cursor)
        else:
            audio_url = await self.get_audio_url_from_search(link_or_file_path, cursor)
        return audio_url

    async def get_audio_url_from_spotify_track(self, link_or_file_path: str, cursor):
        song_name = await self.get_spotify_track_name(link_or_file_path)
        if song_name:
            search_query = urllib.parse.urlencode({'search_query': song_name})
            async with aiohttp.ClientSession() as session:
                async with session.get('http://www.youtube.com/results?' + search_query) as response:
                    htm_content = await response.read()
            search_results = re.findall(r"watch\?v=(\S{11})", htm_content.decode())
            url = 'http://www.youtube.com/watch?v=' + search_results[0]
            info_dict = self.ydl.extract_info(url, download=False)
            audio_url = info_dict['url']
            cursor.execute("INSERT INTO audio_cache VALUES (?, ?)",
                           (url, audio_url))  # Store the YouTube URL in the cache
        else:
            audio_url = None
        cursor.execute("INSERT INTO audio_cache VALUES (?, ?)",
                       (link_or_file_path, audio_url))  # Store the original Spotify URL in the cache
        self.conn.commit()
        return audio_url

    async def get_audio_url_from_spotify_playlist(self, link_or_file_path: str):
        track_urls = await self.get_spotify_playlist_tracks(link_or_file_path)
        if track_urls:
            self.queue.extend(track_urls)
            audio_url = self.queue[0]
        else:
            audio_url = None
        return audio_url

    async def get_audio_url_from_youtube_video(self, link_or_file_path: str, cursor):
        url = link_or_file_path.split('&')[0]
        info_dict = self.ydl.extract_info(url, download=False)
        audio_url = info_dict['url']
        cursor.execute("INSERT INTO audio_cache VALUES (?, ?)",
                       (link_or_file_path, audio_url))
        self.conn.commit()
        return audio_url

    async def get_audio_url_from_search(self, link_or_file_path: str, cursor):
        query_string = urllib.parse.urlencode({'search_query': link_or_file_path})
        async with aiohttp.ClientSession() as session:
            async with session.get('http://www.youtube.com/results?' + query_string) as response:
                htm_content = await response.read()
        search_results = re.findall(r"watch\?v=(\S{11})", htm_content.decode())
        url = 'http://www.youtube.com/watch?v=' + search_results[0]
        info_dict = self.ydl.extract_info(url, download=False)
        audio_url = info_dict['url']
        cursor.execute("INSERT INTO audio_cache VALUES (?, ?)",
                       (link_or_file_path, audio_url))
        self.conn.commit()
        return audio_url

    async def wait_for_audio_finish(self):
        if self.voice_channel and (self.voice_channel.is_playing() or self.voice_channel.is_paused()):
            while self.voice_channel.is_playing() or self.voice_channel.is_paused():
                await asyncio.sleep(1)
            if self.loop:
                await self.play_audio(self.current_audio)
            else:
                await self.play_next_song()

    async def play_next_song(self):
        if self.queue:
            if not self.voice_channel.is_playing() and not self.voice_channel.is_paused():
                next_song = self.queue.pop(0)
                await self.play_audio(next_song)
            else:
                print("Audio is already playing or paused. Cannot play next song.")
        else:
            print("The queue is empty.")

    async def send_message(self, message: discord.Message, response: str, is_private: bool):
        try:
            await (message.author.send(response) if is_private else message.channel.send(response))
        except Exception as e:
            print(e)

    async def join_voice_channel(self, message: discord.Message):
        response = ''
        if self.voice_channel is None:
            voice_state = message.author.voice
            if voice_state and voice_state.channel:
                self.voice_channel = await voice_state.channel.connect()
                response = 'Joined the voice channel!'
            else:
                response = 'You are not in a voice channel!'
        await self.send_message(message, response, is_private=False)

    async def disconnect_voice_channel(self):
        if self.voice_channel:
            await self.voice_channel.disconnect()
            self.voice_channel = None
            self.current_audio = None
            self.queue = []

    async def now_playing(self, message: discord.Message):
        if self.current_audio:
            if self.current_audio.startswith('https://open.spotify.com/track/'):
                track_name = await self.get_spotify_track_name(self.current_audio)
                response = f"Currently playing: {track_name}\n- {self.current_audio}"
            else:
                response = f"Currently playing: {self.current_audio}"
        else:
            response = "No song is currently playing."

        await self.send_message(message, response, is_private=False)

    async def get_spotify_track_name(self, track_url: str) -> Optional[str]:
        track_id = track_url.split('/')[-1].split('?')[0]
        track_info = self.sp.track(track_id)
        track_name = track_info['name'] if track_info else None
        artist_name = track_info['artists'][0]['name'] if track_info else None
        return f"{track_name} {artist_name}" if track_name else None

    async def get_spotify_playlist_tracks(self, playlist_url: str) -> Optional[list[str]]:
        playlist_id = playlist_url.split('/')[-1].split('?')[0]
        offset = 0
        track_urls = []

        while True:
            playlist_info = self.sp.playlist_items(playlist_id, offset=offset)
            tracks = playlist_info['items'] if playlist_info else []
            for track in tracks:
                if track['track'] and track['track']['external_urls'] and 'spotify' in track['track']['external_urls']:
                    track_urls.append(track['track']['external_urls']['spotify'])
            if playlist_info['next']:
                offset += 100
            else:
                break

        return track_urls

    @staticmethod
    def clean_lyrics(lyrics: str) -> str:
        lines = lyrics.split('\n')
        cleaned_lines = [line for line in lines if
                         not line.startswith(
                             '[') and 'Embed' not in line and 'You might also like' not in line and 'Contributors' not in line and 'Translations' not in line and not line.endswith(
                             'Lyrics')]
        return '\n'.join(cleaned_lines)

    @staticmethod
    def extract_artist_and_song_from_title(title: str) -> Tuple[Optional[str], Optional[str]]:
        parts = title.split(' - ', 1)
        if len(parts) == 2:
            artist, song = parts
            # Remove extra information after the first '|' character
            song = re.sub(r"\|.*", "", song)
            return artist.strip(), song.strip()
        else:
            return None, None

    async def fetch_lyrics_from_genius(self, song_name: str) -> Optional[str]:
        genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
        artist, title = self.extract_artist_and_song_from_title(song_name)
        if artist and title:
            song = genius.search_song(title, artist)
        else:
            song = genius.search_song(song_name)
        if song:
            lyrics = self.clean_lyrics(song.lyrics)
            if detect(lyrics) == 'en':  # Only return the lyrics if they are in English
                return lyrics
        return None

    @staticmethod
    async def get_youtube_video_title(url: str) -> str:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('title', None)

    async def display_queue(self, message: discord.Message):
        if self.queue:
            response = "Current Queue:\n"
            for index, item in enumerate(self.queue):
                if item.startswith('https://open.spotify.com/track/'):
                    song_name = await self.get_spotify_track_name(item)
                elif item.startswith('https://www.youtube.com/watch?v='):
                    song_name = await self.get_youtube_video_title(item)
                else:
                    song_name = item
                response += f"{index + 1}. {song_name}\n"

                # If the response is getting close to the Discord character limit, send it and start a new one
                if len(response) > 1800:
                    await self.send_message(message, response, is_private=False)
                    response = ""
            # Send any remaining songs in the queue
            if response:
                await self.send_message(message, response, is_private=False)
        else:
            response = "The queue is empty."
            await self.send_message(message, response, is_private=False)

    async def start(self):
        await self.connect_to_database()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_ready():
            print(f'{client.user} is now running!')

        @client.event
        async def on_message(message: discord.Message):
            if message.author == client.user:
                return

            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)

            print(f'{username} said: "{user_message}" ({channel})')

            # Check if the user has issued a command within the last few seconds
            current_time = time.time()
            if username in self.command_timestamps and current_time - self.command_timestamps[
                username] < self.COOLDOWN_TIME:
                response = 'You are issuing commands too quickly. Please wait a few seconds before issuing another command.'
                await self.send_message(message, response, is_private=False)
                return

            # Update the timestamp of the last command for this user
            self.command_timestamps[username] = current_time

            response = responses.get_response(message, user_message)
            await self.send_message(message, response, is_private=False)

            await self.handle_music_commands(message, user_message)

        @client.event
        async def on_voice_state_update(member, before, after):
            if self.voice_channel and self.voice_channel.guild == member.guild:
                if before.channel == self.voice_channel and after.channel != self.voice_channel:
                    await self.disconnect_voice_channel()

        await client.start(TOKEN)

    async def handle_music_commands(self, message, user_message):
        if user_message.startswith('!music'):
            await self.handle_music_command(message, user_message)

        elif user_message.startswith('!force'):
            await self.handle_force_command(message, user_message)

        elif user_message.startswith('!reset'):
            await self.handle_reset_command()

        elif user_message == '!Qnext':
            await self.handle_qnext_command(message)

        elif user_message == '!stop':
            await self.handle_stop_command(message)

        elif user_message == '!pause':
            await self.handle_pause_command(message)

        elif user_message == '!resume':
            await self.handle_resume_command(message)

        elif user_message == '!np':
            await self.now_playing(message)

        elif user_message == '!Q':
            await self.display_queue(message)

        elif user_message == '!loop':
            await self.handle_loop_command(message)

        elif user_message == '!loop stop':
            await self.handle_loop_stop_command(message)

        elif user_message.startswith('!lyrics'):
            await self.handle_lyrics_command(message)

        elif user_message.startswith('!cc'):
            await self.handle_cc_command(message)

        elif user_message.startswith('!Qforce'):
            await self.handle_qforce_command(message, user_message)

    async def handle_music_command(self, message, user_message):
        response = 'Command not recognized.'  # Default value
        song_link = user_message.split(' ', 1)[1].strip() if len(user_message.split(' ', 1)) > 1 else None

        if song_link:
            await self.join_voice_channel(message)
            if self.voice_channel:
                try:
                    self.queue.append(song_link)
                    response = 'Song added to the queue!'
                    if not self.voice_channel.is_playing():
                        await self.play_next_song()
                except Exception as e:
                    print(f"Error playing audio: {e}")
        else:
            response = 'Please provide a song link or name!'

        await self.send_message(message, response, is_private=False)

    async def handle_force_command(self, message, user_message):
        song_link = user_message.split(' ', 1)[1].strip() if len(user_message.split(' ', 1)) > 1 else None

        if song_link and self.voice_channel:
            self.queue.clear()  # Clear the queue
            self.voice_channel.stop()
            await self.play_audio(song_link)
            response = 'Playing the requested song!'
        else:
            response = 'Please provide a song link or join a voice channel!'

        await self.send_message(message, response, is_private=False)

    async def handle_reset_command(self):
        if self.voice_channel:
            self.voice_channel.stop()
            self.queue.clear()
            self.current_audio = None
            await self.disconnect_voice_channel()

    async def handle_qnext_command(self, message):
        if self.queue and self.voice_channel:
            self.voice_channel.stop()
            await self.play_next_song()
            response = 'Playing the next song from the queue!'
        else:
            response = 'The queue is empty or I am not in a voice channel!'

        await self.send_message(message, response, is_private=False)

    async def handle_stop_command(self, message):
        if self.voice_channel:
            if self.voice_channel.is_playing():
                self.voice_channel.stop()
            await self.disconnect_voice_channel()
            response = 'Stopped playing and disconnected from the voice channel!'
        else:
            response = 'I am not in a voice channel!'

        await self.send_message(message, response, is_private=False)

    async def handle_pause_command(self, message):
        if self.voice_channel and self.voice_channel.is_playing():
            self.voice_channel.pause()
            response = 'Paused the current song!'
        else:
            response = 'No song is currently playing!'

        await self.send_message(message, response, is_private=False)

    async def handle_resume_command(self, message):
        if self.voice_channel and self.voice_channel.is_paused():
            self.voice_channel.resume()
            response = 'Resumed the current song!'
        else:
            response = 'No song is currently paused!'

        await self.send_message(message, response, is_private=False)

    async def handle_loop_command(self, message):
        if self.voice_channel and self.current_audio:
            self.loop = True
            response = 'Looping the current song!'
        else:
            response = 'No song is currently playing or I am not in a voice channel!'

        await self.send_message(message, response, is_private=False)

    async def handle_loop_stop_command(self, message):
        if self.voice_channel:
            self.loop = False
            response = 'Stopped looping the current song!'
        else:
            response = 'I am not in a voice channel!'

        await self.send_message(message, response, is_private=False)

    async def handle_lyrics_command(self, message):
        if self.current_audio:
            song_name = None
            if self.current_audio.startswith('https://open.spotify.com/track/'):
                song_name = await self.get_spotify_track_name(self.current_audio)
            elif self.current_audio.startswith('https://www.youtube.com/watch?v='):
                song_name = await self.get_youtube_video_title(self.current_audio)

            if song_name:
                print(f"Fetching lyrics for song: {song_name}")
                lyrics = await self.fetch_lyrics_from_genius(song_name)
                print(f"Genius API response: {lyrics}")
                if lyrics:
                    chunk_size = 2000
                    lyrics = lyrics.replace('\r\n', '\n')
                    lines = lyrics.split('\n')
                    formatted_lyrics = ''
                    for line in lines:
                        formatted_lyrics += f"    {line}\n"
                    formatted_lyrics = formatted_lyrics.rstrip()

                    chunks = [formatted_lyrics[i:i + chunk_size] for i in
                              range(0, len(formatted_lyrics), chunk_size)]
                    for chunk in chunks:
                        await self.send_message(message, chunk, is_private=False)
                else:
                    response = 'Lyrics not found.'
                    await self.send_message(message, response, is_private=False)
            else:
                response = 'Cannot fetch lyrics for the current song.'
                await self.send_message(message, response, is_private=False)
        else:
            response = 'No song is currently playing.'
            await self.send_message(message, response, is_private=False)

    async def handle_cc_command(self, message):
        if self.voice_channel:
            self.voice_channel.stop()
            self.queue.clear()
            self.current_audio = None
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM audio_cache")
            self.conn.commit()
            response = 'Cleared the audio cache and stopped playing.'
        else:
            response = 'I am not in a voice channel!'
        await self.send_message(message, response, is_private=False)

    async def handle_qforce_command(self, message, user_message):
        song_position = user_message.split(' ', 1)[1].strip() if len(user_message.split(' ', 1)) > 1 else None

        if song_position and song_position.isdigit() and self.voice_channel:
            song_position = int(song_position)
            if 0 < song_position <= len(self.queue):
                song_link = self.queue.pop(song_position - 1)  # Remove the song from the queue
                self.voice_channel.stop()  # Stop the current song
                await self.play_audio(song_link)  # Play the selected song
                response = f'Playing the song at position {song_position} from the queue!'
            else:
                response = f'There is no song at position {song_position} in the queue!'
        else:
            response = 'Please provide a valid song position or join a voice channel!'

        await self.send_message(message, response, is_private=False)


if __name__ == '__main__':
    music_player = MusicPlayer()
    asyncio.run(music_player.start())
