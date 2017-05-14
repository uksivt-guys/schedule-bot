# -*- coding: utf-8 -*-

import telebot
from telebot import types
from datetime import datetime, date, time

import const
import keyboards
from keys import SUBSCRIBER_TOKEN
from database import db as database


bot = telebot.TeleBot(SUBSCRIBER_TOKEN)



#конструктор строки расписания групп
def str_schedule_group(schedule):
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


#формирование расписания с заменами (type_schedule = True)/без (type_schedule = False)
def weekday_schedule(group_id, num_weekday, type_schedule = False):
	mes = '----На ' + const.get_day_week(num_weekday) + ' для ' + database.get_groups(group_id)[0]['name'] + '----\n'

	gen_schedule = database.get_schedule(group_id, num_weekday)

	#тип расписания(с заменами - true/без замен - false)
	if type_schedule:
		replacements = database.get_replacement(group_id, num_weekday)

	for lesson in range(0, 7):
		group_type_sched = -1
		if type_schedule:
			replacement = search_lesson(replacements, lesson)
			if replacement != 0:
				if replacement[0]['group_type'] == 0:
					mes += str_schedule_group(replacement[0])
					continue

				elif len(replacement) == 2:
					for replac in replacement:
						mes += str_schedule_group(replac)
					continue

				else:
					mes += str_schedule_group(replacement[0])
					group_type_sched = {1:2,2:1}[replacement[0]['group_type']]

		schedule = search_lesson(gen_schedule, lesson, group_type_sched)
		if schedule != 0:
			for sched in schedule:
				mes += str_schedule_group(sched)

	return mes


#конструктор строки расписания преподавателя
def str_schedule_teacher(schedule):
	str_sched = ''
	if schedule['subject_name'] != '-':
		str_sched += str(schedule['lesson_number']) + '. ' + str(schedule['group_name'])
		str_sched += ' (' + str(schedule['group_type']) + ' подгруппа)' if  schedule['group_type'] != 0 else ''
		str_sched += ' - ' + str(schedule['room']) + '\n'
	return str_sched


#формирование расписания на преподавателя
def teacher_schedule(teacher_id, num_weekday, type_schedule = False):
	mes = '----На ' + const.get_day_week(num_weekday) + ' для ' + database.get_teachers(teacher_id)[0]['name'] + '----\n'
	
	teacher_schedule = database.get_teacher_schedule(teacher_id, num_weekday)

	if type_schedule:
		replacements = database.get_teacher_replacements(teacher_id, num_weekday)

	for lesson in range(0, 7):
		if type_schedule:
			schedule = search_lesson(replacements, lesson)
			if schedule == 0:
				schedule = search_lesson(teacher_schedule, lesson)
		else:
			schedule = search_lesson(teacher_schedule, lesson)

		if schedule != 0:
			mes += str_schedule_teacher(schedule[0])

	return mes


#старт бота (начало чата с ботом)
@bot.message_handler(commands=['start'])
def start_chat(message):
	greet_mes = 'Привет, ' + message.chat.first_name + '!\nЯ прототип бота расписания, моя задача информировать тебя о расписании твоей группы на сегодня, на завтра, на всю неделю! Рекомендую, сначала выбрать группу.'
	menu = keyboards.keyboard_menu()
	bot.send_message(message.chat.id, greet_mes, reply_markup=menu)


