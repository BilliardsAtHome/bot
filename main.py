from flask import Flask, request
from flask_cors import CORS, cross_origin
import time
from break_info import BreakInfo


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



# handle requests to /billiards/api
@app.route("/billiards/api") # endpoint relative to how nginix is set up
@cross_origin()
async def onRequest():
    breakInfo = BreakInfo(request)
    breakInfo.timestamp = round(time.time())

    #TODO enter data into databases here. all 7+ breaks in one, bests per user in another.

    # this is just temp to make sure it works, removoe later
    return f"<p>{breakInfo}</p>"