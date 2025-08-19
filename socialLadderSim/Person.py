from enum import Enum
import Parameters as P

class Person:
    def __init__(self, id, money=P.MONEY, clout=P.CLOUT, rizz=P.RIZZ):
        self.id = id
        self.money = money
        self.clout = clout
        self.rizz = rizz
        self.status = self.EmotionalState.NORMAL

    class EmotionalState(Enum):
        SUPERIOR = "superior"
        NORMAL = "normal"
        INFERIOR = "inferior"

    def change_status(self, new_status):
        if new_status == -1:
            self.status = self.EmotionalState.INFERIOR
        elif new_status == 0:
            self.status = self.EmotionalState.NORMAL
        elif new_status == 1:
            self.status = self.EmotionalState.SUPERIOR

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_money(self):
        return self.money

    def set_money(self, money):
        self.money = money

    def get_clout(self):
        return self.clout

    def set_clout(self, clout):
        self.clout = clout

    def get_rizz(self):
        return self.rizz

    def set_rizz(self, rizz):
        self.rizz = rizz
