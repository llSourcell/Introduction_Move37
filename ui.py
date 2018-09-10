from tkinter import *
from tkinter import messagebox
import math

CELL_SIZE = 80
CELL_PADDING = 10
ARROW_LENGTH = CELL_SIZE / 2

class GridWorldWindow(object):
    """Manages all of the UI
    """
    def __init__(self, metadata):
        self.window = Tk()
        self.window.title('Gridworld')
        self.window.geometry('{}x{}'.format(1080, 720))

        # extract data from the JSON
        self.grid_width = metadata['width']
        self.grid_height = metadata['height']
        self.obstacles = [tuple(obstacle) for obstacle in metadata['obstacles']]
        self.terminals = [tuple(terminal['state']) for terminal in metadata['terminals']]

        self.canvas_width = metadata['width'] * CELL_SIZE
        self.canvas_height = metadata['height'] * CELL_SIZE

        # create the tkinder IDs for all of the modifiable UI
        self.ids_text = [[0 for col in range(self.grid_width)] for row in range(self.grid_height)]
        self.ids_rect = [[0 for col in range(self.grid_width)] for row in range(self.grid_height)]
        self.ids_arrow = [[0 for col in range(self.grid_width)] for row in range(self.grid_height)]

        self._create_buttons()

        self.canvas = Canvas(self.window, width=self.canvas_width, height=self.canvas_height, bg='black')
        self.canvas.pack(padx=10, pady=10)

        self._create_grid()

    def _create_buttons(self):
        self.frame_value_buttons = Frame(self.window)
        self.frame_value_buttons.pack(padx=5, pady=5)

        self.frame_policy_buttons = Frame(self.window)
        self.frame_policy_buttons.pack(padx=5, pady=5)

        self.frame_reset_buttons = Frame(self.window)
        self.frame_reset_buttons.pack(padx=5, pady=5)
        
        self.btn_value_iteration_1_step = Button(self.frame_value_buttons, text='1-Step Value Iteration', anchor=W)
        self.btn_value_iteration_1_step.pack(side=LEFT)

        self.btn_value_iteration_100_steps = Button(self.frame_value_buttons, text='100-Step Value Iteration', anchor=E)
        self.btn_value_iteration_100_steps.pack(side=LEFT)

        self.btn_value_iteration_slow = Button(self.frame_value_buttons, text='Slow Value Iteration', anchor=E)
        self.btn_value_iteration_slow.pack(side=LEFT)

        self.btn_policy_iteration_1_step = Button(self.frame_policy_buttons, text='1-Step Policy Iteration', anchor=E)
        self.btn_policy_iteration_1_step.pack(side=LEFT)

        self.btn_policy_iteration_100_steps = Button(self.frame_policy_buttons, text='100-Step Policy Iteration', anchor=E)
        self.btn_policy_iteration_100_steps.pack(side=LEFT)

        self.btn_policy_iteration_slow = Button(self.frame_policy_buttons, text='Slow Policy Iteration', anchor=E)
        self.btn_policy_iteration_slow.pack(side=LEFT)

        self.btn_reset = Button(self.frame_reset_buttons, text='Reset', anchor=E)
        self.btn_reset.pack(side=LEFT)

    def _create_grid(self):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if (row, col) in self.obstacles:
                    fill = 'grey'
                    text = None
                else:
                    fill = None
                    text = '0.00'

                self.ids_rect[row][col] = self.canvas.create_rectangle(col * CELL_SIZE, row * CELL_SIZE, (col+1) * CELL_SIZE, (row+1) * CELL_SIZE, fill=fill, outline='white')
                if (row, col) in self.terminals:
                    self.canvas.create_rectangle(col * CELL_SIZE + CELL_PADDING, row * CELL_SIZE + CELL_PADDING, (col+1) * CELL_SIZE - CELL_PADDING, (row+1) * CELL_SIZE - CELL_PADDING, fill=fill, outline='white')

                self.ids_text[row][col] = self.canvas.create_text(col * CELL_SIZE + CELL_SIZE/2, row * CELL_SIZE + CELL_SIZE/2,  text=text, fill='white')
                self.ids_arrow[row][col] = self.canvas.create_line(0, 0, 0, 0, width=2, arrow=LAST, fill='white')

    def _compute_color(self, value):
        # negative values are redder while positive values are greener
        if value == 0:
            return '#000000'
        elif value > 0:
            g = math.floor(255 if value >= 1.0 else value * 256)
            return '#{:02x}{:02x}{:02x}'.format(0, g, 0)
        elif value < 0:
            r = math.floor(255 if -value >= 1.0 else -value * 256)
            return '#{:02x}{:02x}{:02x}'.format(r, 0, 0)
    
    def show_dialog(self, text):
        messagebox.showinfo('Info', text)

    def update_grid(self, values, policy):
        for state, value in values.items():
            rect_id = self.ids_rect[state[0]][state[1]]
            text_id = self.ids_text[state[0]][state[1]]
            arrow_id = self.ids_arrow[state[0]][state[1]]

            self.canvas.itemconfig(rect_id, fill=self._compute_color(value))
            self.canvas.itemconfig(text_id, text='{:.2f}'.format(value))

            if state not in self.terminals:
                self.canvas.coords(arrow_id,
                    state[1] * CELL_SIZE +  CELL_SIZE/2 + policy[state][1] * ARROW_LENGTH - policy[state][1],
                    state[0] * CELL_SIZE +  CELL_SIZE/2 + policy[state][0] * ARROW_LENGTH - policy[state][0],
                    state[1] * CELL_SIZE +  CELL_SIZE/2 + policy[state][1] * ARROW_LENGTH,
                    state[0] * CELL_SIZE +  CELL_SIZE/2 + policy[state][0] * ARROW_LENGTH)
    
    def clear(self):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                rect_id = self.ids_rect[row][col]
                text_id = self.ids_text[row][col]
                arrow_id = self.ids_arrow[row][col]

                if (row, col) in self.obstacles:
                    fill = 'grey'
                    text = None
                else:
                    fill = self._compute_color(0)
                    text = '0.00'
                self.canvas.itemconfig(rect_id, fill=fill)
                self.canvas.itemconfig(text_id, text=text)
                self.canvas.coords(arrow_id, 0, 0, 0, 0)

    def run(self):
        # run the UI loop
        mainloop()

