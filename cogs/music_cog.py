import asyncio
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False

        self.music_queue = []
        self.YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'noplaylist': True,
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}


        self.FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin -loglevel quiet',
    'options': '-vn -ac 2 -ar 44100'
}



        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)['entries'][0]
                return {'source': info['formats'][0]['url'], 'title': info['title']}
            except Exception as e:
                print(f"Error while searching YouTube: {e}")
                return None

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue.pop(0)[0]['source']
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc is None:
                    await ctx.send("Couldn't connect to the voice channel")
                    return
        
            while not self.vc.is_connected():
                await asyncio.sleep(1)  

            self.music_queue.pop(0)

            print(f"🔗 Extracted URL: {m_url}")  # Debugging: Check if URL is valid
            await ctx.send(f"Now playing: {m_url}")  # Show URL in Discord

            try:
                self.vc.play(
                    discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                    after=lambda e: print(f"🎵 Playback finished with error: {e}")
                )
                print("🎧 Audio is playing in Discord!")  # Debug message
            except Exception as e:
                print(f"❌ FFmpeg Error: {e}")
                await ctx.send(f"FFmpeg error: {e}")
        else:
            self.is_playing = False


    @commands.command(name="play", aliases=['p'], help="Play the selected song from YouTube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("Please connect to a voice channel first.")
            return

        voice_channel = ctx.author.voice.channel
        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if song is None:
                await ctx.send("Could not download the song. Please try another search term.")
            else:
                await ctx.send(f"Added {song['title']} to the queue!")
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song")
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            await ctx.send("Music paused.")
        elif self.is_paused:
            self.vc.resume()
            await ctx.send("Music resumed.")

    @commands.command(name="resume", help="Resumes the current song")
    async def resume(self, ctx):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
            await ctx.send("Resumed playing.")

    @commands.command(name="skip", help="Skips the current song")
    async def skip(self, ctx):
        if self.vc is not None and self.vc.is_playing():
            self.vc.stop()
            await self.play_music(ctx)
            await ctx.send("Song skipped.")

    @commands.command(name="queue", help="Shows the current music queue")
    async def queue(self, ctx):
        if len(self.music_queue) > 0:
            queue_str = "\n".join([f"{i + 1}. {song[0]['title']}" for i, song in enumerate(self.music_queue[:5])])
            await ctx.send(f"Current Queue:\n{queue_str}")
        else:
            await ctx.send("No songs in the queue.")

    @commands.command(name="clear", help="Clears the queue")
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared.")

    @commands.command(name="leave", help="Makes the bot leave the voice channel")
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I'm not connected to a voice channel.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
