import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import font
from tkinter import simpledialog
import os
import json

APP_SETTINGS = {
    "font_family": "Liberation Mono",
    "font_size": 12,
    "bg_color": "#000000", # Black
    "font_color": "#FFFFFF" # White
}

class NotePad():
    """class for notepad"""
    def __init__(self):
        
        #--- Creating window for program
        self.window = tk.Tk()
        self.window.title('Text editor')
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.configure(bg=APP_SETTINGS['bg_color'])

        #--- Loads recent files
        try:
            with open('recent_files.json', 'r') as f:
                    self.recent_files = json.load(f)
        except FileNotFoundError:
            self.recent_files = []

        #--- Text edit parameters 
        self.scrollbar = tk.Scrollbar(self.window)
        self.text_edit = tk.Text(self.window,
        font=(APP_SETTINGS['font_family'], APP_SETTINGS['font_size']),
        bg=APP_SETTINGS['bg_color'], 
        fg=APP_SETTINGS['font_color'],
        insertbackground = APP_SETTINGS['font_color'],

                    # --- Terminal specific additions ---
        blockcursor=True,  # Changes the thin cursor line to a solid block
        relief=tk.FLAT,    # Removes the default 3D sunken border around the text box
        padx=10,           # Adds internal padding so text doesn't touch the window edge
        pady=10,
    
        yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.config(command=self.text_edit.yview)
        self.text_edit.grid(row=1, column=0, sticky='nsew')
        self.scrollbar.grid(row=1, column=1, sticky='ns')
        self.filepath = None
        self.menu_bar()

        self.window.bind('<Control-s>', lambda x: self.save_file())
        self.window.bind('<Control-o>', lambda x: self.open_file())
            
        self.window.mainloop()

    def menu_buttons(self):
        frame = tk.Frame(self.window, relief=tk.FLAT, bd=2)
        save_button = tk.Button(frame, text='Save', command= self.save_file)
        open_button = tk.Button(frame, text='Open', command= self.open_file)
        new_button = tk.Button(frame, text='New', command= self.new_file)
        close_button = tk.Button(frame, text='Close', command= self.close_file)

    #--- Layout for buttons
        save_button.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        open_button.grid(row=0, column=1, padx=5, sticky='ew')
        new_button.grid(row=0, column=2, padx=5, sticky='ew')
        close_button.grid(row=0, column=3, padx=5, sticky='ew')
            
        frame.grid(row=0, column=0, sticky='ew')

        self.scrollbar.config(command=self.text_edit.yview)
        self.text_edit.grid(row=1, column=0, sticky='nsew')
        self.scrollbar.grid(row=1, column=1, sticky='ns')
        self.filepath = None
        self.menu_bar()

        self.window.bind('<Control-s>', lambda x: self.save_file())
        self.window.bind('<Control-o>', lambda x: self.open_file())
            
        
        self.window.mainloop()

    def menu_bar(self):
        self.menubar = tk.Menu(self.window)

        self.menu_file = tk.Menu(self.menubar)
        self.menu_edit = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')
        self.menu_recent = tk.Menu(self.menu_file)
        self.menu_file.add_cascade(menu=self.menu_recent, label='Open Recent')

        self.menu_file.add_command(label='New', command= self.new_file)
        self.menu_file.add_command(label='Open', command= self.open_file)
        self.menu_file.add_command(label='Close', command= self.close_file)
        self.menu_file.add_command(label='Save', command= self.save_file)
        self.menu_file.add_command(label='Save As...', command= self.save_as)
        


        for f in self.recent_files:
            self.menu_recent.add_command(label=os.path.basename(f), command= lambda f=f: self.open_file(filepath=f))
                    

        self.menu_file.add_separator()
        self.window.option_add('*tearOff', tk.FALSE) 
        self.window['menu'] = self.menubar
        return self.menu_recent


    def make_tag(self):
        current_tags = self.text_edit.tag_names()
        if "bold" in current_tags:
            self.weight = "bold"
        else:
            self.weight = "normal"

        if "italic" in current_tags:
            self.slant = "italic"
        else:
            self.slant = "roman"

        if "underline" in current_tags:
            self.underline = 1
        else:
            self.underline = 0

        if "overstrike" in current_tags:
            self.overstrike = 1
        else:
            self.overstrike = 0

        self.big_font = tk.Font.Font(self.text_edit, self.text_edit.cget("font"))
        self.big_font.configure(slant=self.slant, weight=self.weight, underline=self.underline, overstrike=self.overstrike, family="Liberation Mono", size=12)
        self.text_edit.tag_config("BigTag", font=self.big_font, foreground="#000000", background="#FFFFFF")
        if "BigTag" in current_tags:
            self.text_edit.tag_remove("BigTag", 1.0, tk.END)
        self.text_edit.tag_add("BigTag", 1.0, tk.END)

    def new_file(self):

        self.text_edit.delete('1.0', tk.END)
        self.window.title('New File')
        

    def close_file(self):
        self.window.destroy()

        
    def update_recent_files(self, filepath):
        self.recent_files.append(filepath)
        if len(self.recent_files) > 5:
            self.recent_files.pop(0)
    
        with open('recent_files.json', 'w') as f:
            json.dump(self.recent_files, f)
        self.menu_recent.delete(0, tk.END)
        for f in self.recent_files:
            self.menu_recent.add_command(label=os.path.basename(f), command= lambda f=f: self.open_file(filepath=f))




    def open_file(self, filepath=None):

        if filepath is None:
            filepath = askopenfilename(filetypes=[('Text Files', '.txt')])
        if not filepath:
            return
        self.filepath = filepath
        self.text_edit.delete(1.0, tk.END)
        with open(self.filepath, 'r') as f:
            content = f.read()
            self.text_edit.insert(tk.END, content)
        self.window.title(f'Open File: {self.filepath}')
        self.update_recent_files(self.filepath)


    def save_as(self):
        self.filepath = asksaveasfilename(filetypes=[('Text Files', '.txt')])

        if not self.filepath:
            return
        
        with open(self.filepath, 'w') as f:
            self.content = self.text_edit.get(1.0, tk.END)
            f.write(self.content)
        self.window.title(f'Save File: {self.filepath}')
        self.update_recent_files(self.filepath)


    def save_file(self):
        if not self.filepath:
            self.save_as()
            return

        if self.filepath is None: 
                return
        self.text2save = str(self.text_edit.get(1.0, tk.END)) 
        with open(self.filepath, 'w') as f:
            f.write(self.text2save) 
        self.new_name = ""



    def rename(self, filepath=None):
        if self.filepath == "":
            self.open_file()

        arr = self.filepath.split('/')
        self.path = ""
        for i in range(0 , len(arr) -1):
            self.path = self.path + arr[i] + '/'
        
        self.new_name = tk.simpledialog.askstring("Rename", "Enter new name")
        os.rename(self.filepath , str(self.path) + str(self.new_name))
        self.filepath = str(self.path) + str(self.new_name)
        self.window.title(self.filepath + " - Script Editor")

    # EDIT MENU METHODS

    def cut(self, event=None):
        self.window.clipboard_clear()
        self.text_edit.clipboard_append(string=self.text_edit.selection_get())
        #index of the first and yhe last letter of our selection.
        self.text_edit.delete(index1=tk.SEL_FIRST, index2=tk.SEL_LAST)


    def copy(self, event=None):
        # first clear the previous text on the clipboard.
        print (self.text_edit.index(tk.SEL_FIRST))
        print (self.text_edit.index(tk.SEL_LAST))
        self.window.clipboard_clear()
        self.text_edit.clipboard_append(string=self.text_edit.selection_get())

    def paste(self, event=None):
        # get gives everyting from the clipboard and paste it on the current cursor position
        # it does'nt removes it from the clipboard.
        self.text_edit.insert(tk.INSERT, self.window.clipboard_get())

    def delete(self):
        self.text_edit.delete(index1=tk.SEL_FIRST, index2=tk.SEL_LAST)

    def undo(self):
        self.window.edit_undo()

    def redo(self):
        self.window.edit_redo()

    def select_all(self, event=None):
        self.text_edit.tag_add(tk.SEL, "1.0", tk.END)

    def delete_all(self):
        self.text_edit.delete(1.0, tk.END)


app = NotePad()
