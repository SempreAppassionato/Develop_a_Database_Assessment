# First Name Last name (This is a synced to a public repository)
# This application helps users better understand the results from Round 1 of NCIC 2024

""" 
Development next steps: 
- Aesthetics of input prompts
- Update comments
"""

import sqlite3

class colour:
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

# CONSTANTS AND VARIABLES ________________________________________________
DATABASE = "NZIC.db"
global username
global password

# FUNCTIONS  ___________________________________________________________

# Authentication functions
def authenticate_user(): # added to main code
    global username
    global password
    username = input("username: ")
    password = input("password: ")
    if username == "admin" and password == "password":
        return 1
    if username == "root" and password == "raspberrypi":
        return 2

def root_user_authentication(): # added to main code
    global username
    global password
    if username == "admin" and password == "password":
        print("Root user authentication required.")
        username = input("username: ")
        password = input("password: ")
        root_user_authentication()
    if username == "root" and password == "raspberrypi":
        return True
    else:
        print("Invalid username or password. Please try again.\n")
        username = input("username: ")
        password = input("password: ")
        root_user_authentication()

# Query functions
def print_all_contestants(): # main code 1 
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    sql = "select real_name, username from User"
    cursor.execute(sql)
    results = cursor.fetchall()
    for item in results:
        print(colour.BOLD + "Name: " + colour.END + item[1] + "\n" + colour.BOLD + "Username: " + colour.END + item[0] + "\n\n")
    db.close()

def custom_query(): # main code LAST
    print(colour.BOLD + "Please enter your SQL query below" + colour.END)
    try:
        userquery = str(input(": "))
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute(userquery)
        results = cursor.fetchall()
        for item in results:
            print(item)
        db.close()
    except:
        print("Invalid query, please try again.")

def individual_score(): # main code 2
    try:
        userIdentification = str(input(colour.BOLD + "Please enter a username or real name to search for: ") + colour.END).strip()
        userIdentification = str(userIdentification)
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        sql = "select User.real_name, User.username, SUM(question_score) from User, Question_score where User.id = Question_score.user_id and (User.real_name = '" + userIdentification + "' or User.username = '" + userIdentification + "')"
        cursor.execute(sql)
        rawResults = cursor.fetchall()
        if rawResults != [(None, None, None)]:
            results = rawResults[0]
            print(colour.BOLD + "Name: " + colour.END + results[0])
            print(colour.BOLD + "Username: " + colour.END + results[1])
            print(colour.BOLD + "Total score: " + colour.END + str(results[2]) + "\n")
        else:
            print("Your query did not return any results. Please try again.")
        db.close()
    except:
        print("Invalid query, please try again.")

def search_username(): # main code 3
    try:
        search = str(input(colour.BOLD + "Please enter a username or real name to search for: " + colour.END))
        search = '%' + search + '%'
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        sql = "select real_name, username from User where real_name like ? or username like ?"
        cursor.execute(sql, (search, search))
        results = cursor.fetchall()
        print(results)
        if results == []:
            print("Your query did not return any results. Please try again.")
        else:
            for item in results:
                print(colour.BOLD + "Name: " + colour.END + item[0] + "\n" + colour.BOLD + "Username: " + colour.END + item[1] + "\n\n")
        db.close()
    except:
        print("Invalid query, please try again.")

# MAIN CODE __________________________________________________________________
# Initial authentication 


while True:
    if authenticate_user() == 1:
        print("Login succeded, you have admin privileges.\n")
        break
    elif authenticate_user() == 2:
        print("Login succeeded, you have root priviliges.\n")
        break
    else:
        print("Invalid username or password. Please try again.\n")
        continue

# Deciding what to do
while True:
    print(colour.BOLD + "Welcome!" + colour.END)
    print("1 - View all contestants' names and usernames")
    print("2 - View the score of a contestant by username or real name")
    print("3 - Search for a username or real name")
    print("4 - Enter a custom SQL query (root access required)")
    print("Press any other key to exit.\n")
    choice = input(": ")
    if choice == "1":
        print_all_contestants()
    elif choice == "2":
        individual_score()
    elif choice == "3":
        search_username()
    elif choice == "4":
        if root_user_authentication():
            custom_query()
    else:
        break