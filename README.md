# Data-streamer
A python benchmarking tool for testing different analytic processes and their suitability for use in real time data stream processing.
This project uses pybind11 to connect between cpp and python code to build a truely multi-threaded application within a python wrapper.
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




