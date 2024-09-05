from telebot.bot import TelegramBot
from telebot.user import User
from telebot.database import DBSettings

DBSettings.path = 'test.db'

with open('token.txt', 'r') as token_file:
    token_str = token_file.read().strip(' \n')

bot = TelegramBot(token=token_str)

bot.polling()
