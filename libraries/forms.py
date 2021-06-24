#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#add path with necessary files to python
import sys, os

'''
#curdir = os.path.abspath(os.curdir)
path = os.path.abspath(__file__)
curdir = os.path.dirname(path)
sys.path.insert(0, curdir + '/other_files')
sys.path.insert(0, curdir + '/wheel_platform/RPi')
'''


#import necessary libraries for initiating Qt_object
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QByteArray, QEvent, QThread, pyqtSlot, pyqtSignal 

import threading
import time

import init
import lang_source
import record
import output

import reclib
import morse_handler

class InitWindow(QtWidgets.QWidget, init.Ui_Form):
    def __init__(self, widjet, func, pos):
        super().__init__()
        self.setupUi(self)

        self.path = os.path.abspath(__file__)
        self.curdir = os.path.dirname(self.path)
        self.widjet = widjet
        self.func = func
        self.img = QtGui.QImage(self.curdir + "/initImg.jpg")
        self.palette = QtGui.QPalette()
        self.palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(self.img))
        self.setPalette(self.palette)
        self.pos = pos
        
        self.setWindowFlags(Qt.FramelessWindowHint)#nessesary for hide menu bar
        self.move(pos["x"], pos["y"])
        

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Action', "Do you want to close APP?",
                                              QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        dlt = 10
        if event.isAutoRepeat(): dlt = 30
        if event.key() == Qt.Key_Up:
            self.pos.update({"y":self.pos["y"]-dlt})
            self.widjet.posUpdate(self.pos)
        elif event.key() == Qt.Key_Down:
            self.pos.update({"y":self.pos["y"]+dlt})
            self.widjet.posUpdate(self.pos)
        elif event.key() == Qt.Key_Left:
            self.pos.update({"x":self.pos["x"]-dlt})
            self.widjet.posUpdate(self.pos)
        elif event.key() == Qt.Key_Right:
            self.pos.update({"x":self.pos["x"]+dlt})
            self.widjet.posUpdate(self.pos)
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            self.func("init next")
            
    def mouseReleaseEvent(self, event):
        self.func("init next")

