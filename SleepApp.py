''' Sleep App Version 4:
Version 4 will focus on improving the sleep goal system, the ability to delete incorrect sleep recors, 
a journalling systyem using complex techniques, bedtime reminders, and improvements to the interface such as icons and clearer layouts
The program will also have more classes to reduce clutter and repetition in the code. 
This version will also use more classes, inheritacne, and polymorphism to seperate different parts of the program and reduce repeated code'''

#importing libraries
from tkinter import *
from tkinter import ttk
import json
import hashlib
from datetime import *
from cryptography.fernet import Fernet
import matplotlib.pyplot as plt
from tkinter import messagebox
from PIL import Image, ImageTk


#CONSTANTS  
#Constant for creating a json file to store the user data
USER_FILE  ="users.json"
MIN_PASS= 8
MIN_USER=3
YEAR_LEVELS = range(1, 14)  #Year levels from 1 to 13
YEAR_ELIGIBILITY = [9, 10, 11, 12, 13] 
KEY_FILE = "histroy.key"
HISTORY_FILE = "sleep_history.json"
MOOD_OPTIONs= ["😁 Great", "🙆 Okay", "🥱 Tired"]

#loads the encryption key or creates if it does not exist
def load_key():
    """Loads the fernet enryption key used to protect sleep data"""
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

#Base class that proides JSON loading and saving for other storage classes
class JSONStore:
    """Base class used to load  and save data in JSON files"""
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
        """This function saves the data to the json file."""
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
            return False  #User already exists
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
    """Base class for accessing and protecting a user's sleep data"""
    def __init__(self, filename, username):
        super().__init__(filename)
        self.username = username
        if username not in self.data:
            self.data[username] = []

    def encrypt_value(self, value):
        """Encrypts private sleep data before it is saved."""
        return f.encrypt(value.encode()).decode()
    
    def decrypt_value(self, value):
        """Decrypts stored sleep data so it can be used by the program"""
        return f.decrypt(value.encode()).decode()

class SleepHistory(SleepSession):
    """This class manages the sleep history for each user, inheriting from SleepSession."""
    def add_sleep_entry(self, entry):
        """adds a completed sleep entry and saves the updated history """
        self.data[self.username].append(entry)
        self.save_data()
    def delete_sleep_entry(self, index):
        """This function deletes one sleep record ."""
        if 0 <= index < len(self.data[self.username]): #Check if the index is valid
            del self.data[self.username][index]
            self.save_data()
            return True
        return False
    
class SleepJournal(SleepHistory):
    """adds ecrypted journal notes to nidivdual sleep history entries."""
    def add_note(self,index, note):
        if 0 <=index < len(self.data[self.username]):  #Check if the index is valid
            self.data[self.username][index]["note"] = self.encrypt_value(note)  #Encrypt the note before saving
            self.save_data()
            return True
        return False
        
    def get_note(self, index):
        if 0 <= index < len(self.data[self.username]):  #Check if the index is valid
            encrypted_note = self.data[self.username][index].get("note", "")
            return self.decrypt_value(encrypted_note) if encrypted_note else ""
        return ""
class SleepAnalysis(SleepSession):
    """processes stored sleep data so it can be used for graphs and feedback"""
    def get_duration(self):
        """decrypts and returns the recorded sleep duration."""
        durations = []
        for entry in self.data[self.username]:
            try:
                duration_str = self.decrypt_value(entry["duration"])
                duration_parts = duration_str.split(':')
                hours = int(duration_parts[0])
                durations.append(hours)
            except(ValueError, KeyError):
                pass      
        return durations
    
    def get_mood(self):
        """decrypts and returns the recorded mood for each sleep entry."""
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
        """calculates the user's  average sleep """
        durations = []
        for entry in self.data[self.username]:
            try:
                duration_str = self.decrypt_value(entry["duration"])
                duration_parts = duration_str.split(':')
                hours = int(duration_parts[0])
                minutes = int(duration_parts[1])
                total_hours = hours + minutes / 60  #Convert minutes to hours and add to total
                durations.append(total_hours)

            except(ValueError, KeyError):
                pass
        #Calculate the average sleep if sleep records exist
        if durations:
            average_duration = sum(durations) / len(durations)
            return average_duration
        return None
        
    
