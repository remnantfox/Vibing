import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True

# --- THE CHANGE IS HERE ---
# Changed command_prefix from '!' to 'v!'
bot = commands.Bot(command_prefix="v!", intents=intents)

queues = {}
titles = {} # To keep track of song names for the !queue command

YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True', 'quiet': True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

def check_queue(ctx, id):
    if id in queues and queues[id] != []:
        source = queues[id].pop(0)
        titles[id].pop(0)
        ctx.voice_client.play(source, after=lambda e: check_queue(ctx, id))

@bot.command()
async def play(ctx, url):
    if not ctx.author.voice:
        return await ctx.send("Join a voice channel first!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    guild_id = ctx.message.guild.id

    async with ctx.typing(): # Shows 'Bot is typing...' while loading the song
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
            title = info.get('title', 'Unknown Song')
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            if guild_id not in queues:
                queues[guild_id] = [source]
                titles[guild_id] = [title]
            else:
                queues[guild_id].append(source)
                titles[guild_id].append(title)
            await ctx.send(f"✅ Added to queue: **{title}**")
        else:
            ctx.voice_client.play(source, after=lambda e: check_queue(ctx, guild_id))
            await ctx.send(f"🎶 Now playing: **{title}**")

@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸️")

@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed ▶️")

@bot.command()
async def queue(ctx):
    guild_id = ctx.message.guild.id
    if guild_id in titles and titles[guild_id]:
        song_list = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles[guild_id])])
        await ctx.send(f"**Upcoming Songs:**\n{song_list}")
    else:
        await ctx.send("The queue is empty!")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send("Skipped! ⏭️")

bot.run('MTQ3NTA3NDAxMzMzNTEyNjE5Nw.G6DMk2.G36gxueVOXUTkExKJvbh8z7mWDSqbmyn6XO4d0')
