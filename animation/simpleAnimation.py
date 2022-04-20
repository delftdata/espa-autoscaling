import tkinter as tk
import random

class Circle:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, canvas):

def move():
    x_vel = 5
    y_vel = 0
    alive = True

    canvas1.move(circle, x_vel, y_vel)
    coordinates = canvas1.coords(circle)

    x = coordinates[0]
    y = coordinates[1]

    # if outside screen move to start position
    print(canvas_width)
    print(x)
    if x > canvas_width-100:
        alive = False
    if alive:
        window.after(33, move)


canvas_width = 500
canvas_height = 500

window = tk.Tk()
window.geometry(str(canvas_height) + "x" + str(canvas_width))

canvas1 = tk.Canvas(window, height=canvas_height, width=canvas_width)
canvas1.grid(row=0, column=0, sticky='w')


start_x = 75
start_y = 187.5

x = start_x
y = start_y

width  = 5
height = 5

x_vel = 5
y_vel = 5


coord = [x, y, x+width, y+height]
circle = canvas1.create_oval(coord, outline="red", fill="red")

coord = [400-20, 100-20, 400, 100]
rect2 = canvas1.create_rectangle(coord, outline="Blue", fill="Blue")

coord = [400-20, 200-20, 400, 200]
rect2 = canvas1.create_rectangle(coord, outline="Blue", fill="Blue")

coord = [400-20, 300-20, 400, 300]
rect2 = canvas1.create_rectangle(coord, outline="Blue", fill="Blue")

move()

window.mainloop()