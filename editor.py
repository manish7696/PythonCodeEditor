import tkinter as tk
from tkinter import Menu, filedialog, messagebox
import re
import subprocess

class Editor:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1366x768")

        self.text_widget = tk.Text(root, background="#1F1F1F", spacing1=2, spacing2=2, foreground="#CCCCCC", insertbackground="#CCCCCC", borderwidth=2, font=('Helvetica', 12, 'normal'))
        self.text_widget.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.6)
        self.text_widget.bind("<KeyRelease>", self.colorize_code)

        self.text_widget.focus_set()

        self.text_widget.tag_configure('keyword', foreground='#3B8EE9')
        self.text_widget.tag_configure('comment', foreground='#265347')
        self.text_widget.tag_configure('string', foreground='#FF632D')
        self.text_widget.tag_configure('parentheses', foreground='yellow')

        self.keyword_pattern = r'\b(and|as|assert|break|class|continue|def|del|elif|else|except|False|finally|for|from|global|if|import|in|is|lambda|None|nonlocal|not|or|pass|raise|return|True|try|while|with|yield)\b'
        self.comment_pattern = r'#.*'
        self.string_pattern = r'(\'\'\'(.*?)\'\'\'|\"(.*?)\"|\'(.*?)\')'
        self.parentheses_pattern = r'(\(|\))'

        self.root.bind('<Control-s>', self.save_file)

        # menu
        menubar = Menu(root)
        root.config(menu=menubar)

        file_menu = Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        self.run_command_button = tk.Button(root, text="Run Command", command=self.run_command)
        self.run_command_button.place(relx=0.3, rely=0.68, relwidth=0.25)

        self.command_entry = tk.Entry(root, width=50)
        self.command_entry.place(relx=0.02, rely=0.69)

        self.command_entry.bind('<Return>', self.run_command_on_enter)
        self.root.bind('<F5>', self.run_current_file)

        self.output_text = tk.Text(root, background="#1F1F1F", foreground="#CCCCCC", insertbackground="#CCCCCC", borderwidth=2, font=('Helvetica', 12, 'normal'))
        self.output_text.place(relx=0.02, rely=0.75, relwidth=0.96, relheight=0.3)

        self.current_file = None

    def colorize_code(self, event):
        code = self.text_widget.get("1.0", "end")

        for tag, pattern in [('keyword', self.keyword_pattern), ('comment', self.comment_pattern), ('string', self.string_pattern)]:
            for match in re.finditer(pattern, code):
                start, end = match.start(), match.end()
                self.text_widget.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")

        for match in re.finditer(self.parentheses_pattern, code):
            start, end = match.start(), match.end()
            self.text_widget.tag_add('parentheses', f"1.0+{start}c", f"1.0+{end}c")

    def new_file(self):
        self.text_widget.delete("1.0", tk.END)
        self.current_file = None

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert("1.0", content)
            self.current_file = file_path

    def save_file(self, event=None):
        if self.current_file:
            content = self.text_widget.get("1.0", tk.END)
            with open(self.current_file, 'w') as file:
                file.write(content)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as file:
                content = self.text_widget.get("1.0", tk.END)
                file.write(content)
            self.current_file = file_path

    def run_command(self):
        command = self.command_entry.get()
        if not command:
            messagebox.showerror("Error", "Please enter a command.")
            return

        try:
            result = subprocess.check_output(command, shell=True, text=True)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", result)
        except subprocess.CalledProcessError as e:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", f"Command failed with error:\n{e}")

    def run_command_on_enter(self, event):
        self.run_command()

    def run_current_file(self, event):
        if self.current_file:
            try:
                with open(self.current_file, 'r') as file:
                    code = file.read()
                result = subprocess.check_output(f'python "{self.current_file}"', shell=True, text=True)
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert("1.0", result)
            except subprocess.CalledProcessError as e:
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert("1.0", f"Command failed with error:\n{e}")
            except Exception as e:
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert("1.0", f"Error:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    editor = Editor(root)
    root.mainloop()
