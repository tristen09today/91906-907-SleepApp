'''This is the Version 2 of the code for my Sleep App. 
This version will be focusing on complex techniques like encryption via cryptography, 
inheritance and polymorphism. Including, added features like, year verification, sleep histroy, and sleep quality analysis.'''
from tkinter import *
import json
import hashlib
from datetime import *
from cryptography.fernet import Fernet



#CONSTANTS  
#Constant for creating a json file to store the user data
USER_FILE  ="users.json"
MIN_PASS= 8
MIN_USER=3
KEY_FILE = "histroy.key"

#Generating a key to encrypt the user's sleep history and sleep quality analysis

def load_key():
    try:
        with open("KEY_FILE", "rb") as file:
            return file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("KEY_FILE", "wb") as file:
            file.write(key)
        return key

key = load_key()
f = Fernet(key)

#using inheritance to create a base class for user management and a derived class for sleep session management

class JSONStore:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """This function loads the data from the json file."""
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_data(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=4)

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
    
#handles each user's sleep session, also inherits from the JSONStore class to manage sleep data
class SleepSession(JSONStore):
    def __init__(self, filename, username):
        super().__init__(filename)
        self.username = username
        if username not in self.data:
            self.data[username] = []
#JUST ADDED
class SleepHistory(SleepSession):
    def __init__(self, filename, username):
        super().__init__(filename, username)

    def add_sleep_entry(self, entry):
        self.data[self.username].append(entry)
        self.save_data()



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
    if len(password) < MIN_PASS:
        reg_message_label.config(text="Password must be at least 8 characters long.", fg="red")
        return
    if len(username) < MIN_USER:
        reg_message_label.config(text="Username must be at least 3 characters long.", fg="red")
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
    
    # Save the sleep session to the user's sleep history
    username = username_entry.get()
    sleep_history = SleepHistory("sleep_history.json", username)
    sleep_entry = {
        "start_time": sleep_time.strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": wake_time.strftime('%Y-%m-%d %H:%M:%S'),
        "duration": str(duration)
    }
  
    encrypted_entry = {
        "start_time": f.encrypt(sleep_entry["start_time"].encode()).decode(),
        "end_time": f.encrypt(sleep_entry["end_time"].encode()).decode(),
        "duration": f.encrypt(sleep_entry["duration"].encode()).decode()
    }
    sleep_history.add_sleep_entry(encrypted_entry)
    
#
def show_history():
    history_frame.tkraise()
    username = username_entry.get()
    sleep_history = SleepHistory("sleep_history.json", username)
    history_text.delete(1.0, END)  # Clear previous history
    if username in sleep_history.data:
        for entry in sleep_history.data[username]:
            decrypted_entry = {
                "start_time": f.decrypt(entry["start_time"].encode()).decode(),
                "end_time": f.decrypt(entry["end_time"].encode()).decode(),
                "duration": f.decrypt(entry["duration"].encode()).decode()
            }
            history_text.insert(END, f"Start: {decrypted_entry['start_time']}, End: {decrypted_entry['end_time']}, Duration: {decrypted_entry['duration']}\n")

    
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
Button(dashboard_frame, text="View Sleep History", command=show_history).pack(pady=5)
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


#Sleep History Frame

history_frame = Frame(content_container, bg="lightgray")
history_frame.grid(row=0, column=0, sticky="nsew")
Label(history_frame, text="Sleep History", font=("Arial", 16), bg="lightgray").pack(pady=10)
history_text = Text(history_frame, width=40, height=10)
history_text.pack(pady=5)
Button(history_frame, text="Back to Dashboard", command=show_dashboard).pack(pady=5)




#Show the login frame first when the app opens
login_frame.tkraise()



#This is to 
window.mainloop()

