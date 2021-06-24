#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#libraries for design (PyQt5)
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QEventLoop, QThread, QObject, pyqtSlot, pyqtSignal

#libraries for morse decoding
import scipy.io.wavfile as wavfile
import pydub
# from pydub import pyaudioop
import csv
from numpy.fft import fft
from matplotlib.pyplot import *
from numpy import *

import sys, os

import functions

#DEBUG = True
DEBUG = False


class Convertor(QObject):
    
    run_trigger = pyqtSignal()
    stop_trigger = pyqtSignal()

    def __init__(self, widjet, path, lang, report=None):
        super(Convertor, self).__init__()

        self.run_trigger.connect(self.run)
        self.stop_trigger.connect(self.stop)

        self.widjet = widjet
        self.functions = functions.Functions(DEBUG)
        self.curdir = os.path.abspath(os.curdir) + "/libraries/"
        self.path_to_csv = [self.curdir+"codes.csv", self.curdir+"RUcodes.csv"]
        self.srFile = ""
        self.lang = lang #True - RU, False - ENG
        self.report = report
        self.is_stopped = False
        self.plotter = None
        self.path = path + "/output/"

    @pyqtSlot()
    def run(self):
        try:
            if DEBUG: print("debug mode turn ON")
            self.widjet.recv.emit("infoStart convertation")
            self.plotter = DummyPlotter()
            the_file, pulses, code_string = None, None, None
            if not self.report is None:
                self.plotter = Plotter(self.path, self.report)
                if DEBUG: print("grafical OUPUT turn ON")
            
            if not self.is_stopped:
                self.widjet.recv.emit("infoReading audio file...")
                the_file = SoundFile(self, self.srFile)
                the_file.saveplot("original")
    
            if not self.is_stopped:
                self.widjet.recv.emit("infoFiltering...")
                signalFilter = SignalFilter(self)
                signalFilter.filter(the_file)
                #the_file.saveas("filtered.wav")
              
            if not self.is_stopped:
                self.widjet.recv.emit("infoPrerearing pulses...")
                analyzer = SpectreAnalyzer(self, the_file.rate)
                pulses = analyzer.findpulses(the_file)
            
            if not self.is_stopped:
                self.widjet.recv.emit("infoGeting Morse Pulses...")
                pul_translator = PulsesTranslator()
                code_string = pul_translator.tostring(self, pulses)
                self.widjet.recv.emit("puls"+code_string)
                
            if not self.is_stopped:
                self.widjet.recv.emit("infoReading audio file...")
                str_translator = StringTranslator(self.lang, self.path_to_csv)
                #print(code_string)
                s = str_translator.totext(code_string)
                self.widjet.recv.emit("mesg"+s)
                #print(s)
        except Exception as e:
            print(e)
            self.widjet.recv.emit("err")
             
        msg = "finished"
        if self.is_stopped: msg = "force qiut"
        self.widjet.recv.emit(msg)
        


    @pyqtSlot()
    def stop(self):
        self.is_stopped = True


class Plotter:
    def __init__(self, path, format="pdf"):
        self.format=format
        self.path = path
        
    def saveplot(self, name, data, length=-1, height=-1, dpi=None):
        plot(data)
        if length != -1:
            axis(xmax=length)
        if height != -1:
            axis(ymax=height)
        savefig(self.path + name + "." + self.format, format=self.format, dpi=dpi)
        cla()

    def specgram(self, name, signal):
        nfft = 1024#256  # Length of the windowing segments
        fs = 44100#44100   # Sampling frequency
        spectrogram = specgram(signal, NFFT=nfft, Fs=fs, noverlap=900, cmap=cm.gist_heat)
        #savefig(self.path + name + "." + self.format, format=self.format)
        cla()
        return spectrogram

class DummyPlotter:
    def saveplot(self, name, data, length=-1, height=-1, dpi=None):
        return None

    def specgram(self, name, signal):
        nfft = 1024  # Length of the windowing segments
        fs = 44100#44100   # Sampling frequency
        #print(signal)
        spectrogram = specgram(signal, NFFT=nfft, Fs=fs, noverlap=900, cmap=cm.gist_heat)
        cla()
        return spectrogram

