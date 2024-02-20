# billiards

## files
- main.py : flask stuff
- bot.py : bot stuff
- config.ini : config stuff

## pip packages
- discord
- flask
- flask_cors

## config.ini
[discord]
server = {server ID}
channel = {channel ID}

[secrets]
token = {app token}
appID = {app ID}

## testing setup
python3 -m venv env
source env/bin/activate
pip install discord flask

flask --app main run