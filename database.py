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

	#проверка пользователя на подписку на группу
	def check_subscribe_group(self, chat_id):
		return len(self.get_subscribe_group(chat_id))

	def check_subscribe_teacher(self, chat_id):
		return len(self.get_subscribe_teacher(chat_id))

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
		sql = 'SELECT  weekday, lesson_number, groups.name, group_type, room'
		sql += ' FROM general_schedule INNER JOIN subjects ON subjects.id = general_schedule.subject_id INNER JOIN groups ON groups.id = general_schedule.group_id'
		sql += ' WHERE teacher_id = ' + str(teacher_id) + ' order by weekday, lesson_number;'
		result = self.__sql_query_with_result__(sql)
		teacher_schedule = list()
		for schedule in result:
			teacher_schedule.append({
				'weekday': schedule[0],
				'lesson_number': schedule[1],
				'group_name': schedule[2],
				'group_type': schedule[3],
				'room': schedule[4]
				})
		return teacher_schedule

	#получение замен преподавателя
	def get_teacher_replacements(self, teacher_id, num_weekday):
		sql = 'SELECT  weekday(day), lesson_number, groups.name, group_type, room'
		sql += ' FROM replacements INNER JOIN subjects ON subjects.id = subject_id INNER JOIN groups on groups.id = group_id'
		sql += ' WHERE day >= date(now()) and teacher_id = ' + str(teacher_id) + ' ORDER BY day, lesson_number;'
		result = self.__sql_query_with_result__(sql)
		teacher_replacements = list()
		for replacement in result:
			teacher_replacements.append({
				'weekday': replacement[0],
				'lesson_number': replacement[1],
				'group_name': replacement[2],
				'group_type': replacement[3],
				'room': replacement[4]
				})
		return teacher_replacements

	#получение имени преподавателя
	def get_teacher_name(self, teacher_id):
		sql = 'SELECT name FROM teachers WHERE id = ' + str(teacher_id) + ';'
		return self.__sql_query_with_result__(sql)[0][0]

	#получение списка групп
	def get_groups(self, group_id = 0):
		sql = 'SELECT id, name FROM groups '
		sql += 'ORDER BY name;' if group_id == 0 else 'WHERE id = ' + str(group_id) + ' ORDER BY name;'
		result = self.__sql_query_with_result__(sql)
		groups = list()
		for group in result:
			groups.append({
				'id': group[0],
				'name': group[1]
				})
		return groups

	#добавление подписки на группу
	def add_subscribe_group(self, chat_id, group_id):
		sql = 'INSERT INTO subscribe_group (chat_id, group_id) VALUES (' + str(chat_id) + ', ' + str(group_id) + ');'
		self.__sql_query_non_result__(sql)

	#удаление подписки на группу
	def del_subscribe_group(self, chat_id, group_id):
		sql = 'DELETE FROM subscribe_group WHERE chat_id = ' + str(chat_id) + ' and group_id = ' + str(group_id) + ';'
		self.__sql_query_non_result__(sql)

	#получение подписок на группы
	def get_subscribe_group(self, chat_id):
		sql = 'SELECT group_id, groups.name FROM subscribe_group INNER JOIN groups ON groups.id = subscribe_group.group_id '
		sql += 'WHERE chat_id = ' + str(chat_id) + ';'
		result = self.__sql_query_with_result__(sql)
		groups = list()
		for group in result:
			groups.append({
				'id': group[0],
				'name': group[1]
				})
		return groups

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

	#получение списка преподавателей
	def get_teachers(self, teacher_id = 0):
		sql = 'SELECT id, name FROM teachers '
		sql += 'ORDER BY name;' if teacher_id == 0 else 'WHERE id = ' + str(teacher_id) + ' ORDER BY name;' 
		result = self.__sql_query_with_result__(sql)
		teachers = list()
		for teacher in result:
			teachers.append({
				'id': teacher[0],
				'name': teacher[1]
				})
		return teachers

	#добавление подписки на преподавателя
	def add_subscribe_teacher(self, chat_id, teacher_id):
		sql = 'INSERT INTO subscribe_teacher (chat_id, teacher_id) VALUES (' + str(chat_id) + ', ' + str(teacher_id) + ');'
		self.__sql_query_non_result__(sql)

	#удаление подписки на преподавателя
	def del_subscribe_teacher(self, chat_id, teacher_id):
		sql = 'DELETE FROM subscribe_teacher WHERE chat_id = ' + str(chat_id) + ' and teacher_id = ' + str(teacher_id) + ';'
		self.__sql_query_non_result__(sql)

	#получение подписок на преподавателей
	def get_subscribe_teacher(self, chat_id):
		sql = 'SELECT teacher_id, teachers.name FROM subscribe_teacher INNER JOIN teachers ON teachers.id = subscribe_teacher.teacher_id '
		sql += 'WHERE chat_id = ' + str(chat_id) + ';'
		result = self.__sql_query_with_result__(sql)
		teachers = list()
		for teacher in result:
			teachers.append({
				'id': teacher[0],
				'name': teacher[1]
				})
		return teachers

db = SqlDB(KeysDB.HOST, KeysDB.USER, KeysDB.PASSWORD, KeysDB.DATABASE)