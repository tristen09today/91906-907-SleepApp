''' This is Version 4 of the code for my Sleep App.
This version will focus on improving the sleep goal system, the ability to delete incorrect sleep recors, 
a journalling systyem using complex techniques, bedtime reminders, and improvements to the interface such as icons and clearer layouts
The program will also have more classes to reduce clutter and repetition in the code. Implementing Classes, inheritance and polymorphism. '''

#importing libraries
from tkinter import *
from tkinter import ttk
import json
import hashlib
from datetime import *
from cryptography.fernet import Fernet
import matplotlib.pyplot as plt
from tkinter import messagebox


#CONSTANTS  
#Constant for creating a json file to store the user data
USER_FILE  ="users.json"
MIN_PASS= 8
MIN_USER=3
KEY_FILE = "histroy.key"
HISTORY_FILE = "sleep_history.json"
YEAR_LEVELS = range(1, 14)  #Year levels from 1 to 13
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
    """This class is used to manage the data stored in a json file."""
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
class UserStore(JSONStore):
    """This class manages user data, including registration and login functionality. It inherits
     from the JSONStore class to handle data storage as it caries the load and save_data already."""

    def __init__(self, filename):
        super().__init__(filename)
        self.users = self.data

    def hash_password(self, password):
        """This function hashes the password to make it private."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        """Using the hash_password function, this function registers 
        a new user by storing their username and hashed password in the users dictionary."""
        if username in self.users:
            return False  # User already exists
        self.users[username] = self.hash_password(password)
        self.save_data()
        return True

    def login_user(self, username, password):
        """This function checks if the username and password match the stored data."""
        hashed_password = self.hash_password(password)
        if username in self.users and self.users[username] == hashed_password:
            return True
        return False
    
class SleepSession(JSONStore):
    """handles each user's sleep session, also inherits from the JSONStore class to manage sleep data"""
    def __init__(self, filename, username):
        super().__init__(filename)
        self.username = username
        if username not in self.data:
            self.data[username] = []

    def encrypt_value(self, value):
        """This function encrypts a given value using Fernet encryption."""
        return f.encrypt(value.encode()).decode()
    
    def decrypt_value(self, value):
        """This function decrypts a given value using Fernet decryption."""
        return f.decrypt(value.encode()).decode()

class SleepHistory(SleepSession):
    """This class manages the sleep history for each user, inheriting from SleepSession."""
    def add_sleep_entry(self, entry):
        self.data[self.username].append(entry)
        self.save_data()
    def delete_sleep_entry(self, index):
        """This function deletes one sleep record ."""
        if 0 <= index < len(self.data[self.username]): # Check if the index is valid
            del self.data[self.username][index]
            self.save_data()
            return True
        return False
class SleepJournal(SleepHistory):
    """This class manages journal notes for each user's sleep records inheriting from SleepHistory."""
    def add_note(self, note):
        if self.data[self.username]:
            self.data[self.username][-1]["note"] = self.encrypt_value(note)
            self.save_data()
            return True
        return False

class SleepAnalysis(SleepSession):
    """This class gets data from the user's sleep history for analysis"""
    def get_duration(self):
        """This function retrieves the sleep durations from the user's sleep history."""
        durations = []
        for entry in self.data[self.username]:
            try:
                duration_str = self.decrypt_value(entry["duration"])
                duration_parts = duration_str.split(':')
                hours = int(duration_parts[0])
                durations.append(hours)
            except:
                pass
        return durations
    
    def get_mood(self):
        moods=[]
        for entry in self.data[self.username]:
            if entry.get("mood"):
                try:
                    mood = self.decrypt_value(entry["mood"])
                    moods.append(mood)
                except:
                    pass
        return moods
    def get_average(self):
        durations = self.get_duration()
        if durations:
            return sum(durations) / len(durations)
        return None
        
    
#Using polymorphism to create a base class for graphs and derived classes for specific graph types 
class SleepGraph(SleepAnalysis):
    """This is the base class for creating graphs using polymorphism"""
    def create_graph():
        pass

class MoodGraph(SleepGraph):
    """This class creates a bar graph showing the distribution of 
    moods from the user's sleep history."""
    def create_graph(self):
        mood_counts = {mood: 0 for mood in MOOD_OPTIONs}
        for mood in self.get_mood():
            if mood in mood_counts:
                mood_counts[mood] += 1
        plt.bar(mood_counts.keys(), mood_counts.values(), color=['green', 'yellow', 'red'])
        plt.title(f"{self.username}'s Mood Distribution")
        plt.xlabel("Mood")
        plt.ylabel("Count")
        plt.show()