#Using polymorphism to create a base class for graphs and derived classes for specific graph types 
class SleepGraph(SleepAnalysis):
    """This is the base class for creating graphs using polymorphism"""
    def create_graph(self):
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
                graph_duration.append(8)  #Group all durations of 8 hours or more into the "8+ hours" category
            else:
                graph_duration.append(hour)
        counts = [graph_duration.count(i) for i in range(9)]  #Count occurrences of each duration from 0 to 8
        labels = [f"{i} hours" for i in range(8)] + ["8+ hours"] #Create labels for the pie chart

        graph_count =[]
        graph_label=[]
        for i in range(len(counts)):
         if counts[i] > 0:
                graph_count.append(counts[i]) #only append if the count is bigger than 0 
                graph_label.append(labels[i]) #if count is bigger than 0, append the label to the graph. 

       
        #Pie chart to show the distribution of sleep durations
        plt.pie(graph_count, labels=graph_label, autopct='%1.1f%%', startangle=90)
        plt.title(f"{self.username}'s Sleep Duration Distribution")
        plt.axis('equal') #so it draws a circle
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

def show_graphs():
    """Brings the graphs and analysis frame to the front and hides other frames."""
    graphs_frame.tkraise()
    improvements()  #Call the improve_graph function to update the average sleep duration
    
   


#To check if the login is successful or not and display message accordingly
def handle_login():
    username = username_entry.get().strip()
    password = password_entry.get()
    if user_store.login_user(username, password):
        welcome.config(text=f"Welcome! {username}!", fg="blue")
        show_dashboard()
    else:
        login_message_label.config(text="Invalid username or password.", fg="red")
        login_message_label.pack(pady=5)

#To check if the registration is successful or not and display message 
def handle_register():
    username = reg_username_entry.get().strip()
    password = reg_password_entry.get()
    year = reg_year_var.get()

    #Check if the user and pass fields are empty 
    if username == "" or password == "":
        reg_message_label.config(text="Username and password cannot be empty.", fg="red")
        reg_message_label.pack(pady=5)
        return
     #check if username is less than 3 characters
    if len(username) < MIN_USER:
        reg_message_label.config(text="Username must be at least 3 characters long.", fg="red")
        reg_message_label.pack(pady=5)
        return
    #check if pass is lss than 8 characters
    if len(password) < MIN_PASS:
        reg_message_label.config(text="Password must be at least 8 characters long.", fg="red")
        reg_message_label.pack(pady=5)
        return
    
     #if year level not from 9 to 13
    if int(year) not in YEAR_ELIGIBILITY:
        reg_message_label.config(text="You must be in year 9 to 13 to register.", fg="red")
        reg_message_label.pack(pady=5)
        return
    
    if user_store.register_user(username, password):
        show_login() #if registration is successful, show the login frame
        
    else:
        reg_message_label.config(text="Username already exists. Please choose another.", fg="red")
        reg_message_label.pack(pady=5)
        
def set_goal(goal_time):
    """Sets the user's chosen bedtime goal """
    bedtime_goalvar.set(goal_time)
    alarm_on.set(False)

def show_alarm():
    """This function shows a popup window when the user's bedtime goal is reached."""
    alarm_popup = Toplevel(window)
    alarm_popup.title("Bedtime Reminder")
    alarm_popup.geometry("300x100")
    Label(alarm_popup, text="ITS TIME TO GO TO BED!", font=("Helvetica", 14)).pack(pady=20)
    Button(alarm_popup, text="OK", command=lambda:stop_alarm(alarm_popup)).pack(pady=10)
    play_alarm(alarm_popup)  #Play the alarm sound when the popup is shown

def stop_alarm(alarm_popup):
    """This function stops the alarm sound and closes the alarm popup window."""
    alarm_popup.destroy()  #Close the alarm popup      


def play_alarm(alarm_popup,count=0):
    """This function plays the alarm sound when the user's bedtime goal is reached."""
    if alarm_popup.winfo_exists() and count < 100:  #Play the alarm sound for 100 seconds or until the popup is closed
        window.bell()  #Play the alarm sound
        window.after(1000, play_alarm, alarm_popup, count + 1)  #Call the function again after 1 second
        



