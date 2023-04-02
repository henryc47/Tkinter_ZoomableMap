#zoom_map.py
#A python package to create a zoomable map (like Google Maps) using tkinter

#dependencies
import tkinter as tk


#this class is the zoomable map
class ZoomMap(self):

    #create the map
    def __init__(self,map_width,map_height,window,background="white",zoom_control="<MouseWheel>",drag_start_control='<ButtonPress-1>',drag_end_control="<B1-Motion>",print_warnings=True):
        self.map_width = map_width #width (horizontal length) of the map display in pixels
        self.map_height = map_height #height (vertical length) of the map display in pixels
        self.map_center_x = int(self.map_width/2) #midpoint of the map in pixels, horizontal
        self.map_center_y = int(self.map_height/2) #midpoint of the map in pixels, vertical
        self.window = window #tk object in which the canvas is drawn
        self.background = background #background object, at the moment only supports tk colours
        self.print_warnings = print_warnings #do we print warning and error messages
        #create the canvas object
        self.map = tk.Canvas(self.window,bg=self.background,width=self.map_width,height=self.map_height)
        #bind the canvas to the controls to zoom and drag the image
        #try blocks catch invalid keybindings and replace them with the defaults
        #bind zoom
        try:
            self.canvas.bind(zoom_control,self.zoom_map)
        except:
            if self.print_warnings:
                print("WARNING : ",zoom_control,' not a valid keybinding for tkinter. Defaulting to  "<MouseWheel>", for zoom keybinding')
            self.canvas.bind("<MouseWheel>",self.zoom_map)
        #bind starting to drag the map
        try:
            self.canvas.bind(drag_start_control,self.drag_start_map)
        except:
            if self.print_warnings:
                print("WARNING : ",drag_start_control,' not a valid keybinding for tkinter. Defaulting to  "<ButtonPress-1>", for drag start keybinding')
            self.canvas.bind("<ButtonPress-1>",self.drag_start_map)
        #bind stopping a drag
        try:
            self.canvas.bind(drag_end_control,self.drag_end_map)
        except:
            if self.print_warnings:
                print("WARNING : ",drag_end_control,' not a valid keybinding for tkinter. Defaulting to  "<B1-Motion>", for drag end keybinding')
            self.canvas.bind("<B1-Motion>",self.drag_end_map)

    #zoom the map in/out
    def zoom_control(self,event):
        pass #placeholder for now

    #start dragging the map
    def drag_start_control(self,event):
        pass #placeholder for now

    #stop dragging the map
    def drag_end_control(self,event):
        pass #placeholder for now





    