class DurationGraph(SleepGraph):
    """This class creates a pie chart showing the distribution of sleep durations
      from the user's sleep history."""
    def create_graph(self):
        durations = self.get_duration()
        graph_duration=[]
        for hour in durations:
            if hour >= 8:
                graph_duration.append(8)  # Group all durations of 8 hours or more into the "8+ hours" category
            else:
                graph_duration.append(hour)
        counts = [graph_duration.count(i) for i in range(9)]  # Count occurrences of each duration from 0 to 8
        labels = [f"{i} hours" for i in range(8)] + ["8+ hours"] # Create labels for the pie chart

        graph_count =[]
        graph_label=[]
        for i in range(len(counts)):
         if counts[i] > 0:
                graph_count.append(counts[i]) # only append if the count is bigger than 0 
                graph_label.append(labels[i]) # if count is bigger than 0, append the label to the graph. 

        #Pie chart to show the distribution of sleep durations
        plt.pie(graph_count, labels=graph_label, autopct='%1.1f%%', startangle=90)
        plt.title(f"{self.username}'s Sleep Duration Distribution")
        plt.axis('equal') # so it draws a circle
        plt.show()

        
    
#one instance of the UserStore class is created to manage user data
user_store = UserStore(USER_FILE)


#these are the main functions to show the differnet frames
def show_login():
    """Brings the login frame to the front and hides other frames."""
    login_frame.tkraise()


def show_register():
    """Brings the register frame to the front and hides other frames."""
    register_frame.tkraise()

def show_dashboard():
    """Brings the dashboard frame to the front and hides other frames."""
    dashboard_frame.tkraise()

def show_sleep():
    """Brings the sleep session frame to the front and hides other frames."""
    sleep_frame.tkraise()

def show_history():
    """Brings the sleep history frame to the front and hides other frames."""
    history_frame.tkraise()

def show_graphs():
    """Brings the graphs and analysis frame to the front and hides other frames."""
    graphs_frame.tkraise()
    improvements()  # Call the improve_graph function to update the average sleep duration
    
   


#To check if the login is successful or not and display message accordingly
def handle_login():
    username = username_entry.get().strip()
    password = password_entry.get()
    if user_store.login_user(username, password):
        welcome.config(text=f"Welcome, {username}!", fg="blue")
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
    #Check if the user and pass fields are empty 
    if username == "" or password == "":
        reg_message_label.config(text="Username and password cannot be empty.", fg="red")
        return
    #check if pass is lss than 8 characters
    if len(password) < MIN_PASS:
        reg_message_label.config(text="Password must be at least 8 characters long.", fg="red")
        return
    #check if username is less than 3 characters
    if len(username) < MIN_USER:
        reg_message_label.config(text="Username must be at least 3 characters long.", fg="red")
        return
    
    if user_store.register_user(username, password):
        show_login() # if registration is successful, show the login frame
        
    else:
        reg_message_label.config(text="Username already exists. Please choose another.", fg="red")
        
#This function is to set the user's sleep goal and show the remaining time until when the user should go to bed
def set_goal(goal_time):
    """Sets the user's chosen bedtime goal """
    bedtime_goalvar.set(goal_time)

def update_bedtime_timer():
        goal_time = bedtime_goalvar.get()
        if goal_time != "" and wake_button['state'] == DISABLED:  # Only update if the user is still sleeping
            goal_time_obj = datetime.strptime(goal_time, "%I:%M %p")
            now = datetime.now()

            goal_datetime = now.replace(hour=goal_time_obj.hour, minute=goal_time_obj.minute, second=0, microsecond=0)
       
            if goal_datetime<now:
                goal_datetime += timedelta(days=1)  # If the goal time is earlier than now, assume it's for the next day

            time_remaining = goal_datetime - now
            total_seconds = int(time_remaining.total_seconds())
            hours= total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            bedtime_status.config(text=f"Time until bedtime goal: {hours:02d}:{minutes:02d}:{seconds:02d}", fg="blue")
        window.after(1, update_bedtime_timer)  # Update every second
         
