from flask import Flask, request
from flask_cors import CORS, cross_origin
import time
from break_info import BreakInfo
from database import Database


# Flask setup
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


# handle requests to /billiards/api
@app.route("/billiards/api") # endpoint relative to how nginix is set up
@cross_origin()
def onRequest():
    try:
        # convert to regular dictionary (single value)
        args = request.args.to_dict()
        # unpack fields from dictionary
        breakInfo = BreakInfo(**args)
        breakInfo.timestamp = round(time.time())
    except (TypeError, ValueError) as error:
        print(error)
        # wrong argument count / name / type
        return ""

    if breakInfo.sunk + breakInfo.off > 6:
        breakDB = Database('breaks.db')
        breakDB.add(breakInfo)
    usersDB = Database('users.db')
    usersDB.set_user_best(breakInfo)
    # dont remove this, you need it
    return f"<p>{breakInfo}</p>"