def update_bedtime_timer():
        """This function updates the bedtime timer every second to show the 
        remaining time until the user's bedtime goal."""
        goal_time = bedtime_goalvar.get()
        if goal_time != "": #if the user has set a bedtime goal, calculate the remaining time until that goal
            now = datetime.now()
            
            if now.strftime("%I:%M %p") == goal_time and not alarm_on.get():  #If the current time matches the goal time and the alarm is not already on
                    alarm_on.set(True)  #Set the alarm on
                    show_alarm()  #Show the alarm popup
                    bedtime_status.config(text="GO TO SLEEP!")  #Reset the bedtime status to 0
                    bedtime_goalvar.set("")  #Reset the bedtime goal to empty
            else:
                goal_time_obj = datetime.strptime(goal_time, "%I:%M %p")
                goal_datetime = now.replace(hour=goal_time_obj.hour, minute=goal_time_obj.minute, second=0, microsecond=0)
       
                if goal_datetime<now:
                    goal_datetime += timedelta(days=1)  #If the goal time is earlier than now, assume it's for the next day

                time_remaining = goal_datetime - now
                total_seconds = int(time_remaining.total_seconds())
                hours= total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                bedtime_status.config(text=f"BedTime : {hours:02d}:{minutes:02d}:{seconds:02d}",)

        window.after(1000, update_bedtime_timer)  #Update bedtime timer every second
         
def update_timer(sleep_time):
    """This function updates the sleep timer every 
    second while the user is sleeping"""
    #changed state to instate as button is using ttk
    if wake_button.instate(["!disabled"]): #Only update if the user is still sleeping
        now = datetime.now()
        duration = now - sleep_time
        duration = duration - timedelta(microseconds=duration.microseconds)  #Remove microseconds for cleaner display
        timer_label.config(text=str(duration))
        timer_label.after(1000, update_timer, sleep_time)  #Update every second

def handle_sleep():
    """To show the starting time of the sleep session and disable 
    the start button while enabling the wake button"""
    sleep_time = datetime.now()
    
    sleep_status.config(text=f"Started sleeping at: {sleep_time.strftime('%I:%M:%S %p')}")
    sleep_status.grid(row=1, column=0, pady=5)
    start_button.config(state=DISABLED) #Disable the start button while sleeping
    wake_button.config(state=NORMAL, command = lambda: handle_wake(sleep_time))  #Enable the wake button and set its command
    wake_button.config(state=NORMAL)

    #For each button in the mood_button_frame, disable it while sleeping    
    for button in mood_button_frame.winfo_children():
        button.config(state=DISABLED)  
    wake_button.grid()  
    mood_button_frame.grid_remove()  
    sleep_back_button.grid_remove()  
    update_timer(sleep_time)  

    
def handle_wake(sleep_time):
    """ To show the duration of the sleep session and enable 
        the start button while disabling the wake button   """
    wake_time = datetime.now()
    duration = wake_time - sleep_time
    duration = duration - timedelta(microseconds=duration.microseconds)  
    sleep_status.config(text=f"Woke up at: {wake_time.strftime('%I:%M:%S %p')}")

    start_button.config(state=NORMAL) 
    wake_button.config(state=DISABLED)
    #for loop to enable the mood buttons after waking up
    for button in mood_button_frame.winfo_children():
        button.config(state=NORMAL)  
        
    wake_button.grid_remove()  
    mood_button_frame.grid()  
    sleep_back_button.grid()  
 
    #Saves the sleep session to the user's sleep history
    username = username_entry.get()
    #Creates a SleepHistory object for current user
    sleep_history = SleepHistory(HISTORY_FILE, username)
    sleep_entry = {
        "start_time": sleep_time.strftime('%Y/%m/%d %I:%M:%S %p'),
        "end_time": wake_time.strftime('%Y/%m/%d %I:%M:%S %p'),
        "duration": str(duration)
    }
    #Encrypt the sleep entry
    encrypted_entry = {
        "start_time":sleep_history.encrypt_value(sleep_entry["start_time"]),
        "end_time": sleep_history.encrypt_value(sleep_entry["end_time"]),
        "duration": sleep_history.encrypt_value(sleep_entry["duration"]),
        "mood": "",
        "note": ""
    }
    #This adds the encrypted sleep entry to the user's sleep history and saves it to the json file
    sleep_history.add_sleep_entry(encrypted_entry)