def update_timer(sleep_time):
    """This function updates the sleep timer every 
    second while the user is sleeping"""
    if wake_button['state'] == NORMAL:  # Only update if the user is still sleeping
        now = datetime.now()
        duration = now - sleep_time
        duration = duration - timedelta(microseconds=duration.microseconds)  # Remove microseconds for cleaner display
        timer_label.config(text=str(duration))
        timer_label.after(1000, update_timer, sleep_time)  # Update every second

def handle_sleep():
    """To show the starting time of the sleep session and disable 
    the start button while enabling the wake button"""
    global sleep_time
    sleep_time = datetime.now()
    goal_time = bedtime_goalvar.get()
    if goal_time != "":
        goal_time_obj = datetime.strptime(goal_time, "%I:%M %p")
        goal_datetime = sleep_time.replace(hour=goal_time_obj.hour, minute=goal_time_obj.minute, second=0, microsecond=0)

        #If the goal time is earlier than the current time, assume it's for the next day
        difference = sleep_time - goal_datetime

        if difference.total_seconds() > 0:
                sleep_status.config(text=f"Started sleeping at: {sleep_time.strftime('%H:%M:%S')}\n"
                f"you are going to bed {int(difference.total_seconds() // 60)} minutes later than your goal.", fg="red")

        else:
             sleep_status.config(text=f"Started sleeping at: {sleep_time.strftime('%H:%M:%S')}\n"
            f"you are going to bed {int(-difference.total_seconds() // 60)} minutes earlier than your goal.", fg="green")
    else:
        sleep_status.config(text=f"Started sleeping at: {sleep_time.strftime('%H:%M:%S')}")

    #reset bedtime status  after starting sleep
    bedtime_goalvar.set("")  # Clear the bedtime goal after starting sleep
    bedtime_status.config(text="")

    start_button.config(state=DISABLED)
    wake_button.config(state=NORMAL)    
    for button in mood_button_frame.winfo_children():
        button.config(state=DISABLED)  
        wake_button.grid()  
        mood_button_frame.grid_remove()  
        sleep_back_button.grid_remove()  
        update_timer(sleep_time)  
     
def handle_note(note):
    """This function handles the note input after waking up. It updates
      the sleep status and saves the note to the last sleep entry."""
    note = journal_text.get("1.0", END).strip()  # Get the note from the Text widget
    if note == "":
        messagebox.showwarning("Empty Note", "Please enter a note before saving.")
        return
    username= username_entry.get()
    sleep_journal = SleepJournal(HISTORY_FILE, username)
    if sleep_journal.add_note(note):
        messagebox.showinfo("Note Saved", "Your note has been saved successfully.")
        journal_text.delete("1.0", END)  # Clear the Text widget after saving
    
def handle_wake():
    """ To show the duration of the sleep session and enable 
        the start button while disabling the wake button   """
    wake_time = datetime.now()
    duration = wake_time - sleep_time
    duration = duration - timedelta(microseconds=duration.microseconds)  
    sleep_status.config(text=f"Woke up at: {wake_time.strftime('%H:%M:%S')}")
    start_button.config(state=NORMAL)
    wake_button.config(state=DISABLED)
    for button in mood_button_frame.winfo_children():
        button.config(state=NORMAL)  
        wake_button.grid_remove()  
        mood_button_frame.grid()  
        dashboard_frame.grid()  
        sleep_back_button.grid()  
 
    # Save the sleep session to the user's sleep history
    username = username_entry.get()
    sleep_history = SleepHistory(HISTORY_FILE, username)
    sleep_entry = {
        "start_time": sleep_time.strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": wake_time.strftime('%Y-%m-%d %H:%M:%S'),
        "duration": str(duration)
    }
  
    encrypted_entry = {
        "start_time":sleep_history.encrypt_value(sleep_entry["start_time"]),
        "end_time": sleep_history.encrypt_value(sleep_entry["end_time"]),
        "duration": sleep_history.encrypt_value(sleep_entry["duration"]),
        "mood": "",
        "note": ""
    }
    sleep_history.add_sleep_entry(encrypted_entry)

