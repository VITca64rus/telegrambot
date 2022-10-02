import telebot
import os
from dotenv import load_dotenv
from random import randint

load_dotenv()
bot = telebot.TeleBot(os.environ["TOKEN"])

keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Рандомное фото')
keyboard1.row('Загрузить фото')
keyboard1.row('/help')

def get_file_name():
    '''Рандомно определяет фото и возвращает id'''
    id_photo = None
    try:
        with open('ids_photo.txt', 'r') as file_ids:
            photos_id = []
            for line in file_ids:
                photos_id.append(line)
        num_files = len(photos_id)
        id_photo = photos_id[randint(0, num_files - 1)][0:-1]
    except FileNotFoundError:
        pass
    return id_photo

@bot.message_handler(commands=['start'])
def start_message(message):
    '''Отправляет приветственное сообщение на команду start'''
    bot.send_message(message.chat.id, 'Привет, я покажу тебе Бака', reply_markup=keyboard1)

@bot.message_handler(commands=['help'])
def help_message(message):
    '''Отправляет сообщение c описанием допустимых команд'''
    bot.send_message(message.chat.id, '/start - Для начала общения с ботом\n\n\
    Кнопка меню "Рандомное фото" - запрос бота прислать рандомную фотографию Бака\n\n\
    Кнопка меню "Загрузить фото" - позволяет загрузить новое фото (при отправке фото \
    в сообщении должен быть передан пароль)\n\n\
    /help - Помощь по функцианалу бота', reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    '''Обрабатывает входящие текстовые сообщения'''
    if message.text in ["Рандомное фото", "бак", "Бак", "buck", 'Buck']:
        id_photo = get_file_name()
        if id_photo is not None:
            bot.send_photo(message.chat.id, id_photo, reply_markup=keyboard1)
        else:
            bot.send_message(message.chat.id, 'Нет загруженных фотографий', reply_markup=keyboard1)
    elif message.text == 'Загрузить фото':
        bot.send_message(message.chat.id, 'Пришли фотографию с паролем', reply_markup=keyboard1)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.", \
            reply_markup=keyboard1)

@bot.message_handler(content_types=['photo'])
def get_photo_messages(message):
    '''Обрабатывает входящие картинки'''
    photo_id = message.photo[0].file_id
    if message.caption != os.environ["PASS_PHOTO"]:
        bot.send_message(message.chat.id, "Некорректный пароль", reply_markup=keyboard1)
    else:
        with open('ids_photo.txt', 'a') as file_ids:
            file_ids.write(photo_id + '\n')

bot.polling(none_stop=True, interval=0)