#обработка инлайн клавиатуры (меню под сообщениями)
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	chat_id = call.message.chat.id

	if call.message:
		#отправка расписания на определенный день недели
		if 'schedule_on' in call.data:
			weekday = int(float(call.data[13:]))
			keyboard = ''
			mes = call.message.text + ' ' + const.get_day_week(weekday)

			#для преподавателя
			if 'преподавателя' in call.message.text:
				teachers = database.check_subscribe_teacher(chat_id)
				if teachers == 1:
					teacher_id = database.get_subscribe_teacher(chat_id)[0]['id']
					bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes, reply_markup = keyboard)
					if weekday == 6:
						for i in range(0,6):
							message = teacher_schedule(teacher_id, i, const.types_schedule[1] in call.message.text)
							bot.send_message(chat_id, message)
					else:
						message = teacher_schedule(teacher_id, weekday, const.types_schedule[1] in call.message.text)
						bot.send_message(chat_id, message)
					return
				elif teachers > 1:
					keyboard = keyboards.inline_keyboard_subscribe_teacher_schedule(chat_id)
				else:
					mes = 'Сначала добавь подписку на преподавателя'

			#для группы
			else:
				groups = database.check_subscribe_group(chat_id)
				if groups == 1:
					group_id = database.get_subscribe_group(chat_id)[0]['id']
					bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes, reply_markup = keyboard)
					if weekday == 6:
						for i in range(0,6):
							message = weekday_schedule(group_id, i, const.types_schedule[1] in call.message.text)
							bot.send_message(chat_id, message)
					else:
						message = weekday_schedule(group_id, weekday, const.types_schedule[1] in call.message.text)
						bot.send_message(chat_id, message)
					return
				elif groups > 1:
					keyboard = keyboards.inline_keyboard_subscribe_group_schedule(chat_id)
				else:
					mes = 'Сначала добавь подписку на группу'

			bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes, reply_markup = keyboard)
		
		#добавление подписки на группу
		if 'add_group' in call.data:
			group_id = call.data[11:]
			try:
				database.add_subscribe_group(chat_id, group_id)
				mes = 'Добавлена подписка на ' + database.get_groups(group_id)[0]['name']
			except Exception:
				mes = 'Ты уже подписаны на эту группу'
			finally:
				bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes)

		#удаление подписки на группу
		if 'del_group' in call.data:
			group_id = call.data[11:]
			mes = 'Удалена подписка на ' + database.get_groups(group_id)[0]['name']
			database.del_subscribe_group(chat_id, group_id)
			bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes)

		#отправка расписания
		if 'sch_group' in call.data:
			group_id = call.data[11:]
			groups = database.get_subscribe_group(chat_id) if group_id == 'all' else [{'id': int(group_id)}]
			mes = call.message.text + ' для '
			mes += 'всех' if group_id == 'all' else database.get_groups(int(group_id))[0]['name']
			type_schedule = const.types_schedule[1] in call.message.text

			start_weekday = const.get_day_week(call.message.text[call.message.text.rfind(' ') + 1:])
			end_weekday = start_weekday + 1
			if start_weekday == 6:
				end_weekday = start_weekday
				start_weekday = 0

			bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes)

			for group in groups:
				for weekday in range(start_weekday, end_weekday):
					mes = weekday_schedule(group['id'], weekday, type_schedule)
					bot.send_message(chat_id, mes)

		#добавление подписки на преподавателя
		if 'add_teacher' in call.data:
			teacher_id = call.data[13:]
			try:
				database.add_subscribe_teacher(chat_id, teacher_id)
				mes = 'Добавлена подписка на ' + database.get_teachers(teacher_id)[0]['name']
			except Exception:
				mes = 'Ты уже подписан на этого преподавателя'
			finally:
				bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes)

		#удаление подписки на преподавателя
		if 'del_teacher' in call.data:
			teacher_id = call.data[13:]
			mes = 'Удалена подписка на ' + database.get_teachers(teacher_id)[0]['name']
			database.del_subscribe_teacher(chat_id, teacher_id)
			bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes)

		if 'sch_teacher' in call.data:
			teacher_id = call.data[13:]
			teachers = database.get_subscribe_teacher(chat_id) if teacher_id == 'all' else [{'id': int(teacher_id)}]
			mes = call.message.text + ' для '
			mes += 'всех' if teacher_id == 'all' else database.get_teachers(int(teacher_id))[0]['name']
			type_schedule = const.types_schedule[1] in call.message.text

			start_weekday = const.get_day_week(call.message.text[call.message.text.rfind(' ') + 1:])
			end_weekday = start_weekday + 1
			if start_weekday == 6:
				end_weekday = start_weekday
				start_weekday = 0

			bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mes)

			for teacher in teachers:
				for weekday in range(start_weekday, end_weekday):
					mes = teacher_schedule(teacher['id'], weekday, type_schedule)
					bot.send_message(chat_id, mes)


