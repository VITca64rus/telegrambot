'''Бот для отображения рандомных фотографии, есть возможность добавлять фото'''
import os
from random import randint
from collections import defaultdict

import telebot
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.environ["TOKEN"])

keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Рандомное фото')
keyboard1.row('Загрузить фото')
keyboard1.row('Удалить фото')
keyboard1.row('/help')

keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard2.row('Да')
keyboard2.row('Нет')

START, SHOW_ALL_PHOTO, DELETE_PHOTO = range(3)
USER_STATE=defaultdict(lambda:START)

def update_state(message,state):
    '''Изменить состояние пользователя'''
    USER_STATE[message.chat.id]=state

def get_state(message):
    '''Получить текущее состояние пользователя'''
    return USER_STATE[message.chat.id]

def get_file_name():
    '''Рандомно определяет фото и возвращает id'''
    id_photo = None
    try:
        with open('ids_photo.txt', 'r', encoding="utf-8") as file_ids:
            photos_id = []
            for line in file_ids:
                photos_id.append(line)
        num_files = len(photos_id)
        id_photo = photos_id[randint(0, num_files - 1)][0:-1]
    except FileNotFoundError:
        pass
    return id_photo

def get_all_photos():
    '''Возвращает список всех фото'''
    photos_id = []
    try:
        with open('ids_photo.txt', 'r', encoding="utf-8") as file_ids:
            for line in file_ids:
                photos_id.append(line[0:-1])
    except FileNotFoundError:
        pass
    return photos_id

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

@bot.message_handler(func=lambda message: get_state(message) == SHOW_ALL_PHOTO)
def show_all_photo(message):
    '''Показывает все фотографии и их id'''
    if message.text == 'Да':
        photos_id = get_all_photos()
        i = 0
        for photo in photos_id:
            bot.send_photo(message.chat.id, photo, caption=str(i), reply_markup=keyboard1)
            i += 1
        bot.send_message(message.chat.id, 'Введите номер картинки \
        для удаления и через пробел пароль. Если передумали \
        удалять введите не существующий номер')
        update_state(message, DELETE_PHOTO)
    else:
        bot.send_message(message.chat.id, 'Удаление прекращено')
        update_state(message, START)

@bot.message_handler(func=lambda message: get_state(message) == DELETE_PHOTO)
def delete_photo(message):
    '''Удаляет фотографию'''
    id_pass = message.text.split(' ')
    try:
        if id_pass[1] == os.environ["PASS_PHOTO"]:
            photos_id = get_all_photos()
            try:
                photos_id.pop(int(id_pass[0]))
                with open('ids_photo.txt', 'w', encoding="utf-8") as file_ids:
                    for photo in photos_id:
                        file_ids.write(photo + '\n')
                bot.send_message(message.chat.id, 'Удаление успешно', reply_markup=keyboard1)
                update_state(message, START)
            except IndexError:
                bot.send_message(message.chat.id, 'Удаление прекращено', reply_markup=keyboard1)
                update_state(message, START)
            except ValueError:
                bot.send_message(message.chat.id, 'Под номером картинки передано не число. Удаление прекращено', reply_markup=keyboard1)
                update_state(message, START)
        else:
            bot.send_message(message.chat.id, 'Некорректный пароль. Удаление \
                прекращено', reply_markup=keyboard1)
            update_state(message, START)
    except IndexError:
        bot.send_message(message.chat.id, 'Нет номера картинки или пароля. \
            Удаление прекращено', reply_markup=keyboard1)
        update_state(message, START)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    '''Обрабатывает входящие текстовые сообщения'''
    if message.text in ["Рандомное фото", "бак", "Бак", "buck", 'Buck']:
        id_photo = get_file_name()
        if id_photo is not None:
            bot.send_photo(message.chat.id, id_photo, reply_markup=keyboard1)
        else:
            bot.send_message(message.chat.id, 'Нет загруженных фотографий', reply_markup=keyboard1)
    elif message.text == 'Удалить фото':
        bot.send_message(message.chat.id, 'Сейчас я отображу все фотографии. Нажмите "Да" если хотите продолжить', \
            reply_markup=keyboard2)
        update_state(message, SHOW_ALL_PHOTO)
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
        with open('ids_photo.txt', 'a', encoding="utf-8") as file_ids:
            file_ids.write(photo_id + '\n')
        bot.send_message(message.chat.id, "Фотография успешно загружена", reply_markup=keyboard1)

bot.polling(none_stop=True, interval=0)
