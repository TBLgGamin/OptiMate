import asyncio
from bot import MusicPlayer


async def main():
    music_player = MusicPlayer()
    await music_player.start()

if __name__ == '__main__':
    asyncio.run(main())