def handle_mood(mood):
    """This function handles the mood selection after waking up. It updates
      the sleep status and saves the mood to the last sleep entry."""
    sleep_status.config(text=f"Selected mood: {mood}")
    # Save the mood to the last sleep entry
    username = username_entry.get()
    sleep_history = SleepHistory(HISTORY_FILE, username)
    if username in sleep_history.data and sleep_history.data[username]:
        last_entry = sleep_history.data[username][-1]
        last_entry["mood"] = sleep_history.encrypt_value(mood)  # Encrypt the mood before saving  
        sleep_history.save_data() 
        mood_button_frame.grid_remove()  # Hide the mood button frame after selection
        journal_frame.grid()  # Show the journaling frame after mood selection 
    



#Function to show the user's sleep history, decrypting the sleep time.
def show_history():
    """This function displays the user's sleep history in a table format. It decrypts 
    the stored sleep data and appends the history frame."""
    history_frame.tkraise()
    username = username_entry.get()
    sleep_history = SleepHistory(HISTORY_FILE, username)
   
    for widget in history_rows.winfo_children():
        widget.destroy()  # Clear previous history entries

    header = ["Start Time", "End Time", "Duration", "Mood", "Delete"]
    for col, text in enumerate(header):
         Label(history_rows, text=text, font=("Arial", 12, "bold")).grid(row=0, column=col, padx=15)


    if username in sleep_history.data:
        for entry in sleep_history.data[username]:
            if  entry.get("mood"):
                mood = sleep_history.decrypt_value(entry["mood"])
            else:
                mood = "Not-recorded"
            #to decrypt the sleep history and display it in a table format
            decrypted_entry = {
                "start_time":sleep_history.decrypt_value(entry["start_time"]),
                "end_time": sleep_history.decrypt_value(entry["end_time"]),
                "duration": sleep_history.decrypt_value(entry["duration"]),
                "mood": mood
            }
            #for loop to display the decrypted sleep history in a table format
            for col, key in enumerate(["start_time", "end_time", "duration", "mood"]):
                Label(history_rows, text=decrypted_entry[key], font=("Arial", 9)).grid(row=sleep_history.data[username].index(entry) + 1, column=col, padx=5, pady=2)

            #Button to delete the entry, running the delete_entry function
            Button(history_rows, text="Delete", font =("Arial", 8), command=lambda r=sleep_history.data[username].index(entry): 
                   delete_entry(r)).grid(row=sleep_history.data[username].index(entry) + 1, column=4, padx=5, pady=2)


def delete_entry(index):
    """This function deletes a sleep entry from the user's sleep history."""
    answer = messagebox.askyesno("Delete Entry", "Are you sure you want to delete this entry?")
    if answer:
        username = username_entry.get()
        sleep_history = SleepHistory(HISTORY_FILE, username)
        sleep_history.delete_sleep_entry(index)
        show_history()  # Refresh the history display after deletion
            
            
def mood_graph():
    """This function generates a pie chart 
    showing the distribution of moods from the user's sleep history."""
    username = username_entry.get()
    mood_analysis = MoodGraph(HISTORY_FILE, username)
    mood_analysis.create_graph()  # Call the create_graph method of MoodGraph
   

def sleep_graph():
    """This function generates a bar graph showing the duration of sleep sessions from the user's sleep history."""
    username = username_entry.get()
    duration_analysis = DurationGraph(HISTORY_FILE, username)
    duration_analysis.create_graph()  # Call the create_graph method of DurationGraph
    
   

def improvements():
    username = username_entry.get()
    sleep_analysis = SleepAnalysis(HISTORY_FILE, username)
    average = sleep_analysis.get_average()  # Get the average sleep duration
    if average is not None:
        average_label.config(text=f"Average Sleep Duration: {average:.2f} hours", fg="blue")
        if average <7:  # if average is less than 7 hours, give advice to get more sleep
            advice = "Try to get more sleep each night."

        else: #else give advice that the user is getting enough sleep
            advice = "Great job! You are getting enough sleep."

        advices_label.config(text=advice)

    else:
        average_label.config(text="No sleep data available.", fg="black")
        advices_label.config(text="Complete a session.", fg="black") 
 
#Window

window=Tk()
window.title("sleep app")
window.geometry("470x400")


#Tkinter Variables


#Dropdown variables
hour_var = StringVar(value="10")
minute_var = StringVar(value="00")
ampm_var = StringVar(value="PM")
bedtime_goalvar = StringVar(value="")


title_frame = Frame(window, bg="lightblue", height=80)
title_frame.pack(fill=X)

Label(title_frame, text="Sleep App", font=("arial", 18)).pack(pady=10)

