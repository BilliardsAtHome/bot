# billiards

## files
- main.py : flask stuff
- bot.py : bot stuff
- config.ini : config stuff
- database.py : sqlite wrapper
- break_info.py : class to store break info
- users.db : users' best breaks
- breaks.db : all 7+ breaks

## pip packages
pip install -r requirements

## config.ini
```
[discord]
server = {server ID}
channel = {channel ID}
role = {role id}
color = {bot color (462b5d)}

[secrets]
token = {app token}
appID = {app ID}

[io]
timestamp = {timestamp of last check time}
check = {time in seconds between checks in the time loop}
```

## venv note
python3 -m venv env
source env/bin/activate
pip install discord.py flask flask_cors

flask --app main run