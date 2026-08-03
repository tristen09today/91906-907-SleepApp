'''This is the Version 1 of the code for my Sleep App. 
This will be a basic version implmenting complex techniques like Json, Tkinter, Hashing, Encryption.'''

from tkinter import *
import json
import hashlib
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



