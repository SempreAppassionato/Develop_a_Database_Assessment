# First Name Last name (This is a synced to a public repository)
# This application helps users better understand the results from Round 1 of NCIC 2024

""" 
Development next steps: 
- Make the code shorter by making an execute SQL function
- add comments 
"""

import sqlite3
import time

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
    print(colour.RED + "Checking user priveleges. (Root User required)" + colour.END)
    if username == "admin" and password == "password":
        print(colour.DARKCYAN + "Root user authentication required." + colour.END)
    if username == "root" and password == "raspberrypi":
        return True
    try:
        username = str(input("username: "))
        password = str(input("password: "))
    except:
        pass
    if username == "root" and password == "raspberrypi":
        return True
    else:
        print(colour.RED + "Invalid username or password. Please try again.\n" + colour.END)
        while True:
            print("Try again? (y/n)")
            choice = input(": ")
            if choice == "y" or choice == "Y":
                root_user_authentication()
            else:
                break

# Query functions
def print_all_contestants(): # Main code 1
    sql = "select real_name, username, school from User"
    results = run_sql(sql)
    print(colour.BOLD + colour.UNDERLINE + "\n\nName" + "                                    " + "Username                                " + "School                                         " + colour.END)
    for item in results:
        print(f"{item[1]:<40}{item[0]:<40}{item[2]:<40}\n")

def individual_score(username=None): # JOINED main code 2
    try:
        if username != None:
            userIdentification = username
        else: 
            userIdentification = str(input(colour.BOLD + "Please enter a username or real name to search for: " + colour.END))
            userIdentification = userIdentification.strip()
        userIdentification = str(userIdentification)
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        sql = "select User.real_name, User.username, User.school, SUM(question_score) from User, Question_score where User.id = Question_score.user_id and (User.real_name = '" + userIdentification + "' or User.username = '" + userIdentification + "')"
        cursor.execute(sql)
        rawResults = cursor.fetchall()
        if rawResults != [(None, None, None)]:
            results = rawResults[0]
            print(colour.BOLD + "\nName: " + colour.END + results[1])
            print(colour.BOLD + "Username: " + colour.END + results[0])
            print(colour.BOLD + "School: " + colour.END + results[2])
            print(colour.BOLD + "Total score: " + colour.END + str(results[3]) + "\n")
        else:
            print(colour.DARKCYAN + "Your query did not return any results. Please try again." + colour.END)
        db.close()
    except:
        print(colour.RED + "Invalid query, please try again.\n" + colour.END)

def search_username(): # JOINED main code 2
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

def custom_query(): # main code 3
    global dangerous
    dangerous = False
    print(colour.BOLD + "Please enter your SQL query below" + colour.END)
    try:
        userquery = str(input(": "))
    except:
        print(colour.RED + "Invalid query, please try again." + colour.END)
    dangerousKeywords = ["drop", "delete"]
    if any(keyword in userquery.lower() for keyword in dangerousKeywords):
        print(colour.RED + "Invalid query, please do not try again." + colour.END)
        dangerous = True
    concerningKeywords = ["update", "insert", "create", "replace"]
    if any(keyword in userquery.lower() for keyword in concerningKeywords):
        choice = are_you_sure()
        if choice == 2:
            dangerous = True
        elif choice == 1:
            dangerous = False
    if dangerous != True:
        results = run_sql(userquery)
        if results != 1:
            for item in results:
                print(item)

def rank_by_total_score(): # main code 4
    sql = "select rank, real_name, username, sum(question_score) from Question_score, User where user.id = Question_score.user_id group by user.id order by rank asc;"
    results = run_sql(sql)
    print(colour.BOLD + colour.UNDERLINE + "Rank" + " Name" + "                                    " + "Username                            " + "Score" + colour.END)
    for item in results:
        print(f"{item[0]:<5}{item[1]:<40}{item[2]:<36}{item[3]:<5}")

