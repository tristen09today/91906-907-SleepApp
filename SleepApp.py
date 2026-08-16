'''This is the Version 2 of the code for my Sleep App. 
This version will be focusing on complex techniques like encryption via cryptography, 
inheritance and polymorphism. Including, added features like, year verification, sleep histroy, and sleep quality analysis.'''
from tkinter import *
from tkinter import ttk
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
YEAR_LEVELS = range(1, 14)  # Year levels from 1 to 13
YEAR_ELIGIBILITY = [9, 10, 11, 12, 13] 
MOOD_OPTIONs= ["Great", "Okay", "Tired"]

#Generating a key to encrypt the user's sleep history and sleep quality analysis
def load_key():
    try:
        with open(KEY_FILE, "rb") as file:
            return file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as file:
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
    year = reg_year_var.get()

    #if year level not from 9 to 13
    if int(year) not in YEAR_ELIGIBILITY:
        reg_message_label.config(text="You must be in year 9 to 13 to register.", fg="red")
        return

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

def set_goal(goal_time):
    try:
        goal_time_obj = datetime.strptime(goal_time, "%H:%M")
        now = datetime.now()
        goal_datetime = now.replace(hour=goal_time_obj.hour, minute=goal_time_obj.minute, second=0, microsecond=0)
        if goal_datetime < now:
            goal_datetime += timedelta(days=1)  # Set to next day if the time has already passed
        time_until_goal = goal_datetime - now
        hours, remainder = divmod(time_until_goal.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        welcome.config(text=f"Time until bedtime: {hours}h {minutes}m {seconds}s", fg="blue")
    except ValueError:
        welcome.config(text="Invalid time format. Please use HH:MM.", fg="red")
        
#To show the starting time of the sleep session and disable the start button while enabling the wake button
def handle_sleep():
    global sleep_time
    sleep_time = datetime.now()
    sleep_status.config(text=f"Started sleeping at: {sleep_time.strftime('%H:%M:%S')}")
    start_button.config(state=DISABLED)
    wake_button.config(state=NORMAL)    
    for button in mood_button_frame.winfo_children():
        button.config(state=DISABLED)  # Disable mood buttons during sleep session
    
 #To show the duration of the sleep session and enable the start button while disabling the wake button   
def handle_wake():
    wake_time = datetime.now()
    duration = wake_time - sleep_time
    duration = duration - timedelta(microseconds=duration.microseconds)  
    sleep_status.config(text=f"Woke up at: {wake_time.strftime('%H:%M:%S')}\nDuration of sleep: {duration}")
    start_button.config(state=NORMAL)
    wake_button.config(state=DISABLED)
    for button in mood_button_frame.winfo_children():
        button.config(state=NORMAL)  # Enable mood buttons after waking up
 
    

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
        "duration": f.encrypt(sleep_entry["duration"].encode()).decode(),
        "mood": f.encrypt(sleep_entry.get("mood").encode()).decode() if "mood" in sleep_entry else ""
    }
    sleep_history.add_sleep_entry(encrypted_entry)

# Function to handle mood selection
def handle_mood(mood):
    sleep_status.config(text=f"Selected mood: {mood}")
    # Save the mood to the last sleep entry
    username = username_entry.get()
    sleep_history = SleepHistory("sleep_history.json", username)
    if username in sleep_history.data and sleep_history.data[username]:
        last_entry = sleep_history.data[username][-1]
        last_entry["mood"] = f.encrypt(mood.encode()).decode()
        sleep_history.save_data()    
    
    
