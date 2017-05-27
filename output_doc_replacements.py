# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from database import db as database
from datetime import datetime, date, timedelta


app = Flask(__name__)


def output_doc_replacement(replacement, schedule):
	output_replacement = list()

	for item_replac in replacement:
		if item_replac['subject_name'] == '-':
			item_replac['subject_name'] = 'Нет занятий'
			item_replac['teacher_name'] = ' '
			item_replac['room'] = ' '

	for item_replac in replacement:
		if item_replac['group_type'] != 0:
			try:
				next_replac = replacement[replacement.index(item_replac) + 1]
				if next_replac['lesson_number'] == item_replac['lesson_number']:
					replacement.remove(next_replac)
				else:
					next_replac = {'group_type': 1 if item_replac['group_type'] == 2 else 2, 'subject_name': ' ', 'teacher_name': ' ', 'room': ' '}
			except IndexError:
				next_replac = {'group_type': 1 if item_replac['group_type'] == 2 else 2, 'subject_name': ' ', 'teacher_name': ' ', 'room': ' '}

		for item_sched in schedule:
			if item_sched['lesson_number'] == item_replac['lesson_number']:
				if item_sched['group_type'] != 0:
					try:
						next_sched = schedule[schedule.index(item_sched) + 1]
						if next_sched['lesson_number'] == item_sched['lesson_number']:
							schedule.remove(next_sched)
						else:
							next_sched = {'group_type': 1 if item_sched['group_type'] == 2 else 2, 'subject_name': ' ', 'teacher_name': ' ', 'room': ' '}
					except IndexError:
						next_sched = {'group_type': 1 if item_sched['group_type'] == 2 else 2, 'subject_name': ' ', 'teacher_name': ' ', 'room': ' '}

				sched = item_sched
				schedule.remove(sched)
				break
		else:
			sched = {'group_type': 0, 'subject_name': ' ', 'teacher_name': ' '}

		lesson_number = item_replac['lesson_number']
		schedule_subject = sched['subject_name'] if sched['group_type'] == 0 else sched['subject_name'] + '/' + next_sched['subject_name'] if sched['group_type'] == 1 else next_sched['subject_name'] + '/' + sched['subject_name']
		schedule_teacher = sched['teacher_name'] if sched['group_type'] == 0 else sched['teacher_name'] + '/' + next_sched['teacher_name'] if sched['group_type'] == 1 else next_sched['teacher_name'] + '/' + sched['teacher_name']

		replacement_subject = ''
		if item_replac['group_type'] == 0:
			replacement_subject = item_replac['subject_name']
			replacement_teacher = item_replac['teacher_name']
			replacement_room = item_replac['room']

		elif item_replac['group_type'] == 1:

			if sched['group_type'] == 0 or next_replac['subject_name'] != ' ':
				replacement_subject = item_replac['subject_name'] + '/' + next_replac['subject_name']
				replacement_teacher = item_replac['teacher_name'] + '/' + next_replac['teacher_name']
				replacement_room = item_replac['room'] + '/' + next_replac['room']

			else:
				if sched['group_type'] == 2:
					replacement_subject = item_replac['subject_name'] + '/' + sched['subject_name']
					replacement_teacher = item_replac['teacher_name'] + '/' + sched['teacher_name']
					replacement_room = item_replac['room'] + '/' + sched['room']

				elif next_sched['group_type'] == 2:
					replacement_subject = item_replac['subject_name'] + '/' + next_sched['subject_name']
					replacement_teacher = item_replac['teacher_name'] + '/' + next_sched['teacher_name']
					replacement_room = item_replac['room'] + '/' + next_sched['room']

		elif item_replac['group_type'] == 2:

			if sched['group_type'] == 0 or next_replac['subject_name'] != ' ':
				replacement_subject = next_replac['subject_name'] + '/' + item_replac['subject_name']
				replacement_teacher = next_replac['teacher_name'] + '/' + item_replac['teacher_name']
				replacement_room = next_replac['room'] + '/' + item_replac['room']
			
			else:
				if sched['group_type'] == 1 and next_replac['subject_name'] != ' ':
					replacement_subject = sched['subject_name'] + '/' + item_replac['subject_name']
					replacement_teacher = sched['teacher_name'] + '/' + item_replac['teacher_name']
					replacement_room = sched['room'] + '/' + item_replac['room']

				elif next_sched['group_type'] == 1 and next_replac['subject_name'] != ' ':
					replacement_subject = next_sched['subject_name'] + '/' + item_replac['subject_name']
					replacement_teacher = next_sched['teacher_name'] + '/' + item_replac['teacher_name']
					replacement_room = next_sched['room'] + '/' + item_replac['room']

		if schedule_subject != ' ' or replacement_subject != 'Нет занятий':
			output_replacement.append({
				'lesson_number': lesson_number,
				'schedule_subject': schedule_subject,
				'schedule_teacher': schedule_teacher,
				'replacement_subject': replacement_subject,
				'replacement_teacher': replacement_teacher,
				'replacement_room': replacement_room
				})

	return output_replacement


@app.route('/today/')
def replacements_today():
	date = date.today()
	return replacements_to_date(date.year, date.month, date.day)

@app.route('/tomorrow/')
def replacements_tomorrow():
	date = date.today() + timedelta(days=1)
	return replacements_to_date(date.year, date.month, date.day)

@app.route('/<int:year>/<int:month>/<int:day>/')
def replacements_to_date(year, month, day):
	replacements = list()
	dt = date(year, month, day)
	groups = database.get_groups()
	for group in groups:
		schedule = database.get_schedule(group['id'], datetime.weekday(dt))
		replacement = database.get_replacement(group['id'], dt)

		if len(replacement) > 0:
			replacements.append({
				'group': group['name'],
				'replacement': output_doc_replacement(replacement, schedule)
				})
	return render_template('index.html', date = str(dt), replacements = replacements)

if __name__ == "__main__":
	app.run()