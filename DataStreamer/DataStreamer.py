
from itertools import islice
from random import random
import time
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
from DataStreamerCpp import dsStream  #custom module that wraps the cpp file api.
from matplotlib import interactive
import datetime as dt
import matplotlib.animation as animation
interactive(True)


cppProcess = dsStream()
CSVfileName ="../datasets/kdd99-unsupervised-ad.csv"
MAXROWS = 100


#update the graph
def update_line(hl, new_data):
    hl.set_xdata(numpy.append(hl.get_xdata(), new_data))
    hl.set_ydata(numpy.append(hl.get_ydata(), new_data))
    plt.draw()




    # This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    # Read temperature (Celsius) from TMP102
    temp_c = round(tmp102.read_temp(), 2)

    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(temp_c)

    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ys = ys[-20:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('TMP102 Temperature over Time')
    plt.ylabel('Temperature (deg C)')

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


        #currently the code is breaking here, TODO figure out why getCurrentInputCount is breaking.
        #error is in the processThread in the cpp file.
        #I think the problem is there is no error checking for running front() and pop_front() when the dqueue is empty. TODO add in try catch blocks to fix this.
            #for i in range (100):                
            #    print("inputCount: {}".format(cppProcess.getCurrentInputCount()))
            #    plt.scatter
            #    time.sleep(0.01)
        #inputCount = pd.DataFrame([])

        hl, = plt.plot([],[])
        # Data for plotting
        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)

        fig, ax = plt.subplots()
        ax.plot(t, s)

        ax.set(xlabel='time (s)', ylabel='voltage (mV)',title='About as simple as it gets, folks')
        ax.grid()

        plt.show()
        #input()
        #inputSeries = pd.DataFrame
        #for i in range (1000):
         
        #inputCount = pd.DataFrame({"input":cppProcess.getCurrentInputCount()})                
        #update_line(hl, inputCount)
        # Create figure for plotting
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        xs = []
        ys = []
        ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
        time.sleep(10)
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
    startDataStream()
    

