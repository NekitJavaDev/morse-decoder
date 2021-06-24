#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#add path with necessary files to python
import sys, os

path = os.path.abspath(__file__)
curdir = os.path.dirname(path)
sys.path.insert(0, curdir + '/libraries')

#import necessary libraries for initiating Qt_object
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QByteArray, QEvent

import threading #library for implementing multithreading

#design
import forms

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.pos = {"x": 450, "y": 250}
        self.fileSource = "" #path to *.mp3 source file
        
        self.init_win = forms.InitWindow(self, self.pr_handler, self.pos)
        self.choose_win = forms.ChooseWin(self.pr_handler, self.pos)
        self.record_win = forms.RecordWin(self.pr_handler, self.pos)
        self.resCalc = forms.ResCalc(self.pr_handler, self.pos, curdir)
        
        self.langSet = 1  # 1 - RU, 0 - ENG

        self.init_win.show()

    def pr_handler(self, msg):
        com = msg.split()
        if com[0] == "init":
            if com[1] == "next":
                self.init_win.hide()
                self.choose_win.show()
        elif com[0] == "check":
            if com[1] == "return":
                self.reset_func()
                self.choose_win.hide()
                self.init_win.show()
            else:
                #self.langSet = int(msg[-2])
                self.resCalc.lang_update(int(msg[-2]))
                if int(msg[-1]):
                    #self.fileSource = self.choose_win.selectFile[0]
                    self.resCalc.path_update(self.choose_win.selectFile[0])
                    self.choose_win.hide()
                    self.resCalc.show()
                    
                else:
                    self.choose_win.hide()
                    self.record_win.show()
                    
        elif com[0] == "record":
            if com[1] == "return":
                self.reset_func()
                self.record_win.hide()
                self.init_win.show()
            elif com[1] == "next":
                #self.fileSource = self.record_win.selectFile
                self.resCalc.path_update(self.record_win.selectFile) 
                self.record_win.hide()
                self.resCalc.show()

        elif com[0] == "rescalc":
            if com[1] == "return":
                self.reset_func()
                self.resCalc.hide()
                self.init_win.show()
            if com[1] == "close":
                self.resCalc.hide()
                self.close()
                
    def posUpdate(self, pos):
        self.init_win.move(self.pos["x"], self.pos["y"])
        self.choose_win.move(self.pos["x"], self.pos["y"])
        self.record_win.move(self.pos["x"], self.pos["y"])
        self.resCalc.move(self.pos["x"], self.pos["y"])
                
    def reset_func(self):
        self.choose_win.reset()
        self.record_win.reset()
        self.resCalc.reset()


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainWindow()  # Создаём объект класса ExampleApp
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
