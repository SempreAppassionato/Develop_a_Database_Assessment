# First Name Last name (This is a synced to a public repository)
# This application helps users better understand the results from Round 1 of NCIC 2024

""" 
Development next steps: 
- Add overall ranking and ranking by one's score on individual questions 
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
global resultsList
global username
global password
global dangerous
global customUsername
global customPassword
resultsList = []
DATABASE = "NZIC.db"

customUsername = "22343"
customPassword = "library"

# FUNCTIONS  ___________________________________________________________

# Authentication functions
def authenticate_user(username, password): # added to main code
    global customUsername
    if username == "admin" and password == "password":
        return 1
    elif username == "root" and password == "raspberrypi":
        return 2
    elif username == customUsername and password == customPassword:
        return 1
    else:
        print(colour.RED + "Invalid username or password. Please try again.\n" + colour.END)
        return -1

def root_user_authentication(): # added to main code
    global username
    global password
    if username == "admin" and password == "password":
        print(colour.DARKCYAN + "Root user authentication required." + colour.END)
        username = input("username: ")
        password = input("password: ")
        root_user_authentication()
    if username == "root" and password == "raspberrypi":
        return True
    else:
        print(colour.RED + "Invalid username or password. Please try again.\n" + colour.END)
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
    print(colour.BOLD + colour.UNDERLINE + "\n\nName" + "                                    " + "Username                            " + colour.END)
    for item in results:
        print(f"{item[1]:<40}{item[0]:<40}\n")
    db.close()

def custom_query(): # main code LAST
    global dangerous
    dangerous = False
    exit = False
    print(colour.BOLD + "Please enter your SQL query below" + colour.END)
    try:
        userquery = str(input(": "))
    except:
        print(colour.RED + "Invalid query, please try again." + colour.END)
    dangerousKeywords = ["drop", "delete"]
    if any(keyword in userquery.lower() for keyword in dangerousKeywords):
        print(colour.RED + "Invalid query, please do not try again." + colour.END)
        dangerous = True
    concerningKeywords = ["update", "insert", "create"]
    if any(keyword in userquery.lower() for keyword in concerningKeywords):
        if are_you_sure() == 2:
            dangerous = True
        elif are_you_sure() == 1:
            dangerous = False
    if dangerous != True:
        try: 
            db = sqlite3.connect(DATABASE)
            cursor = db.cursor()
        except: 
            print(colour.RED + "Database connection error" + colour.END)
        try:
            cursor.execute(userquery)
            results = cursor.fetchall()
        except: 
            print(colour.RED + "Invalid query, please try again." + colour.END)
            exit = True
        if exit != True:
            for item in results:
                print(item)
        print("\n\n")
        db.close()

def individual_score(username=None): # not in main code anymore
    try:
        if username != None:
            userIdentification = username
        else: 
            userIdentification = str(input(colour.BOLD + "Please enter a username or real name to search for: " + colour.END))
            userIdentification = userIdentification.strip()
        userIdentification = str(userIdentification)
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        sql = "select User.real_name, User.username, SUM(question_score) from User, Question_score where User.id = Question_score.user_id and (User.real_name = '" + userIdentification + "' or User.username = '" + userIdentification + "')"
        cursor.execute(sql)
        rawResults = cursor.fetchall()
        if rawResults != [(None, None, None)]:
            results = rawResults[0]
            print(colour.BOLD + "\nName: " + colour.END + results[0])
            print(colour.BOLD + "Username: " + colour.END + results[1])
            print(colour.BOLD + "Total score: " + colour.END + str(results[2]) + "\n")
        else:
            print(colour.DARKCYAN + "Your query did not return any results. Please try again." + colour.END)
        db.close()
    except:
        print(colour.RED + "Invalid query, please try again.\n" + colour.END)

def search_username(): # main code 3
    global resultsList
    try:
        search = str(input(colour.BOLD + "Please enter a username or real name to search for: " + colour.END))
        search = '%' + search + '%'
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        sql = "select real_name, username from User where real_name like ? or username like ?"
        cursor.execute(sql, (search, search))
        results = cursor.fetchall()
        if results == []:
            print(colour.END + colour.DARKCYAN + "Your query did not return any results. Please try again. \n" + colour.END)
        else:
            for item in results:
                resultsList.append(item[1])
        db.close()
    except:
        print(colour.RED + "Invalid query, please try again." + colour.END)

def rank_by_total_score(): # main code 5
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    sql = "select rank, real_name, username from User order by rank asc"
    cursor.execute(sql)
    results = cursor.fetchall()
    print(colour.BOLD + colour.UNDERLINE + "Rank" + " Name" + "                                    " + "Username                            " + colour.END)
    for item in results:
        print(f"{item[0]:<5}{item[1]:<40}{item[2]:<40}")
    db.close()

def rank_by_question_score(): # main code y
    try:
        questionID = int(input("Please enter the a question number: "))
    except:
        print(colour.RED + "Invalid question number, please try again." + colour.END)
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    sql = "select username, real_name, name, question_score, max_points from User, Question_score, Question where (Question.id = ?) and (Question.id = Question_score.question_id and user.id = Question_score.user_id) order by question_score desc;"
    cursor.execute(sql, (questionID,))
    results = cursor.fetchall()
    print(results)
    print(type(results))
    print("The question is " + results[0][2] + " and the maximum points is " + str(results[0][4]) + ".")
    print(colour.BOLD + colour.UNDERLINE + "Rank" + " Name" + "                                    " + "Username                                " + "Points       "+ colour.END)
    i = 1
    for item in results:
        print(f"{i:<5}{item[0]:<40}{item[1]:<40}{item[3]:<40}")
        i += 1
    db.close()

# other functions
def are_you_sure(): # used to ask the user if they are sure they want to run a dangerous query
    print(colour.RED + "Are you sure you want to run this query? (y/n)" + colour.END)
    choice = input(": ")
    if choice == "y":
        return 1 #not dangerous
    else:
        return 2 # dangerous

def try_again():
    # when a warning pops with a try again message, this function will be used to see if the user wants to run it again
    # if yes, run again
    # if no, return to main menu
    pass

# other functions

# MAIN CODE __________________________________________________________________

while True: # Initial authentication 
    username = input("username: ")
    password = input("password: ")
    login = authenticate_user(username, password)
    if login == 1:
        print(colour.GREEN + "Login succeded, you have admin privileges.\n" + colour.END)
        break
    elif login == 2:
        print(colour.GREEN + "Login succeeded," + colour.RED + " you have root priviliges.\n" + colour.END)
        break
    else:
        continue

print(colour.BOLD + "Welcome!" + colour.END)
while True: # Main menu
    print("1 - View all contestants' names and usernames")
    print("3 - Search for a username or real name")
    print("4 - Enter a custom SQL query (root access required)")
    print("5 - View the overall ranking by total score")
    print("6 - View the ranking by score on a specific question")
    print(colour.PURPLE + "\nPress press " + colour.BOLD + "q" + colour.END + colour.PURPLE + " to exit\n" + colour.END)
    choice = input(": ")
    if choice == "1":
        print_all_contestants()
    elif choice == "3":
        search_username()
        for user in resultsList:
            individual_score(user)
        resultsList = [] # clearing the results list 
    elif choice == "4":
        if root_user_authentication():
            custom_query()
    elif choice == "5":
        rank_by_total_score()
    elif choice == "6":
        rank_by_question_score()
    elif choice == "q" or "Q" or "q " or "Q ":
        print(colour.GREEN + "\n\nHow was your experience of this application? Your feedback will be sincerely appreciated. \nContact: 22343@burnside.school.nz\n\n\n\n")
        break