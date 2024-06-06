""" 
The purpose of this application is to allow users to view specific information from the results of the New Zealand Informatics Competition (NZIC). The data I will use is from Round 1 of NZIC in 2024. 
The data is stored in a SQLite database. The application will allow users to view the following information:
    - all contestants and their details
    - the details of a specific user
    - the overall ranking by total score
    - the ranking by score on a specific question
    - the internal ranking of a chosen school
    - more information for experienced users through custom SQL queries (root access required)

This application is for young people seeking to understand more about the results of the competition or interested in taking part in it. 
It can also help schools understand the performance of their students in the competition.


Development next steps: 
- add comments 
- testing


ERD for the database: 
 _____________________________           ______________________________           _____________________________ 
|            User             |         |         Question_score       |         |          Question           |
| PK |     id      |  INTEGER |-|------<| FK |   user_id    |  INTEGER |   .---|-| PK |     id      |  INTEGER |
|    |  username   |   TEXT   |         | FK |  question_id |  INTEGER |>--'     |    |    name     |   TEXT   |
|    |  real_name  |   TEXT   |         |    |question_score|  INTEGER |         |    |  max_points |  INTEGER |
|    |   school    |   TEXT   |          ''''''''''''''''''''''''''''''           '''''''''''''''''''''''''''''
|    |    rank     |  INTEGER |
''''''''''''''''''''''''''''''
"""

import sqlite3 # to access the databse
import time # to add time delay 

class colour: # defining class colour to easily change colours in print statements later
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
username = None # username for authentication
password = None # password for authentication

dangerous = False # boolean value that becomes True when a dangerous keyword is detected in custom_query
questionID = None # used for rank_by_question_score function
resultsList = [] # list that stores the details of each user found when using the search_username function
DATABASE = "NZIC.db" #constant 

dangerousKeywords = ["drop", "delete", "1=1"] # dangerous keywords that will be blocked by custom_query
concerningKeywords = ["update", "insert", "create", "replace"] # concerning keywords that will be questioned by custom_query by still run if they are sure

# custom username and password to be modified when neccessary 
customUsername = "22343"
customPassword = "library"


# FUNCTIONS  ___________________________________________________________
# Authentication functions
def authenticate_user(username, password): # used in the initial authentication loop
    # Function inputs: username, password 
    # Function returns: 
    # 1: normal access 
    # 2: root access
    # -1: failed authentiation
    global customUsername
    global customPassword
    if username == "admin" and password == "password":
        return 1 # normal access 
    elif username == "root" and password == "raspberrypi":
        return 2 # root access 
    elif username == customUsername and password == customPassword:
        return 1 # also normal access 
    else:
        print(colour.RED + "Invalid username or password. Please try again.\n" + colour.END)
        return -1 # failed authentication 

def root_user_authentication(): # used when a user tries to access the custom_query function
    # Function inputs: none, but reads from global username, password 
    # Function returns: True/False indicating whether root authentication has succeded 
    global username
    global password
    print(colour.RED + "Checking user priveleges..." + colour.END)
    if username == "admin" and password == "password": # admin is not root
        print(colour.DARKCYAN + "This user is not in the sudoers file.\nThis incident has been reported to the administrator." + colour.END)
        time.sleep(1)
        print("\nNo, just a little Linux joke. Please login as the root user below (;")
    if username == "root" and password == "raspberrypi": 
        print("Passed.")
        return True # root user authenticated 
    try: 
        # at this point in the code, if it has not returned True, then this means 
        # the current user is not root and input is needed 
        username = str(input(colour.BOLD + "username: " + colour.END))
        password = str(input(colour.BOLD + "password: " + colour.END))
    except: # catching errors 
        print(colour.RED + "Invalid username or password, please try again." + colour.END)
        try_again(0)
        return False # not root 
    if username == "root" and password == "raspberrypi": # this time, if the input is correct 
        return True # yes root 
    else: # try again
        print(colour.RED + "Invalid username or password.\n" + colour.END)
        try_again(0) # if the user does not want to try again, then the try_again function will exit
        return False # and return false so in the main code it does not continue to custom_query

# Query functions
def print_all_contestants(): # Menu No. 1
    # Function inputs: none 
    # Function purpose: prints all contestants 
    # Function prints: a table containing the name, username, and schools of every contestant 
    sql = "select real_name, username, school from User"
    results = run_sql(sql) #using the run_sql function see later 
    print(colour.BOLD + colour.UNDERLINE + "\n\nName" + "                                    " + "Username                                " + "School                                         " + colour.END)
    for item in results:
        print(f"{item[1]:<40}{item[0]:<40}{item[2]:<40}\n")