#обработка меню
@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):

	chat_id = message.chat.id
	teachers = database.check_subscribe_teacher(chat_id)
	groups = database.check_subscribe_group(chat_id)
	weekday = datetime.weekday(datetime.now())
	mes = 'Нет такой команды!'
	keyboard = ''

	#нажатие на кнопку настроек
	if message.text == 'Настройки':
		keyboard = keyboards.keyboard_menu_settings()
		mes = 'Меню настроек'

	#возвращение в главное меню
	elif message.text == 'Назад':
		keyboard = keyboards.keyboard_menu()
		mes = 'Главное меню'

	#нажатие на кнопку добавления подписки на группу
	if message.text == 'Добавить подписку на группу':
		keyboard = keyboards.inline_keyboard_groups()
		mes = 'Выбери группу, на которую будешь подписан'

	#нажатие на кнопку удаления подписки на группу
	elif message.text == 'Удалить подписку на группу':
		if groups != 0:
			keyboard = keyboards.inline_keyboard_subscribe_group_delete(chat_id)
			mes = 'Выбери группу, подписку которой хочешь удалить'
		else:
			mes = 'Сначала добавь подписку на группу'

	#меню для расписания без замен
	elif message.text == 'Расписание без замен':
		if groups != 0:
			keyboard = keyboards.keyboard_menu_schedule(0)
			mes = 'Меню расписания'
		else:
			mes = 'Сначала добавь подписку на группу'

	#меню для расписания с заменами
	elif message.text == 'Расписание с заменами':
		if groups != 0:
			keyboard = keyboards.keyboard_menu_schedule(1)
			mes = 'Меню расписания'
		else:
			mes = 'Сначала добавь подписку на группу'

	#расписание на сегодня
	elif 'на сегодня' in message.text:
		if groups != 0:
			if 0 <= weekday <= 5:
				if groups == 1:
					group_id = database.get_subscribe_group(chat_id)[0]['id']
					mes = weekday_schedule(group_id, weekday, const.types_schedule[1] in message.text)	

				else:
					mes = const.types_schedule[0] + ' на' if (const.types_schedule[0] in message.text) else const.types_schedule[1] + ' на'
					mes += ' ' + const.get_day_week(weekday)
					keyboard = keyboards.inline_keyboard_subscribe_group_schedule(chat_id)

			else:
				mes = 'В воскресенье нет занятий!'
		else:
			mes = 'Сначала добавь подписку на группу'

	#расписание на зватра
	elif 'на завтра' in message.text:
		if groups != 0:
			if 0 <= weekday <= 4:
				if groups == 1:
					group_id = database.get_subscribe_group(chat_id)[0]['id']
					mes = weekday_schedule(group_id, weekday + 1, const.types_schedule[1] in message.text)

				else:
					keyboard = keyboards.inline_keyboard_subscribe_group_schedule(chat_id)
					mes = const.types_schedule[0] + ' на' if (const.types_schedule[0] in message.text) else const.types_schedule[1] + ' на'
					mes += ' ' + const.get_day_week(weekday + 1)

			if weekday == 6:
				if groups == 1:
					group_id = database.get_subscribe_group(chat_id)[0]['id']
					mes = weekday_schedule(group_id, 0, const.types_schedule[1] in message.text)
				else:
					keyboard = keyboards.inline_keyboard_subscribe_group_schedule(chat_id)
					mes = const.types_schedule[0] + ' на' if (const.types_schedule[0] in message.text) else const.types_schedule[1] + ' на'
					mes += ' ' + const.get_day_week(0)

			if weekday == 5:
				mes = 'В воскресенье нет занятий!'
		else:
			mes = 'Сначала добавь подписку на группу'

	#расписание на определенный день недели
	elif 'на другой день недели' in message.text:
		if groups != 0:
			keyboard = keyboards.inline_keyboard_day_week()
			mes = const.types_schedule[0] + ' на' if (const.types_schedule[0] in message.text) else const.types_schedule[1] + ' на'
		else:
			mes = 'Сначала добавь подписку на группу'

	#расписание на всю неделю
	elif 'на неделю' in message.text:
		if groups == 1:
			group_id = database.get_subscribe_group(chat_id)[0]['id']
			for i in range(0, 6):
				mes = weekday_schedule(group_id, i, const.types_schedule[1] in message.text)
				bot.send_message(chat_id, mes)
			return
		elif groups > 1:
			keyboard = keyboards.inline_keyboard_subscribe_group_schedule(chat_id)
			mes = const.types_schedule[0] + ' на' if (const.types_schedule[0] in message.text) else const.types_schedule[1] + ' на'
			mes += ' неделю'
		else:
			mes = 'Сначала добавь подписку на группу'

	#нажатие на кнопку добавления подписки на преподавателя
	if message.text == 'Добавить подписку на преподавателя':
		keyboard = keyboards.inline_keyboard_teachers()
		mes = 'Выбери группу, на которую будешь подписан'

	#нажатие на кнопку удаления подписки на преподавателя
	if message.text == 'Удалить подписку на преподавателя':
		if teachers != 0:
			keyboard = keyboards.inline_keyboard_subscribe_teacher_delete(chat_id)
			mes = 'Выбери группу, на которую будешь подписан'
		else:
			mes = 'Сначала добавь подписку на преподавателя'

	#расписание на преподавателя без замен
	elif message.text == 'Расписание преподавателя без замен':
		if teachers > 0:
			keyboard = keyboards.inline_keyboard_day_week()
			mes = 'Расписание преподавателя без замен на'
		else:
			mes = 'Сначала добавь подписку на преподавателя'
		'''if teachers == 1:
			teacher_id = database.get_subscribe_teacher(chat_id)[0]['id']
			mes = teacher_schedule(teacher_id)
		elif teachers > 1:
			keyboard = keyboards.inline_keyboard_subscribe_teacher_schedule(chat_id)
			mes = '''

	#расписание на преподавателя c заменами
	elif message.text == 'Расписание преподавателя с заменами':
		if teachers > 0:
			keyboard = keyboards.inline_keyboard_day_week()
			mes = 'Расписание преподавателя с заменами на'
		else:
			mes = 'Сначала добавь подписку на преподавателя'

	bot.send_message(chat_id, mes, reply_markup=keyboard)


if __name__ == '__main__':
	bot.polling(none_stop=True)