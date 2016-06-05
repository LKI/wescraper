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

if __name__ == "__main__":
    cookies = Cookie()
    init_list = [
        cookies.new_with_suv('E7CEFA89EEEBD96E9D77CDDCEE0B7C76', '0A20146766CA0D0A000000005753DDA2', '1465114018152092'),
        cookies.new_with_suv('200A3D4E2A2C1EAABDB2E2512AC8CACB', '0A2014676F1C920A000000005753E030', '1465114672478651'),
        cookies.new_with_suv('CAE1D5A7C1C4F4425BF0305EC1E46D8F', '0A2014676F1C920A000000005753E05B', '1465114721115845'),
        cookies.new_with_suv('E6D3FC16212716A2C47DB61322665669', 'C7F1DD346A20900A000000005753E549', '1465115977684714'),
        cookies.new_with_suv('231438D0E4E1D0670113C244E5696087', 'C7F1DD346B20900A000000005753E553', '1465115987543482'),
    ]
    for cookie in init_list:
        if not cookies.has(cookie):
            cookies.add(cookie)
    cookies.dump()
    print "Current cookies are:"
    print cookies.get_cookies()