#Function to show the user's sleep history, decrypting the sleep time.
def show_history():
    history_frame.tkraise()
    username = username_entry.get()
    sleep_history = SleepHistory("sleep_history.json", username)
    history_text.delete(1.0, END)  # Clear previous history
    if username in sleep_history.data:
        for entry in sleep_history.data[username]:
            if  entry.get("mood"):
                mood = f.decrypt(entry["mood"].encode()).decode()
            else:
                mood = "Not recorded"
        
            decrypted_entry = {
                "start_time": f.decrypt(entry["start_time"].encode()).decode(),
                "end_time": f.decrypt(entry["end_time"].encode()).decode(),
                "duration": f.decrypt(entry["duration"].encode()).decode(),
                "mood": mood
            }
            header = ["Date","Start Time", "End Time", "Duration", "Mood"]
            for column in header:
                history_text.insert(END, f"{column}\t")
            history_text.insert(END, "\n")

            history_text.insert(END, f"Start: {decrypted_entry['start_time']}, End: {decrypted_entry['end_time']}, Duration: {decrypted_entry['duration']}, Mood: {decrypted_entry['mood']}\n")
 
    
#Window

window=Tk()
window.title("sleep app")
window.geometry("400x350")

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
#year level dropdown menu
Label(register_frame, text="Year Level", bg="lightyellow").pack()
reg_year_var = StringVar(register_frame)
reg_year_var.set(YEAR_LEVELS[0])  # Set default value
reg_year_menu = OptionMenu(register_frame, reg_year_var, *YEAR_LEVELS)
reg_year_menu.pack()

Button(register_frame, text="Register", command=handle_register).pack(pady=5)
Button(register_frame, text="Back to Login", command=show_login).pack(pady=5)
reg_message_label = Label(register_frame, text="", font=("Arial", 12), bg="lightyellow")
reg_message_label.pack(pady=5)


#Dashboard Frame
dashboard_frame = Frame(content_container, bg="lightblue")
dashboard_frame.grid(row=0, column=0, sticky="nsew")
welcome = Label(dashboard_frame, text="", font=("Arial", 16), bg="lightblue")
welcome.pack(pady=10)

#Dropdown values
hours = [f"{i:02d}" for i in range(24)]
minutes = [f"{i:02d}" for i in range(0, 60, 5)] # 5-minute intervals

#Dropdown variables
hour_var = StringVar(value="12")
minute_var = StringVar(value="00")

#Layout
Label(dashboard_frame, text="Set Sleep Schedule:", bg="lightblue").pack(pady=5)

#Create a sub-frame to keep items side-by-side
goal_input_frame = Frame(dashboard_frame, bg="lightblue")
goal_input_frame.pack(pady=5)
combo = ttk.Combobox(goal_input_frame, textvariable=hour_var, values=hours, width=5, state ="readonly")
combo.pack(side=LEFT, padx=2)

Label(goal_input_frame, text=":", bg="lightblue", font=("Arial", 12, "bold")).pack(side=LEFT, padx=2)
combo2 = ttk.Combobox(goal_input_frame, textvariable=minute_var, values=minutes, width=5, state ="readonly")
combo2.pack(side=LEFT, padx=2)

Button(dashboard_frame, text="Set Goal", command=lambda: set_goal(f"{hour_var.get()}:{minute_var.get()}")).pack(pady=5)
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
#Mood Check in 
mood_button_frame = Frame(sleep_frame, bg="lightgray")
mood_button_frame.pack(pady=5)
for mood in MOOD_OPTIONs:
    Button(mood_button_frame, text=mood, command=lambda m=mood: handle_mood(m),
    state=DISABLED
    ).pack(side=LEFT, padx=5)
  # Disable mood buttons initially



Button(sleep_frame, text="Back to Dashboard", command=show_dashboard).pack(pady=5)


#Sleep History Frame

history_frame = Frame(content_container, bg="lightgray")
history_frame.grid(row=0, column=0, sticky="nsew")
Label(history_frame, text="Sleep History", font=("Arial", 16), bg="lightgray").pack(pady=10)
history_text = Text(history_frame, width=50, height=10)
history_text.pack(pady=5)
history_text.config(state=NORMAL)
Button(history_frame, text="Back to Dashboard", command=show_dashboard).pack(pady=5)




#Show the login frame first when the app opens
login_frame.tkraise()



#This is to 
window.mainloop()

