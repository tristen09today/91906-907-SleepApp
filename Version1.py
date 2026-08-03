'''This is the Version 1 of the code for my Sleep App. 
This will be a basic version implmenting complex techniques like Json, Tkinter, Hashing, Encryption.'''

from tkinter import *
import json
import hashlib
import os
#storing the user data in a json file
USER_FILE  ="users.json"

#login function
#Function for loading users 
def load_users():
    try:
        with open(USER_FILE, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}
    return users


def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def hash_password(password):  
    #turns password into hash so real password is not stored  
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    users = load_users()
    if username in users:
        return False  # User already exists
    users[username] = hash_password(password)
    save_users(users)
    return True


def login_user(username, password):
    users = load_users()
    hashed_password = hash_password(password)
    if username in users and users[username] == hashed_password:
        return True
    return False

def show_login():
    login_frame.tkraise()


def show_register():
    register_frame.tkraise()

def handle_login():
    username = username_entry.get()
    password = password_entry.get()
    if login_user(username, password):
        message_label.config(text="Login successful!", fg="green")
    else:
        message_label.config(text="Invalid username or password.", fg="red")

#Window

window=Tk()
window.title("sleep app")
window.geometry("400x300")

title_frame = Frame(window, bg="lightblue", height=80)
title_frame.pack(fill=X)

Label(title_frame, text="Sleep App", font=("Arial", 18)).pack(pady=10)


#login Frame
login_frame = Frame(window, bg="lightgreen")
login_frame.pack(fill=BOTH, expand=True)
Label(login_frame, text="Login", font=("Arial", 16)).pack(pady=10)
Label(login_frame, text="Username").pack()
username_entry = Entry(login_frame)
username_entry.pack()
Label(login_frame, text="Password").pack()
password_entry = Entry(login_frame, show="*")
password_entry.pack()
Button(login_frame, text="Login", command=handle_login).pack(pady=5)
Button(login_frame, text="Register", command=show_register).pack(pady=5)
message_label = Label(login_frame, text="", font=("Arial", 12))
message_label.pack(pady=5)
window.mainloop()