def handle_mood(mood):
    """This function handles the mood selection after waking up. It updates
      the sleep status and saves the mood to the last sleep entry."""
    sleep_status.config(text=f"Selected mood: {mood}")
    #Save the mood to the last sleep entry
    username = username_entry.get()
    sleep_history = SleepHistory(HISTORY_FILE, username)
    if username in sleep_history.data and sleep_history.data[username]:
        last_entry = sleep_history.data[username][-1]
        last_entry["mood"] = sleep_history.encrypt_value(mood)  #Encrypt the mood before saving  
        sleep_history.save_data() 
        mood_button_frame.grid_remove()  #Hide the mood button frame after selection
        show_dashboard()  #Return to the dashboard after mood selection
        



#Function to show the user's sleep history, decrypting the sleep time.
def show_history():
    """ It decrypts the current users;s sleep records and display them ni the TreeView"""
    history_frame.tkraise()
    username = username_entry.get()
    sleep_history = SleepHistory(HISTORY_FILE, username)
   
    for row in history_table.get_children():
        history_table.delete(row)  #Clear existing rows in the table
    if username in sleep_history.data:

        #Loops thorugh each sleep entry and uses its index as the TreeVie item ID  eg index 0,1,2,3,4
        for index, entry in enumerate(sleep_history.data[username]):
            
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
            #This inserts the decrypted sleep entry into the history table 
            history_table.insert("", "end", iid=index, #"" is the root and "end" is to append the  entry at the end of the table
                                 
            #These are the values displayed on the TreeView
            values=(
                decrypted_entry["start_time"],
                decrypted_entry["end_time"], 
                decrypted_entry["duration"],
                 mood
                 )
            )
     
def handle_note():
    """This function handles the saving of a note for a selected sleep entry."""
    note = journal_text.get("1.0", END).strip()  #Get the note from the Text widget
    if note == "":
        messagebox.showwarning("Empty Note", "Please enter a note before saving.")
        return
    index = journal_popup.selected_index  #Get the selected entry index from the journal_frame
    username = username_entry.get()
    sleep_journal = SleepJournal(HISTORY_FILE, username)
    if sleep_journal.add_note(index, note):
        messagebox.showinfo("Note Saved", "Your note has been saved successfully.")
        journal_text.delete("1.0", END)  #Clear the Text widget after saving
        close_journal()  #Hide the journaling frame after saving
    else:
        messagebox.showerror("Error", "Failed to save the note. Please try again.")


def view_note():
    selected = history_table.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a sleep entry to view the note.")
        return
    index = int(selected[0])  #Get the selected entry index
    username = username_entry.get()
    sleep_journal= SleepJournal(HISTORY_FILE, username)
    journal_popup.selected_index = index  #Store the selected index in the journal_popup
    note = sleep_journal.get_note(index)

    journal_text.delete("1.0", END)  #Clear the Text widget before inserting the note

    if note:
        journal_text.insert("1.0", note)  #Insert the note into the Text widget

    #Show popup
    journal_popup.deiconify()  #Show the journal popup
    journal_popup.transient(window)  #Make the popup stay on top of the main window
    journal_popup.grab_set()  #Make the popup modal
   
def close_journal():
    journal_popup.withdraw()  #Hide the journaling frame when closing
    journal_popup.grab_release()  #Release the grab when closing the popup

def delete_entry():
    """This function deletes a sleep entry from the user's sleep history."""
    selected = history_table.selection()
    if not selected:
         messagebox.showwarning("No Selected", "Please select a sleep entry to delete.")
         return
    index = int(selected[0])  #Get the selected entry index
    answer = messagebox.askyesno("Delete Entry", "Are you sure you want to delete this entry?")
    if answer:
        username = username_entry.get()
        sleep_history = SleepHistory(HISTORY_FILE, username)
        sleep_history.delete_sleep_entry(index)
        show_history()  #Refresh the history display after deletion
            
            