def individual_score(listOfUsernames=None): # Menu No. 2 (joined)
    # Part of Menu No. 2. Called after search_username is run 
    # Function inputs: resultsList from search_username 
    # Function prints: the username, school, and total score of all the contestants that came up in the search 
    try:
        if listOfUsernames != None: # this happens every time in the current use case for this function
            userIdentification = listOfUsernames
        else: # this else statement is redunant here 
            userIdentification = str(input(colour.BOLD + "\nPlease enter a username or real name to search for: " + colour.END))
            userIdentification = userIdentification.strip()
        userIdentification = str(userIdentification) # make sure it's string 
        sql = "select User.real_name, User.username, User.school, SUM(question_score) from User, Question_score where User.id = Question_score.user_id and (User.real_name = ? or User.username = ?)"
        rawResults = run_sql(sql, userIdentification) # getting raw results 
        if rawResults != [(None, None, None)]: 
            results = rawResults[0] # printing results 
            print(colour.BOLD + "\nName: " + colour.END + results[1])
            print(colour.BOLD + "Username: " + colour.END + results[0])
            print(colour.BOLD + "School: " + colour.END + results[2])
            print(colour.BOLD + "Total score: " + colour.END + str(results[3]) + "\n")
        else:
            print(colour.DARKCYAN + "Your query did not return any results." + colour.END)
            try_again(2) # prompting to try again
            return # if try again exits with no, then the function ends by returning to the main code
    except:
        print(colour.RED + "Invalid query.\n" + colour.END)
        try_again(2)
        return # if try again exits with no, then the function ends by returning to the main code

def search_username(): # JOINED main code 2
    global resultsList # used to store the results of the search 
    try: # protecting against rogue inputs
        search = str(input(colour.BOLD + "Please enter a username or real name to search for: " + colour.END))
        search = '%' + search + '%'
        sql = "select real_name, username from User where real_name like ? or username like ?"
        rawResults = run_sql(sql, search) # getting raw results
        if rawResults == []: # if raw results are empty
            print(colour.END + colour.DARKCYAN + "Your query did not return any results. Please try again. \n" + colour.END)
            try_again(2)
            return
        else:
            for item in rawResults:
                resultsList.append(item[1]) # add to results list to be input into individual_score
    except:
        print(colour.RED + "Invalid query." + colour.END)
        try_again(2)
        return

def custom_query(): # main code 3
    global dangerous
    global dangerousKeywords
    global concerningKeywords
    dangerous = False
    show_ERD()
    print(colour.BOLD + "Please enter your SQL query below" + colour.END)
    try:
        userquery = str(input(": "))
    except:
        print(colour.RED + "Invalid query, please try again." + colour.END)
        try_again(3)
        return
    if any(keyword in userquery.lower() for keyword in dangerousKeywords):
        print(colour.RED + "Invalid query, please do not try again." + colour.END)
        dangerous = True
    
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
    rawResults = run_sql(sql)
    print(colour.BOLD + colour.UNDERLINE + "Rank" + " Name" + "                                    " + "Username                            " + "Score" + colour.END)
    for item in rawResults:
        print(f"{item[0]:<5}{item[1]:<40}{item[2]:<36}{item[3]:<5}")

def rank_by_question_score(): # main code 5
    global questionID
    questionID = None
    try:
        questionID = int(input("Please enter the a question number (1, 2, 3, 4, or 5): "))
    except:
        print(colour.RED + "Invalid question number." + colour.END)
        try_again(5)
        return
    if questionID not in [1, 2, 3, 4, 5]:
        print(colour.RED + "Invalid question number." + colour.END)
        try_again(5)
        return
    sql = "select username, real_name, name, question_score, max_points from User, Question_score, Question where (Question.id = ?) and (Question.id = Question_score.question_id and user.id = Question_score.user_id) order by question_score desc;"
    try:
        rawResults = run_sql(sql, questionID)
        print("\n\nThe question " + colour.BOLD + rawResults[0][2] + colour.END + " yelids a maximum of " + colour.BOLD + str(rawResults[0][4]) + colour.END + " points.\n")
        print(colour.BOLD + colour.UNDERLINE + "Question Rank" + " Name" + "                                    " + "Username                                " + "Score       "+ colour.END)
        i = 1
        for item in rawResults:
            print(f"{i:<10}    {item[0]:<40}{item[1]:<40}{item[3]:<40}")
            i += 1
    except:
        print(colour.RED + "Invalid question number.\n" + colour.END)
        try_again(5)
        return

