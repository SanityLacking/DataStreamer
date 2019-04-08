
from itertools import islice
from random import random
import time
import csv
import os
import numpy as np
import matplotlib as plt
import pandas as pd
import sys
from DataStreamerCpp import dsStream

cppProcess = dsStream()
CSVfileName ="../datasets/kdd99-unsupervised-ad.csv"
MAXROWS = 100
#COUNT = 500000  # Change this value depending on the speed of your computer
#DATA = list(islice(iter(lambda: (random() - 0.5) * 3.0, None), COUNT))

#e = 2.7182818284590452353602874713527

#def sinh(x):
#    return (1 - (e ** (-2 * x))) / (2 * (e ** -x))

#def cosh(x):
#    return (1 + (e ** (-2 * x))) / (2 * (e ** -x))

#def tanh(x):
#    tanh_x = sinh(x) / cosh(x)
#    return tanh_x

#def test(fn, name):
#    start = time.perf_counter()
#    result = fn(DATA)
#    duration = time.perf_counter() - start
#    print('{} took {:.3f} seconds\n\n'.format(name, duration))

#    for d in result:
#        assert -1 <= d <= 1, " incorrect values"



def startDataStream():   
    count = 0
    inputFile =[]
    with open(CSVfileName, "r", newline='') as csvfile:
        for row in csvfile:
            if MAXROWS > 0 and count >= MAXROWS:
               break
            count= count + 1
            inputFile.append(row.encode('utf-8'))
            sys.stdout.write("currently reading {} rows \r".format(count))
            sys.stdout.flush()
        csvfile.close()
        print("total rows counted:{}".format(count))
         
        string_length = len(inputFile)
        print("inputCount: {}".format(cppProcess.getCurrentInputCount()))


        sent = cppProcess.initReaders(inputFile)
        print("initReader {}".format(sent))
        
        
        #time.sleep(1) #apparently using a sleep breaks things for some reason? no idea why.
        #for i in range (1000):

        try:
            for i in range (10):
                print("inputCount: {}".format(cppProcess.getCurrentInputCount()))
                time.sleep(0.1)
        except:
            print("it broke again")
        
        print("inputCount contents: {}".format(cppProcess.getCurrentInput()))

        ### Results ###
        results = cppProcess.getResults()
        print("return results: {}".format(results))                         
        results = ''.join(results)
        try:
            df = pd.read_csv(pd.compat.StringIO(results), header=None)
            print(df.head())
            print(df.shape)
        except: 
            print("error: results not in a csv format.")
        



if __name__ == "__main__":
    #print('Running benchmarks with COUNT = {}'.format(COUNT))
    #test(lambda d: [tanh(x) for x in d], '[tanh(x) for x in d] (Python implementation)')
    #from superfastcode import fast_tanh2
    #test(lambda d: [fast_tanh2(x) for x in d], '[fast_tanh2(x) for x in d] (PyBind11 C++ extension)')



    startDataStream()
    
    #print("start Counter")
    #cppProcess.startCounter(2)
    #print(cppProcess.getCounter())
    #for i in range (50):
    #    time.sleep(0.1)
    #    print(cppProcess.getCounter())

    #print("after threads")
    #print(cppProcess.getCounter())    
    ##print(cppProcess.sum(2))