def mood_graph():
    """Creates a bar graph shownig the user's recorded moods"""
    username = username_entry.get()
    mood_analysis = MoodGraph(HISTORY_FILE, username)
    mood_analysis.create_graph()  #Call the create_graph method of MoodGraph
   

def sleep_graph():
    """Creates a pie chart showing the distribution of sleep durations."""
    username = username_entry.get()
    duration_analysis = DurationGraph(HISTORY_FILE, username)
    duration_analysis.create_graph()  #Call the create_graph method of DurationGraph
    
   

def improvements():
    """calculates the average sleep duration from the user's sleep history and 
    provides advice based on the average."""
    username = username_entry.get()
    sleep_analysis = SleepAnalysis(HISTORY_FILE, username)
    average = sleep_analysis.get_average()  #Get the average sleep duration
    if average is not None:
        average_label.config(text=f"Average Sleep Duration: {average:.2f} hours", fg="blue")
        if average <7:  #if average is less than 7 hours, give advice to get more sleep
            advice = "Try to get more sleep each night."

        else: #else give advice that the user is getting enough sleep
            advice = "Great job! You are getting enough sleep."

        advices_label.config(text=advice)

    else:
        average_label.config(text="No sleep data available.", fg="black")
        advices_label.config(text="Complete a session.", fg="black") 

#This function animates the gif in the sleep frame by updating the image
def animate_gif(frame=0):
    """ animates the gif in the sleep frame by updating the image every 100 milliseconds."""
    sleep_background.config(image=gif_frame[frame])
    frame +=1
    if frame == len(gif_frame):
        frame = 0
    sleep_frame.after(100, animate_gif, frame)  

 
#Window setup
window=Tk()
window.title("sleep app")
window.geometry("340x440")
window.resizable(False, False)  #Disable window resizing

#importing Images 
background_image = PhotoImage(file="images/background.png")

#importing gif and converting it to a list of frames for animation
gif = Image.open("images/background1.gif")
gif_frame=[]
try:
    while True:
        frame = ImageTk.PhotoImage(gif.copy().convert("RGBA"))
        gif_frame.append(frame)
        gif.seek(len(gif_frame))  #Move to the next frame
except EOFError:
    pass  #End of frames


#Tkinter Variables


#Dropdown values
hours = [f"{i:02d}" for i in range(1,13)]
minutes = [f"{i:02d}" for i in range(60)] #all the minutes
ampm= ["AM", "PM"]

#bedtime goal and alarm variables
bedtime_goalvar = StringVar(value="")
alarm_on = BooleanVar(value=False)

#Style Variables
style = ttk.Style()
style.theme_use("clam")  #Use the "clam" theme for better aesthetics
#For login and register buttons, set the font, background color, and foreground color
style.configure("Login.TButton", font=("Helvetica", 14, "bold"),  background ="#2940C7", foreground="white")
#For the function buttons, set the font, background color, and foreground color
style.configure("Function.TButton", font=("Helvetica", 10, "bold"),  background ="#2940C7", foreground="white")
#For Sleep and Wake buttons, set the font, background color, and foreground color
style.configure("Sleep.TButton", font=("Helvetica", 18, "bold"),  background ="#2940C7", foreground="white")
style.map("TButton", background=[("active", "#0D1A66")])  #Change background color on hover

style.configure("Treeview", font=("Helvetica", 9 ))
style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), background="#FFEFB3", foreground="#1528A1")


#Dropdown variables
hour_var = StringVar(value="10")
minute_var = StringVar(value="00")
ampm_var = StringVar(value="PM")


header_frame = Frame(window, bg = "#1528A1")
header_frame.pack(fill=X)

Label(header_frame, text="☾ Sleep App", font=("Helvetica", 17, "bold"), bg = "#1528A1", fg="white",).pack(side=TOP, pady=5)
#Container to hold frames in the same spot
#so tkraise() can bring one to the front and hide the other
content_container = Frame(window)
content_container.pack(fill=BOTH, expand=True)
content_container.grid_rowconfigure(0, weight=1)
content_container.grid_columnconfigure(0, weight=1)