#Container to hold login_frame and register_frame in the same spot
#so tkraise() can bring one to the front and hide the other
content_container = Frame(window)
content_container.pack(fill=BOTH, expand=True)
content_container.grid_rowconfigure(0, weight=1)
content_container.grid_columnconfigure(0, weight=1)


#login Frame
login_frame = Frame(content_container, bg="lightgreen")
login_frame.grid(row=0, column=0, sticky="nsew")
Label(login_frame, text="Login", font=("arial", 16), bg="lightgreen").pack(pady=10)
Label(login_frame, text="Username", bg="lightgreen").pack()
username_entry = Entry(login_frame)
username_entry.pack()
Label(login_frame, text="Password", bg="lightgreen").pack()
password_entry = Entry(login_frame, show="*")
password_entry.pack()
Button(login_frame, text="Login", command=handle_login).pack(pady=5)
Button(login_frame, text="Register", command=show_register).pack(pady=5)
login_message_label = Label(login_frame, text="", font=("arial", 12), bg="lightgreen")
login_message_label.pack(pady=5)

#register Frame
register_frame = Frame(content_container, bg="lightyellow")
register_frame.grid(row=0, column=0, sticky="nsew")
Label(register_frame, text="Register", font=("arial", 16), bg="lightyellow").pack(pady=10)
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
reg_message_label = Label(register_frame, text="", font=("arial", 12), bg="lightyellow")
reg_message_label.pack(pady=5)


#Dashboard Frame
dashboard_frame = Frame(content_container, bg="lightblue")
dashboard_frame.grid(row=0, column=0, sticky="nsew")
dashboard_frame.grid_columnconfigure(0, weight=1)
welcome = Label(dashboard_frame, text="", font=("arial", 13), bg="lightblue")
welcome.grid(row=0, column=0, pady=10)


#Dropdown values
hours = [f"{i:02d}" for i in range(1,13)]
minutes = [f"{i:02d}" for i in range(0, 60, 5)] # 5-minute intervals
ampm= ["AM", "PM"]


#Layout
bedtime_status = Label(dashboard_frame, text="", font=("Arial", 12), bg="lightblue")
bedtime_status.grid(row=1, column=0, pady=5)
Label(dashboard_frame, text="Set Bedtime Target:", bg="lightblue").grid(row=2, column=0, pady=5)

#Create a sub-frame to keep items side-by-side
goal_input_frame = Frame(dashboard_frame, bg="lightblue")
goal_input_frame.grid(row=3, column=0, pady=5)

combo = ttk.Combobox(goal_input_frame, textvariable=hour_var, values=hours, width=5, state ="readonly")
combo.grid(row=0, column=0, padx=2)
Label(goal_input_frame, text=":", bg="lightblue", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=2)
combo2 = ttk.Combobox(goal_input_frame, textvariable=minute_var, values=minutes, width=5, state ="readonly")
combo2.grid(row=0, column=2, padx=2)
combo3 = ttk.Combobox(goal_input_frame, textvariable=ampm_var, values=ampm, width=5, state ="readonly")
combo3.grid(row=0, column=3, padx=2)

Button(dashboard_frame, text="Set Goal", command=lambda: set_goal(f"{hour_var.get()}:{minute_var.get()} {ampm_var.get()}")).grid(row=4, column=0, pady=5)
Button(dashboard_frame, text="Start Sleep Session", command=show_sleep).grid(row=5, column=0, pady=5)
Button(dashboard_frame, text="View Sleep History", command=show_history).grid(row=6, column=0, pady=5)
Button(dashboard_frame, text = "Graphs and help", command =show_graphs).grid(row=7, column=0, pady=5)
Button(dashboard_frame, text ="Logout", command=show_login).grid(row=8, column=0, pady=5)


#sleep session frame  
sleep_frame = Frame(content_container, bg="lightgray")
sleep_frame.grid(row=0, column=0, sticky="nsew")
sleep_frame.grid_columnconfigure(0, weight=1)

