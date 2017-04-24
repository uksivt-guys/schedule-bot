# -*- coding: utf-8 -*-
from database import db as database
from telebot import types
from const import HUD, types_schedule, day_week
from session import Users
import json

def user_menu():
    markup = types.ReplyKeyboardMarkup()
    markup.row("Авторизоваться")
    return markup

def admin_menu(chat_id=0):
    markup = types.ReplyKeyboardMarkup()
    markup.row(HUD.BUTTON_MESSAGE)
    markup.row(HUD.BUTTON_REPLACEMENT)
    if(chat_id != 0 and Users[chat_id].replacements != 0):
        markup.row(HUD.BUTTON_PUBLISH_REPLACEMENTS)
    markup.row(HUD.BUTTON_LOADFILE)
    markup.row(HUD.BUTTON_EXIT)
    return markup

# REPLACEMENTS #

def group_menu(groups):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(*[types.InlineKeyboardButton(text=i, callback_data=json.dumps({0:"rep_select_group", 1:i})) for i in groups])
    return markup

def subject_menu(subjects):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in range(0, 7):
        text = str(i) + ". " + str(subjects[i])
        btn = types.InlineKeyboardButton(text=text, callback_data=json.dumps({0:"replace", 1:str(i)}))
        markup.add(btn)
    return markup

def subjects_list_menu(subjects):
    markup = types.InlineKeyboardMarkup(row_width=1)
    already = []
    for i in subjects:
        text = i['1']
        id = i['0']
        if text in already:
            continue
        already.append(text)
        data = json.dumps({0:"apply_replace", 1:id}, ensure_ascii=False)
        btn = types.InlineKeyboardButton(text=text, callback_data=data)
        markup.add(btn)
    btn = types.InlineKeyboardButton(text="Нет пары", callback_data=json.dumps({0:"apply_replace", 1:-1}))
    markup.add(btn)
    return markup

def subgroup_menu():
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(types.InlineKeyboardButton(text="Все", callback_data=json.dumps({0:"subgroup", 1:0})))
    markup.add(types.InlineKeyboardButton(text="Подгруппа 1", callback_data=json.dumps({0:"subgroup",1:1})))
    markup.add(types.InlineKeyboardButton(text="Подгруппа 2", callback_data=json.dumps({0: "subgroup", 1: 2})))
    return markup


#инлайн клавиатура дней недели
def inline_keyboard_day_week():
    keyboard = types.InlineKeyboardMarkup()
    for i in range(0, 6):
        button = types.InlineKeyboardButton(text=day_week[i], callback_data='schedule_on -' + str(i))
        keyboard.add(button)
    return keyboard

#инлайн клавиатура групп
def inline_keyboard_groups():
    keyboard = types.InlineKeyboardMarkup()
    groups = database.get_groups()
    for group in groups:
        group_button = types.InlineKeyboardButton(text=group['name'], callback_data='set_group -' + str(group['id']))
        keyboard.add(group_button)
    return keyboard

#инлайн клавиатура преподавателей
def inline_keyboard_teachers():
    keyboard = types.InlineKeyboardMarkup()
    teachers = database.get_teachers()
    for teacher in teachers:
        teacher_button = types.InlineKeyboardButton(text=teacher['name'], callback_data='schedule_teacher -' + str(teacher['id']))
        keyboard.add(teacher_button)
    return keyboard

#главное меню
def keyboard_menu():
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row('Расписание без замен', 'Расписание с заменами')
    keyboard.row('Расписание на преподавателя')
    keyboard.row('Выбрать группу')
    return keyboard

#меню расписания
def keyboard_menu_schedule(type):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row(types_schedule[type] + ' на сегодня', types_schedule[type] + ' на завтра')
    keyboard.row(types_schedule[type] + ' на другой день недели', types_schedule[type] + ' на неделю')
    keyboard.row('Назад')
    return keyboard