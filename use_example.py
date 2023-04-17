#an example of how the zoom_map library should be used

import pandas as pd #for loading node and line info  from csv files
import tkinter as tk

#extract latitude and longitude from a string of coordinates (in the format provided by google maps)
def extract_coordinates(coordinates):
    #extract the latitude and longitude strings
    latitude = ''
    longitude = ''
    extracting_longitude = False
    i = 0
    while i < len(coordinates):
        if coordinates[i] == ',':
            extracting_longitude = True
            i = i + 2
        else:
            if extracting_longitude:
                longitude += coordinates[i]
            else:
                latitude += coordinates[i]
            i = i + 1
        
    return float(latitude),float(longitude)

class example():
    def __init__(self):
        self.setup_data() #import and setup data for our example
        self.create_window() #create the window

    def setup_data(self):
        while True: #wait till valid mode selected
            select_mode = input("Are we using 'manual' or 'node' lines: ")
            if select_mode == 'manual':
                print("manual lines selected")
                break
            elif select_mode == 'node':
                print('node lines selected')
                break
            else:
                print(select_mode," not a valid mode, please type 'manual' or 'node' ")

        #now we have selected a mode, import the example files
        nodes_csv = pd.read_csv('example_nodes.csv',thousands=r',')
        lines_csv = pd.read_csv('example_lines.csv',thousands=r',')
        #extract info from nodes
        self.node_names = nodes_csv["Name"].to_list()
        node_positions = nodes_csv["Location"].to_list()
        self.node_latitudes = []
        self.node_longitudes = []
        #extract node coordinates
        for position in node_positions:
            latitude,longitude = extract_coordinates(position)
            self.node_latitudes.append(latitude)
            self.node_longitudes.append(longitude)

    #create the window in which our map will be displayed
    def create_window(self):
        #create a tkinter window in which we will place our map
        self.window = tk.Tk()
        self.window.attributes("-fullscreen", True) #make the window full screen
        #window.eval('tk::PlaceWindow . center')
        self.window.title('Network Simulation')
        
        
    def setup_map(self):
        window_width = self.window.winfo_screenwidth()
        window_height = self.window.winfo_screenheight()
        self.canvas_width = window_width-440
        self.canvas_height = window_height-100

def main():
    a = example()
    finish = input('exit?\n')



if __name__=="__main__":
    main()