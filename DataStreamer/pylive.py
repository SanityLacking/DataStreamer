#file for functions to do my live plotting.
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time
# use ggplot style for more sophisticated visuals

plt.style.use('ggplot')

#custom pause function that doesn't force the window back into the foreground.
def mypause(interval):
    backend = plt.rcParams['backend']
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            canvas.start_event_loop(interval)
            return


def live_plotter(x_vec,y1_data,line1,identifier='',pause_time=0.016, figure = None ):        
    if line1==[]:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()        
        if type(figure) is not matplotlib.figure.Figure:    #check to determine if a figure is handed to the function. if so, use it, else make one.
            fig = plt.figure(figsize=(13,6))              
            print("no figure")
        else:
            fig = figure
            print("provided figure")
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec,y1_data,'-o',alpha=0.8)        
        #update plot label/title
        plt.ylabel('Y Label')
        plt.title('Title: {}'.format(identifier))       
        plt.show()
            
    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    # adjust limits if new data goes beyond bounds
    if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
        plt.ylim([np.min(y1_data)-np.std(y1_data),np.max(y1_data)+np.std(y1_data)])
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    #plt.pause(pause_time)
    mypause(pause_time)   
    
    # return line so we can update it again in the next iteration
    return line1

