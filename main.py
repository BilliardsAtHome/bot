from flask import Flask, request
from flask_cors import CORS, cross_origin
import discord
from configparser import RawConfigParser

# Flask setup
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

#TODO implement databases for users/breaks
    # users, highest break, count, best time
    # every 7+, input/rng values, owner, timestamp
#TODO figure out embed builder for leaderboard (buttons to nav pages)
#TODO function for reporting/logging incoming requests, call in onReq
#TODO slash commands
    # leaderboard
    # claim user ID for incoming breaks
#! figure out flask setup, for virtual env and such
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

class BreakInfo:
    def __init__(self, request):
        self.user = request.args.get("user")
        self.seed = request.args.get("seed")
        self.kseed = request.args.get("kseed")
        self.sunk = request.args.get("sunk")
        self.off = request.args.get("off")
        self.frame = request.args.get("frame")
        self.up = request.args.get("up")
        self.left = request.args.get("left")
        self.right = request.args.get("right")
        self.posY = request.args.get("posx")
        self.posY = request.args.get("posy")
        self.power = request.args.get("power")
        self.foul = request.args.get("foul")
        self.checksum = request.args.get("checksum")


# Globals
globals = Globals("config.ini")
client = discord.Client(intents=discord.Intents.default())


# handle requests to /billiards/api
@app.route("/billiards/api") # endpoint relative to how nginix is set up
@cross_origin()
def onRequest():
    # puts makes class with parameters
    breakInfo = BreakInfo(request)
    # TODO call to handling function here 

@app.route("/")
@cross_origin()
def homePage():
    a = request.args.get("a")
    return f"<p>{a}</p>"



# bot stuff here
@client.event
async def on_ready():
    # Called once when the bot establishes a connection with the Discord API.

    # Find channel through the API
    globals.server = client.get_guild(globals.serverID)
    globals.channel = client.get_channel(globals.channelID)

    assert globals.server is not None, "Can't find/access the discord server"
    assert globals.channel is not None, "Can't find/access the discord channel"


# functions
    


# Start the bot
client.run(globals.token)