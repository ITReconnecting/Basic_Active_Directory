"""
Datclasses: https://www.youtube.com/watch?v=CvQ7e6yUtnw
CSV: https://realpython.com/python-csv/
"""

from users import Users
from dataclasses import dataclass, field
import socket
import csv

#GUI
import tkinter as tk
from tkinter import ttk
from tkinter import Tk, Frame, Menu

@dataclass
class User:
    username: str
    password: str
    groups: list[str] = field(default_factory=list)
    enabled: bool = True

@dataclass
class Group:
    name: str
    permissions: dict = field(default_factory=dict)

class Active_Directory:

    def __init__(self) -> None:
        self.accounts = Users()
        self.groups = []

    def create_user(self, username, password, groups, enabled):

        for group in groups:
            if self.search_group(group) == 102:
                return 103

        user = User(username, password, groups, enabled)
        code = self.accounts.insert([username, user])
        
        return code

    def remove_user(self, username):
        code = self.accounts.delete(username)
        
        return code
    
    def search_user(self, username):
        data = self.accounts.search(username)
        
        return data

    def create_group(self, name, permisions):
        self.groups.append([name, Group(name, permisions)])

        return 200

    def delete_group(self, group_d):
        for group in self.groups:
            if group[0] == group_d:
                self.groups.remove(group)
                return 200

    def add_user_group(self, username, group):
        old_data = self.accounts.search(username)
        new_data = old_data.groups.append(group)
        self.accounts.update(username, [username, new_data])

        return 200

    def remove_user_group(self, username, group):
        old_data = self.accounts.search(username)
        new_data = old_data.groups.remove(group)
        self.accounts.update(username, [username, new_data])

        return 200
    
    def search_group(self, group_s):
        for group in self.groups:
            if group == group_s:
                return 200
        
        return 103

class Translator:

    def __init__(self):
        self.AD = Active_Directory()

    def check_permissions(self, username, permission):
        user = self.AD.search_user(username)

        for user_group in user.groups:
            for group in self.AD.groups:
                if user_group == group[0]:
                    for permision in group[1]:
                        if permision == permission:
                            return 200
        return 408

class Server:

    def __init__(self, translator):
        self.transltor = translator
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("127.0.0.1", 8080))

        self.server.listen(5)

        while True:
            client, address = self.server.accept()
            self.handle(client)

    def handle(self, client):
        while True:
            command = client.recv(1024)

            if command == "check_permision":
                username = client.recv(1024)
                user_permision = client.recv(1024)

                code = self.transltor.check_permissions(username, user_permision)

                return code

class Users_GUI(ttk.LabelFrame):

    def __init__(self, container):
        super().__init__(container)

        self['text'] = 'Users'

        options = {'padx': 5, 'pady': 5}

        columns = ('User', 'Groups', 'Enabled')
        tree = ttk.Treeview(self, columns=columns, show='headings')

        tree.heading('User', text='User')
        tree.heading('Groups', text='Groups')
        tree.heading('Enabled', text='Enabled')

        with open('accounts.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                insert = [row[0], row[2], row[3]]
                tree.insert('', tk.END, values=insert)

        tree.bind('<<TreeviewSelect>>')
        tree.grid(row=0, column=0, sticky='nsew', **options)

        self.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")

class New_Account_GUI(ttk.LabelFrame):
    def __init__(self, container, AD):
        super().__init__(container)

        self.chosen_group = None
        self.AD = AD

        self['text'] = 'Create an Account'

        options = {'padx': 5, 'pady': 5}

        self.username_text_label = ttk.Label(self, text="Username:")
        self.username_text_label.grid(column=0, row=0, sticky='w', **options)

        self.username = tk.StringVar()
        self.username_entry = ttk.Entry(self, textvariable=self.username)
        self.username_entry.grid(column=1, row=0, sticky='w', **options)
        self.username_entry.focus()

        self.password_text_label = ttk.Label(self, text="Password:")
        self.password_text_label.grid(column=0, row=1, sticky='w', **options)

        self.password = tk.StringVar()
        self.password_entry = ttk.Entry(self, show="*", textvariable=self.password)
        self.password_entry.grid(column=1, row=1, sticky='w', **options)
        self.password_entry.focus()

        self.groups_text_label = ttk.Label(self, text="Groups:")
        self.groups_text_label.grid(column=0, row=2, sticky='w', **options)

        self.sgroup = tk.IntVar()
        self.chosen_group = tk.StringVar

        ttk.Radiobutton(
            self,
            text='Admin',
            value=0,
            variable=self.sgroup).grid(column=1, row=2, sticky='w', **options)

        ttk.Radiobutton(
            self,
            text='User',
            value=1,
            variable=self.sgroup).grid(column=2, row=2, sticky='w', **options)

        self.enable_text_label = ttk.Label(self, text="Enabled:")
        self.enable_text_label.grid(column=0, row=3, sticky='w', **options)

        self.enabled = tk.BooleanVar()

        self.is_enabled = tk.IntVar()

        ttk.Radiobutton(
            self,
            text='True',
            value=0,
            variable=self.is_enabled).grid(column=1, row=3, sticky='w', **options)

        ttk.Radiobutton(
            self,
            text='False',
            value=1,
            variable=self.is_enabled).grid(column=2, row=3, sticky='w', **options)

        self.insert_button = ttk.Button(self, cursor="mouse", text='Create Account')
        self.insert_button.grid(column=0, row=4, sticky='w', **options)
        self.insert_button.configure(command=self.insert)

        self.result_label = ttk.Label(self)
        self.result_label.grid(column=1, row=4, sticky='w', **options)

        self.grid(column=0, row=0, padx=5, pady=5, sticky="nsew")

    def insert(self):

        print(self.is_enabled.get())

        enabled = None
        chosen_group = None

        if self.is_enabled.get() == 0:
            enabled = True
        elif self.is_enabled.get() == 1:
            enabled = False

        if self.sgroup.get() == 0:
            chosen_group = "Admin"
        elif self.sgroup.get() == 1:
            chosen_group = "User"

        result = self.AD.create_user(self.username.get(), self.password.get(), chosen_group, enabled)

        if result == 200:
            self.result_label.config(text="Success!")
        elif result == 101:
            self.result_label.config(text="Data verification failed!")

class App(tk.Tk):

    def __init__(self, AD):
        super().__init__()

        self.AD = AD

        self.title('Active Directory')

        #625x275

        self.geometry('625x275')

        menubar = Menu(self)
        self.config(menu=menubar)

        options_menu = Menu(menubar)

        options_menu.add_command(
            label='View Users',
            command=self.Users_Table
        )

        options_menu.add_command(
            label='Create User',
            command=self.create_users
        )

        options_menu.add_separator()

        options_menu.add_command(
            label='Exit',
            command=self.destroy
        )

        menubar.add_cascade(
            label="Options",
            menu=options_menu
        )

    def Users_Table(self):
        frame_1 = Users_GUI(self)

        frame_1.grid(row=0, column=0)

        self.geometry('625x275')

    def create_users(self):
        frame_1 = New_Account_GUI(self, self.AD)

        frame_1.grid(row=0, column=0)

        self.geometry('325x220')

if __name__ == "__main__":

    AD = Active_Directory()
    app = App(AD)
    start = Users_GUI(app)
    app.mainloop()