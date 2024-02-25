import discord
from discord import app_commands
from discord.ext import tasks
from configparser import RawConfigParser
from break_info import BreakInfo
from database import Database
import time
from os import path

#TODO figure out embed builder for leaderboard (buttons to nav pages)
#TODO slash commands
    # leaderboard
    # user (basically leaderboard but for one person)
#! figure out server stuff, nginx/gunicorn

# Classes
class Globals:
    def __init__(self, path: str):
        parser = RawConfigParser()
        parser.read(path, encoding="utf-8")

        self.serverID = int(parser.get("discord", "server"))
        self.channelID = int(parser.get("discord", "channel"))
        self.token = str(parser.get("secrets", "token"))
        self.appID = int(parser.get("secrets", "appID"))

        self.server = None
        self.channel = None

    def timestamp(self, path):
        parser = RawConfigParser()
        parser.read(path, encoding="utf-8")
        
        oldTimestamp = int(parser.get("io", "timestamp"))
        newTimestamp = round(time.time())
        parser['io']['timestamp'] = str(newTimestamp)
        with open(path, 'w') as configfile:
            parser.write(configfile)
        print(f"wrote {newTimestamp}")

        return oldTimestamp

# Globals
globals = Globals("config.ini")
client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)


# Function
async def recordCheck(timestamp)-> BreakInfo | None:
    breaksDB = Database('breaks.db')
    oldBest = breaksDB.get_global_best_at_before(timestamp)
    newBest = breaksDB.get_new_global_best(timestamp)

    #TODO try except maybe not necessary? check BreakInfo vs None comparison and see if it catches
    try:
        if newBest > oldBest:
            return newBest
    except (TypeError) as e:
        print(e)
        return None

def stringToColor(string: str):
    val1 = format(hash(string) % 255, '02x')
    val2 = format(hash(string[1:] + string[:1]) % 255, '02x')
    val3 = format(hash(string[2:] + string[:2]) % 255, '02x')
    return "#" + val1 + val2 + val3


# bot stuff here
@tree.command(
    name="ping",
    description="ping :3")
async def command_a(interaction: discord.Interaction):
    await interaction.response.send_message("h", ephemeral = True)

@tree.command(name = "get-user", description = "Gets a user's high score")
@app_commands.describe(user = "What user?")
async def getUser(interaction: discord.Interaction, user: discord.User):
    usersDB = Database('users.db')
    if usersDB.contains_user(user.id):
        bestBreak: BreakInfo = usersDB.get_user_best(user.id)
        userEmbed = discord.Embed(title = f"{user.name} High Score", color = discord.Colour.from_str(stringToColor(user.name)))
        userEmbed.add_field(name = "Out of Play", value = bestBreak.sunk + bestBreak.off, inline = True)
        userEmbed.add_field(name = "Off table", value = bestBreak.off, inline = True)
        userEmbed.add_field(name = "Foul", value = bestBreak.foul, inline = True)
        userEmbed.add_field(name = "Time", value = f"{bestBreak.frame/60:.2f}", inline = True)
        userEmbed.add_field(name = "Frames", value = f"{bestBreak.frame}", inline = True)
        userEmbed.set_footer(icon_url = "https://github.com/aspynect/billiards-bruteforcer-bot/assets/4ball.png")

        await interaction.response.send_message(embed = userEmbed)
        #await interaction.response.send_message(f"<@{user.id}>\n{bestBreak.sunk + bestBreak.off = }\n{bestBreak.off = }\n{bestBreak.foul = }\n{bestBreak.frame = }", ephemeral = True)
    else:
        await interaction.response.send_message(f"<@{user.id}> does not have a high score.")

@tree.command(name = "get-leaderboard", description = "Gets the high scores leaderboard")
async def getUser(interaction: discord.Interaction):
    pass

@tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id == 439441145466978305:
        sync = await tree.sync()
        await interaction.response.send_message(f"Synced {len(sync)} commands", ephemeral = True)
    else:
        await interaction.response.send_message('You must be the owner to use this command!', ephemeral = True)

@client.event
async def on_ready():
    # Find channel through the client cache
    globals.server = client.get_guild(globals.serverID)
    globals.channel = client.get_channel(globals.channelID)
    assert globals.server is not None, "Can't find/access the discord server"
    assert globals.channel is not None, "Can't find/access the discord channel"
    # task_watch_file.start()

# Periodically checks database for new top entry
#TODO change to a minute when done testing
@tasks.loop(seconds=5)
async def task_watch_file():
    if not path.exists('breaks.db'):
        return
    timestamp = globals.timestamp("config.ini")
    newBreak = await recordCheck(timestamp)
    if type(newBreak) != type(None):
        await globals.channel.send(f"User <@{newBreak.user}> got a {newBreak.sunk + newBreak.off} break with {newBreak.off} ball(s) off the table in {newBreak.frame / 60:.2f} seconds ({newBreak.frame} frames)!")


# TODO slash commands for show leaderboard, and show user (by ping)


# Start the bot
client.run(globals.token)