Label(sleep_frame, text="Sleep Session", font=("Arial", 16), bg="lightgray").grid(row=0, column=0, pady=10)
sleep_status = Label(sleep_frame, text="", font=("Arial", 12), bg="lightgray")
sleep_status.grid(row=1, column=0, pady=5)
timer_label = Label(sleep_frame, text="00:00:00", font=("Arial", 35, "bold"), bg="lightgray")
timer_label.grid(row=2, column=0, pady=5)
start_button = Button(sleep_frame, text="Start Sleep", command=handle_sleep, width=15, height=2)
start_button.grid(row=3, column=0, pady=5)
wake_button = Button(sleep_frame, text="Wake Up", command=handle_wake, state=DISABLED)
wake_button.grid(row=4, column=0, pady=5)
#Journaling Frame
journal_frame = Frame(sleep_frame, bg="lightgray")
journal_frame.grid(row=5, column=0, pady=5)
Label(journal_frame, text="Add a Note:", font=("Arial", 12), bg="lightgray").grid(row=0, column=0, pady=5)
journal_text = Text(journal_frame, width=40, height=5)
journal_text.grid(row=1, column=0, pady=5)
save_note_button = Button(journal_frame, text="Save Note", command=handle_note)
save_note_button.grid(row=2, column=0, pady=5)
journal_frame.grid_remove()  # Hide the journaling frame initially

#Mood Check in 
mood_button_frame = Frame(sleep_frame, bg="lightgray")
mood_button_frame.grid(row=5, column=0, pady=5)
for mood in MOOD_OPTIONs:
    Button(mood_button_frame, text=mood, command=lambda m=mood: handle_mood(m),
    state=DISABLED
    ).grid(row=0, column=MOOD_OPTIONs.index(mood), padx=5)
mood_button_frame.grid_remove()  # Disable mood buttons initially
sleep_back_button=Button(sleep_frame, text="Back to Dashboard", command=show_dashboard)
sleep_back_button.grid(row=6, column=0, pady=5)




#Sleep History Frame
history_frame = Frame(content_container, bg="lightgray")
history_frame.grid(row=0, column=0, sticky="nsew")
history_table_frame = Frame(history_frame, bg="white", bd=1, relief="solid")
history_table_frame.grid(row=1, column=0 , padx=10, pady=10, sticky="nsew")


# Create a canvas for the scrollable area
history_canvas = Canvas(history_table_frame, bg="white", width= 430, height=200)
history_canvas.grid(row=1, column=0, columnspan=5, sticky="nsew")

#scrollbar for the canvas
scrollbar = Scrollbar(history_table_frame, orient="vertical", command=history_canvas.yview)
scrollbar.grid(row=1, column=5, sticky="ns")
history_canvas.configure(yscrollcommand=scrollbar.set)

history_rows = Frame(history_canvas, bg="white")
history_canvas.create_window((0, 0), window=history_rows, anchor="nw")

#update scroll region when new entries are added
history_rows.bind("<Configure>", lambda e: history_canvas.configure(scrollregion=history_canvas.bbox("all")))

history_back_button= Button(history_frame, text="Back to Dashboard", command=show_dashboard)
history_back_button.grid(row=3, column=0, pady=5)


#Graphs and Feedback Frame
graphs_frame = Frame(content_container, bg="lightgray")
graphs_frame.grid(row=0, column=0, sticky="nsew")
graphs_frame.grid_columnconfigure(0, weight=1)

graphs_label = Label(graphs_frame, text="Graphs and Feedback", font=("Arial", 16, "bold"), bg="lightgray")
graphs_label.grid(row=0, column=0, pady=5) 

graph_button_frame=Frame(graphs_frame, bg="lightgray")
graph_button_frame.grid(row=2, column=0, pady=5)
Button(graph_button_frame, text="Mood Graph", command=mood_graph).grid(row=0, column=0, padx=5)
Button(graph_button_frame, text="Sleep Graph", command=sleep_graph).grid(row=0, column=1, padx=5)

Label(graphs_frame, text="Improvement:", font=("Arial", 16, "bold"), bg="lightgray").grid(row=3, column=0, pady=5)

improvement_frame = Frame(graphs_frame, bg="white", bd=1, relief="solid")
improvement_frame.grid(row=4, column=0, pady=5)

average_label = Label(improvement_frame, text="", font=("Arial", 14))
average_label.grid(row=0, column=0, pady=5)
advices_label = Label(improvement_frame, text="", font=("Arial", 14))
advices_label.grid(row=1, column=0, pady=5)

graphs_back_button = Button(graphs_frame, text="Back to Dashboard", command=show_dashboard)
graphs_back_button.grid(row=5, column=0, pady=5)

#Show the login frame first when the app opens
login_frame.tkraise()


update_bedtime_timer()  

#This is to  
window.mainloop()
