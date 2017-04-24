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

Admin.init(db)

bot = telebot.TeleBot(keys.DISPATCHER_TOKEN)
bot_2 = telebot.TeleBot(keys.SUBSCRIBER_TOKEN)

@bot.message_handler(commands=["start"])
def initilization(message):
    chat_id = message.chat.id
    AntiCrash(chat_id)
    if(Admin.isAdmin(chat_id)):
        markup = keyboards.admin_menu()
        bot.send_message(message.chat.id, HUD.START, reply_markup=markup)
    else:
        markup = keyboards.user_menu()
        bot.send_message(message.chat.id, HUD.START, reply_markup=markup)

@bot.message_handler(commands=["help"])
def helping(message):
    bot.send_message(message.chat.id, HUD.HELP)

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
    elif (text == HUD.BUTTON_LOADFILE):
        Users[chat_id].Action = HUD.ACTION_LOADFILE
        bot.send_message(chat_id, HUD.LOADFILE)
    elif (text == HUD.BUTTON_EXIT):
        Admin.remAdmin(db, message.chat.id)
        markup = keyboards.user_menu()
        bot.send_message(message.chat.id, HUD.DISCONNECT, reply_markup=markup)
    elif (text == HUD.BUTTON_REPLACEMENT):
        markup = keyboards.group_menu(["2П-1", "2П-2", "3П-1"])
        bot.send_message(message.chat.id, HUD.REPLACEMENT_SELECT_GROUP, reply_markup=markup)
    elif (Users[chat_id].Action == HUD.ACTION_MESSAGE):
        send_msg = message.chat.first_name + " " + message.chat.last_name + ": " + text
        for u in Users:
            try:
                bot_2.send_message(u, send_msg)
            except:
                pass
        Users[chat_id].Action = 0
        return
    elif (text == HUD.BUTTON_PUBLISH_REPLACEMENTS):
        try:
            Users[chat_id].replacements.PublishReplacements(bot_2)
            markup = keyboards.admin_menu()
            bot.send_message(chat_id, "..", reply_markup=markup)
        except:
            pass
        return
    elif (Users[chat_id].replacements != 0 and Users[chat_id].replacements.room):
        rep = Users[chat_id].replacements
        rep.room = text
        rep.intoBase()
        markup = keyboards.admin_menu(chat_id=chat_id)
        bot.send_message(chat_id, "..", reply_markup=markup)
        return
    else:
        bot.send_message(chat_id, HUD.HELP_INFO)

@bot.callback_query_handler(func=lambda res: True)
def cllbck(res):
    res.data = json.loads(res.data)
    key = res.data['0']
    value = res.data['1']
    message = res.message
    if(key=="rep_select_group"):
        group = res.data['1']
        rep = Replacement(db=db, group=group)
        subjects = rep.getSchedule()
        markup = keyboards.subject_menu(subjects)
        bot.send_message(message.chat.id, "test", reply_markup=markup)
        Users[message.chat.id].replacements = rep
    if(key=="replace"):
        rep = Users[message.chat.id].replacements
        rep.number = value
        if(type(rep) == int):
            return
        markup = keyboards.subjects_list_menu(rep.getSubjects())
        bot.send_message(message.chat.id, "test", reply_markup=markup)
    if(key=="apply_replace"):
        rep = Users[message.chat.id].replacements
        rep.replace_subject = value
        if(type(rep)==int):
            return
        markup = keyboards.subgroup_menu()
        bot.send_message(message.chat.id, "test", reply_markup=markup)
    if(key=="subgroup"):
        rep = Users[message.chat.id].replacements
        if(type(rep)==int):
            return
        rep.subgroup = value
        rep.getTeacher()
        bot.send_message(message.chat.id, "Введите номер аудитории")
        rep.room = True

bot.polling(none_stop=True,interval=0)
