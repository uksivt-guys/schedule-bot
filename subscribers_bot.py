# -*- coding: utf-8 -*-

import telebot
from telebot import types
from datetime import datetime, date, time

import const
import keyboards
from keys import SUBSCRIBER_TOKEN
from database import db as database


bot = telebot.TeleBot(SUBSCRIBER_TOKEN)



#конструктор строки расписания (type[True, False] - для 2 догруппы)
def constructor_str_schedule(schedule):
	str_sched = ''
	if schedule['subject_name'] != '-':
		str_sched += str(schedule['lesson_number']) + '. '
		str_sched += str(schedule['group_type']) + ' подгруппа ' if (schedule['group_type'] != 0) else ''	
		str_sched += schedule['subject_name'] + ' - ' + schedule['teacher_name'] + ' (' + schedule['room'] + ')\n'
	return str_sched


#поиск предмета в расписании по номеру пары
def search_lesson(schedule, lesson_num, group_type = -1):
	result = list()
	#отбор из всего расписания нужный придмет по номеру пары
	for sched in schedule:
		if sched['lesson_number'] == lesson_num:
			result.append(sched)
	
	last_val = len(result) - 1

	#если нет пары в заменах/расписании
	if last_val == -1:
		return 0

	#если надо найти результат определенного типа группы (полная группа/определенная подгруппа)
	if (group_type != -1):
		for i in range(last_val, -2, -1):
			#если не найдено результатов с таким типом группы, возвращаем 0
			if i == -1:
				return 0
			#возврат найденного результата
			if result[i]['group_type'] == group_type:
				return [result[i]]

	#если всего один результат, то возвращаем только его
	if last_val == 0:
		return result

	#если послений элемент является для всей группы, то возвращаем его
	if result[last_val]['group_type'] == 0:
		return	[result[last_val]]

	#если последний результат является не для всей группы
	if result[last_val]['group_type'] in (1, 2):
		#если последний результат и предыдущий является для обоих подгрупп, то возвращаем их, если же нет, то последний для одной погруппы
		if (result[last_val - 1]['group_type'] in (1, 2)) and (result[last_val]['group_type'] != result[last_val - 1]['group_type']):
			return [result[last_val - 1], result[last_val]]

		return [result[last_val]]


#отправка расписания на преподавателя
def send_teacher_schdule(message, teacher_id):
	for i in range(0, 7):
		teacher_schedule = database.get_teacher_schedule(teacher_id, i)
		if len(teacher_schedule) > 0:
			mes = 'На ' + const.day_week[i] + '\n'
			for schedule in teacher_schedule:
				mes += str(schedule['lesson_number']) + '. ' + str(schedule['group_name']) + ' - ' + str(schedule['room']) + '\n'
			bot.send_message(message.chat.id, mes)


#формирование расписания с заменами (type_schedule = True)/без (type_schedule = False)
def weekday_schedule(group_id, num_weekday, type_schedule = False):
	message = 'Расписание на '

	if num_weekday in const.day_week:
		message += const.day_week[num_weekday] + '\n'

	gen_schedule = database.get_schedule(group_id, num_weekday)

	if type_schedule:
		replacements = database.get_replacement(group_id, num_weekday)

	for i in range(0, 7):
		group_type_sched = -1
		#тип расписания(с заменами - true/без замен - false)
		if type_schedule:
			replacement = search_lesson(replacements, i)
			if replacement != 0:
				if replacement[0]['group_type'] == 0:
					message += constructor_str_schedule(replacement[0])
					continue

				elif len(replacement) == 2:
					for replac in replacement:
						message += constructor_str_schedule(replac)
					continue

				else:
					message += constructor_str_schedule(replacement[0])
					group_type_sched = {1:2,2:1}[replacement[0]['group_type']]

		schedule = search_lesson(gen_schedule, i, group_type_sched)
		if schedule != 0:
			for sched in schedule:
				message += constructor_str_schedule(sched)

	return message


