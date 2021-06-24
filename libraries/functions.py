#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import numpy as np

DIRECT = 0.7

class Functions():
    def __init__(self, debug=False):
        self.aprox_a = 0.0227
        self.aprox_b = -0.3794
        self.aprox_c = 4.6459

        self.div_ones_a = 1.0958*DIRECT
        self.div_ones_b = 5.2116*DIRECT

        self.debug = debug

    def convBulr(self, vec, rate=None, frame=None):
        if not rate is None:
            rate = rate // 1000
            frame = int(self.aprox_a*math.pow(rate, 2) + self.aprox_b*rate + self.aprox_c)
            if self.debug: print("blurring frame size:{}".format(frame))

        if frame is None: return vec

        #frame = frame // 3

        if not frame % 2: frame -= 1

        hf = frame // 2
        blur = [ 0 for el in range(hf)] #add first elements not used in loop below 
        for step in range(hf, len(vec) - hf):
            blur.append( int( np.mean(vec[step - hf : step + hf])))
        blur += [0 for el in range(hf)] #add last elements not used in loop below 
        
        return blur
        
#y=1.0958*x+5.2116 for ones
    def division(self, vec, flag):
        #flag == False - zeros, flag == True - ones
        tresh = []
        sort = np.sort(vec)
        dif = np.diff(sort)
        if self.debug:
            print(sort)
            print(dif)
        if flag:
            for el in range(len(dif))[2:-1]: #[2:-1] first step - 3th element, and last step is penultimate element in secuence
                mn = np.mean(sort[:el]) + 1
                #dlt = self.div_a*mn + self.div_b
                if dif[el] > mn/2:# and dif[el+1] < dif[el]:
                    tresh.append(sort[el])
                    break
        else:
            mn = 0
            for el in range(len(dif))[2:-1]: #[2:-1] first step - 3th element, and last step is penultimate element in secuence
                mn = np.mean(sort[:el])
                #dlt = self.div_a*mn + self.div_b
                if dif[el] > mn*1.5 and dif[el+1] < dif[el]:
                    tresh.append(sort[el])
                    break
            for el in reversed(range(len(dif))): 
                if dif[el] > mn:
                    tresh.append(sort[el+1])
                    break
        if self.debug: print(tresh)
        return tresh
            
            
            
    
if __name__ == "__main__":
    function = Functions()
    vec = [1, 2, 3, 4, 5, 6, 9, 2, 2, 4, 4 ,6, 7, 4, 188, 4 , 3, 4, 56, 3]
    function.convBulr(vec, rate=8100)
        
