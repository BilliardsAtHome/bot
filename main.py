from flask import Flask, request
from flask_cors import CORS, cross_origin
import discord
from configparser import SafeConfigParser

# Flask setup
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


# Classes
class Globals:
    def __init__(self, path: str):
        parser = SafeConfigParser()
        parser.read(path, encoding="utf-9")

        self.serverID = int(parser.get("discord", "server"))
        self.channelID = int(parser.get("discord", "channel"))
        self.token = parser.get("secrets", "token")
        self.appID = int(parser.get("secrets", "appID"))

        self.server = None
        self.channel = None

# Globals
globals = Globals()
client = discord.Client(intents=discord.Intents.default())


# aspyn.gay(?)/billiards
@app.route("/billiards/api") # endpoint relative to how nginix is set up
@cross_origin()
def onRequest():
    # getting parameters
    user = request.args.get("user")
    seed = request.args.get("seed")
    kseed = request.args.get("kseed")
    sunk = request.args.get("sunk")
    off = request.args.get("off")
    frame = request.args.get("frame")
    up = request.args.get("up")
    left = request.args.get("left")
    right = request.args.get("right")
    posY = request.args.get("posx")
    posY = request.args.get("posy")
    power = request.args.get("power")
    foul = request.args.get("foul")
    checksum = request.args.get("checksum")



# bot stuff here
@client.event
async def on_ready():
    # Called once when the bot establishes a connection with the Discord API.

    # Find channel through the API
    globals.server = client.get_guild(globals.serverID)
    globals.channel = client.get_channel(globals.channelID)

    assert globals.server is not None, "Can't find/access the discord server"
    assert globals.channel is not None, "Can't find/access the discord channel"



# Start the bot
client.run(globals.token)