#старт бота (первый запуск бота)
@bot.message_handler(commands=['start'])
def start_chat(message):
	greet_mes = 'Привет, ' + message.chat.first_name + '!\nЯ прототип бота расписания, моя задача информировать тебя о расписании твоей группы на сегодня, на завтра, на всю неделю! Рекомендую, сначала выбрать группу.'
	menu = keyboards.keyboard_menu()
	bot.send_message(message.chat.id, greet_mes, reply_markup=menu)


#обработка инлайн клавиатуры (меню под сообщениями)
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	if call.message:
		#запись группы
		if 'set_group' in call.data:
			database.set_group(call.message.chat.id, call.data[11:])
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Ваша группа записана!')

		#отправка расписания на определенный день недели
		if 'schedule_on' in call.data:
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text + ' ' + const.day_week[int(float(call.data[13:]))])
			group_id = database.check_chat_id(call.message.chat.id)
			if group_id != 0:
				message = weekday_schedule(group_id, int(float(call.data[13:])), const.types_schedule[1] in call.message.text)
				bot.send_message(call.message.chat.id, message)
			else:
				bot.send_message(call.message.chat.id, 'Сначала выбери свою группу')


		#отправка расписания на преподавателя
		if 'schedule_teacher' in call.data:
			mes = 'Расписание ' + database.get_teacher_name(int(float(call.data[18:])))
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = mes)
			send_teacher_schdule(call.message, int(float(call.data[18:])))


#обработка меню
@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):

	group_id = database.check_chat_id(message.chat.id)
	keyboard = ''

	#нажатие на кнопку выбора группы в меню
	if message.text == 'Выбрать группу':
		keyboard = keyboards.inline_keyboard_groups()
		mes = 'Выбери свою группу, на которую будешь подписан'

	#расписание на преподавателя
	elif message.text == 'Расписание на преподавателя':
		keyboard = keyboards.inline_keyboard_teachers()
		mes = 'Выбери преподователя'

	#возвращение в главное меню
	elif message.text == 'Назад':
		keyboard = keyboards.keyboard_menu()
		mes = 'Главное меню'

	elif group_id != 0:

		#расписание на сегодня
		if 'на сегодня' in message.text:
			if 0 <= datetime.weekday(datetime.now()) <= 5:
				mes = weekday_schedule(group_id, datetime.weekday(datetime.now()), const.types_schedule[1] in message.text)

			else:
				mes = 'В воскресенье нет занятий!'

		#расписание на зватра
		elif 'на завтра' in message.text:
			if 0 <= datetime.weekday(datetime.now()) <= 4:
				mes = weekday_schedule(group_id, datetime.weekday(datetime.now()) + 1, const.types_schedule[1] in message.text)

			if datetime.weekday(datetime.now()) == 6:
				mes = weekday_schedule(group_id, 0, const.types_schedule[1] in message.text)

			if datetime.weekday(datetime.now()) == 5:
				mes = 'В воскресенье нет занятий!'

		#расписание на определенный день недели
		elif 'на другой день недели' in message.text:
			keyboard = keyboards.inline_keyboard_day_week()
			mes = const.types_schedule[0] + ' на' if (const.types_schedule[0] in message.text) else const.types_schedule[1] + ' на'


		#меню для расписания без замен
		elif message.text == 'Расписание без замен':
			keyboard = keyboards.keyboard_menu_schedule(0)
			mes = 'Меню расписания'

		#меню для расписания с заменами
		elif message.text == 'Расписание с заменами':
			keyboard = keyboards.keyboard_menu_schedule(1)
			mes = 'Меню расписания'

		#расписание на всю неделю
		elif 'на неделю' in message.text:
			#bot.send_message(message.chat.id, 'Расписание на неделю')
			for i in range(0, 6):
				mes = weekday_schedule(group_id, i, const.types_schedule[1] in message.text)
				bot.send_message(message.chat.id, mes)
			return

	else:
		mes = 'Сначала выбери свою группу'

	bot.send_message(message.chat.id, mes, reply_markup=keyboard)


if __name__ == '__main__':
	bot.polling(none_stop=True)