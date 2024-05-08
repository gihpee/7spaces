import telebot
from telebot import types
import requests


bot = telebot.TeleBot("7072119894:AAF0QW3hzeL_ZU_Fym-UKgVZJpXwc1YbiwM")


def send_application(phone_number, agent_fio, email):
    message = f'New application:\nPhone number: {phone_number}\nAgent FIO: {agent_fio}\nEmail: {email}'
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('Accept', callback_data=f'acc_{phone_number}'))

    bot.send_message(chat_id="-4244970973", text=message, reply_markup=kb)


def send_collection_link(username, email, collection_id):
    message = f'User with phone number: {username} and email: {email} has shared his collection: https:домен/collection/{collection_id}'
    bot.send_message(chat_id="-4244970973", text=message)
