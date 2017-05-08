import telebot
from datetime import datetime, date, time


from keys import SUBSCRIBER_TOKEN
from database import db as database
from subscribers_bot import weekday_schedule


bot = telebot.TeleBot(SUBSCRIBER_TOKEN)

groups = database.get_groups()

day = datetime.weekday(datetime.now()) + 1 if 0 <= datetime.weekday(datetime.now()) <= 4 else 0 if datetime.weekday(datetime.now()) == 6 else 6

if day != 6:
	for group in groups:
		schedule = weekday_schedule(group['id'], day, True)
		subscribers = database.get_group_subscribers(group['id'])
		for subscriber in subscribers:
			bot.send_message(subscriber['id'], schedule)
