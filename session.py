# -*- coding: utf-8 -*-
from const import HUD

Users = dict()

def AntiCrash(id):
	if not (id in Users):
		Users[id] = User_Data()

class User_Data(object):
	isAdmin = False
	Action = HUD.ACTION_MENU
	replacements = 0
