# -*- coding: utf-8 -*-

import pymysql
from keys import KeysDB

class  SqlDB(object):
	"""docstring for  db"""
	def __init__(self, host, user, passw, db):
		self.connection = pymysql.connect(host, user, passw, db, charset='utf8')

	def __sql_query_with_result__(self, sql):
		cursor = self.connection.cursor()
		cursor.execute(sql)
		result = cursor.fetchall()
		return result

	def __sql_query_non_result__(self, sql):
		cursor = self.connection.cursor()
		cursor.execute(sql)
		cursor.close()
		self.connection.commit()

	#проверка пользователя на подписку
	def check_chat_id(self, chat_id):
		sql = 'SELECT group_id FROM schedule.subscribe_group where chat_id = ' + str(chat_id) + ';'
		result = self.__sql_query_with_result__(sql)
		if (len(result) != 0):
			return result[0][0]
		else:
			return 0

	#получение расписания на день недели
	def get_schedule(self, group_id, num_weekday):
		sql = 'SELECT general_schedule.lesson_number, general_schedule.group_type, subjects.name, teachers.name, general_schedule.room'
		sql += ' FROM general_schedule INNER JOIN teachers ON general_schedule.teacher_id = teachers.id INNER JOIN subjects ON subjects.id = general_schedule.subject_id'
		sql += ' WHERE group_id = ' + str(group_id) + ' and weekday = ' + str(num_weekday) + ' order by lesson_number;'
		result = self.__sql_query_with_result__(sql)
		gen_schedule = list()
		for schedule in result:
			gen_schedule.append({
				'lesson_number': schedule[0],
				'group_type': schedule[1],
				'subject_name': schedule[2],
				'teacher_name': schedule[3],
				'room': schedule[4]
				})
		return gen_schedule

	#получение замен на день недели
	def get_replacement(self, group_id, num_weekday):
		sql = 'SELECT replacements.lesson_number, replacements.group_type, subjects.name, teachers.name, replacements.room'
		sql += ' FROM replacements INNER JOIN teachers ON replacements.teacher_id = teachers.id INNER JOIN subjects ON replacements.subject_id = subjects.id'
		sql += ' WHERE group_id = ' + str(group_id) + ' and day >= date(now()) and weekday(day) = ' + str(num_weekday) + ' order by lesson_number;'
		result = self.__sql_query_with_result__(sql)
		replacements = list()
		for replacement in result:
			replacements.append({
				'lesson_number': replacement[0],
				'group_type': replacement[1],
				'subject_name': replacement[2],
				'teacher_name': replacement[3],
				'room': replacement[4]
				})
		return replacements

	#получение расписания преподавателя
	def get_teacher_schedule(self, teacher_id, num_weekday):
		sql = 'SELECT  lesson_number, groups.name, room'
		sql += ' FROM general_schedule INNER JOIN subjects ON subjects.id = general_schedule.subject_id INNER JOIN groups ON groups.id = general_schedule.group_id'
		sql += ' WHERE teacher_id = ' + str(teacher_id) + ' and weekday = ' + str(num_weekday) + ' order by lesson_number;'
		result = self.__sql_query_with_result__(sql)
		teacher_schedule = list()
		for schedule in result:
			teacher_schedule.append({
				'lesson_number': schedule[0],
				'group_name': schedule[1],
				'room': schedule[2]
				})
		return teacher_schedule

	#получение имени преподавателя
	def get_teacher_name(self, teacher_id):
		sql = 'SELECT name FROM teachers WHERE id = ' + str(teacher_id) + ';'
		return self.__sql_query_with_result__(sql)[0][0]

	#получение списка групп
	def get_groups(self):
		sql = 'SELECT id, name FROM groups ORDER BY name;'
		result = self.__sql_query_with_result__(sql)
		groups = list()
		for group in result:
			groups.append({
				'id': group[0],
				'name': group[1]
				})
		return groups

	#получение списка преподавателей
	def get_teachers(self):
		sql = 'SELECT id, name FROM teachers ORDER BY name;'
		result = self.__sql_query_with_result__(sql)
		teachers = list()
		for teacher in result:
			teachers.append({
				'id': teacher[0],
				'name': teacher[1]
				})
		return teachers

	#подписка на группу
	def set_group(self, chat_id, group_id):
		sql = ''
		if (not self.check_chat_id(chat_id)):
			sql = 'INSERT INTO subscribe_group (chat_id, group_id) VALUES (' + str(chat_id) + ', ' + group_id + ');'
		else:
			sql = 'UPDATE subscribe_group SET group_id = ' + group_id + ' WHERE chat_id = ' + str(chat_id) + ';'
		self.__sql_query_non_result__(sql)

	#получение списка подписчиков на группу
	def get_group_subscribers(self, group_id):
		sql = 'SELECT chat_id FROM subscribe_group WHERE group_id = ' + str(group_id) + ';'
		result = self.__sql_query_with_result__(sql)
		subscribers = list()
		for subscriber in result:
			subscribers.append({
				'id': subscriber[0]
				})
		return subscribers


db = SqlDB(KeysDB.HOST, KeysDB.USER, KeysDB.PASSWORD, KeysDB.DATABASE)
