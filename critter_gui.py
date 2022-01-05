#!/usr/bin/env python3
import tkinter as tk
import threading
import critter_model
import critter_main
import color

EMPTY_CHAR = '.'


class CritterGUI():
    def __init__(self, model):
        # Keep track of whether the simulation is currently running or not.
        self.is_running = False
        
        self.model = model
        self.width = 15*self.model.width
        self.height = 15*self.model.height

        self.root = tk.Tk()
        self.root.grid()
        
        self.canvas = tk.Canvas(self.root, bg="white", width=self.width, height=self.height)
        self.canvas.grid(columnspan = 25, rowspan = 10, sticky = 'W')
        self.rectangle = self.canvas.create_rectangle((0, 0, self.width, self.height), fill='white', outline='white')

        # Class states.
        self.classes_label = tk.Label(self.root, text='Classes (Alive + Wins = Total):')
        self.classes_label.grid(column = 25, row = 0, columnspan = 3)
        self.critter_classes = list(self.model.critter_class_states.keys())
        self.num_classes = len(self.critter_classes)
        self.class_state_labels = {}
        ROW=3
        for x in range(self.num_classes):
            self.class_state_labels.update({self.critter_classes[x].__name__:
                                    tk.Label(self.root, text=self.critter_classes[x].__name__+": 25 + 0 = 25\nKarma: 0 Health:2500")})
            self.class_state_labels[self.critter_classes[x].__name__].grid(column=25, row=ROW)
            ROW=ROW+1


        self.speed_label = tk.Label(self.root, text='Speed:')
        self.speed_label.grid(column = 0, row = 10)

        # Change speed of the simulation.
        self.speed_var = tk.IntVar()
        self.speed_var.set(10)
        self.scale = tk.Scale(self.root, variable = self.speed_var, orient='horizontal',
                              length = 100, sliderlength = 10, from_=1, to=10)
        self.scale.grid(column = 1, row = 10)

        # Move count.
        self.move_count = 0
        self.move_count_label = tk.Label(self.root, text='0 moves')
        self.move_count_label.grid(column = 3, row = 10)
        
        # Go - when go, start simulation
        self.go_button = tk.Button(self.root, text = 'Go', bg = 'green',
                                   width = 6, command = self.go)
        self.go_button.grid(column = 8, row = 10)

        # Stop - when pressed, command should pause the simulation
        self.stop_button = tk.Button(self.root, text = 'Stop', bg = 'red',
                                     width = 6, command = self.stop)
        self.stop_button.grid(column = 9, row = 10)

        # Tick - simulation should still not be running, but should update by 1 move
        self.tick_button = tk.Button(self.root, text = 'Tick', bg = 'yellow',
                                     width = 6, command = self.tick)
        self.tick_button.grid(column = 10, row = 10)

        # Reset - stop running, display a new critter model.
        self.reset_button = tk.Button(self.root, text = 'Reset', bg = 'blue',
                                      width = 6, command = self.reset)
        self.reset_button.grid(column = 11, row = 10)

        # Representation of the critter world.
        self.chars = [[self.canvas.create_text((x*15 + 7.5, y*15+7.5), text='', font=('Courier New', -15))
                       for y in range(self.model.height)]
                      for x in range(self.model.width)]

        # Display current critter model.
        self.display()
        self.start()

    def draw_char(self, char, color, x, y):
        """
        Displays a single char at position (x, y) on the canvas.
        """
        self.canvas.itemconfig(self.chars[x][y], text=char, fill=color_to_hex(color), font='Courier 13 bold')
        self.canvas.tag_raise(self.chars[x][y])

    def display(self):
        """
        Draw all characters representing critters or empty spots.
        """
        # Clear screen
        self.canvas.tag_raise(self.rectangle)
        # Draw all critters
        for x in range(self.model.width):
            for y in range(self.model.height):
                critter = self.model.grid[x][y]
                if critter:
                    self.draw_char(critter.getChar(), critter.getColor(), x, y)
                else:
                    self.draw_char(EMPTY_CHAR, color.BLACK, x, y)
    
    def update(self):
        """
        Repeatedly updates the GUI with the appropriate characters and colors from
        the critter simulation, until stop button is pressed to pause simulation. 
        """
        if self.is_running == True:
            self.model.update()
            self.display()
            self.incrementMove()
            self.changeClassState()
            self.root.after(int(500/self.speed_var.get()), self.update)

    def incrementMove(self):
        """
        Increment move count by one and display.
        """
        self.move_count=self.move_count+1
        self.move_count_label.config(text=str(self.move_count)+' moves')

    def changeClassState(self):
        """
        Change the display of states of all critter classes.
        """
        for x in range(self.num_classes):
            alive=self.model.critter_class_states[self.critter_classes[x]].alive
            wins=self.model.critter_class_states[self.critter_classes[x]].wins
            karma=self.model.critter_class_states[self.critter_classes[x]].karma
            health=self.model.critter_class_states[self.critter_classes[x]].health
            total=alive+wins
            self.class_state_labels[self.critter_classes[x].__name__].config(text=self.critter_classes[x].__name__+": "+
			    str(alive)+" + "+str(wins)+" = "+ str(total) + "\nKarma: " + str(karma) + " Health: " + str(health))
                                                                                 
    def go(self):
        "Actually runs the GUI. Pretty straightforward."
        self.is_running = True
        self.update()
     
    def stop(self):
        "Pause updating."
        self.is_running = False

    def tick(self):
        "Move all critters by 1 step."
        self.is_running = False
        self.model.update()
        self.display()
        self.incrementMove()
        self.changeClassState()

    def reset(self):
        "Stop simulation, reset critter model."
        self.is_running = False
        self.model.reset(25)
        self.display()
        self.move_count = 0
        self.move_count_label.config(text='0 moves')

    def start(self):
        self.root.mainloop()

def color_to_hex(color):
    """
    Converts RGB colors to hex string, because tkinter thought that
    passing numeric types as strings was an AWESOME idea.
    """
    return '#%02x%02x%02x'.upper() % (color.r, color.g, color.b)