class ChooseWin(QtWidgets.QWidget, lang_source.Ui_Form):
    def __init__(self, func, pos):
        super().__init__()
        self.setupUi(self)

        self.path = os.path.abspath(__file__)
        self.curdir = os.path.dirname(self.path)
        self.img = QtGui.QImage(self.curdir + "/init.jpg")
        self.palette = QtGui.QPalette()
        self.palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(self.img))
        self.setPalette(self.palette)
        
        self.ru_button.setFlat(True)
        self.ru_button.setWindowOpacity(0.1)
        self.eng_button.setFlat(True)
        self.file_button.setFlat(True)
        self.record_button.setFlat(True)

        self.func = func

        self.selectFile = ""
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.move(pos["x"], pos["y"])
        
        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.setExclusive(True)
        self.btn_grp.addButton(self.ru_button)
        self.btn_grp.addButton(self.eng_button)
        self.btn_grp.addButton(self.file_button)
        self.btn_grp.addButton(self.record_button)
        self.btn_grp.buttonClicked.connect(self.on_click)

        self.step.clicked.connect(self.countinue)
        self.step.setFlat(True)
        self.step.hide()

        self.btnDict = {"ru_button":     0,
                        "eng_button":    0,
                        "file_button":   0,
                        "record_button": 0,
                        "ru_button_pair": "eng_button",
                        "eng_button_pair": "ru_button",
                        "file_button_pair": "record_button",
                        "record_button_pair": "file_button"
                        }
        self.styleSheets = ["color: black;", #default
                            "color: white;"] #grey


        

    def on_click(self, btn):
        btn_name = btn.objectName()   #geting name of pressed button
        flag = self.btnDict[btn_name]  #read color flag of pressed button
        self.btnDict.update({btn_name: not flag}) #write changed color flag
        pair = self.btnDict[btn_name+"_pair"] #get name of paired button ru-eng
        self.btnDict.update({pair: flag})  #paired buttons in the same position

        if self.btnDict["ru_button"]^self.btnDict["eng_button"]:
            if self.btnDict["record_button"]^self.btnDict["file_button"]:
                self.step.show()
        
        self.btnColorUpdate()

        if btn_name == "file_button":
            self.selectFile = QtWidgets.QFileDialog.getOpenFileName(self, "Open File",
                                                          os.path.abspath(os.curdir) + "/source",
                                                          "AudioFiles (*.mp3 *.wav)")
            self.file_button.setText("File\nSelected")

    def btnColorUpdate(self):
        self.ru_button.setStyleSheet(self.styleSheets[self.btnDict["ru_button"]])
        self.eng_button.setStyleSheet(self.styleSheets[self.btnDict["eng_button"]])
        self.file_button.setStyleSheet(self.styleSheets[self.btnDict["file_button"]])
        self.record_button.setStyleSheet(self.styleSheets[self.btnDict["record_button"]])

    def countinue(self):
        command = "check "
        #set language flag
        if self.btnDict["ru_button"]: command += "1"
        else:                         command += "0"
        #set source flag
        if self.btnDict["file_button"]: command += "1"
        else:                           command += "0"
        self.func(command)

    def reset(self):
        #reset language and source flags
        self.btnDict.update({"ru_button": 0})
        self.btnDict.update({"eng_button": 0})
        self.btnDict.update({"file_button": 0})
        self.btnDict.update({"record_button": 0})
        #reset choose_btn name
        self.file_button.setText("select\nfile")
        #hide continue button
        self.step.hide()
        #update design
        self.btnColorUpdate()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.btnDict["ru_button"]^self.btnDict["eng_button"]:
                if self.btnDict["record_button"]^self.btnDict["file_button"]:
                    self.countinue()
        if event.key() == Qt.Key_Escape:
            reply = QtWidgets.QMessageBox.question(self, 'Action', "Return to\nStart window?",
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                self.func("check return")


class RecordWin(QtWidgets.QWidget, record.Ui_Form):
    def __init__(self, func, pos):
        super().__init__()
        self.setupUi(self)
        
        self.func = func

        self.path = os.path.abspath(__file__)
        self.curdir = os.path.dirname(self.path)
        self.img = QtGui.QImage(self.curdir + "/init.jpg")
        self.palette = QtGui.QPalette()
        self.palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(self.img))
        self.setPalette(self.palette)

        self.recording_now = False

        self.reciver.connect(self.status_reciver)

        self.selectFile = os.path.abspath(os.curdir)+"/output.wav"
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.move(pos["x"], pos["y"])

        self.stopSignal = threading.Event()
        self.ready = threading.Event()

        self.morseWriter = reclib.MorseWriter(self, self.selectFile, self.ready)
        self.thread = QThread()
        self.thread.start()
        self.morseWriter.moveToThread(self.thread)
        
        self.pushButton.clicked.connect(self.REC_control)


    reciver = pyqtSignal(str)

    def REC_control(self):
        if self.recording_now:
            self.morseWriter.stop_trigger.emit(True)
            
        else:
            if self.morseWriter.recorded:
                self.func("record next")
            else:
                self.morseWriter.run_trigger.emit()
                
    #@pyqtSlot()
    def status_reciver(self, msg):
        if msg == "started":
            self.recording_now = True
            self.pushButton.setText("REC")

        elif msg == "REC":
            self.pushButton.setStyleSheet("color: red;")
            th = threading.Thread(target=self.counter)
            th.start()

        elif msg == "saving":
            self.stopSignal.set()
            self.pushButton.setText("saving...")
            self.pushButton.setStyleSheet("color: blue;")

        elif msg == "finished":
            self.pushButton.setText("continue")
            self.pushButton.setStyleSheet("color: rgb(228, 227, 239);")
            self.ready.set()
            self.recording_now = False

        elif msg == "force quit":
            self.func("record return")

    def counter(self):
        timer = time.time()
        while not self.stopSignal.is_set():
            time.sleep(1)
            dif = int(time.time() - timer)
            minute = dif % 100 // 60
            second = dif % 60
            label = "{}{}:{}{}".format(minute//10, minute%10, second//10, second%10)
            self.label_2.setText(label)

    def reset(self):
        self.recording_now = False
        self.stopSignal.clear()
        self.ready.clear()
        self.pushButton.setText("START")
        self.label_2.setText("-:--")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.recording_now:
                reply = QtWidgets.QMessageBox.question(self, 'Action', "Do you want to stop recording\nand\nreturn to Start window?",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.morseWriter.stop_trigger.emit(False)
                    #self.ready.wait()
                    #self.func("record return")

            else:
                reply = QtWidgets.QMessageBox.question(self, 'Action', "Return to\nStart window?",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.func("record return")



class ResCalc(QtWidgets.QWidget, output.Ui_Form):
    def __init__(self, func, pos, path):
        super().__init__()
        self.setupUi(self)

        self.lang = None
        self.func = func

        self.is_process = False
        self.text = []#Soutput
        self.ind = [0, 11]
        self.output.setStyleSheet("color: white;")

        self.recv.connect(self.reciver)

        self.path = os.path.abspath(__file__)
        self.curdir = os.path.dirname(self.path)
        self.img = QtGui.QImage(self.curdir + "/init.jpg")
        self.palette = QtGui.QPalette()
        self.palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(self.img))
        self.setPalette(self.palette)

        self.convertor = morse_handler.Convertor(self, path, self.lang)

        self.thread = QThread()
        self.thread.start()
        self.convertor.moveToThread(self.thread)
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.move(pos["x"], pos["y"])

        self.pushButton.setFlat(True)
        self.pushButton.setStyleSheet("color: white;")
        self.pushButton.clicked.connect(self.presHandl)

        self.output.setWordWrap(True)

        
    recv = pyqtSignal(str)

    def path_update(self, path):
        self.convertor.srFile = path

    def lang_update(self, lang):
        self.convertor.lang = lang

    def presHandl(self):
        if len(self.text) > 0:
            self.func("rescalc close")
        else:
            self.is_process = True
            self.pushButton.setText("computing")
            self.pushButton.setStyleSheet("color: rgb(157, 100, 255);")
            self.pushButton.setEnabled(False)
            self.convertor.run_trigger.emit()
             
        
    def reciver(self, msg):
        buff = []
        if msg[:4] == "info" :
            buff.append(msg[4:])

        elif msg[:4] == "puls":
            buff.append("\n------- binary representation--------\n")
            buff = self.msg_split(buff, msg[4:], 100)

        elif msg[:4] == "mesg":
            buff.append("\n------- decoded text-------\n")
            buff = self.msg_split(buff, msg[4:], 50)

        elif msg == "finished":
            self.is_process = False
            self.pushButton.setEnabled(True)
            self.pushButton.setText("CLOSE")

        elif msg == "err":
            buff.append("\n\nIncorrect file")
            self.is_process = False
            
        elif msg == "force qiut":
            self.func("rescalc return")
            
        self.output_update(buff=buff)
        
    def msg_split(self, buff, msg, tresh):
        while len(msg) > tresh:
            buff.append(msg[:tresh])
            msg = msg[tresh:]
        buff.append(msg)
        return buff
            
    def output_update(self, buff=None, move=None):
        if not move is None and len(self.text) > 11:
            if move and self.ind[0]>0:
                self.ind[0], self.ind[1] = self.ind[0]-1, self.ind[1]-1
            elif not move and self.ind[1] < len(self.text)-1:
                self.ind[0], self.ind[1] = self.ind[0]+1, self.ind[1]+1
        else:
            for i in range(len(buff)):
                self.text.append(buff[i])
                
            self.ind[0], self.ind[1] = len(self.text)-11, len(self.text)-1
        out_str = ""
        if len(self.text) > 11:
            for i in range(self.ind[0], self.ind[1]+1):
                out_str += self.text[i] + "\n"
        else:
            for i in range(len(self.text)):
                out_str += self.text[i] + "\n"
        self.output.setText(out_str)

    def reset(self):
        self.text = ""
        self.output.setText(self.text)
        self.pushButton.setText("START")
            

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if not self.is_process: self.presHandl()

        if event.key() == Qt.Key_Escape:
            if self.is_process:
                reply = QtWidgets.QMessageBox.question(self, 'Action', "Do you want to stop recording\nand\nreturn to Start window?",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.convertor.stop_trigger.emit()

            else:
                reply = QtWidgets.QMessageBox.question(self, 'Action', "Close APP?",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.func("rescalc close")
        elif event.key() == Qt.Key_Up:
            self.output_update(move=True)

        elif event.key() == Qt.Key_Down:
            self.output_update(move=False)

        elif event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_R:
                self.pushButton.setStyleSheet("color: rgb(255, 10, 80);")
                self.convertor.report = "pdf"
