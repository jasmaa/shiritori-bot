# Shiritori Bot

Reddit bot that moderates Shiritori games

## Setup
  - `pip install -r requirements.txt`
  - Create `praw.ini` in the repo folder and add your credentials in the following format:
  ```
	[shiritori-bot]
	client_id=<your version here>
	client_secret=<your version here>
	user_agent=Shiritori Bot 1.0
	password=<your version here>
	username=<your version here>
  ```
  - `python bot.py`