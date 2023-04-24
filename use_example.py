#an example of how the zoom_map library should be used

import pandas as pd #for loading node and line info  from csv files
import tkinter as tk
import zoom_map

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
        self.setup_map() #create the map

    def setup_data(self):
        while True: #wait till valid mode selected
           select_mode = input("Are we using 'manual' or 'node' lines: ")
           if select_mode == 'manual':
               print("manual lines selected")
               self.node_type = 'none'
               break
           elif select_mode == 'node':
               print('node lines selected')
               self.node_type = 'node'
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
        self.num_nodes = len(self.node_names)
        self.node_radii = [5]*self.num_nodes
        self.node_colours = ['black']*self.num_nodes
        #extract info from lines
        self.line_start_nodes = lines_csv["Start"].to_list()
        self.line_end_nodes =   lines_csv["End"].to_list()
        self.num_lines = len(self.line_start_nodes)
        self.line_width = [3]*self.num_lines
        self.line_colour = ['grey']*self.num_lines
        self.line_names = ['testing name']*self.num_lines
        self.line_info_name = 'none'
        self.line_info_type = 'none'
        self.lines_info = ['nothing']*self.num_lines
        if self.node_type=='node':
            self.start_node_index = []
            self.end_node_index = []
            self.start_node_type = ['node']*self.num_lines
            self.end_node_type = ['node']*self.num_lines
            for i in range(self.num_lines):
                start_node_name = self.line_start_nodes[i]
                end_node_name = self.line_end_nodes[i]
                start_node_index = self.get_node_index(start_node_name)
                end_node_index = self.get_node_index(end_node_name)
                self.start_node_index.append(start_node_index)
                self.end_node_index.append(end_node_index)
                

    
    #lookup a node name within the list of nodes and return it's index
    #this does not have any safety mechanisms yet
    def get_node_index(self,node_name):
        node_index = self.node_names.index(node_name)
        return node_index


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
        map_width = window_width-440
        map_height = window_height-100
        self.map = zoom_map.ZoomMap(map_width,map_height,self.window,'white')
        #option selection
        #now map is created, draw the nodes
        self.map.create_nodes(self.node_longitudes,self.node_latitudes,self.node_radii,self.node_colours,self.node_names)
        if self.node_type=='node':
            self.map.create_lines(self.line_width,self.line_colour,self.line_names,self.line_info_name,self.line_info_type,self.lines_info,lines_start_node_type=self.start_node_type,lines_end_node_type=self.end_node_type,lines_start_node_index=self.start_node_index,lines_end_node_index=self.end_node_index)
        self.map.determine_scale() #use automatic scaling by default
        self.map.calculate_pixel_coordinates() #calculate pixel coordinates of objects
        self.map.render_lines() #render the lines
        self.map.render_nodes() #render the nodes

        
        

def main():
    a = example()
    finish = input('exit?\n')



if __name__=="__main__":
    main()