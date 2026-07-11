import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox, simpledialog
import os
import json

APP_SETTINGS = {
    "font_family": "Fixedsys",
    "font_size": 12,
    "bg_color": "#000000", # Black
    "font_color": "#FFFFFF" # White
}

class NotePad:
    """Class for a minimalist terminal-style text editor."""
    def __init__(self):
        
        # --- Creating window for program
        self.window = tk.Tk()
        self.window.title('Text Editor')
        
        # Grid weight set to 0 now that the top button frame is gone
        self.window.rowconfigure(0, weight=1) 
        self.window.columnconfigure(0, weight=1)
        self.window.configure(bg=APP_SETTINGS['bg_color'])

        # --- Loads recent files
        self.recent_files = []
        try:
            if os.path.exists('recent_files.json'):
                with open('recent_files.json', 'r') as f:
                    self.recent_files = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        # --- Initialize UI Menus
        self.menu_bar()

        # --- Text edit parameters (Scrollbar completely removed)
        self.text_edit = tk.Text(
            self.window, 
            undo=True, 
            font=(APP_SETTINGS['font_family'], APP_SETTINGS['font_size']),
            bg=APP_SETTINGS['bg_color'], 
            fg=APP_SETTINGS['font_color'],
            insertbackground=APP_SETTINGS['font_color'],
            blockcursor=True,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            borderwidth=0,         # Removes lingering default Tkinter borders
            highlightthickness=0   # Removes focus borders
        )

        # Shifted to row 0 so it fills the whole window
        self.text_edit.grid(row=0, column=0, sticky='nsew')
        self.filepath = None

        # --- Bindings
        self.window.bind('<Control-s>', lambda x: self.save_file())
        self.window.bind('<Control-o>', lambda x: self.open_file())
            
        self.window.mainloop()

    def menu_bar(self):
        self.menubar = tk.Menu(self.window)

        # --- File Menu
        self.menu_file = tk.Menu(self.menubar, tearoff=0)
        self.menu_recent = tk.Menu(self.menu_file, tearoff=0)
        
        self.menu_file.add_command(label='New', command=self.new_file)
        self.menu_file.add_command(label='Open...', command=self.open_file)
        self.menu_file.add_cascade(menu=self.menu_recent, label='Open Recent')
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Save', command=self.save_file)
        self.menu_file.add_command(label='Save As...', command=self.save_as)
        self.menu_file.add_command(label='Rename File', command=self.rename)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Close', command=self.close_file)
        
        self.menubar.add_cascade(menu=self.menu_file, label='File')

        # --- Edit Menu (Fully populated)
        self.menu_edit = tk.Menu(self.menubar, tearoff=0)
        self.menu_edit.add_command(label="Undo", command=self.undo)
        self.menu_edit.add_command(label="Redo", command=self.redo)
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Cut", command=self.cut)
        self.menu_edit.add_command(label="Copy", command=self.copy)
        self.menu_edit.add_command(label="Paste", command=self.paste)
        self.menu_edit.add_separator()
        self.menu_edit.add_command(label="Select All", command=self.select_all)
        self.menu_edit.add_command(label="Delete All", command=self.delete_all)
        
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')

        self._refresh_recent_menu()
        self.window['menu'] = self.menubar

    def _refresh_recent_menu(self):
        """Helper to clear and rebuild the recent files menu."""
        self.menu_recent.delete(0, tk.END)
        for f in self.recent_files:
            self.menu_recent.add_command(label=os.path.basename(f), command=lambda path=f: self.open_file(filepath=path))

    def update_recent_files(self, filepath):
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
            
        self.recent_files.insert(0, filepath)
        if len(self.recent_files) > 5:
            self.recent_files.pop() 
    
        with open('recent_files.json', 'w') as f:
            json.dump(self.recent_files, f)
            
        self._refresh_recent_menu()

    def new_file(self):
        self.text_edit.delete('1.0', tk.END)
        self.filepath = None
        self.window.title('New File - Text Editor')

    def close_file(self):
        self.window.destroy()

    def open_file(self, filepath=None):
        if filepath is None:
            filepath = askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if not filepath:
            return
            
        self.filepath = filepath
        self.text_edit.delete(1.0, tk.END)
        
        try:
            with open(self.filepath, 'r') as f:
                content = f.read()
                self.text_edit.insert(tk.END, content)
            self.window.title(f'{os.path.basename(self.filepath)} - Text Editor')
            self.update_recent_files(self.filepath)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not open file: {e}")

    def save_as(self):
        filepath = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
        )

        if not filepath:
            return
            
        self.filepath = filepath
        with open(self.filepath, 'w') as f:
            content = self.text_edit.get(1.0, tk.END)
            f.write(content)
            
        self.window.title(f'{os.path.basename(self.filepath)} - Text Editor')
        self.update_recent_files(self.filepath)

    def save_file(self):
        if not self.filepath:
            self.save_as()
            return

        content = self.text_edit.get(1.0, tk.END) 
        with open(self.filepath, 'w') as f:
            f.write(content) 

    def rename(self):
        if not self.filepath:
            tk.messagebox.showwarning("Warning", "No file is currently open to rename.")
            return

        directory = os.path.dirname(self.filepath)
        old_name = os.path.basename(self.filepath)
        
        new_name = tk.simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        if new_name:
            new_filepath = os.path.join(directory, new_name)
            try:
                os.rename(self.filepath, new_filepath)
                
                if self.filepath in self.recent_files:
                    self.recent_files.remove(self.filepath)
                
                self.filepath = new_filepath
                self.window.title(f'{new_name} - Text Editor')
                self.update_recent_files(self.filepath)
            except Exception as e:
                tk.messagebox.showerror("Error", f"Could not rename file: {e}")

    # --- EDIT MENU METHODS ---

    def cut(self, event=None):
        try:
            self.copy()
            self.delete()
        except tk.TclError:
            pass

    def copy(self, event=None):
        try:
            self.window.clipboard_clear()
            self.window.clipboard_append(self.text_edit.selection_get())
        except tk.TclError:
            pass 

    def paste(self, event=None):
        try:
            self.text_edit.insert(tk.INSERT, self.window.clipboard_get())
        except tk.TclError:
            pass 

    def delete(self):
        try:
            self.text_edit.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def undo(self, event=None):
        try:
            self.text_edit.edit_undo()
        except tk.TclError:
            pass 

    def redo(self, event=None):
        try:
            self.text_edit.edit_redo()
        except tk.TclError:
            pass 

    def select_all(self, event=None):
        self.text_edit.tag_add(tk.SEL, "1.0", tk.END)
        self.text_edit.mark_set(tk.INSERT, "1.0")
        self.text_edit.see(tk.INSERT)
        return 'break' 

    def delete_all(self):
        self.text_edit.delete(1.0, tk.END)

if __name__ == "__main__":
    app = NotePad()