#login Frame
login_frame = Frame(content_container)
login_frame.grid(row=0, column=0, sticky="nsew")
login_background = Label(login_frame, image=background_image)
login_background.place(relwidth=1, relheight=1)

Label(login_frame, text="Login", font=("Helvetica", 18, "bold"),bg = "#1528A1", fg="white").pack(pady=10)
Label(login_frame, text="Username",font =("Helvetica", 14, "bold"),bg = "#1528A1", fg="white").pack(pady=10)

username_entry = Entry(login_frame, width = 13, bg = "#FFEFB3", fg = "black")
username_entry.pack()

Label(login_frame, text="Password",font =("Helvetica", 14, "bold"),bg = "#1528A1", fg="white").pack(pady=5)
password_entry = Entry(login_frame, show="*", width = 13, bg = "#FFEFB3", fg = "black")
password_entry.pack()
ttk.Button(login_frame, text="Login", command=handle_login, style="Login.TButton").pack(pady=10)
ttk.Button(login_frame, text="Register", command=show_register, style="Login.TButton").pack(pady=5)
login_message_label = Label(login_frame, text="", font=("Helvetica", 12, "bold"), bg = "#1528A1")  


#register Frame
register_frame = Frame(content_container)
register_frame.grid(row=0, column=0, sticky="nsew")
register_background = Label(register_frame, image=background_image)
register_background.place(relwidth=1, relheight=1)
Label(register_frame, text="Register", font=("Helvetica", 18, "bold"),bg ="#1528A1", fg="white").pack(pady=10)
Label(register_frame, text="Username", font=("Helvetica", 14, "bold"), bg="#1528A1", fg = "white").pack(pady=10)
reg_username_entry = Entry(register_frame,width = 13, bg = "#FFEFB3", fg = "black")
reg_username_entry.pack()
Label(register_frame, text="Password", font=("Helvetica", 14, "bold"), bg="#1528A1", fg = "white").pack(pady=5)
reg_password_entry = Entry(register_frame, show="*",width = 13, bg = "#FFEFB3", fg = "black")
reg_password_entry.pack()
#year level dropdown menu
Label(register_frame, text=" Select Year Level", font=("Helvetica", 14, "bold"), bg="#1528A1", fg = "white").pack(pady=10)
reg_year_var = StringVar(register_frame)
reg_year_var.set(YEAR_LEVELS[0])  #Set default value
reg_year_menu = OptionMenu(register_frame, reg_year_var, *YEAR_LEVELS) #it is called as a class and creates a dropdown menu with the year levels as options
reg_year_menu.pack()

ttk.Button(register_frame, text="Register", command=handle_register, style ="Login.TButton").pack(pady=5)
ttk.Button(register_frame, text="Back to Login", command=show_login, style="Login.TButton").pack(pady=5)
reg_message_label = Label(register_frame, text="", font=("Helvetica", 12, "bold"), bg = "#1528A1") 


#Dashboard Frame
dashboard_frame = Frame(content_container)
dashboard_frame.grid(row=0, column=0, sticky="nsew")
dashboard_frame.grid_columnconfigure(0, weight=1)

dashboard_background = Label(dashboard_frame, image=background_image)
dashboard_background.place(relwidth=1, relheight=1)

#welcome section
welcome = Label(dashboard_frame, text="", font=("Helvetica", 13, "bold"), bg="white")
welcome.grid(row=0, column=0, pady=10)


#Layout
goal_frame = Frame(dashboard_frame, bg="#FFEFB3", bd =3, relief="groove")
goal_frame.grid(row=1, column=0, pady=10)


Label(goal_frame, text="🌙 Set Bedtime Target:", bg="white", font=("Helvetica", 16, "bold"), fg = "#1528A1").grid(row=0, column=0, pady=5)
ttk.Button(goal_frame, text="Set Goal", command=lambda: set_goal(f"{hour_var.get()}:{minute_var.get()} {ampm_var.get()}"), style = "Function.TButton").grid(row=3, column=0, pady=5)

