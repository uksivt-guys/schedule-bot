# -*- coding: utf-8 -*-

import telebot
import adminList as Admin
from sqldata import db
import keys
import keyboards
from loadSchedule import load_schedule
from replacement import Replacement
import json
import datetime
from session import Users, AntiCrash
from const import HUD
import messageGroup
from notification_group import send_replacements_to_subscribers
import flask_app
import pdfkit

Admin.init(db)

bot = telebot.TeleBot(keys.DISPATCHER_TOKEN)
bot_2 = telebot.TeleBot(keys.SUBSCRIBER_TOKEN)


@bot.message_handler(commands=["start"])
def initilization(message):
    chat_id = message.chat.id
    AntiCrash(chat_id)
    if (Admin.isAdmin(chat_id)):
        markup = keyboards.admin_menu()
        bot.send_message(message.chat.id, HUD.START, reply_markup=markup)
    else:
        markup = keyboards.user_menu()
        bot.send_message(message.chat.id, HUD.START, reply_markup=markup)


@bot.message_handler(commands=["help"])
def helping(message):
    bot.send_message(message.chat.id, HUD.HELP)


@bot.message_handler(commands=["myid"])
def myid(message):
    bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(content_types=["document"])
def load_sc(message):
    chat_id = message.chat.id
    AntiCrash(chat_id)
    if (Users[chat_id].Action == HUD.ACTION_LOADFILE):
        load_schedule(message, bot, db)
    else:
        bot.send_message(chat_id, HUD.HELP_INFO)
        return


@bot.message_handler(content_types=["text"])
def msg_handler(message):
    text = message.text
    chat_id = message.chat.id
    AntiCrash(chat_id)
    rep = Users[message.chat.id].replacements

    if (text == HUD.BUTTON_AUTH):
        bot.send_message(chat_id, HUD.AUTH)
        return
    elif (text == HUD.PASSWORD):
        Admin.newAdmin(db, chat_id)
        markup = keyboards.admin_menu()
        bot.send_message(chat_id, HUD.AUTH_SUCCESS, reply_markup=markup)
        return

    if not (Admin.isAdmin(chat_id)):
        bot.send_message(chat_id, HUD.HELP_INFO)
        return

    if (text == HUD.BUTTON_MESSAGE):
        Users[chat_id].Action = HUD.ACTION_MESSAGE
        bot.send_message(chat_id, HUD.SEND_MSG)
    elif (text == HUD.BUTTON_MESSAGE_GROUP):
        Users[chat_id].Action = HUD.ACTION_MESSAGE_GROUP
        markup = keyboards.group_message_menu(messageGroup.getGroups())
        bot.send_message(chat_id, "Выберете группу", reply_markup=markup)
    elif (text == HUD.BUTTON_LOADFILE):
        Users[chat_id].Action = HUD.ACTION_LOADFILE
        bot.send_message(chat_id, HUD.LOADFILE)
    elif (text == HUD.BUTTON_EXIT):
        Admin.remAdmin(db, message.chat.id)
        markup = keyboards.user_menu()
        bot.send_message(message.chat.id, HUD.DISCONNECT, reply_markup=markup)
    elif (text == HUD.BUTTON_REPLACEMENT):
        rep = Replacement()
        Users[chat_id].replacements = rep
        markup = keyboards.replacement_menu(0, rep)
        bot.send_message(message.chat.id, "Выберете курс", reply_markup=markup)
    elif text == HUD.BUTTON_PUBLISH_REPLACEMENTS:
        send_replacements_to_subscribers()
        bot.send_message(chat_id, "Уведомления отправлены")
    elif (Users[chat_id].Action == HUD.ACTION_MESSAGE):
        if (text == "отм"):
            Users[chat_id].Action = 0
            return
        send_msg = message.chat.first_name + " " + message.chat.last_name + ": " + text
        for u in Users:
            try:
                bot_2.send_message(u, send_msg)
            except:
                pass
        Users[chat_id].Action = 0
        return
    elif (Users[chat_id].Action == HUD.ACTION_MESSAGE_GROUP_TYPING):
        if (text == "отм"):
            Users[chat_id].Action = 0
            return
        send_msg = message.chat.first_name + " " + message.chat.last_name + ": " + text
        messageGroup.sendGroupMessage(bot_2, send_msg, Users[chat_id].message_group)
        Users[chat_id].Action = 0
    elif text == HUD.BUTTON_EXPORT_REPLACEMENT:
        with flask_app.app.app_context():
            today = datetime.datetime.now().date()
            today_repacment = flask_app.replacements_today()
            file_name = '{}/замены-{}.pdf'.format(keys.PATH_TO_PDF_FILES, today.isoformat())
            pdfkit.from_string(today_repacment, file_name)
            doc = open(file_name, 'rb')
            bot.send_document(chat_id, doc)

            tomorrow = datetime.datetime.now().date() + datetime.timedelta(days=1)
            tomorrow_repacment = flask_app.replacements_tomorrow()
            file_name = '{}замены-{}.pdf'.format(keys.PATH_TO_PDF_FILES, tomorrow.isoformat())
            pdfkit.from_string(tomorrow_repacment, file_name)
            doc = open(file_name, 'rb')
            bot.send_document(chat_id, doc)

    elif rep != 0 and rep.is_typing_room():
        rep.setRoom(text)
        markup = keyboards.replacement_menu(rep.state, rep)
        bot.send_message(message.chat.id, rep.getText(), reply_markup=markup)
    else:
        bot.send_message(chat_id, HUD.HELP_INFO)


@bot.callback_query_handler(func=lambda res: True)
def cllbck(res):
    res.data = json.loads(res.data)
    key = res.data['0']
    value = res.data['1']
    message = res.message
    if (key == "message_group"):
        Users[message.chat.id].Action = HUD.ACTION_MESSAGE_GROUP_TYPING
        Users[message.chat.id].message_group = value
        bot.send_message(message.chat.id, HUD.SEND_MSG)
        return
    rep = Users[message.chat.id].replacements
    if (rep == 0):
        return
    state = rep.action(key, value)
    markup = keyboards.replacement_menu(state, rep)
    if (markup == 0):
        bot.send_message(message.chat.id, rep.getText())
    else:
        bot.send_message(message.chat.id, rep.getText(), reply_markup=markup)


if __name__ == '__main__':
    if not keys.TELERGRAM_LOGGER_ENABLED:
        bot.polling(none_stop=True, interval=0)
    else:
        import logging
        import telegram_logger
        import traceback

        logger = logging.getLogger()
        telegram_handle = telegram_logger.TelegramHandler()
        telegram_handle.setLevel(logging.WARNING)
        logger.addHandler(telegram_handle)
        logger.warning('Бот диспетчера запушен')
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            telegram_logger.send_msg_to_tele_logger(traceback.format_exc())
