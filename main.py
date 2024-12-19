import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

import wavelink
import typing

load_dotenv()

token = str(os.getenv("DISCORD_TOKEN"))
client_id = str(os.getenv("CLIENT_ID"))
guild_id = str(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.message_content= True
nesa_brain = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents,
    help_command=commands.MinimalHelpCommand()
)


@nesa_brain.event
async def on_ready():
    if(nesa_brain.user):
        print(f"{nesa_brain.user.name} is ready to serve you. Master ~ᡣ𐭩")
    else:
        print("I'm ready to serve you. Master ~ᡣ𐭩")
    await connect_nodes()

@nesa_brain.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
  # Everytime a node is successfully connected, we
  # will print a message letting it know.
  print(f"Node with ID {payload.session_id} has connected")
  print(f"Resumed session: {payload.resumed}")

@nesa_brain.group()
async def greetings(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Please specify a valid subcommand for greetings.")

@greetings.command()
async def hello(ctx):
    await ctx.send(f"Hello, <@{ctx.author.id}> ~ᡣ𐭩")

@greetings.command()
async def bye(ctx):
    await ctx.send(f"Bye bye , <@{ctx.author.id}> ~ᡣ𐭩")

@nesa_brain.command(description="Sends the bot's latency.")
async def ping(ctx):
    latency_ms = nesa_brain.latency * 1000
    await ctx.send(f"Pong! Latency is {latency_ms:.2f} ms")

class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)

nesa_brain.help_command = MyNewHelp()


# music
async def connect_nodes():
  """Connect to our Lavalink nodes."""
  await nesa_brain.wait_until_ready() # wait until the bot is ready

  nodes = [
    wavelink.Node(
      identifier="Nesa_brain", # This identifier must be unique for all the nodes you are going to use
      uri="https://lava-v4.ajieblogs.eu.org:443", # Protocol (http/s) is required, port must be 443 as it is the one lavalink uses
      password="https://dsc.gg/ajidevserver",

    )
  ]

  await wavelink.Pool.connect(nodes=nodes, client=nesa_brain)




@nesa_brain.command(description="Play music.")
async def play(ctx, search: str):
  # First we may define our voice client,
  # for this, we are going to use typing.cast()
  # function just for the type checker know that
  # `ctx.voice_client` is going to be from type
  # `wavelink.Player`
  if not ctx.author.voice:
    return await ctx.send("Error: You are not in a voice channel.")
  vc = typing.cast(wavelink.Player, ctx.voice_client)

  if not vc: # We firstly check if there is a voice client
    vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

  # Now we are going to check if the invoker of the command
  # is in the same voice channel than the voice client, when defined.
  # If not, we return an error message.
  if ctx.author.voice.channel.id != vc.channel.id:
    await ctx.send("You must be in the same voice channel as the bot.")
    return

  # Now we search for the song. You can optionally
  # pass the "source" keyword, of type "wavelink.TrackSource"
  tracks = await wavelink.Playable.search(search)

  if not tracks: # In case the song is not found
    return await ctx.send("No song found.") # we return an error message
  song = tracks[0]
  await vc.play(song) # Else, we play it
  await ctx.send(f"Now playing: `{song.title}`") # and return a success message

nesa_brain.run(token)
