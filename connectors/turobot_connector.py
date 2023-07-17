#deps:pyTelegramBotAPI

import telebot
from telebot import types

from app.sdk import Connections

TOKEN = "6327981692:AAFI_yvmfSgIp4EnkzlSCAfYq1wT0w9W9Lw"
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

core_id = "64a2ad8e023f7c3c4c16ea17"
connections = Connections(core_id)

class ResponseHandler:

    def __init__(self, response, end_line="[br]"):
        self.end_line = end_line
        self.raw_text: str = response.replica
        self.variables: dict = response.variables
        self.decode_text: str = self.variables_decode(self.raw_text, self.variables)
        self.encode_text: str = self.variables_encode(self.decode_text, self.variables)
        self.split_text = self.encode_text.split(self.end_line)
        self.text = '\n'.join(self.split_text)

    def __repr__(self):
        return f"Handler(text={self.text}, var={self.variables}"

    def __str__(self):
        return self.text

    @staticmethod
    def variables_decode(text, variables):
        for i, key in enumerate(variables):
            text = text.replace(f"[{key}]", f"[[{i}]]")
        return text

    @staticmethod
    def variables_encode(text, variables):
        for i, value in enumerate(variables.values()):
            text = text.replace(f"[[{i}]]", value)
        return text


@bot.message_handler(func=lambda message: True)
def proxy(message):
    chat_id = message.chat.id  # определение chat.id по полученному сообщению
    response = connections.response(chat_id, message.text, tol=0.8)
    # формирование респонса в зависимости от получаемого сообщения
    # chat_id - куда отправляем сообщение
    # message.text - передаваемое на сторону НЧ сообщение пользователя
    # tol - точность
    phs = response.variables.get('picture', "None")
    # получаем из variables путь к каждой фотографии, если фото нет, то путь = None
    buttons = response.variables.get('buttons', "None")
    # получаем из variables названия кнопок, если кнопок нет, то отправляем None
    handler = ResponseHandler(response)
    if phs != "None":
        if buttons != "None":
            # если получены и кнопки, и фотографии
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            # создаем клавиатуру, которая будет отправлять query по нажати кнопки, скроется после нажатия
            markup.add(*buttons.split(','), row_width=2)
            # добавляем полученные из variables кнопки
            # row_width - количество кнопок в строке
            bot.send_message(chat_id, handler.text, reply_markup=markup)
            # отправляем сообщение с клавиатурой
            for ph in phs.split(','):
                bot.send_photo(chat_id, open(ph, 'rb'))
                # отправляем каждое из полученных фото отдельным сообщением
        else:
            bot.send_message(chat_id, handler.text, reply_markup=types.ReplyKeyboardRemove())
            # если кнопок нет, отправляем найденное текстовое сообщение
            for ph in phs.split(','):
                bot.send_photo(chat_id, open(ph, 'rb'))
                # отправляем каждое из полученных фото отдельным сообщением
    else:
        if buttons != "None":
            # если фотографий нет, но есть кнопки
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            # создаем клавиатуру, которая будет отправлять query по нажати кнопки, скроется после нажатия
            markup.add(*buttons.split(','), row_width=2)
            # добавляем полученные из variables кнопки
            # row_width - количество кнопок в строке
            bot.send_message(chat_id, handler.text, reply_markup=markup)
            # отправляем сообщение с клавиатурой
        else:
            bot.send_message(chat_id, handler.text, reply_markup=types.ReplyKeyboardRemove())
            # отправляем простое текстовое сообщение, если нет ни кнопок, ни фото
            
bot.infinity_polling()