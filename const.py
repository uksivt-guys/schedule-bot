def get_day_week(weekday):
	if type(weekday) == int:
		return {
		0: 'понедельник',
		1: 'вторник',
		2: 'среду',
		3: 'четверг',
		4: 'пятницу',
		5: 'субботу',
		6: 'неделю'
		}[weekday]
	if type(weekday) == str:
		return {
		'понедельник': 0,
		'вторник': 1,
		'среду': 2,
		'четверг': 3,
		'пятницу': 4,
		'субботу': 5,
		'неделю': 6
		}[weekday]

types_schedule = {
	0: 'без замен',
	1: 'с заменами'
}

class LoadFileType(object):
	SELECTED = False
	FIRST_COURSE = 1
	OTHER_COURSES = 2

class HUD(object):

	# TEXT
	START = u"Добрый день!\nЭто меню диспетчера для бота-расписания @propotype_schedule_bot\nЗдесь можно добавить/обновить расписание для групп, сделать массовую рассылку студентам."
	NOT_ADMIN = u"Извините, но у вас недостаточно прав!\n(Пароль: 1010)"
	AUTH = u"Введите пароль, чтобы подтвердить свою личность\n(Пароль от тестового режима: 1010)"
	PASSWORD = u"1010"
	AUTH_SUCCESS = u"Вы вошли в систему!"
	HELP_INFO = u"Введите /help для получения списка команд."
	DISCONNECT = u"Вы вышли из системы!"
	LOADFILE = u"Добавьте файл в формате xlsx/xls для импорта расписания."
	LOADFILE_COURSE = u"Выберете тип:"
	LOADFILE_SUCCESS = u"Расписание обновлено!"
	LOADFILE_ERROR = u"Расписание обновлено, но имеет ошибки! Проверьте следующие ячейки:\n"
	HELP = u"Порядок работы с приложением:\n1. Нажмите кнопку \"Авторизоваться\"\n(Если по каким-то причинам ее нет, то введите повторно команду /start)\n2. Введите ключ авторизации (По умолчанию: 1010)\n3. Выберете нужное вам действие из списка в меню"
	SEND_MSG = u"Введите ваше сообщение (Для отмены введите 'отм'):"

	# BUTTONS
	BUTTON_MESSAGE = u"Написать сообщение всем"
	BUTTON_MESSAGE_GROUP = u"Написать сообщение группе"
	BUTTON_REPLACEMENT = u"Добавить замены"
	BUTTON_REPLACEMENT_VIEW = u"Показать все замены"
	BUTTON_LOADFILE = u"Загрузить расписание"
	BUTTON_AUTH = u"Авторизоваться"
	BUTTON_EXIT = u"Выйти"

	# ACTIONS
	ACTION_MENU = 0
	ACTION_MESSAGE = 1
	ACTION_MESSAGE_GROUP = 2
	ACTION_MESSAGE_GROUP_TYPING = 3

	ACTION_LOADFILE = LoadFileType()
