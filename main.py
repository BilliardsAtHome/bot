from flask import Flask, request
from flask_cors import CORS, cross_origin
import time


# Flask setup
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

#TODO implement databases for users/breaks (call in onrequest)
    # users, highest break, count, best time
    # every 7+, input/rng values, owner, timestamp
#TODO figure out embed builder for leaderboard (buttons to nav pages)
#TODO slash commands
    # leaderboard
    # claim user ID for incoming breaks? if using that method
#! figure out server stuff, nginx/gunicorn



# Classes
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
        self.posX = request.args.get("posx")
        self.posY = request.args.get("posy")
        self.power = request.args.get("power")
        self.foul = request.args.get("foul")
        self.checksum = request.args.get("checksum")
        self.timestamp = None

    def __repr__(self):
        return f"{self.user} {self.seed} {self.kseed} {self.sunk} {self.off} {self.frame} {self.up} {self.left} {self.right} {self.posX} {self.posY} {self.power} {self.foul} {self.checksum}"


# handle requests to /billiards/api
@app.route("/billiards/api") # endpoint relative to how nginix is set up
@cross_origin()
def onRequest():
    breakInfo = BreakInfo(request)
    breakInfo.timestamp = round(time.time())

    #TODO enter data into databases here. all 7+ breaks in one, bests per user in another.

    # this is just temp to make sure it works, removoe later
    return f"<p>{breakInfo}</p>"