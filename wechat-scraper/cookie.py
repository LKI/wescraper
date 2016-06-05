import os.path as op
from time import time
from random import random

class Cookie:
    cookies = []
    fname = "temp_cookies.lst"
    def __init__(self):
        if not op.exists(self.fname):
            return
        with open(self.fname, "rb") as f:
            l = f.readlines()
            for i in range(0, len(l) / 3):
                cookie = self.new_with_suv(l[3 * i].strip(), l[3 * i + 1].strip(), l[3 * i + 2].strip())
                self.cookies = self.cookies + [cookie]

    def dump(self):
        with open(self.fname, "wb") as f:
            for cookie in self.cookies:
                f.write(cookie['SNUID'])
                f.write("\n")
                f.write(cookie['SUID'])
                f.write("\n")
                f.write(cookie['SUV'])
                f.write("\n")

    def get_suv(self):
        return str(int(time() * 1000000) + int(random() * 1000))

    def get_cookies(self):
        return self.cookies

    def new(self, snuid, suid):
        return { 'SNUID' : snuid, 'SUID' : suid, 'SUV' : self.get_suv()}

    def new_with_suv(self, snuid, suid, suv):
        return { 'SNUID' : snuid, 'SUID' : suid, 'SUV' : suv}

    def same(self, cx, cy):
        if (cx['SNUID'] == cy['SNUID'] and cx['SUID'] == cy['SUID'] and cx['SUV'] == cy['SUV']):
            return True
        return False

    def has(self, cookie):
        for c in self.cookies:
            if self.same(c, cookie):
                return True
        return False

    def add(self, cookie):
        self.cookies = self.cookies + [cookie]

    def remove(self, cookie):
        for i in range(0, len(self.cookies)):
            if self.same(self.cookies[i], cookie):
                self.cookies = self.cookies[:i] + self.cookies[i+1:]
                return
