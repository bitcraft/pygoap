from pygoap import CallableAction, CalledOnceAction, ACTIONSTATE_FINISHED



class look(CalledOnceAction):
    def start(self):
        self.caller.environment.look(self.caller)
        super(look, self).start()

class pickup_object(CalledOnceAction):
    def start(self):
        print "pickup"

class drink_rum(CallableAction):
    def start(self):
        self.caller.drunkness = 1
        super(drink_rum, self).start()
        print self.caller, "is drinking some rum"
        
    def update(self, time):
        if self.valid():
            print self.caller, "is still drinking..."
            self.caller.drunkness += 1
            if self.caller.drunkness == 5:
                self.finish()
        else:
            self.fail()     

    def finish(self):
        print self.caller, "says \"give me more #$*@$#@ rum!\""
        super(drink_rum, self).finish()

class idle(CallableAction):
    def ok_finish(self):
        return True

    def finish(self):
        self.state = ACTIONSTATE_FINISHED
        print self.caller, "finished idling"
        #CallableAction.finish(self)
        #del self.caller.blackboard.tagDB['idle']

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
