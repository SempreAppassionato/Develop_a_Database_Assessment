# First Name Last name (This is a synced to a public repository)
# This application helps users better understand the results from Round 1 of NCIC 2024

""" 
Development next steps: 
- More functions
    - Especially a search function

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
        return True
    if username == "root" and password == "raspberrypi":
        return True

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
        print(color.BOLD + "Name: " + color.END + item[1] + "\n" + color.BOLD + "Username: " + color.END + item[0] + "\n\n")
    db.close()

def custom_query(): # main code LAST
    print("Please enter your SQL query below")
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

def individual_score(): # main code 3
    try:
        userIdentification = str(input("Please enter a username or real name to search for: ")).strip()
        userIdentification = str(userIdentification)
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        sql = "select User.real_name, User.username, SUM(question_score) from User, Question_score where User.id = Question_score.user_id and (User.real_name = '" + userIdentification + "' or User.username = '" + userIdentification + "')"
        cursor.execute(sql)
        rawResults = cursor.fetchall()
        if rawResults != [(None, None, None)]:
            results = rawResults[0]
            print(color.BOLD + "Name: " + color.END + results[0])
            print(color.BOLD + "Username: " + color.END + results[1])
            print(color.BOLD + "Total score: " + color.END + str(results[2]) + "\n")
        else:
            print("Your query did not return any results. Please try again.")
        db.close()
    except:
        print("Invalid query, please try again.")

def search_username(): # main code 4
    search = str(input("Please enter a username or real name to search for: "))
    search = '%' + search + '%'
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    sql = "select real_name, username from User where real_name like ? or username like ?"
    cursor.execute(sql, (search, search))
    results = cursor.fetchall()
    for item in results:
        print(color.BOLD + "Name: " + color.END + item[0] + "\n" + color.BOLD + "Username: " + color.END + item[1] + "\n\n")
    db.close()



# MAIN CODE __________________________________________________________________
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
    print("3 - Exit")
    # see total user score by username or real name
    choice = input(": ")
    if choice == "1":
        print_all_contestants()
    elif choice == "2":
        if root_user_authentication():
            custom_query()
    elif choice == "3":
        break
    elif choice == "4":
        individual_score()
    else:
        break