# billiards

## files
- main.py : flask stuff
- bot.py : bot stuff
- config.ini : config stuff
- database.py : sqlite wrapper
- break_info.py : class to store break info
- users.db : users' best breaks
- breaks.db : all 7+ breaks

## config.ini
```ini
[discord]
server = {server ID}
channel = {channel ID}

[secrets]
token = {app token}
appID = {app ID}
```

## testing setup
```
pipenv shell
flask --app main run
```
