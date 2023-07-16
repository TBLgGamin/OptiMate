
import discord

def get_response(message: discord.Message, user_message: str) -> str:
    # Convert the user message to lowercase for case-insensitive matching
    p_message = user_message.lower()

    if p_message == '!hello':
        # Respond with a greeting if the user message is '!hello'
        return 'Hey there! How can I assist you?'

    if not p_message.startswith('!'):
        # Empty response if the message doesn't start with "!"
        return ''

    if p_message == '!helpme':
# Respond with a help message if the user message is '!helpme'
        return '''**🤖 OptiMate Bot Commands**

    OptiMate is a Discord bot that can play music, recommend games, and more. Here are the commands you can use:

    **🎵 Music Commands**
     `!Music (youtube/spotify link or song name)`: Plays music from the provided YouTube link or adds it to the Queue.
     `!Pause`: Pauses the currently playing song.
     `!Resume`: Resumes playback of the paused song.
     `!Stop`: Stops the bot from playing music and makes it leave the voice channel.
     `!Qnext`: Skips to the next song in the queue.
     `!Force (youtube/spotify link or song name)`: Interrupts the current song and plays the song from the provided link
     (**Incompatible with playlists!**).
     `!loop`: Loops the song that is currently playing.
     `!loop stop`: Stop looping the song that is currently playing.
     `!Q`: Shows the songs that are currently in the queue (**Incompatible with playlists**).
     `!np`: Shows the song that is currently playing.
     `!lyrics`: Shows the lyrics of the song that is currently playing.
     `!Reset`: Clears the bots queue and all it's other tasks (**Debug and crash functionality**).

    **🎮 Game Commands**
     `!wtp`: Gives a random game recommendation.
     `!quote (game)`: Provides a random quote from the specified game.

    **🤗 Other Commands**
     `!hello`: Makes the bot say hello to you.
    '''

    # Check if the message should be handled by bot.py
    if p_message.startswith('!music') or p_message == '!stop' or p_message.startswith('!force') or p_message.startswith('!local') or p_message == '!q' or p_message == '!qnext' or p_message == '!pause' or p_message == '!resume' or p_message == '!np' or p_message == '!reset' or p_message == '!loop' or p_message == '!loop stop' or p_message == '!lyrics':
        # No response required for certain specific commands
        return ''

    # Respond with an unknown command message if none of the conditions above match
    return 'Unknown command :/\n\nTry typing: !helpme to get some help''
