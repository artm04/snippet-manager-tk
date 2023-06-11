from database import SnippetsDatabase
from judge0ce import Judge0CEClient
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import Menu
import logging, os
import webbrowser

logger = logging.getLogger("snippets_app")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("snippets_app.log")
file_handler.setLevel(logging.DEBUG)


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def log(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class SnippetsApp:
    def __init__(self, db):
        self.db = db
        self.root = tk.Tk()
        self.root.title("Snippets App")
        self.root.geometry("900x600")



        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), background="#E1E1E1")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])  # Remove borders

        style.configure("TButton", font=("Arial", 14), background="#E1E1E1", borderwidth=0, focusthickness=0,
                        focuscolor="#E1E1E1", highlightthickness=0, relief=tk.GROOVE)
        style.layout("TButton", [('Button.button', {'children': [('Button.focus', {'children': [('Button.padding', {'children': [('Button.label', {'side': 'left', 'expand': 1})]})]})], 'sticky': 'nswe'})])
        
        # https://www.iconsdb.com/black-icons/code-icon.html  
        self.root.iconbitmap("favicon.ico")

        self.create_widgets()
    

    

    @log
    def create_widgets(self):
        self.login_frame = tk.Frame(self.root, bg="#f2f2f2", bd=2, relief=tk.GROOVE)
        self.login_frame.pack(pady=20)

        self.username_label = tk.Label(self.login_frame, text="Username:", font=("Arial", 12), bg="#f2f2f2")
        self.username_label.grid(row=0, column=0, padx=10, pady=5)

        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 12), bd=2, relief=tk.SOLID)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        self.password_label = tk.Label(self.login_frame, text="Password:", font=("Arial", 12), bg="#f2f2f2")
        self.password_label.grid(row=1, column=0, padx=10, pady=5)

        self.password_entry = tk.Entry(self.login_frame, show="*", font=("Arial", 12), bd=2, relief=tk.SOLID)
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", font=("Arial", 12), bg="#4CAF50", fg="white", bd=2, relief=tk.GROOVE, command=self.login)
        self.login_button.grid(row=2, column=0, padx=10, pady=5)
        self.login_button.config(width=20, height=2, bg='#4CAF50', fg='white', font=('Arial', 12), bd=0, highlightthickness=0, activebackground='#4CAF50', activeforeground='white')
        self.login_button.config(highlightbackground='#4CAF50', highlightcolor='#4CAF50')
        self.login_button.config(cursor='hand2')
        self.login_button.config(borderwidth=0, relief=tk.RIDGE)
        self.login_button.bind("<Enter>", lambda event, h=self.login_button: h.config(borderwidth=2))
        self.login_button.bind("<Leave>", lambda event, h=self.login_button: h.config(borderwidth=0))

        self.logout_button = ttk.Button(self.root, text="Logout", command=self.logout)
    
 
        self.register_button = tk.Button(self.login_frame, text="Register", font=("Arial", 12), bg="#2196F3", fg="white", bd=2, relief=tk.GROOVE, command=self.register)
        self.register_button.grid(row=2, column=1, padx=10, pady=5)
        self.register_button.config(width=20, height=2, bg='#2196F3', fg='white', font=('Arial', 12), bd=0, highlightthickness=0, activebackground='#2196F3', activeforeground='white')
        self.register_button.config(highlightbackground='#2196F3', highlightcolor='#2196F3')
        self.register_button.config(cursor='hand2')
        self.register_button.config(borderwidth=0, relief=tk.RIDGE)
        self.register_button.bind("<Enter>", lambda event, h=self.register_button: h.config(borderwidth=2))
        self.register_button.bind("<Leave>", lambda event, h=self.register_button: h.config(borderwidth=0))

        self.snippet_frame = tk.Frame(self.root)
        self.snippet_frame.pack(pady=20)

        self.new_snippet_button = ttk.Button(self.snippet_frame, text="New Snippet", command=self.open_new_snippet_window)
        self.new_snippet_button.pack(padx=10, pady=5)
        self.new_snippet_button.state(["disabled"])


        self.snippet_treeview = ttk.Treeview(self.snippet_frame, columns=("id", "name", "language", "code"), show="headings", height=15)
        self.snippet_treeview.heading("id", text="ID")
        self.snippet_treeview.heading("name", text="Name")
        self.snippet_treeview.heading("language", text="Language")
        self.snippet_treeview.heading("code", text="Code")
        self.snippet_treeview.pack(padx=10, pady=5)
        self.snippet_treeview.bind("<Button-3>", self.show_context_menu)
        self.update_snippet_treeview()


    @log
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Login Failed", "Username or password cannot be empty")
            return

        if self.db.login(username, password):
            self.show_snippets()
            self.new_snippet_button.state(["!disabled"])
            self.welcome_label = tk.Label(self.snippet_frame, text="Welcome, " + username + "!", font=("Arial", 12))
            self.welcome_label.pack(padx=10, pady=5)


            self.root.title("Snippets App - Welcome, " + username)

            self.root.geometry("700x600")
        
            id = self.db.get_user_by_username(username)[0]

            self.login_frame.pack_forget()
            self.snippet_frame.pack(pady=20)
            self.logout_button.pack(padx=10, pady=5)
            self.admin_button = ttk.Button(self.snippet_frame, text="Admin", command=self.open_admin_window)
            if db.is_admin(id):
                self.admin_button.pack(padx=15, pady=6)
            

        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    @log
    def open_admin_window(self):
        self.admin_window = tk.Toplevel(self.root)
        self.admin_window.title("Admin")
        self.admin_window.geometry("800x600")

        self.admin_frame = tk.Frame(self.admin_window)
        self.admin_frame.pack(pady=20)

        self.users_list = ttk.Treeview(self.admin_frame, columns=("id", "username", "password", "access_code"), show="headings", height=15)
        self.users_list.heading("id", text="ID")
        self.users_list.heading("username", text="Username")
        self.users_list.heading("password", text="Password")
        self.users_list.heading("access_code", text="Access code")
        self.users_list.pack(padx=10, pady=5)
        self.users_list.bind("<Button-3>", self.show_context_menu)
        self.update_users_list()

        self.add_user_button = ttk.Button(self.admin_frame, text="Add User", command=self.open_add_user_window)
        self.add_user_button.pack(padx=10, pady=5)

        self.execute_sql_query_button = ttk.Button(self.admin_frame, text="Execute SQL Query", command=self.open_execute_sql_query_window)
        self.execute_sql_query_button.pack(padx=10, pady=5)

        self.generate_random_users_button = ttk.Button(self.admin_frame, text="Generate Random Users", command=self.generate_random_users)
        self.generate_random_users_button.pack(padx=10, pady=5)

        self.analytics_button = ttk.Button(self.admin_frame, text="Analytics", command=self.open_analytics_window)
        self.analytics_button.pack(padx=10, pady=5)


    @log
    def open_analytics_window(self):
        total_users = self.db.get_total_users()
        total_snippets = self.db.get_total_snippets()
        total_supported_languages = self.db.get_total_supported_languages()
        total_snippets_count_by_language = self.db.get_snippets_count_by_language()
        total_snippets_count_by_user = self.db.get_snippets_count_by_user()

        self.analytics_window = tk.Toplevel(self.admin_window)
        self.analytics_window.title("Analytics")
        self.analytics_window.geometry("800x600")

        self.analytics_frame = tk.Frame(self.analytics_window)
        self.analytics_frame.pack(pady=20)

        self.total_users_label = tk.Label(self.analytics_frame, text="Total users: " + str(total_users))
        self.total_users_label.pack(padx=10, pady=5)

        self.total_snippets_label = tk.Label(self.analytics_frame, text="Total snippets: " + str(total_snippets))
        self.total_snippets_label.pack(padx=10, pady=5)

        self.total_supported_languages_label = tk.Label(self.analytics_frame, text="Total supported languages: " + str(total_supported_languages))
        self.total_supported_languages_label.pack(padx=10, pady=5)

        self.total_snippets_count_by_language_label = tk.Label(self.analytics_frame, text="Total snippets count by language: ")
        self.total_snippets_count_by_language_label.pack(padx=10, pady=5)

        self.total_snippets_count_by_language_treeview = ttk.Treeview(self.analytics_frame, columns=("language", "count"), show="headings", height=10)
        self.total_snippets_count_by_language_treeview.heading("language", text="Language")

        self.total_snippets_count_by_language_treeview.heading("count", text="Count")
        self.total_snippets_count_by_language_treeview.pack(padx=10, pady=5)
        for language, count in total_snippets_count_by_language:
            self.total_snippets_count_by_language_treeview.insert("", "end", values=(language, count))

        self.total_snippets_count_by_user_label = tk.Label(self.analytics_frame, text="Total snippets count by user: ")
        self.total_snippets_count_by_user_label.pack(padx=10, pady=5)

        self.total_snippets_count_by_user_treeview = ttk.Treeview(self.analytics_frame, columns=("username", "count"), show="headings", height=10)
        self.total_snippets_count_by_user_treeview.heading("username", text="Username")
        self.total_snippets_count_by_user_treeview.heading("count", text="Count")
        self.total_snippets_count_by_user_treeview.pack(padx=10, pady=5)
        for username, count in total_snippets_count_by_user:
            self.total_snippets_count_by_user_treeview.insert("", "end", values=(username, count))


    @log
    def open_add_user_window(self):
        self.add_user_window = tk.Toplevel(self.admin_window)
        self.add_user_window.title("Add User")
        self.add_user_window.geometry("300x400")

        self.add_user_frame = tk.Frame(self.add_user_window)
        self.add_user_frame.pack(pady=20)

        self.username_label = tk.Label(self.add_user_frame, text="Username")
        self.username_label.pack(padx=10, pady=5)

        self.username_entry = tk.Entry(self.add_user_frame)
        self.username_entry.pack(padx=10, pady=5)

        self.password_label = tk.Label(self.add_user_frame, text="Password")
        self.password_label.pack(padx=10, pady=5)

        self.password_entry = tk.Entry(self.add_user_frame)
        self.password_entry.pack(padx=10, pady=5)

        # popup choice
        self.access_code_label = tk.Label(self.add_user_frame, text="Access code")
        self.access_code_label.pack(padx=10, pady=5)

        self.access_code = tk.StringVar()
        self.access_code.set("1")
        self.access_code_entry = ttk.Combobox(self.add_user_frame, textvariable=self.access_code, state="readonly")
        self.access_code_entry["values"] = ("0", "1", "2")
        self.access_code_entry.pack(padx=10, pady=5)

        self.add_user_button = ttk.Button(self.add_user_frame, text="Add User", command=self.add_user)
        self.add_user_button.pack(padx=10, pady=5)

    @log
    def add_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        access_code = self.access_code.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill in all fields")
            return

        if self.db.get_user_by_username(username):
            messagebox.showerror("Error", "Username already exists")
            return

        self.db.add_user(username, password, access_code)
        self.update_users_list()
        self.add_user_window.destroy()

    @log
    def open_execute_sql_query_window(self):
        self.execute_sql_query_window = tk.Toplevel(self.admin_window)
        self.execute_sql_query_window.title("Execute SQL Query")
        self.execute_sql_query_window.geometry("700x600")
        self.execute_sql_query_window.resizable(False, False)

        self.execute_sql_query_frame = tk.Frame(self.execute_sql_query_window)
        self.execute_sql_query_frame.pack(pady=20)

        self.sql_query_label = tk.Label(self.execute_sql_query_frame, text="SQL Query")
        self.sql_query_label.pack(padx=10, pady=5)

        self.sql_query_text = tk.Text(self.execute_sql_query_frame, height=5)
        self.sql_query_text.pack(padx=10, pady=5)

        self.execute_button = ttk.Button(self.execute_sql_query_frame, text="Execute", command=self.execute_sql_query)
        self.execute_button.pack(padx=10, pady=5)

        self.result_label = tk.Label(self.execute_sql_query_frame, text="Result")
        self.result_label.pack(padx=10, pady=5)

        self.result_text = tk.Text(self.execute_sql_query_frame, height=20)
        self.result_text.pack(padx=10, pady=5)

    
    @log
    def execute_sql_query(self):
        sql_query = self.sql_query_text.get("1.0", tk.END)
        result = self.db.run_and_get_output(sql_query)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, result)

    @log
    def generate_random_users(self):
        self.db.generate_random_users()
        self.update_users_list()
        messagebox.showinfo("Generate Random Users", "Users generated successfully")

    @log
    def update_users_list(self):
        self.users_list.delete(*self.users_list.get_children())
        users = self.db.get_all_users()
        for user in users:
            self.users_list.insert("", tk.END, values=user)

    @log
    def logout(self):
        self.db.logout()
        self.root.title("Snippets App")
        self.root.geometry("900x600")
        self.new_snippet_button.state(["disabled"])
        self.welcome_label.pack_forget()
        self.snippet_treeview.delete(*self.snippet_treeview.get_children())
        self.login_frame.pack_forget()
        self.snippet_frame.pack_forget()
        self.logout_button.pack_forget()
        self.admin_button.pack_forget()
        
        self.create_widgets()
        

    @log
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Login Failed", "Username or password cannot be empty")
            return

        if self.db.register(username, password):
            messagebox.showinfo("Registration Successful", "You have been registered successfully!\n Logging in...")
            self.login()
        else:
            messagebox.showerror("Registration Failed", "Username already exists")

    @log
    def show_snippets(self):
        self.login_frame.pack_forget()
        self.snippet_frame.pack(pady=20)

        self.update_snippet_treeview()

    @log
    def update_snippet_treeview(self):
        self.snippet_treeview.delete(*self.snippet_treeview.get_children())
        self.context_menu = Menu(self.snippet_treeview, tearoff=False)
        self.context_menu.add_command(label="Copy Snippet", command=self.copy_snippet)
        snippets = self.db.get_snippets()
        
        if self.db.current_user is not None:
            snippets = self.db.get_snippets(self.db.current_user)
            self.context_menu.add_command(label="Edit Snippet", command=self.edit_snippet)
            self.context_menu.add_command(label="Delete Snippet", command=self.delete_snippet)
            self.context_menu.add_command(label="Execute Snippet", command=self.copy_snippet)
        
        for snippet in snippets:
            self.snippet_treeview.insert("", tk.END, values=(snippet[0], snippet[1], snippet[2], snippet[3][:10] + "..."))

    @log
    def open_new_snippet_window(self):
        new_snippet_window = tk.Toplevel(self.root)
        new_snippet_window.title("New Snippet")

        name_label = tk.Label(new_snippet_window, text="Name:")
        name_label.grid(row=0, column=0, padx=10, pady=5)

        name_entry = tk.Entry(new_snippet_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        language_label = tk.Label(new_snippet_window, text="Language:")
        language_label.grid(row=1, column=0, padx=10, pady=5)

        language_combo = ttk.Combobox(new_snippet_window, values=self.db.get_supported_languages(), state="readonly")
        language_combo.grid(row=1, column=1, padx=10, pady=5)

        code_label = tk.Label(new_snippet_window, text="Code:")
        code_label.grid(row=2, column=0, padx=10, pady=5)

        code_text = ScrolledText(new_snippet_window, height=10)
        code_text.grid(row=2, column=1, padx=10, pady=5)
        code_text.configure(borderwidth=1, relief="solid")
        code_text.configure(insertbackground="white", insertwidth=1)

        example_code_label = tk.Label(new_snippet_window, text="Example Code:")
        example_code_label.grid(row=3, column=0, padx=10, pady=5)

        example_code_text = ScrolledText(new_snippet_window, height=10)
        example_code_text.grid(row=3, column=1, padx=10, pady=5)
        example_code_text.configure(borderwidth=1, relief="solid")
        example_code_text.configure(insertbackground="white", insertwidth=1)

        stdin_label = tk.Label(new_snippet_window, text="STDIN:")
        stdin_label.grid(row=4, column=0, padx=10, pady=5)

        stdin_text = ScrolledText(new_snippet_window, height=2)
        stdin_text.grid(row=4, column=1, padx=10, pady=5)

        expected_output_label = tk.Label(new_snippet_window, text="Expected Output:")
        expected_output_label.grid(row=5, column=0, padx=10, pady=5)

        expected_output_text = ScrolledText(new_snippet_window, height=2)
        expected_output_text.grid(row=5, column=1, padx=10, pady=5)

        is_private_label = tk.Label(new_snippet_window, text="Is Private:")
        is_private_label.grid(row=6, column=0, padx=10, pady=5)

        is_private_var = tk.BooleanVar()
        is_private_checkbox = tk.Checkbutton(new_snippet_window, variable=is_private_var)
        is_private_checkbox.grid(row=6, column=1, padx=10, pady=5)

    
        command=lambda: self.add_snippet(name=name_entry.get(), language=language_combo.get(), code=code_text.get("1.0", tk.END), example_code=example_code_text.get("1.0", tk.END), stdin=stdin_text.get("1.0", tk.END), expected_output=expected_output_text.get("1.0", tk.END), is_private=is_private_var.get())
        add_button = ttk.Button(new_snippet_window, text="Add", command=command)
        add_button.grid(row=7, column=0, padx=10, pady=5)

    @log
    def add_snippet(self, **kwargs):
        self.db.add_snippet(kwargs["name"], kwargs["language"], kwargs["code"], kwargs["example_code"], kwargs["stdin"], kwargs["expected_output"], kwargs["is_private"])
        messagebox.showinfo("Snippet Added", "Snippet has been added successfully!")
        self.update_snippet_treeview()

    @log
    def show_context_menu(self, event):
        item = self.snippet_treeview.identify_row(event.y)
        if item:
            menu = tk.Menu(self.snippet_frame, tearoff=0)
            menu.add_command(label="Edit Snippet", command=self.edit_snippet, state="disabled")
            menu.add_command(label="Delete Snippet", command=self.delete_snippet, state="disabled")
            self.selected_snippet = self.db.get_snippet(self.snippet_treeview.item(item)["values"][0])
            if self.db.current_user:
                if self.db.is_admin(self.db.get_user(self.db.current_user)[0]) or self.selected_snippet[8] == self.db.current_user:
                    menu.entryconfig("Edit Snippet", state="normal")
                    menu.entryconfig("Delete Snippet", state="normal")
            menu.add_command(label="Execute Snippet", command=self.execute_snippet)
            menu.add_command(label="Copy Snippet", command=self.copy_snippet)
            menu.post(event.x_root, event.y_root)
            

    @log
    def edit_snippet(self):
        edit_snippet_window = tk.Toplevel(self.root)
        edit_snippet_window.title("Edit Snippet")

        name_label = tk.Label(edit_snippet_window, text="Name:")
        name_label.grid(row=0, column=0, padx=10, pady=5)

        name_entry = tk.Entry(edit_snippet_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, self.selected_snippet[1])

        language_label = tk.Label(edit_snippet_window, text="Language:")
        language_label.grid(row=1, column=0, padx=10, pady=5)

        language_combo = ttk.Combobox(edit_snippet_window, values=self.db.get_supported_languages(), state="readonly")
        language_combo.grid(row=1, column=1, padx=10, pady=5)
        language_combo.set(self.selected_snippet[2])

        # TODO Make a widget for code and example code that has line numbers and syntax highlighting
        code_label = tk.Label(edit_snippet_window, text="Code:")
        code_label.grid(row=2, column=0, padx=10, pady=5)

        code_text = ScrolledText(edit_snippet_window, height=10)
        code_text.grid(row=2, column=1, padx=10, pady=5)
        code_text.insert(tk.END, self.selected_snippet[3])

        example_code_label = tk.Label(edit_snippet_window, text="Example Code:")
        example_code_label.grid(row=3, column=0, padx=10, pady=5)

        example_code_text = ScrolledText(edit_snippet_window, height=10)
        example_code_text.grid(row=3, column=1, padx=10, pady=5)
        example_code_text.insert(tk.END, self.selected_snippet[4])

        stdin_label = tk.Label(edit_snippet_window, text="STDIN:")
        stdin_label.grid(row=4, column=0, padx=10, pady=5)

        stdin_text = ScrolledText(edit_snippet_window, height=2)
        stdin_text.grid(row=4, column=1, padx=10, pady=5)
        stdin_text.insert(tk.END, self.selected_snippet[5])

        expected_output_label = tk.Label(edit_snippet_window, text="Expected Output:")
        expected_output_label.grid(row=5, column=0, padx=10, pady=5)

        expected_output_text = ScrolledText(edit_snippet_window, height=2)
        expected_output_text.grid(row=5, column=1, padx=10, pady=5)
        expected_output_text.insert(tk.END, self.selected_snippet[6])

        is_private_label = tk.Label(edit_snippet_window, text="Is Private:")
        is_private_label.grid(row=6, column=0, padx=10, pady=5)

        is_private_var = tk.BooleanVar()
        is_private_checkbox = tk.Checkbutton(edit_snippet_window, variable=is_private_var)
        is_private_checkbox.grid(row=6, column=1, padx=10, pady=5)
        is_private_checkbox.select() if self.selected_snippet[7] == 1 else is_private_checkbox.deselect()

        edit_button = tk.Button(edit_snippet_window, text="Edit Snippet", command=lambda: self.edit_snippet_submit(snippet_id=self.selected_snippet[0], name=name_entry.get(), language=language_combo.get(), code=code_text.get("1.0", tk.END), example_code=example_code_text.get("1.0", tk.END), stdin=stdin_text.get("1.0", tk.END), expected_output=expected_output_text.get("1.0", tk.END), is_private=is_private_var.get()))
        edit_button.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

    @log
    def edit_snippet_submit(self, **kwargs):
        self.db.edit_snippet(kwargs['snippet_id'], kwargs.get('name'), kwargs.get('language'), kwargs.get('code'),
                             kwargs.get('example_code'), kwargs.get('stdin'), kwargs.get('expected_output'),
                             kwargs.get('is_private'))
        messagebox.showinfo("Snippet Edited", "Snippet has been edited successfully!")
        self.update_snippet_treeview()


    @log
    def delete_snippet(self):
        self.db.delete_snippet(self.selected_snippet[0])
        messagebox.showinfo("Snippet Deleted", "Snippet has been deleted successfully!")
        self.update_snippet_treeview()

    @log
    def open_judge0_link(self):
        webbrowser.open_new_tab("https://judge0.com/ce")

    @log
    def copy_snippet(self):
        self.root.clipboard_clear()
        code = self.db.get_snippet(self.selected_snippet[0])[3]
        self.root.clipboard_append(code)
        self.root.update()

    @log
    def show_judge0_api_key_error(self):
        messagebox.showerror("Judge0 API Key Error", "Judge0 API Key not found. Please set the JUDGE0_API_TOKEN environment variable to your Judge0 API Key.")

    @log
    def execute_snippet(self):
        if (api_key := os.environ.get("JUDGE0_API_TOKEN")) is None:
            self.show_judge0_api_key_error()
            return        
        client = Judge0CEClient(api_key)
        
        snippet = self.db.get_snippet(self.selected_snippet[0])

        def is_empty_string(s):
            return len(s) == 0 or s.isspace() or s == "" or s == "\n" or s == "\n\n"


        code = snippet[4] if not is_empty_string(snippet[4]) else snippet[3]
        language = snippet[2]
        stdin = snippet[5]


        result = client.run_code(code, language)
        self.show_execute_snippet_result(result)

    @log
    def show_execute_snippet_result(self, result: dict):
        result_window = tk.Toplevel(self.root)
        result_window.title("Execute Snippet Result")
        result_window.geometry("700x500")

        result_text = ScrolledText(result_window, height=20)
        result_text.grid(row=0, column=0, padx=10, pady=5)
        result_text.insert(tk.END, result)

    @log        
    def update_snippet(self, snippet_id, name, language, code):
        self.db.update_snippet(snippet_id, name, language, code)
        messagebox.showinfo("Snippet Updated", "Snippet has been updated successfully!")
        self.update_snippet_treeview()


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    db = SnippetsDatabase()
    with db:
        app = SnippetsApp(db)
        app.run()
