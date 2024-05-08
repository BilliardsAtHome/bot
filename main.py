from flask import Flask, request
from flask_cors import CORS, cross_origin
import time
from break_info import BreakInfo
from break_db import BreakDB
from user_db import UserDB


# Flask setup
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

# handle requests to /billiards/api
@app.route("/billiards/api") # endpoint relative to how nginix is set up
@cross_origin()
def onRequest():
    allow_submit = True
    print("Request Received")
    print(request.args)
    try:
        uniqueUserDB = UserDB('users.db')
        # convert to regular dictionary (single value)
        args = request.args.to_dict()
        if "user" in args:
            args["user"] = uniqueUserDB.get_discord_id(int(args["user"]))
        else:
            return ""
        # unpack fields from dictionary
        breakInfo = BreakInfo(**args)
        breakInfo.timestamp = round(time.time())

        # confirm data integrity
        if breakInfo.checksum != breakInfo.calcChecksum():
            allow_submit = False
    except (TypeError, ValueError) as error:
        print(error)
        # wrong argument count / name / type
        allow_submit = False

    if not allow_submit:
        return ""

    print(breakInfo)
    if breakInfo.sunk + breakInfo.off > 6:
        breakDB = BreakDB('allBreaks.db')
        breakDB.add(breakInfo)
    usersDB = BreakDB('userBreaks.db')
    usersDB.set_user_best(breakInfo)
    # dont remove this, you need it
    return f"<p>{breakInfo}</p>"
