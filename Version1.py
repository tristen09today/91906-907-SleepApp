'''This is the Version 1 of the code for my Sleep App. 
This will be a basic version implmenting complex techniques like Json, Tkinter, Hashing, Encryption.'''


""" MUST DO DOOSTRINGS """

from tkinter import *
import json
import hashlib
#storing the user data in a json file
USER_FILE  ="users.json"

#Class to manage user data, including registration and login functionality
class UserStore:
    def __init__(self, filename):
        self.filename = filename
        self.users = self.load_users()
    """This function loads the user data from the json file."""
    def load_users(self):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_users(self):
        with open(self.filename, "w") as file:
            json.dump(self.users, file, indent=4)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        if username in self.users:
            return False  # User already exists
        self.users[username] = self.hash_password(password)
        self.save_users()
        return True

    def login_user(self, username, password):
        hashed_password = self.hash_password(password)
        if username in self.users and self.users[username] == hashed_password:
            return True
        return False
#one instance of the UserStore class is created to manage user data
user_store = UserStore(USER_FILE)

def show_login():
    login_frame.tkraise()


def show_register():
    register_frame.tkraise()

def show_dashboard():
    dashboard_frame.tkraise()

#To check if the login is successful or not and display message accordingly
def handle_login():
    username = username_entry.get()
    password = password_entry.get()
    if login_user(username, password):
        login_message_label.config(text="Login successful!", fg="green")

        welcome.config(text=f"Welcome, {username}!", fg="blue")
        welcome.pack(pady=10)
        show_dashboard()
    else:
        login_message_label.config(text="Invalid username or password.", fg="red")

#To check if the registration is successful or not and display message accordingly
def handle_register():
    username = reg_username_entry.get()
    password = reg_password_entry.get()
    if register_user(username, password):
        reg_message_label.config(text="Registration successful! Please login.", fg="green")
        show_login()
    else:
        reg_message_label.config(text="Username already exists. Please choose another.", fg="red")

#Window

window=Tk()
window.title("sleep app")
window.geometry("400x300")

title_frame = Frame(window, bg="lightblue", height=80)
title_frame.pack(fill=X)

Label(title_frame, text="Sleep App", font=("Arial", 18)).pack(pady=10)

#Container to hold login_frame and register_frame in the same spot
#so tkraise() can bring one to the front and hide the other
content_container = Frame(window)
content_container.pack(fill=BOTH, expand=True)
content_container.grid_rowconfigure(0, weight=1)
content_container.grid_columnconfigure(0, weight=1)

#login Frame
login_frame = Frame(content_container, bg="lightgreen")
login_frame.grid(row=0, column=0, sticky="nsew")
Label(login_frame, text="Login", font=("Arial", 16), bg="lightgreen").pack(pady=10)
Label(login_frame, text="Username", bg="lightgreen").pack()
username_entry = Entry(login_frame)
username_entry.pack()
Label(login_frame, text="Password", bg="lightgreen").pack()
password_entry = Entry(login_frame, show="*")
password_entry.pack()
Button(login_frame, text="Login", command=handle_login).pack(pady=5)
Button(login_frame, text="Register", command=show_register).pack(pady=5)
login_message_label = Label(login_frame, text="", font=("Arial", 12), bg="lightgreen")
login_message_label.pack(pady=5)

#register Frame
register_frame = Frame(content_container, bg="lightyellow")
register_frame.grid(row=0, column=0, sticky="nsew")
Label(register_frame, text="Register", font=("Arial", 16), bg="lightyellow").pack(pady=10)
Label(register_frame, text="Username", bg="lightyellow").pack()
reg_username_entry = Entry(register_frame)
reg_username_entry.pack()
Label(register_frame, text="Password", bg="lightyellow").pack()
reg_password_entry = Entry(register_frame, show="*")
reg_password_entry.pack()
Button(register_frame, text="Register", command=handle_register).pack(pady=5)
Button(register_frame, text="Back to Login", command=show_login).pack(pady=5)
reg_message_label = Label(register_frame, text="", font=("Arial", 12), bg="lightyellow")
reg_message_label.pack(pady=5)


#Dashboard Frame
dashboard_frame = Frame(content_container, bg="lightblue")
dashboard_frame.grid(row=0, column=0, sticky="nsew")
welcome = Label(dashboard_frame, text="", font=("Arial", 16), bg="lightblue")
welcome.pack(pady=10)

Button(dashboard_frame, text="Start Sleep Session").pack(pady=5)
Button(dashboard_frame, text ="Logout", command=show_login).pack(pady=5)


#Show the login frame first when the app opens
login_frame.tkraise()





window.mainloop()