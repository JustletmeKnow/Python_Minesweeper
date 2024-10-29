import tkinter as tk
from random import shuffle
from tkinter.messagebox import showinfo, showerror
from tkinter.tix import ROW


colors = {
    0: 'white',
    1: 'blue',
    2: 'green',
    3: '#b3a105',
    4: 'red',
    5: 'pink',
    6: 'purple',
    7: '#750535',
    8: '#064e7a',
}

class MyButton(tk.Button):

    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_bomb = 0
        self.is_open = False


    def __repr__(self):
        return f'MyButton{self.x} {self.y} {self.number} {self.is_mine}'


class Minesweeper:
    window = tk.Tk()
    COLUMNS = 10
    ROW = 10
    MINES = 5
    IS_GAME_OVER = False
    IS_FIRST_CLICK = True
    p1 = tk.PhotoImage(file = 'images.gif')
    window.iconphoto(False, p1)
    window.title('Minesweeper')

    def __init__(self):
        self.k = 0
        Minesweeper.game_over = False
        print('-' * Minesweeper.COLUMNS)
        self.buttons = []
        for i in range(Minesweeper.ROW+2):
            temp = []
            for j in range(Minesweeper.COLUMNS+2):
                btn = MyButton(Minesweeper.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind("<Button-3>", self.right_click)
                temp.append(btn)
            self.buttons.append(temp)
        
    def right_click(self, event):
        if Minesweeper.IS_GAME_OVER:
            return
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '🚩'
            cur_btn['disabledforeground'] = 'red'
        elif cur_btn['text'] == '🚩':
            cur_btn['text'] = ''
            cur_btn['state'] = 'normal'

    def click(self, clicked_button: MyButton):
        if Minesweeper.IS_GAME_OVER:
            return

        if Minesweeper.IS_FIRST_CLICK:
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            Minesweeper.IS_FIRST_CLICK = False

        if clicked_button.is_mine:
            clicked_button.config(text="*", background='red', disabledforeground='black')
            clicked_button.is_open = True
            Minesweeper.IS_GAME_OVER = True
            showinfo('Game over', 'You lose')
            for i in range(1, Minesweeper.ROW + 1):
                for j in range(1, Minesweeper.COLUMNS + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '*'
        else:
            color = colors.get(clicked_button.count_bomb, 'black')
            clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
            if clicked_button.count_bomb:
                self.k += 1
                clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
                clicked_button.is_open = True
            else:
                self.breadth_first_search(clicked_button)
        clicked_button.config(state='disabled')
        clicked_button.config(relief=tk.SUNKEN)
        if self.k == Minesweeper.ROW * Minesweeper.COLUMNS - Minesweeper.MINES:
            showinfo('Game end', 'You win!')
            Minesweeper.IS_GAME_OVER = True
            for i in range(1, Minesweeper.ROW + 1):
                for j in range(1, Minesweeper.COLUMNS + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine:
                        btn['text'] = '*'

    def breadth_first_search(self, btn: MyButton):
        queue = [btn]
        while queue:
            self.k += 1
            cur_btn = queue.pop()
            color = colors.get(cur_btn.count_bomb, 'black')
            if cur_btn.count_bomb:
                cur_btn.config(text=cur_btn.count_bomb, disabledforeground=color)
            else:
                cur_btn.config(text='', disabledforeground=color)
            cur_btn.is_open = True
            cur_btn.config(state=tk.DISABLED)
            cur_btn.config(relief=tk.SUNKEN)

            if cur_btn.count_bomb == 0:
                x, y = cur_btn.x, cur_btn.y
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        #if not (dx - dy) == 1:
                        #    continue

                        next_btn = self.buttons[x + dx][y + dy]
                        if not next_btn.is_open and 1 <= next_btn.x <= Minesweeper.ROW \
                                and 1 <= next_btn.y <= Minesweeper.COLUMNS and next_btn not in queue:
                            queue.append(next_btn)

    def reload(self):
        [child.destroy() for child in self.window.winfo_children()]
        self.__init__()
        self.create_widgets()
        Minesweeper.IS_FIRST_CLICK = True
        Minesweeper.IS_GAME_OVER = False

    def create_settings_win(self):
        win_settings = tk.Toplevel(self.window)
        win_settings.wm_title('Settings')
        tk.Label(win_settings, text='Lines amount').grid(row=0, column=0)
        row_entry = tk.Entry(win_settings)
        row_entry.insert(0, Minesweeper.ROW)
        row_entry.grid(row=0, column=1, padx=20, pady=20)
        tk.Label(win_settings, text='Columns amount').grid(row=1, column=0)
        column_entry = tk.Entry(win_settings)
        column_entry.insert(0, Minesweeper.COLUMNS)
        column_entry.grid(row=1, column=1, padx=20, pady=20)
        tk.Label(win_settings, text='Mine amount').grid(row=2, column=0)
        mines_entry = tk.Entry(win_settings)
        mines_entry.insert(0, Minesweeper.MINES)
        mines_entry.grid(row=2, column=1, padx=20, pady=20)
        save_btn = tk.Button(win_settings, text='Submit',
                  command=lambda: self.change_settings(row_entry, column_entry, mines_entry))
        save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def change_settings(self, row: tk.Entry, column: tk.Entry, mines: tk.Entry):
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Error', 'You have entered an incorrect value')
            return
        if int(row.get()) > 50:
            showerror('Error', 'The maximum value is 50')
            return
        if int(column.get()) > 50:
            showerror('Error', 'The maximum value is 50')
            return
        if int(mines.get()) >= int(row.get()) * int(column.get()) - 2:
            showerror('Error', "There can't be more min than cells")
            return

        Minesweeper.ROW = int(row.get())
        Minesweeper.COLUMNS = int(column.get())
        Minesweeper.MINES = int(mines.get())
        self.reload()

    def create_widgets(self):
        A =  f"Mines: {Minesweeper.MINES}"
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Play', command=self.reload)
        settings_menu.add_command(label='Save', command=self.save)
        settings_menu.add_command(label='Settings', command=self.create_settings_win)
        settings_menu.add_command(label='Exit', command=self.window.destroy)
        menubar.add_cascade(label='File', menu=settings_menu)
        menubar.add_cascade(label=A)

        count = 1
        for i in range(1, Minesweeper.ROW + 1):
            for j in range(1, Minesweeper.COLUMNS + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, stick='NWES')
                count += 1

        #for i in range(1, Minesweeper.ROW + 1):
        #    Minesweeper.window.rowconfigure(i, weight=1) 

        #for j in range(1, Minesweeper.COLUMNS + 1):
        #    Minesweeper.window.columnconfigure(j, weight=1)       
        for i in range(1, Minesweeper.ROW + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)
        
        for i in range(1, Minesweeper.COLUMNS + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)

    def open_all_buttons(self):
        for i in range(Minesweeper.ROW+2):
            for j in range(Minesweeper.COLUMNS+2):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    btn.config(text="*", background='red')
                elif btn.count_bomb in colors:
                    color = colors.get(btn.count_bomb, 'black')
                    btn.config(text=btn.count_bomb, fg=color)
                    self.reload()
                    self.k = 0

    def start(self):
        self.create_widgets()
        #self.open_all_buttons()
        Minesweeper.window.mainloop()

    def save(self):
        f = open('save.txt', 'w+')
        for i in range(1, Minesweeper.ROW+1):
            for j in range(1, Minesweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    f.write('B')
                else:
                    f.write(str(btn.count_bomb))
            f.write('\n')
            print('B')
        f.close()

    def insert_mines(self, number: int):
        index_mines = self.get_mines_places(number)
        print(index_mines)
        for i in range(1, Minesweeper.ROW+1):
            for j in range(1, Minesweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_in_buttons(self):
        for i in range(1, Minesweeper.ROW+1):
            for j in range(1, Minesweeper.COLUMNS+1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i+row_dx][j+col_dx]
                            if neighbour.is_mine:
                                count_bomb+=1
                btn.count_bomb = count_bomb


    @staticmethod
    def get_mines_places(exclude_number: int):
        indexes = list(range(1, Minesweeper.COLUMNS * Minesweeper.ROW + 1))
        print(f'Exclude button number {exclude_number}')
        indexes.remove(exclude_number)
        shuffle(indexes)
        return indexes[:Minesweeper.MINES]


game = Minesweeper()
game.start()
