
import discord
from typing import Optional


def get_response(message: discord.Message, user_message: str) -> Optional[str]:
    p_message = user_message.lower()

    if p_message == '!hello':
        return 'Hey there! How can I assist you?'

    if not p_message.startswith('!'):
        return None  # Return None if message doesn't start with "!"

    if p_message == '!helpme':
        return '''**🤖 OptiMate Bot Commands**

    OptiMate is a Discord bot that can play music, recommend games, and more. Here are the commands you can use:

    **🎵 Music Commands**
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

    **🤗 Other Commands**
     `!hello`: Makes the bot say hello to you.
    '''

        # Check if the message should be handled by bot.py
    if p_message.startswith('!music') or p_message == '!stop' or p_message.startswith('!force') or p_message.startswith('!local') or p_message == '!q' or p_message == '!qnext' or p_message == '!pause' or p_message == '!resume' or p_message == '!np' or p_message == '!reset' or p_message == '!loop' or p_message == '!loop stop' or p_message == '!lyrics' or p_message == '!cc' or p_message.startswith( '!qforce'):
        return None

    return 'Unknown command :/\n\nTry typing: !helpme to get some help'


