# -*- coding: utf-8 -*-
import datetime
import json

from database import db as database
from telebot import types
from const import HUD, types_schedule, get_day_week
from session import Users
from replacement import STATES
from replacement import Replacement

def user_menu():
    markup = types.ReplyKeyboardMarkup()
    markup.row("Авторизоваться")
    return markup

def admin_menu(chat_id=0):
    markup = types.ReplyKeyboardMarkup()
    markup.row(HUD.BUTTON_MESSAGE)
    markup.row(HUD.BUTTON_MESSAGE_GROUP)
    markup.row(HUD.BUTTON_REPLACEMENT)
    #markup.row(HUD.BUTTON_REPLACEMENT_VIEW)
    markup.row(HUD.BUTTON_PUBLISH_REPLACEMENTS)
    markup.row(HUD.BUTTON_LOADFILE)
    markup.row(HUD.BUTTON_EXIT)
    return markup

# REPLACEMENTS #

rep = Replacement()

def replacement_menu(state, rep):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if(state==STATES.SELECT_COURSE):
        for i in range(1, 5):
            markup.add(types.InlineKeyboardButton(text=str(i), callback_data=json.dumps({0: STATES.SELECT_COURSE, 1: i})))
    elif(state==STATES.SELECT_GROUP):
        names = rep.getGroupsNames()
        for i in names:
            i = i[0]
            markup.add(types.InlineKeyboardButton(text=i, callback_data=json.dumps({0:STATES.SELECT_GROUP,1:i})))
    elif(state==STATES.SELECT_DAY):
        weekday = datetime.datetime.today().weekday()
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        for i in range(0, len(days)):
            i = days[i]
            text = i
            if (rep.getWeekDay(i) == weekday):
                text = i + " (Сегодня)"
            if (weekday == 6):
                weekday = -1
            if (rep.getWeekDay(i) == weekday+1):
                text = i + " (Завтра)"
            markup.add(types.InlineKeyboardButton(text=text, callback_data=json.dumps({0: STATES.SELECT_DAY, 1: i},
                                                                                      ensure_ascii=False)))
    elif(state==STATES.SELECT_SUBJECT):
        subjects = rep.getSubjectsNames()

        for i in range(0, 6):
            if i in subjects:
                name = subjects[i]
                text = "%d. %s" % (i, name)
            else:
                name = "-"
                text = "%d. -" % (i)
            markup.add(types.InlineKeyboardButton(text=text, callback_data=json.dumps({0:STATES.SELECT_SUBJECT, 1:i}, ensure_ascii=False)))
    elif(state==STATES.SELECT_REPLACE):
        subjects = rep.getAllSubjects()
        for i in subjects:
            markup.add(types.InlineKeyboardButton(text=subjects[i], callback_data=json.dumps({0:STATES.SELECT_REPLACE, 1:i})))
    elif(state==STATES.SELECT_SUBGROUP):
        markup.add(types.InlineKeyboardButton(text="Все", callback_data=json.dumps({0:STATES.SELECT_SUBGROUP, 1:0})))
        markup.add(types.InlineKeyboardButton(text="1 Подгруппа", callback_data=json.dumps({0: STATES.SELECT_SUBGROUP, 1: 1})))
        markup.add(types.InlineKeyboardButton(text="2 Подгруппа", callback_data=json.dumps({0: STATES.SELECT_SUBGROUP, 1: 2})))

    if not (state==STATES.SELECT_COURSE):
        markup.add(types.InlineKeyboardButton(text="Назад", callback_data=json.dumps({0:STATES.RETURN, 1:0})))
    else:
        markup.add(types.InlineKeyboardButton(text="Закончить", callback_data=json.dumps({0:STATES.END, 1:0})))

    if (state == STATES.UPDATED):
        markup = 0

    return markup

#инлайн клавиатура дней недели
def inline_keyboard_day_week():
    keyboard = types.InlineKeyboardMarkup()
    for i in range(0, 7):
        button = types.InlineKeyboardButton(text=get_day_week(i), callback_data='schedule_on -' + str(i))
        keyboard.add(button)
    return keyboard

#инлайн клавиатура групп
def inline_keyboard_groups():
    keyboard = types.InlineKeyboardMarkup()
    groups = database.get_groups()
    for group in groups:
        group_button = types.InlineKeyboardButton(text=group['name'], callback_data='add_group -' + str(group['id']))
        keyboard.add(group_button)
    return keyboard

#инлайн клавиатура преподавателей
def inline_keyboard_teachers():
    keyboard = types.InlineKeyboardMarkup()
    teachers = database.get_teachers()
    for teacher in teachers:
        teacher_button = types.InlineKeyboardButton(text=teacher['name'], callback_data='add_teacher -' + str(teacher['id']))
        keyboard.add(teacher_button)
    return keyboard

#инлайн клавиатура подписок на группы (для расписания)
def inline_keyboard_subscribe_group_schedule(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    groups = database.get_subscribe_group(chat_id)
    for group in groups:
        group_button = types.InlineKeyboardButton(text='для ' + group['name'], callback_data='sch_group -' + str(group['id']))
        keyboard.add(group_button)
    button = types.InlineKeyboardButton(text='для всех', callback_data='sch_group -all')
    keyboard.add(button)
    return keyboard

#инлайн клавиатура подписок на группы (для удаления)
def inline_keyboard_subscribe_group_delete(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    groups = database.get_subscribe_group(chat_id)
    for group in groups:
        group_button = types.InlineKeyboardButton(text=group['name'], callback_data='del_group -' + str(group['id']))
        keyboard.add(group_button)
    return keyboard

#инлайн клавиатура подписок на преподавателей (для расписания)
def inline_keyboard_subscribe_teacher_schedule(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    teachers = database.get_subscribe_teacher(chat_id)
    for teacher in teachers:
        teacher_button = types.InlineKeyboardButton(text='для ' + teacher['name'], callback_data='sch_teacher -' + str(teacher['id']))
        keyboard.add(teacher_button)
    teacher_button = types.InlineKeyboardButton(text='для всех', callback_data='sch_teacher -all')
    keyboard.add(teacher_button)
    return keyboard

#инлайн клавиатура подписок на преподавателей (для удаления)
def inline_keyboard_subscribe_teacher_delete(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    teachers = database.get_subscribe_teacher(chat_id)
    for teacher in teachers:
        teacher_button = types.InlineKeyboardButton(text=teacher['name'], callback_data='del_teacher -' + str(teacher['id']))
        keyboard.add(teacher_button)
    return keyboard

#главное меню бота подписчиков
def keyboard_menu():
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('Расписание без замен', 'Расписание с заменами')
    keyboard.row('Расписание преподавателя без замен', 'Расписание преподавателя с заменами')
    keyboard.row('Настройки')
    return keyboard

#меню расписания
def keyboard_menu_schedule(type):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row(types_schedule[type] + ' на сегодня', types_schedule[type] + ' на завтра')
    keyboard.row(types_schedule[type] + ' на другой день недели', types_schedule[type] + ' на неделю')
    keyboard.row('Назад')
    return keyboard

#меню настроек подписчика
def keyboard_menu_settings():
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('Добавить подписку на группу', 'Добавить подписку на преподавателя')
    keyboard.row('Удалить подписку на группу', 'Удалить подписку на преподавателя')
    keyboard.row('Назад')
    return keyboard

#text
def group_message_menu(groups):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in groups:
        markup.add(types.InlineKeyboardButton(text=groups[i], callback_data=json.dumps({0:"message_group", 1:i})))
    return markup