bedtime_status = Label(goal_frame, text="", font=("Helvetica", 18, "bold"), bg="#FFEFB3", fg="#1528A1")
bedtime_status.grid(row=1, column=0, pady=5)
#Create a sub-frame to keep items side-by-side
goal_input_frame = Frame(goal_frame, bg="#FFEFB3")
goal_input_frame.grid(row=2, column=0, pady=10)

combo = ttk.Combobox(goal_input_frame, textvariable=hour_var, values=hours, width=5, state ="readonly")
combo.grid(row=0, column=0, padx=5)
Label(goal_input_frame, text=":", font=("Helvetica", 12, "bold")).grid(row=0, column=1)
combo2 = ttk.Combobox(goal_input_frame, textvariable=minute_var, values=minutes, width=5, state ="readonly")
combo2.grid(row=0, column=2, padx=5)
combo3 = ttk.Combobox(goal_input_frame, textvariable=ampm_var, values=ampm, width=5, state ="readonly")
combo3.grid(row=0, column=3, padx=5)
ttk.Button(dashboard_frame, text="Start Sleep Session", command=show_sleep, style = "Login.TButton").grid(row=5, column=0, pady=5)
ttk.Button(dashboard_frame, text="Sleep History/Journalling", command=show_history,style = "Login.TButton").grid(row=6, column=0, pady=5)
ttk.Button(dashboard_frame, text = "Graphs and help", command =show_graphs, style = "Login.TButton").grid(row=7, column=0, pady=5)
ttk.Button(dashboard_frame, text ="Logout", command=show_login, style = "Login.TButton").grid(row=8, column=0, pady=5)

#sleep session frame  
sleep_frame = Frame(content_container, bg="#141B4A")
sleep_frame.grid(row=0, column=0, sticky="nsew")
sleep_frame.grid_columnconfigure(0, weight=1)
sleep_background = Label(sleep_frame, image=gif_frame[0])
sleep_background.place(relwidth=1, relheight=1)

Label
Label(sleep_frame, text="Sleep Session 😴", font=("Helvetica", 16, "bold"), bg="#1528A1", fg = "#FFEFB3").grid(row=0, column=0, pady=10)
sleep_status = Label(sleep_frame, text="", font=("Helvetica", 12, "bold"), bg="#1528A1", fg="white")
timer_label = Label(sleep_frame, text="00:00:00", font=("Helvetica", 60, "bold"), bg="#141B4A", fg="white")
timer_label.grid(row=2, column=0, pady=5)
start_button = ttk.Button(sleep_frame, text="Start Sleep", command=handle_sleep, style = "Sleep.TButton")
start_button.grid(row=3, column=0, pady=10)
wake_button = ttk.Button(sleep_frame, text="Wake Up",style = "Sleep.TButton", state=DISABLED)
wake_button.grid(row=4, column=0, pady=5)
wake_button.grid_remove()  

#Mood Check in 
mood_button_frame = Frame(sleep_frame)
mood_button_frame.grid(row=5, column=0, pady=5)
for mood in MOOD_OPTIONs:
    ttk.Button(mood_button_frame, text=mood, command=lambda m=mood:
                handle_mood(m), style = "Login.TButton", state=DISABLED).grid(row=0, column=MOOD_OPTIONs.index(mood), padx=5)
mood_button_frame.grid_remove()  #hide the mood choices until the user wakes up

sleep_back_button=ttk.Button(sleep_frame, text="Back to Dashboard", command=show_dashboard, style = "Login.TButton")
sleep_back_button.grid(row=6, column=0, pady=5)

#Sleep History Frame
history_frame = Frame(content_container)
Label(history_frame, image=background_image).place(relwidth=1, relheight=1)
history_frame.grid(row=0, column=0, sticky="nsew")
history_frame.grid_columnconfigure(0, weight=1)


Label(history_frame, text="Sleep History", font=("Helvetica", 16, "bold"), bg="white", fg = "#1528A1").grid(row=0, column=0, pady=10)

#TreeView Table
#instead of using a frame to display the sleep history, I used a treeview table to make it easier to read and scroll through the history
columns = ("start_time", "end_time", "duration", "mood") 
history_table = ttk.Treeview(history_frame, columns=columns, show="headings", height=8) #

