# First Name Last name (This is a synced to a public repository)
# This application helps users better understand the results from Round 1 of NCIC 2024

""" 
Development next steps: 
- The ability to have add custom SQL queries for the user
    - This would require a separate admin username and password for safety
- Add more functions 

"""


import sqlite3





class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# Constants and variables 
DATABASE = "NZIC.db"
global username
global password

# Functions
def authenticate_user():
    username = input("username: ")
    password = input("password: ")
    if username == "admin" and password == "password":
        return True

def root_user_authentication():
    if username == "root" and password == "raspberrypi":
        return True
    else:
        username = input("username: ")
        password = input("password: ")
        root_user_authentication()

def print_all_contestants():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    sql = "SELECT real_name, username FROM User"
    cursor.execute(sql)
    results = cursor.fetchall()
    for item in results:
        print(color.BOLD + "Name: " + color.END + item[1] + color.BOLD + " Username: " + color.END + item[0])
    db.close()

def custom_query(userquery):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(userquery)
    results = cursor.fetchall()
    for item in results:
        print(item)
    db.close()

# Main code

# Initial authentication 
while True:
    if authenticate_user():
        print("Welcome!")
        break
    else:
        print("Invalid username or password. Please try again.")
        continue

# Deciding what to do
while True:
    print("What would you like to do?")
    print("1 - View all contestants")
    print("2 - Enter a custom query")
    choice = input(": ")
    if choice == "1":
        print_all_contestants()
    if choice == "2":
        username = input("username: ")
        password = input("password: ")
        if root_user_authentication(username, password):
            while True:
                userquery = input("Enter a custom SQL query: ")
                custom_query(userquery)
                break
        else:
            print("Invalid username or password. Please try again.")
            continue