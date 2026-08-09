'''This is the Version 1 of the code for my Sleep App. 
This will be a basic version implmenting complex techniques like Json, Tkinter, Hashing, Encryption.'''


""" MUST DO DOOSTRINGS """

from tkinter import *
import json
import hashlib
from datetime import *

#storing the user data in a json file
USER_FILE  ="users.json"

#Class to manage user data, including registration and login functionality
class UserStore:
    def __init__(self, filename):
        self.filename = filename
        self.users = self.load_users()


    def load_users(self):
        """This function loads the user data from the json file."""
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

def show_sleep():
    sleep_frame.tkraise()
    


#To check if the login is successful or not and display message accordingly
def handle_login():
    username = username_entry.get()
    password = password_entry.get()
    if user_store.login_user(username, password):
        welcome.config(text=f"Welcome, {username}!", fg="blue")
        welcome.pack(pady=10)
        show_dashboard()
    else:
        login_message_label.config(text="Invalid username or password.", fg="red")

#To check if the registration is successful or not and display message 
def handle_register():
    username = reg_username_entry.get().strip()
    password = reg_password_entry.get()
    if username == "" or password == "":
        reg_message_label.config(text="Username and password cannot be empty.", fg="red")
        return
    if len(password) < 8:
        reg_message_label.config(text="Password must be at least 8 characters long.", fg="red")
        return
    if user_store.register_user(username, password):
        show_login()
    else:
        reg_message_label.config(text="Username already exists. Please choose another.", fg="red")



#To show the starting time of the sleep session and disable the start button while enabling the wake button
def handle_sleep():
    global sleep_time
    sleep_time = datetime.now()
    sleep_status.config(text=f"Started sleeping at: {sleep_time.strftime('%H:%M:%S')}")
    start_button.config(state=DISABLED)
    wake_button.config(state=NORMAL)    
    
 #To show the duration of the sleep session and enable the start button while disabling the wake button   
def handle_wake():
    wake_time = datetime.now()
    duration = wake_time - sleep_time
    duration = duration - timedelta(microseconds=duration.microseconds)  
    sleep_status.config(text=f"Woke up at: {wake_time.strftime('%H:%M:%S')}\nDuration of sleep: {duration}")
    start_button.config(state=NORMAL)
    wake_button.config(state=DISABLED)

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

Button(dashboard_frame, text="Start Sleep Session", command=show_sleep).pack(pady=5)
Button(dashboard_frame, text ="Logout", command=show_login).pack(pady=5)


#sleep session frame
sleep_frame = Frame(content_container, bg="lightgray")
sleep_frame.grid(row=0, column=0, sticky="nsew")

Label(sleep_frame, text="Sleep Session", font=("Arial", 16), bg="lightgray").pack(pady=10)
sleep_status = Label(sleep_frame, text="", font=("Arial", 12), bg="lightgray")
sleep_status.pack(pady=5)
start_button = Button(sleep_frame, text="Start Sleep", command=handle_sleep)
start_button.pack(pady=5)
wake_button = Button(sleep_frame, text="Wake Up", command=handle_wake, state=DISABLED)
wake_button.pack(pady=5)
Button(sleep_frame, text="Back to Dashboard", command=show_dashboard).pack(pady=5)


#Show the login frame first when the app opens
login_frame.tkraise()





window.mainloop()

