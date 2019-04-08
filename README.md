# Data-streamer
A python benchmarking tool for testing different analytic processes and their suitability for use in real time data stream processing.
This project uses [pybind11](https://github.com/pybind/pybind11) to connect between cpp and python code to build a truely multi-threaded application within a python wrapper.
This means that your inputs, outputs and user interface is all handled by python and subsquentialy your favourite brand of data analysis and visulization tools. While the actual data processing is done by worker threads setup within a cpp class object. 


To Run: 
A) Visual Studio Version:
Open the solution up in Visual studio navigate to the python project: DataStreamer.py, Click Start with or without debuging.
Visual studio will take care of the compiling of the cpp code for you and the solution will run.

B) Python application Version:
First Build the cpp code using pybind11
```Python Setup.py ```

Then Run the Datastreamer python file:
```Python Datastreamer.py```

To build this code you need to have two additional files, ```Python.h``` and ```Python36.lib```. These files shoudl be in your visual studio shared folder, somewhere like this: ```C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python36_64\``` and in the *include* and *libs* folders respectively. If your copy of these files are somewhere else, you can point visual studio to them using properties menu for the DataStreamerCpp project in the solution window.


*Projects:*

**DataStreamer** This project is the python wrapper project that encompasses the entire application. 
    *DataStreamer.py* the main python file for the application. Run this file to begin the application outside of visual studio.\
     **DataStreamer/Datasets** the folder where we can load our dataset csv from. Currently it only contains the kdd99 dataset for testing with.\
**DataStreamerCpp** This is the cpp files for the application that are called by the python wrapper to perform the actual processing.
    *Module.cpp* the main file for this project, contains the cpp class that all the work is done through.
