import telebot
import os
from dotenv import load_dotenv
from random import randint

load_dotenv()
bot = telebot.TeleBot(os.environ["TOKEN"])

def get_file_name():
    num_files = sum(os.path.isfile(os.path.join('img', f)) for f in os.listdir('img'))
    file = 'img/' + str(randint(0, num_files - 1)) + '.jpg'
    return file

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "бак" or message.text == "Бак" or message.text == "buck" or message.text == 'Buck':
        path = get_file_name()
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши бак")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

bot.polling(none_stop=True, interval=0)