#Define the headings for each column in the table and rename the columns to make it easier to read and understand
history_table.heading("start_time", text = "Start Time")
history_table.heading("end_time", text = "End Time")
history_table.heading("duration", text = "Duration")
history_table.heading("mood", text = "Mood")

history_table.column("start_time", width=100)
history_table.column("end_time", width=100)
history_table.column("duration", width=55)
history_table.column("mood", width=68)
history_table.grid(row=1, column=0, columnspan=5, pady=5)

#scrollbar to make it easier to scroll through the history table
history_scrollbar = Scrollbar(history_frame, orient="vertical", command=history_table.yview, width=13)
history_scrollbar.grid(row=1, column=5, sticky="ns")
history_table.configure(yscrollcommand=history_scrollbar.set)

#Buttons
history_button_frame = Frame(history_frame, bg="lightgray")
history_button_frame.grid(row=2, column=0, columnspan=5, pady=5)
ttk.Button(history_button_frame, text="Delete Entry", command=delete_entry, style = "Function.TButton").grid(row=0, column=0, padx=5)
ttk.Button(history_button_frame, text="Return to Dashboard", command=show_dashboard, style  = "Function.TButton").grid(row=0, column=1, padx=5)
ttk.Button(history_button_frame, text="Add/ View Note", command=view_note,  style  = "Function.TButton").grid(row=0, column=2, padx=5)

#Journaling Frame
journal_popup = Toplevel(window)
journal_popup.title("Sleep Journal")
journal_popup.geometry("400x300")

journal_popup.protocol("WM_DELETE_WINDOW", close_journal)  #Override the close button to hide the popup instead of destroying it

Label(journal_popup, text="Sleep Journal", font=("Helvetica", 16, "bold")).pack(pady=10)
Label(journal_popup, text="Write your note below:").pack(pady=5)
journal_text = Text(journal_popup, height=10, width=40)
journal_text.pack(pady=5)
button_frame= Frame(journal_popup)
button_frame.pack(pady=5)
Button(button_frame, text="Save Note", command=handle_note).grid(row=0, column=0, padx=5)
Button(button_frame, text="Close", command=close_journal).grid(row=0, column=1, padx=5)
close_journal()  #Hide the journal popup initially


#Graphs and Feedback Frame
graphs_frame = Frame(content_container, bg="#FFEFB3")
graphs_frame.grid(row=0, column=0, sticky="nsew")
graphs_frame.grid_columnconfigure(0, weight=1)

Label(graphs_frame, text="📊 Sleep and Feedback", font=("Helvetica", 16, "bold"), bg="#FFEFB3",  fg= "#1528A1").grid(row=1, column=0, pady=5) 

graph_button_frame=Frame(graphs_frame, bg="#FFEFB3")
graph_button_frame.grid(row=2, column=0, pady=10)
ttk.Button(graph_button_frame, text="Mood Graph", command=mood_graph, style = "Login.TButton").grid(row=0, column=0, padx=5)
ttk.Button(graph_button_frame, text="Sleep Graph", command=sleep_graph, style = "Login.TButton").grid(row=0, column=1, padx=5)

Label(graphs_frame, text="🤔 Sleep Feedback:", font=("Helvetica", 16, "bold"), bg="#FFEFB3",  fg= "#1528A1").grid(row=3, column=0, pady=5)

improvement_frame = Frame(graphs_frame, bg="white", bd=1, relief="solid")
improvement_frame.grid(row=4, column=0, pady=10)

average_label = Label(improvement_frame, text="", font=("Helvetica", 14, "bold"), bg = "white")
average_label.grid(row=0, column=0, pady=5)
advices_label = Label(improvement_frame, text="", font=("Helvetica", 14, "bold"), bg = "white")
advices_label.grid(row=1, column=0, pady=5)

graphs_back_button = ttk.Button(graphs_frame, text="Back to Dashboard", command=show_dashboard, style = "Login.TButton")
graphs_back_button.grid(row=5, column=0, pady=5)

#Show the login frame first when the app opens
login_frame.tkraise()
#Function to update the bedtime timer every second
update_bedtime_timer()  

animate_gif()  #Start the GIF animation no the sleep screen

#This is to keep the window open and running until the user closes it 
window.mainloop()