class SoundFile:

    def __init__(self, handler, path):
        #1 - leer el archivo con las muestras
        #	el resultado de read es una tupla, el elemento 1 tiene las muestras
        if path[-3:] == "mp3":
            the_file = pydub.AudioSegment.from_mp3(path)
            self.rate = the_file.frame_rate
            self.data = the_file.get_array_of_samples()
            self.length = len(self.data)
        # elif path[-3:] == "wav":
        #     the_file = wavfile.read(path)
        #     self.rate = the_file[0]
        #     self.length = len(the_file[1])
        #     self.data = the_file[1]
        elif path[-3:] == "wav":
            the_file = wavfile.read(path)
            self.rate = the_file[0]
            self.data = the_file[1]
            self.length = len(self.data)
        if DEBUG: print("Rate: {}, length: {}".format(self.rate, self.length))
        self.handler = handler
        # appendea ceros hasta completar una potencia de 2
        power = 10
        while pow(2,power) < self.length:
            power += 1
        #print(power)
        self.data = append(self.data, zeros(pow(2,power) - self.length))
	
    def setdata(self, data):
        self.data = data

    def getdata(self):
        return self.data

    def getlength(self):
        return self.length

    def saveas(self, path):
        wavfile.write(path, self.rate, self.data)

    def saveplot(self, fileName):
        self.handler.plotter.saveplot(fileName,self.data,length=self.length)


class SignalFilter:
    def __init__(self, handler):
        self.handler = handler

    def filter(self, soundfile):
        #2 - aplico transformada de fourier
        trans = fft.rfft(soundfile.getdata())
        trans_real = abs(trans)
	#2b - lo grafico
        self.handler.plotter.saveplot("transformed",trans_real)
	#3 - busco la frecuencia
        band = 2000
        # ignore the first 200Hz
        hzignored = 200
        frec = hzignored + argmax(trans_real[hzignored:])
        #print( argmax(trans_real[hzignored:]))
	#print( trans_real[frec])
        #print( frec)
        mn = int((frec - band / 2) if (frec > band / 2) else 0)
        filter_array = append(zeros(mn), ones(band))
        filter_array = append(filter_array, zeros(len(trans_real) - len(filter_array)))
        filtered_array = multiply(trans, filter_array)
        self.handler.plotter.saveplot("filtered_trans",abs(filtered_array))
        #4 - antitransformo
        filtered_signal = array(fft.irfft(filtered_array)[:soundfile.getlength()], dtype="int16")
        self.handler.plotter.saveplot("filtered_signal",filtered_signal)
        soundfile.setdata(filtered_signal)

class SpectreAnalyzer:
    def __init__(self, handler, rate):
        self.handler = handler
        self.rate = rate
        

    def spectrogram(self, signal):
        spectrogram = self.handler.plotter.specgram("spectrogram", signal)
        return spectrogram

    def sumarizecolumns(self, mat):
        vec_ones = ones(len(mat))
        vec_sum = (matrix(vec_ones) * matrix(mat)).transpose()
        self.handler.plotter.saveplot("frecuency_volume",vec_sum[1500:])
        blur = self.handler.functions.convBulr(vec_sum, self.rate)
        self.handler.plotter.saveplot("f_blur",blur[1500:])
        return blur

    def findpresence(self, vec_sum):
        presence = zeros(len(vec_sum))
        #threshold = max(vec_sum) / 2.0
        threshold = mean(vec_sum)
        if DEBUG: print("treshhold: {}, mean: {}".format(threshold, mean(vec_sum)))
        for i in range(len(presence)):
            if vec_sum[i] > threshold:
                presence[i] = 1
        self.handler.plotter.saveplot("presence", presence[1500:], dpi=300, height=5)
        return presence

    def findpulses(self, soundfile):
        spec = self.spectrogram(soundfile.getdata())
        # spec[0] es la matriz del rojo
        red_matrix = spec[0]
        vec_sum = self.sumarizecolumns(red_matrix)
        presence = self.findpresence(vec_sum)
        return presence

class ShortLong:
    '''
    def __init__(self, shorts, longs):
        self.shortmean = mean(shorts)
        self.shortstd = std(shorts)
        self.longmean = mean(longs)
        self.longstd = std(longs)
        print("short: (" + repr(self.shortmean) + ", " + repr(self.shortstd) + ")\n\long: (" + repr(self.longmean) + ", " + repr(self.longstd) + ")")
    '''
    def __init__(self, shorts, longs):
        ###print("short = "+str(len(shorts)))
        ###print("long = "+str(len(longs)))
        self.shortmean = around(mean(shorts))
        self.shortstd = self.dev(shorts, self.shortmean)
        self.longmean = around(mean(longs))
        self.longstd = self.dev(longs, self.longmean)
        #print("short: (" + repr(self.shortmean) + ", " + repr(self.shortstd) + ")\n\long: (" + repr(self.longmean) + ", " + repr(self.longstd) + ")")

    def dev(self, vec, mean):
        mx = max(vec)
        mn = min(vec)
        dev = mx - mean
        if dev < mean - mn: dev = mean - mn
        return dev
    
    def tostring(self):
        return "short: (" + repr(self.shortmean) + ", " + repr(self.shortstd) + ")\n\long: (" + repr(self.longmean) + ", " + repr(self.longstd) + ")"

