import asyncio
import sqlite3
import urllib.parse
import urllib.request
import re
from typing import Optional
import discord
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from config import TOKEN, GENIUS_ACCESS_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from bs4 import BeautifulSoup
import aiohttp
import responses


class MusicPlayer:
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -af dynaudnorm'
    }

    def __init__(self):
        self.voice_channel = None
        self.current_audio = None
        self.queue = []
        self.audio_cache = {}
        self.ydl = youtube_dl.YoutubeDL({
            'format': 'bestaudio[abr<=96]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'Opus',
                'preferredquality': '96',
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

    async def disconnect_from_database(self):
        if self.conn:
            self.conn.close()

    async def play_audio(self, link_or_file_path: str):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT audio_url FROM audio_cache WHERE link_or_file_path = ?",
                           (link_or_file_path,))
            result = cursor.fetchone()
            if result is None:
                if link_or_file_path.startswith('https://open.spotify.com/track/'):
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
                    else:
                        audio_url = None
                elif link_or_file_path.startswith('https://open.spotify.com/playlist/'):
                    track_urls = await self.get_spotify_playlist_tracks(link_or_file_path)
                    if track_urls:
                        self.queue.extend(track_urls)
                        audio_url = self.queue[0]
                    else:
                        audio_url = None
                elif link_or_file_path.startswith('https://www.youtube.com/watch?v='):
                    url = link_or_file_path.split('&')[0]
                    info_dict = self.ydl.extract_info(url, download=False)
                    audio_url = info_dict['url']
                else:
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
            await self.play_next_song()  # Skip to the next song in case of an error

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
        playlist_info = self.sp.playlist_items(playlist_id)
        tracks = playlist_info['items'] if playlist_info else []
        track_urls = []
        for track in tracks:
            if track['track'] and track['track']['external_urls'] and 'spotify' in track['track']['external_urls']:
                track_urls.append(track['track']['external_urls']['spotify'])
        return track_urls

    async def fetch_lyrics_from_genius(self, song_name: str) -> Optional[str]:
        headers = {
            'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
        }
        simplified_song_name = re.sub(r'\(.*\)', '', song_name)
        simplified_song_name = simplified_song_name.strip()
        params = {
            'q': simplified_song_name,
        }
        response = requests.get('https://api.genius.com/search', headers=headers, params=params)
        search_data = response.json()

        if 'hits' in search_data['response']:
            hits = search_data['response']['hits']
            if hits:
                song_id = hits[0]['result']['id']
                url = f'https://api.genius.com/songs/{song_id}'
                response = requests.get(url, headers=headers)
                song_data = response.json()

                if 'song' in song_data['response']:
                    song = song_data['response']['song']
                    song_title = song['full_title']
                    if 'lyrics_state' in song and song['lyrics_state'] == 'complete':
                        lyrics_url = song['url']
                        lyrics_response = requests.get(lyrics_url)

                        soup = BeautifulSoup(lyrics_response.text, 'html.parser')
                        lyrics_div = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-5 Dzxov')
                        if lyrics_div is not None:
                            lyrics = lyrics_div.get_text(separator="\n").strip()
                            return f"{song_title}\n\n{lyrics}"
                        else:
                            return None

    async def get_youtube_video_title(self, url: str) -> str:
        ydl_opts = {'quiet': True}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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

            chunk_size = 2000
            chunks = [response[i:i + chunk_size] for i in range(0, len(response), chunk_size)]
            for chunk in chunks:
                await self.send_message(message, chunk, is_private=False)
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

            response = responses.get_response(message, user_message)
            await self.send_message(message, response, is_private=False)

            if user_message.startswith('!music'):
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

            elif user_message.startswith('!force'):
                song_link = user_message.split(' ', 1)[1].strip() if len(user_message.split(' ', 1)) > 1 else None

                if song_link and self.voice_channel:
                    self.voice_channel.stop()
                    await self.play_audio(song_link)
                    response = 'Playing the next song!'
                else:
                    response = 'Please provide a song link or join a voice channel!'

                await self.send_message(message, response, is_private=False)

            elif user_message.startswith('!reset'):
                if self.voice_channel:
                    self.voice_channel.stop()
                    self.queue.clear()
                    self.current_audio = None
                    await self.disconnect_voice_channel()

            elif user_message == '!Qnext':
                if self.queue and self.voice_channel:
                    self.voice_channel.stop()
                    await self.play_next_song()
                    response = 'Playing the next song from the queue!'
                else:
                    response = 'The queue is empty or I am not in a voice channel!'

                await self.send_message(message, response, is_private=False)

            elif user_message == '!stop':
                if self.voice_channel:
                    if self.voice_channel.is_playing():
                        self.voice_channel.stop()
                    await self.disconnect_voice_channel()
                    response = 'Stopped playing and disconnected from the voice channel!'
                else:
                    response = 'I am not in a voice channel!'

                await self.send_message(message, response, is_private=False)

            elif user_message == '!pause':
                if self.voice_channel and self.voice_channel.is_playing():
                    self.voice_channel.pause()
                    response = 'Paused the current song!'
                else:
                    response = 'No song is currently playing!'

                await self.send_message(message, response, is_private=False)

            elif user_message == '!resume':
                if self.voice_channel and self.voice_channel.is_paused():
                    self.voice_channel.resume()
                    response = 'Resumed the current song!'
                else:
                    response = 'No song is currently paused!'

                await self.send_message(message, response, is_private=False)

            elif user_message == '!np':
                await self.now_playing(message)

            elif user_message == '!Q':
                await self.display_queue(message)

            elif user_message == '!loop':
                if self.voice_channel and self.current_audio:
                    self.loop = True
                    response = 'Looping the current song!'
                else:
                    response = 'No song is currently playing or I am not in a voice channel!'

                await self.send_message(message, response, is_private=False)

            elif user_message == '!loop stop':
                if self.voice_channel:
                    self.loop = False
                    response = 'Stopped looping the current song!'
                else:
                    response = 'I am not in a voice channel!'

                await self.send_message(message, response, is_private=False)

            elif user_message.startswith('!lyrics'):
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

        @client.event
        async def on_voice_state_update(member, before, after):
            if self.voice_channel and self.voice_channel.guild == member.guild:
                if before.channel == self.voice_channel and after.channel != self.voice_channel:
                    await self.disconnect_voice_channel()

        await client.start(TOKEN)


if __name__ == "__main__":
    player = MusicPlayer()
    asyncio.create_task(player.start())
    asyncio.get_event_loop().run_forever()