def rank_inside_school(): # main code 6
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
    school = str(input(colour.BOLD + "\nPlease enter the name of the school to see the internal ranking of its students: " + colour.END))
    school = school.strip()
    sql = "select real_name, username, sum(question_score) from Question_score, User where (user.id = Question_score.user_id and user.school = ?) group by user.id order by rank asc;"
    try:
        rawResults = run_sql(sql, school)
        if rawResults[0] != []:
            print(colour.BOLD + "\nRanking for " + school + ": \n" + colour.END)
            print(colour.BOLD + colour.UNDERLINE + "Internal-Rank" + " Name" + "                                    " + "Username                                " + "Score       "+ colour.END)
            i = 1
            for item in rawResults:
                print(f"{i:<10}    {item[1]:<40}{item[0]:<40}{item[2]:<40}")
                i += 1
    except:
        print(colour.RED + "Invalid school name, please try again.\n" + colour.END)
        try_again(6)
        return

# other functions
def are_you_sure(): # used to ask the user if they are sure they want to run a dangerous query
    print(colour.RED + "Are you sure you want to run this query? (y/n)" + colour.END)
    choice = input(": ")
    if choice == "y":
        return 1 #not dangerous
    else:
        return 2 # dangerous

def run_sql(query, param=None):
    global DATABASE
    # this function assumes that the input will be the same each time
    # inputRepeat = how many times the ? appears in the query
    try:
        inputRepeat = query.count("?")
    except:
        print(colour.RED + "Query error." + colour.END)
        return 1
    try:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
    except:
        print(colour.RED + "Database connection error" + colour.END)
        db.close()
        return 1
    try:
        if param is not None and inputRepeat == 0:
            cursor.execute(query, (param,))
        elif param is not None and inputRepeat != 0: 
            if isinstance(param, int):
                modifiedQuery = query.replace("?", str(param))
            else:
                param = "'" + param + "'"
                modifiedQuery = query.replace("?", param)
            cursor.execute(modifiedQuery)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
    except:
        print(colour.RED + "Invalid query, please try again." + colour.END)
        db.close()
        return 1
    db.close()
    return results

def try_again(functionNumber):
    while True:
            print(colour.DARKCYAN + "Try again? (y/n)" + colour.END)
            choice = input(": ")
            if choice == "y" or choice == "Y":
                if functionNumber == 1:
                    print_all_contestants()
                elif functionNumber == 2:
                    search_username()
                    for user in resultsList:
                        individual_score(user)
                    resultsList = []
                elif functionNumber == 3:
                    custom_query()
                elif functionNumber == 4:
                    rank_by_total_score()
                elif functionNumber == 5:
                    rank_by_question_score()
                elif functionNumber == 6:
                    rank_inside_school()
                elif functionNumber == 0:
                    root_user_authentication()
            else:
                break

def show_ERD():
    print("\n ERD for the database: ")
    print(" _____________________________           ______________________________           _____________________________")
    print(colour.UNDERLINE + "|            User             |" + colour.END + "         " + colour.UNDERLINE + "|         Question_score       |" + colour.END + "         " + colour.UNDERLINE + "|          Question           |" + colour.END)
    print("| PK |     id      |  INTEGER |-|------<| FK |   user_id    |  INTEGER |   .---|-| PK |     id      |  INTEGER |")
    print("|    |  username   |   TEXT   |         | FK |  question_id |  INTEGER |>--'     |    |    name     |   TEXT   |")
    print("|    |  real_name  |   TEXT   |         " + colour.UNDERLINE + "|    |question_score|  INTEGER |" + colour.END + "         " + colour.UNDERLINE + "|    |  max_points |  INTEGER |" + colour.END)
    print("|    |   school    |   TEXT   |")
    print(colour.UNDERLINE + "|    |    rank     |  INTEGER |\n" + colour.END)

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
    print("\n----------------------------------------------")
    print("1 - View all contestants")
    print("2 - Search for a username or real name to see user details")
    print("3 - Enter a custom SQL query (root access required)")
    print("4 - View the overall ranking by total score")
    print("5 - View the ranking by score on a specific question")
    print("6 - View the internal ranking of a chosen school")
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
    elif choice == "6":
        rank_inside_school()
    elif choice == "q" or choice == "Q" or choice == "q " or choice == "Q ":
        print(colour.DARKCYAN + "\n\nHow was your experience of this application? Your feedback will be sincerely appreciated. \nContact: 22343@burnside.school.nz\n\n\n\n")
        break