class PulsesAnalyzer:
        
    def compress(self, pulses):
        vec = []
        i = 0
                
        if pulses[0] == 1:
            vec += [0]
            i = 1
                
        last = pulses[0]
                
        while i < len(pulses):
            c = 0
            last = pulses[i]
            while i < len(pulses) and pulses[i] == last:
                i += 1
                c += 1
            vec += [c]
            i += 1
                
        vec = vec[1:-1]
        return vec

    def split(self, vec):
        onesl = zeros(1+len(vec)//2)
        zerosl = zeros(len(vec)//2)
        for i in range(len(vec)//2):
            onesl[i] = vec[2*i]
            zerosl[i] = vec[2*i+1]
        onesl[-1] = vec[-1]
        return (onesl, zerosl)

    def findshortlongdup(self, vec):
        sor = sort(vec)
        ###print(sor)
        last = sor[0]
        for i in range(len(sor))[1:]:
            if sor[i] > 2*last:
                shorts = sor[:i-1]
                longs = sor[i:]
                return (shorts, longs)
        return (vec, [])

    def createshortlong(self, shorts, longs):
        return ShortLong(shorts, longs)

    def findshortlong(self, vec):
        dup = self.findshortlongdup(vec)
        return self.createshortlong(dup[0], dup[1])

class SymbolDecoder:
    def __init__(self, th_ones, th_zeros):
        self.th_ones = th_ones[0] #longest point duration 
        self.th_zeros_c = th_zeros[0] #longest delay duration inside caracter
        self.th_zeros_w = th_zeros[1] #smallest delay duration between words

    def getonesymbol(self, drt):
        if drt <= self.th_ones: return "."
        else: return "-"    
        
    def getzerosymbol(self, drt):
        if drt >= self.th_zeros_w: return " | "
        elif drt <= self.th_zeros_c: return ""
        else: return " "

class PulsesTranslator:
    def tostring(self, handler, pulses):
        pa = PulsesAnalyzer()
        comp_vec = pa.compress(pulses)
        if DEBUG:
            ###print(comp_vec)
            st = ""
            for i in range(len(comp_vec)//2):
                st += " " + str(comp_vec[2*i])
                st += " !" + str(comp_vec[2*i + 1])
            st += " " + str(comp_vec[-1])
            print(st)
        
        ###print(reas)
        ###print(len(comp_vec))
        comp_tup = pa.split(comp_vec)
           
        if DEBUG: print("\nones")
        #onessl = pa.findshortlong(comp_tup[0])
        th_ones = handler.functions.division(comp_tup[0], True)
        # zeros are subdivided
        if DEBUG: print("\nzeros")
        th_zeros = handler.functions.division(comp_tup[1], False)
        #dup = pa.findshortlongdup(comp_tup[1])
        #dup2 = pa.findshortlongdup(dup[1])
        ###print("zeros small")
        #zerossl = pa.createshortlong(dup[0], dup2[0])
        ###print("zeros long")
        #zeroextra = pa.createshortlong(dup2[0], dup2[1])
                
        symdec = SymbolDecoder(th_ones, th_zeros)
                
        s = ""
        for i in range(len(comp_vec)//2):
            s += symdec.getonesymbol(comp_vec[2*i])
            s += symdec.getzerosymbol(comp_vec[2*i+1])
        s += symdec.getonesymbol(comp_vec[-1])
        return s

    def debris_elimin(self, vec):
        pass

class Codes:
    def __init__(self, path):
        data = csv.DictReader(open(path), delimiter=',', fieldnames=["char", "code"])
        self.dic = {}
        for entry in data:
            self.dic[entry["code"]] = entry["char"]
        
    def tochar(self, code):
        #if self.dic.has_key(code): #has_key was removed in Python3.x
        if code in self.dic.keys():
            return self.dic[code]
        return "?"

class StringTranslator:
    def __init__(self, lang, path_to_csv):
        self.lang = lang
        self.path_to_csv = path_to_csv
        self.codes = Codes(self.path_to_csv[lang])
        

    def totext(self, s):
        text = ""
        for code in s.split():
            if code == "|":
                char = " "
            else:
                char = self.codes.tochar(code)
            text += char
        return text
