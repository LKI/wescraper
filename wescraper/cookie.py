import config
import os.path as op
from time import time
from random import random

class Cookie:
    cookies = []
    cookie_file = config.cookie_file
    def __init__(self):
        if not op.exists(self.cookie_file):
            return
        with open(self.cookie_file, "rb") as f:
            l = f.readlines()
            for i in range(0, len(l) / 3):
                cookie = self.new_with_suv(l[3 * i].strip(), l[3 * i + 1].strip(), l[3 * i + 2].strip())
                self.cookies = self.cookies + [cookie]

    def dump(self):
        with open(self.cookie_file, "wb") as f:
            for cookie in self.cookies:
                f.write(cookie['SNUID'])
                f.write("\n")
                f.write(cookie['SUID'])
                f.write("\n")
                f.write(cookie['SUV'])
                f.write("\n")

    def get_suv(self):
        return str(int(time() * 1000000) + int(random() * 1000))

    def fetch_one(self):
        if len(self.cookies) < config.pool_size_min:
            chance = 1
        elif len(self.cookies) >= config.pool_size_max:
            chance = 0
        else:
            chance = ((config.rise_chance_max - config.rise_chance_min) * (len(self.cookies) - config.pool_size_min)
                    / (config.pool_size_min - config.pool_size_max) + config.rise_chance_max)
        if random() <= chance:
            return {}
        else:
            return self.cookies[int(random() * len(self.cookies))]

    def get_cookies(self):
        return self.cookies

    def get_banned(self, cookie):
        self.remove(cookie)
        self.dump()
        if 0 == len(self.cookies):
            return None
        return self.cookies[int(random() * len(self.cookies))]

    def set_return_header(self, headers, cookie):
        new_cookie = cookie
        for header in headers:
            for key in ['SNUID', 'SUID']:
                if key == header.split('=')[0]:
                    value = header.split('=')[1].split(';')[0]
                    if key not in new_cookie or value != new_cookie[key]:
                        diff = True
                        new_cookie[key] = value
        if not self.same(new_cookie, cookie):
            new_cookie['SUV'] = self.get_suv()
            self.remove(cookie)
            self.cookies = self.cookies + [new_cookie]
            self.dump()

    def new(self, snuid, suid):
        return { 'SNUID' : snuid, 'SUID' : suid, 'SUV' : self.get_suv()}

    def new_with_suv(self, snuid, suid, suv):
        return { 'SNUID' : snuid, 'SUID' : suid, 'SUV' : suv}

    def same(self, cx, cy):
        same = True
        for key in ['SNUID', 'SUID', 'SUV']:
            same = same and key in cx and key in cy and cx[key] == cy[key]
        return same

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