def rank_by_question_score(): # main code 5
    try:
        questionID = int(input("Please enter the a question number (1, 2, 3, 4, or 5): "))
    except:
        print(colour.RED + "Invalid question number, please try again." + colour.END)
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    sql = "select username, real_name, name, question_score, max_points from User, Question_score, Question where (Question.id = ?) and (Question.id = Question_score.question_id and user.id = Question_score.user_id) order by question_score desc;"
    try:
        cursor.execute(sql, (questionID,))
        results = cursor.fetchall()
        print("The question is " + results[0][2] + " and the maximum points is " + str(results[0][4]) + ".")
        print(colour.BOLD + colour.UNDERLINE + "Question Rank" + " Name" + "                                    " + "Username                                " + "Points       "+ colour.END)
        i = 1
        for item in results:
            print(f"{i:<10}    {item[0]:<40}{item[1]:<40}{item[3]:<40}")
            i += 1
    except:
        print(colour.RED + "Invalid question number, please try again.\n" + colour.END)
    db.close()

def rank_inside_school():
    # select real_name, username, sum(question_score) from Question_score, User where (user.id = Question_score.user_id and user.school = ?) group by user.id order by rank asc;
    print(colour.BOLD + "\nThe following schools had students who participated in this round: " + colour.END)
    print("""
    Macleans College
    Rangitoto College
    Burnside High School
    Auckland Grammar School
    Pinehurst School
    ACG Parnell College
    Wellington College
    Kristin School
    Mount Albert Grammar School
    Murrays Bay Intermediate School
    Avondale College
    Ormiston Senior College
    King's College
    Lynfield College
    Newlands College
    One Tree Hill College
    Long Bay College
    Lincoln High School
    Rototuna High School
    Bucklands Beach Intermediate
    Hamilton Boys' High School
    Papanui High School
    Wellington Girls' College
    St Andrew's College
    New Plymouth Boys' High School
    Kingsway School
    Scots College
    James Hargest College
    Verdon College
    Saint Patrick's College Silverstream
    Homeschooled
    Belmont Intermediate
    Hillcrest High School
    Mount Roskill Grammar
    Westlake Boys High School
    Saint Kentigern Boys' School
    BestCoder
    St Cuthbert's College
    Patumahoe Primary School
    Bayfield High School
    Howick College
    Takapuna Normal Intermediate School
    Wellington Girls' College
    Otumoetai College
    Diocesan School for Girls
    Mount Aspiring College
    Queen's High School
    Ficino School
    Hutt Valley High School
    TAM Code Club
    Wentworth Computer Science College
    Cashmere High School
    Saint Kentigern College
    ACG Sunderland
    Amesbury School
    Newlands Intermediate""")

    school = input("Please enter the name of the school you would like to see the ranking for: ")

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

def run_sql(query):
    try:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
    except:
        print(colour.RED + "Database connection error" + colour.END)
        return 1
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    except:
        print(colour.RED + "Invalid query, please try again." + colour.END)
        return 1
    db.close()
    return results

# other functions


#rank_inside_school()
# MAIN CODE __________________________________________________________________
while True: # Initial authentication 
    try:
        username = str(input("username: "))
        password = str(input("password: "))
    except:
        print(colour.RED + "Error\n" + colour.END)
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
    time.sleep(0.7)
    print("\n\n----------------------------------------------")
    print("1 - View all contestants")
    print("2 - Search for a username or real name to see user details")
    print("3 - Enter a custom SQL query (root access required)")
    print("4 - View the overall ranking by total score")
    print("5 - View the ranking by score on a specific question")
    print(colour.PURPLE + "\nPress press " + colour.BOLD + "q" + colour.END + colour.PURPLE + " to exit" + colour.END)
    print("----------------------------------------------\n")
    choice = input(": ")
    if choice == "1":
        print_all_contestants()
    elif choice == "2":
        search_username()
        for user in resultsList:
            individual_score(user)
        resultsList = [] # clearing the results list 
    elif choice == "3":
        if root_user_authentication():
            custom_query()
    elif choice == "4":
        rank_by_total_score()
    elif choice == "5":
        rank_by_question_score()
    elif choice == "q" or choice == "Q" or choice == "q " or choice == "Q ":
        print(colour.GREEN + "\n\nHow was your experience of this application? Your feedback will be sincerely appreciated. \nContact: 22343@burnside.school.nz\n\n\n\n")
        break