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

ERD for the database: 
 _____________________________           ______________________________           _____________________________ 
|            User             |         |         Question_score       |         |          Question           |
| PK |     id      |  INTEGER |-|------<| FK |   user_id    |  INTEGER |   .---|-| PK |     id      |  INTEGER |
|    |  username   |   TEXT   |         | FK |  question_id |  INTEGER |>--'     |    |    name     |   TEXT   |
|    |  real_name  |   TEXT   |         |    |question_score|  INTEGER |         |    |  max_points |  INTEGER |
|    |   school    |   TEXT   |          ''''''''''''''''''''''''''''''           '''''''''''''''''''''''''''''
|    |    rank     |  INTEGER |
''''''''''''''''''''''''''''''
                                    MAIN CODE STARTS AT LINE 451
"""

import sqlite3 # to access the databse
import time # to add time delay 
import shutil # to get the terminal window size
import getpass # to not display the password or username when entering

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
customUsername = "OSS"
customPassword = "BossIsCool"

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
        time.sleep(2) # haha
        print("\nNo, just a little Linux joke. Please login as the root user below (;")
    if username == "root" and password == "raspberrypi": 
        print("Passed.")
        return True # root user authenticated 
    try: 
        # at this point in the code, if it has not returned True, then this means 
        # the current user is not root and input is needed 
        username = getpass.getpass("username: ") 
        password = getpass.getpass("password: ")
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
    check_window_width()

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
        check_window_width()
    except:
        print(colour.RED + "Invalid query.\n" + colour.END)
        try_again(2) # prompting to try again
        return # if try again exits with no, then the function ends by returning to the main code

def search_username(): # Menu No. 2 (joined)
    # Function input: none 
    # Function purpose: to find names that exactly match or closely resemble the input
    # function returns: search results to resultsList
    global resultsList # used to store the results of the search 
    try: # protecting against rogue inputs
        search = str(input(colour.BOLD + "Please enter a username or real name to search for: " + colour.END))
        search = '%' + search + '%'
        sql = "select real_name, username from User where real_name like ? or username like ?"
        rawResults = run_sql(sql, search) # getting raw results
        if rawResults == []: # if raw results are empty
            print(colour.END + colour.DARKCYAN + "Your query did not return any results. Please try again. \n" + colour.END)
            try_again(2) # prompting to try again
            return
        else:
            for item in rawResults:
                resultsList.append(item[1]) # add to results list to be input into individual_score
    except:
        print(colour.RED + "Invalid query." + colour.END)
        try_again(2)
        return

def custom_query(): # Menu No. 3
    # Function inputs: none
    # Function purpose: to run an SQL query of the user's choice
    # Restraints: cannot use dangerousKeywords, needs to confirm before running queries with concerningKeywords
    # Function outputs: raw SQL results 
    global dangerous # accessing global variables and lists 
    global dangerousKeywords
    global concerningKeywords
    dangerous = False # setting dangerous to False at the beginning
    show_ERD() # printing out the ERD digarm so the user can see the structure of the database 
    print(colour.BOLD + "Please enter your SQL query below" + colour.END)
    try: # protecting against rogue inputs 
        userquery = str(input(": "))
    except:
        print(colour.RED + "Invalid query, please try again." + colour.END)
        try_again(3) # prompting to try again
        return # so if the user does not want to try again, this function ends
    if any(keyword in userquery.lower() for keyword in dangerousKeywords): 
        # if any keywords from the userquery are in the dangerousKeywords list
        print(colour.RED + "Invalid query, please do not try again." + colour.END)
        dangerous = True # setting dangerous to True
    
    if any(keyword in userquery.lower() for keyword in concerningKeywords):
        # if any keywords from the userquery are in the concerningKeywords list
        choice = are_you_sure() # asking the user are you sure 
        if choice == 1: # sure 
            dangerous = False
        elif choice == 2: # not sure 
            dangerous = True
    if dangerous != True: # if it is not deemed dangerous 
        results = run_sql(userquery) # run the SQL query
        if results != 1: # if the results are not an empty
            for item in results: # print out the raw results 
                print(item)
            check_window_width()

def rank_by_total_score(): # Menu No. 4
    # Function inputs: none
    # Function purpose: to rank the contestants by their total score
    # Function prints: the rank, name, username, and total score of each contestant
    sql = "select rank, real_name, username, sum(question_score) from Question_score, User where user.id = Question_score.user_id group by user.id order by rank asc;"
    rawResults = run_sql(sql) # getting raw results
    print(colour.BOLD + colour.UNDERLINE + "Rank" + " Name" + "                                    " + "Username                            " + "Score" + colour.END)
    for item in rawResults: # printing it out in a table
        print(f"{item[0]:<5}{item[1]:<40}{item[2]:<36}{item[3]:<5}")
    check_window_width()

def rank_by_question_score(): # Menu No. 5
    # Function inputs: none
    # Function purpose: to rank the contestants by their score on a specific question
    # Function prints: the rank, name, username, and score of each contestant for a particular question
    global questionID
    questionID = None
    try: # protecting against rogue inputs
        questionID = int(input("Please enter the a question number (1, 2, 3, 4, or 5): "))
    except:
        print(colour.RED + "Invalid question number." + colour.END)
        try_again(5) # prompting to try again
        return # so if the user does not want to try again, this function ends
    if questionID not in [1, 2, 3, 4, 5]: # the questionID must be one of the five questions
        print(colour.RED + "Invalid question number." + colour.END)
        try_again(5)
        return # so if the user does not want to try again, this function ends
    sql = "select username, real_name, name, question_score, max_points from User, Question_score, Question where (Question.id = ?) and (Question.id = Question_score.question_id and user.id = Question_score.user_id) order by question_score desc;"
    try:
        rawResults = run_sql(sql, questionID) # getting raw results
        # question information
        print("\n\nThe question " + colour.BOLD + rawResults[0][2] + colour.END + " yelids a maximum of " + colour.BOLD + str(rawResults[0][4]) + colour.END + " points.\n")
        # printing out the results 
        print(colour.BOLD + colour.UNDERLINE + "Question Rank" + " Name" + "                                    " + "Username                                " + "Score       "+ colour.END)
        i = 1
        for item in rawResults:
            print(f"{i:<10}    {item[0]:<40}{item[1]:<40}{item[3]:<40}")
            i += 1
        check_window_width()
    except: # catching errors 
        print(colour.RED + "Invalid question number.\n" + colour.END)
        try_again(5)
        return

def rank_inside_school(): # Menu No. 6
    # Function inputs: none
    # Function purpose: to rank the contestants by their total score within a specific school
    # Function prints: the rank, name, username, and total score of each contestant within a specific school
    print(colour.BOLD + "\nThe following schools had students who participated in this round: " + colour.END)
    # the diffefrent schools that have participated 
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
    # choosing the school 
    school = str(input(colour.BOLD + "\nPlease enter the name of the school to see the internal ranking of its students: " + colour.END))
    school = school.strip() # getting rid of any trailing whitespaces
    sql = "select real_name, username, sum(question_score) from Question_score, User where (user.id = Question_score.user_id and user.school = ?) group by user.id order by rank asc;"
    try: # protecting against rogue inputs
        rawResults = run_sql(sql, school) # getting raw results
        if rawResults[0] != []: # if raw results are not empty
            print(colour.BOLD + "\nRanking for " + school + ": \n" + colour.END)
            print(colour.BOLD + colour.UNDERLINE + "Internal-Rank" + " Name" + "                                    " + "Username                                " + "Score       "+ colour.END)
            i = 1 # variable for ranking 
            for item in rawResults:
                print(f"{i:<10}    {item[1]:<40}{item[0]:<40}{item[2]:<40}")
                i += 1 # incrementing the rank
            check_window_width()
    except:
        print(colour.RED + "Invalid school name, please try again.\n" + colour.END)
        try_again(6) # if any error, try again
        return

# other functions
def are_you_sure(): 
    # used to ask the user if they are sure they want to run a dangerous query
    # Function inputs: none
    # Function returns: 1 if the user is sure, 2 if the user is not sure
    print(colour.RED + "Are you sure you want to run this query? (y/n)" + colour.END)
    try: # protecting against rogue inputs
        choice = input(": ")
    except: 
        print(colour.RED + "Invalid choice." + colour.END)
        return 2 # dangerous
    if choice == "y" or choice == "Y":
        return 1 # not dangerous
    else:
        return 2 # dangerous

def run_sql(query, param=None):
    # NOTE this function assumes that the input will be the same each time
    # NOTE inputRepeat = how many times the ? appears in the query
    # Function inputs: query, parameter (default none)
    # Function purpose: to run an SQL query
    # Function returns: the rawresults of the query
    global DATABASE # accessing the global database variable
    try:
        inputRepeat = query.count("?") # counting how many times the ? appears in the query to determine how many times the param will be repeated
    except: # if this is an error 
        print(colour.RED + "Query error." + colour.END)
        return 1 # so the that caled this one ends
    try: 
        # if we have reached this point in the code, then the query is valid and the database can be connected to
        db = sqlite3.connect(DATABASE) # connecting to the database
        cursor = db.cursor() # creating a cursor
    except: # if there is a database connection error 
        print(colour.RED + "Database connection error" + colour.END)
        db.close()
        return 1 # so the that caled this one ends
    try:
        if param is not None and inputRepeat == 1: # if there is a parameter and there is 1 ? in the query
            cursor.execute(query, (param,))
        elif param is not None and inputRepeat != 0: # if there is a parameter and there are multiple ? in the query
            if isinstance(param, int): # if the parameter is an integer
                modifiedQuery = query.replace("?", str(param)) # replace the ? with the parameter
            else: # if the parameter is a string
                param = "'" + param + "'" # add quotes around the parameter
                modifiedQuery = query.replace("?", param) # replace the ? with the parameter
            cursor.execute(modifiedQuery) # execute the modified query
        else: # if there is no parameter
            cursor.execute(query) # execute the query 
        results = cursor.fetchall() # fetch all results no matter what parameter 
    except: # if error 
        print(colour.RED + "Invalid query, please try again." + colour.END)
        db.close() # close the database connection
        return 1 # so the that caled this one  ends
    db.close() # still closing the database connection even if there aren't any errors 
    return results # but this time returning the results 

def try_again(functionNumber):
    # Function inputs: functionNumber - to determine which function to run again
    # Function purpose: to prompt the user to try again when an error is encountered with a function
    # Function returns: none
    while True: # loop to prompt the user to try again
            print(colour.DARKCYAN + "Try again? (y/n)" + colour.END)
            choice = input(": ") # asking for the user's choice
            if choice == "y" or choice == "Y": # if yes 
                # running different functions based on the functionNumber input
                if functionNumber == 1:
                    print_all_contestants()
                    break
                elif functionNumber == 2:
                    search_username()
                    for user in resultsList:
                        individual_score(user)
                    resultsList = []
                    break
                elif functionNumber == 3:
                    custom_query()
                    break
                elif functionNumber == 4:
                    rank_by_total_score()
                    break
                elif functionNumber == 5:
                    rank_by_question_score()
                    break
                elif functionNumber == 6:
                    rank_inside_school()
                    break
                elif functionNumber == 0:
                    if root_user_authentication(): # root authentication required 
                        custom_query()
                    break
            else: # anything other than yes 
                break # break the loop

def show_ERD():
    # Function inputs: none
    # Function purpose: to print the ERD diagram for the database when the user wants to run a custom SQL query
    # Function returns: none
    # Function prints: ERD diagram
    print("\n ERD for the database: ")
    print(" _____________________________           ______________________________           _____________________________")
    print(colour.UNDERLINE + "|            User             |" + colour.END + "         " + colour.UNDERLINE + "|         Question_score       |" + colour.END + "         " + colour.UNDERLINE + "|          Question           |" + colour.END)
    print("| PK |     id      |  INTEGER |-|------<| FK |   user_id    |  INTEGER |   .---|-| PK |     id      |  INTEGER |")
    print("|    |  username   |   TEXT   |         | FK |  question_id |  INTEGER |>--'     |    |    name     |   TEXT   |")
    print("|    |  real_name  |   TEXT   |         " + colour.UNDERLINE + "|    |question_score|  INTEGER |" + colour.END + "         " + colour.UNDERLINE + "|    |  max_points |  INTEGER |" + colour.END)
    print("|    |   school    |   TEXT   |")
    print(colour.UNDERLINE + "|    |    rank     |  INTEGER |\n" + colour.END)

def check_window_width():
    # Function inputs: none
    # Function purpose: to check the width of the terminal window and print a warning if it is too small
    # Function returns: none
    # Function prints: a warning if the terminal window is too small
    width = shutil.get_terminal_size()[0] # getting the terminal size
    # shutil.get_terminal_size() returns a tuple with the height and width of the terminal window
    if width < 120: # if it isn't wide enough 
        print(colour.RED + "Your window size may be too small for the content displayed.") # print warning
        print("Please resize your window." + colour.END)

# MAIN CODE __________________________________________________________________
check_window_width() # checking the window width
while True: # Initial authentication loop
    try: # protecting against rogue inputs
        username = getpass.getpass("username: ") # using getpass
        password = getpass.getpass("password: ")
    except: # catching errors
        # the error could be when forcing str type
        print(colour.RED + "Error\n" + colour.END)
    login = authenticate_user(username, password) # using authenticate_user
    if login == 1: # if the user has normal access (value returned by authenticate_user)
        print(colour.GREEN + "Login succeded, you have admin privileges.\n" + colour.END)
        break # break the authentication loop
    elif login == 2: # if the user has root access 
        print(colour.GREEN + "Login succeeded," + colour.RED + " you have root priviliges.\n" + colour.END)
        break # break the authentication loop
    else:
        continue # continue the authentication loop

print(colour.BOLD + "Welcome!" + colour.END) # WELCOME!!!!!!!!!!!!!!!!!
while True: # Main menu (also a loop)
    time.sleep(0.7) # this time delay has been shown to improve user experience
    # printing out the menu
    print("\n----------------------------------------------")
    print("1 - View all contestants")
    print("2 - Search for a username or real name to see user details")
    print("3 - Enter a custom SQL query (root access required)")
    print("4 - View the overall ranking by total score")
    print("5 - View the ranking by score on a specific question")
    print("6 - View the internal ranking of a chosen school")
    print(colour.PURPLE + "\nPress press " + colour.BOLD + "q" + colour.END + colour.PURPLE + " to exit" + colour.END)
    check_window_width()
    print("----------------------------------------------\n")
    choice = input(": ") # taking the user's choices
    if choice == "1": # if the user wants to view all contestants
        print_all_contestants()
    elif choice == "2": # if the user wants to search for a specific contestant
        search_username() # first search username to get a list of results 
        for user in resultsList: # then run individual_score for each contestant in the results list
            individual_score(user) # this gets the detailes of each contestant 
        resultsList = [] # clearing the results list 
    elif choice == "3": # if the user wants to run a custom query
        if root_user_authentication(): # root authentication required 
            custom_query()
    elif choice == "4": # if the user wants to view the overall ranking by total score
        rank_by_total_score()
    elif choice == "5": # if the user wants to view the ranking by score on a specific question
        rank_by_question_score()
    elif choice == "6": # if the user wants to view the internal ranking of a chosen school
        rank_inside_school()
    elif choice == "q" or choice == "Q" or choice == "q " or choice == "Q ": # if the user wants to exit
        print(colour.DARKCYAN + "\n\nHow was your experience of this application? Your feedback will be sincerely appreciated. \nContact: 22343@burnside.school.nz\n\n\n\n")
        # feedback is always nice 
        break # break the main menu loop to exit 