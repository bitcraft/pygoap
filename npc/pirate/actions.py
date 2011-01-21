# -*- coding: utf-8 -*-

from pygoap.action import CallableAction, CalledOnceAction

class pickup_object(CalledOnceAction):
	def start(self):
		print "pickup"

class move(CallableAction):
	def start(self):
		pass

	def update(self):
		pass

	def finish(self):
		pass

class drink_rum(CallableAction):
	def start(self):
		super(drink_rum, self).start()
		self.caller.drunkness = 1
		print "drinking!"
		
	def update(self):
		print "still drinking!!!", self.caller.drunkness
		self.caller.drunkness += 1
		if self.caller.drunkness == 5:
			self.finish()
		
	def finish(self):
		super(drink_rum, self).finish()
		print "give me more #$*@$#@ rum!"

class idle(CalledOnceAction):
	pass

class buy_rum(CalledOnceAction):
	pass

class steal_rum(CalledOnceAction):
	pass

class steal_money(CalledOnceAction):
	pass

class sell_loot(CalledOnceAction):
	pass

class get_loot(CalledOnceAction):
	pass

class go_sailing(CalledOnceAction):
	pass

class beg_money(CalledOnceAction):
	pass

class buy_boat(CalledOnceAction):
	pass

class woo_lady(CalledOnceAction):
	pass

class get_laid(CalledOnceAction):
	pass

class pilage_lady(CalledOnceAction):
	pass

class make_rum(CalledOnceAction):
	pass

class do_dance(CalledOnceAction):
	pass
