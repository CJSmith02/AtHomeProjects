"""
TODO:
- encrypted passwords to file

@author: Caleb Smith
"""
SIGN_IN_STR = ' last signed in at:'
SIGN_OUT_STR = ' last signed out at:'
TOTAL_TIME_STR = ' Total Time Signed in: '
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
USER_STATE_STR = ' is signed in?: '


from datetime import datetime, timedelta
import json
import copy
from cryptography.fernet import Fernet

class JsonDict:
    def __init__(self, json_path, default_dict):
        """retrieve saved dictionaries, else create the default"""
        self.path = json_path      
        try:
            with open(self.path,'r') as f:
                self.info = json.load(f)
        except FileNotFoundError:
            self.info = default_dict
            self.save()
    
    def save(self):
        with open (self.path, 'w') as f:
            json.dump(self.info,f)
            
            
class DataBase(JsonDict):
    def __init__(self, json_path, default_dict):
        
    
    
    def authenticate(self, key, value):
        success = False
        if key in self.info:
            success = (self.info[key] == value)
        return success
    
    def show_keys (self):
        dict_keys = self.info.keys()
        dalist = 'keys in dictionary:'
        for key in dict_keys:
            dalist = dalist + '\n' + key
        return dalist
    
    def add_key (self, key, value):
        if not key in self.info:
            self.info[key]= value
            self.save()
            return "success!"
        else:
            return "That username already exists. Choose a new one."
    
    def remove_key (self, key):
        del self.info[key]
        self.save()
        return "success!"
        
    def change_value(self,key, newvalue):
        if key in self.info:
            self.info[key] = newvalue
            self.save()
            return "success!"
        else:
            return "That key dosen't exist. Try making it"
        
    def save(self):
        fer = Fernet(key)
        saved_users = copy.copy(self.info)
        for user in saved_users:
            #encrypt password (turn it to bytes, encrypt it)
            saved_users[user] = fer.encrypt(saved_users[user].encode())
            #encrypt username
            user = fer.encrypt(user.encode())
        with open (self.path, 'w') as f:
            json.dump(saved_users,f)


class Timer(JsonDict):
    def add_key(self, username):
        self.info[username + SIGN_IN_STR] = None
        self.info[username +SIGN_OUT_STR] = None
        self.info[username + TOTAL_TIME_STR] = "0:00:00"
        self.info[username + USER_STATE_STR] = False
        self.save()
        return "user successfully initialized in system."    
    
    def remove_key(self, username):
        del self.info[username + SIGN_IN_STR]
        del self.info[username +SIGN_OUT_STR]
        del self.info[username + TOTAL_TIME_STR]
        del self.info[username + USER_STATE_STR]
        self.save()
        return "user information deleted from system."   
    
    def check_signed_in(self, username):
        return  self.info[username + USER_STATE_STR]
        
    def sign_in(self, username):
        #if they're already signed in
        self.info[username + SIGN_IN_STR] = datetime.now().strftime(
                                                            DATETIME_FORMAT)
        self.info[username + USER_STATE_STR] = True
        self.save()
        return "success!"
        
    def sign_out(self, username):
        if self.info[username + USER_STATE_STR]: 
            #user signed in
            self.info[username + SIGN_OUT_STR] = datetime.now().strftime(
                                                        DATETIME_FORMAT)
            self.log_total_time(username)
            self.info[username + USER_STATE_STR] = False
            self.save()
            return "success!"
        else:
            return "you have to be signed in to sign out."
            
    def log_total_time (self, username): 
        sign_in_time = self.info[username + SIGN_IN_STR]
        sign_out_time = self.info[username + SIGN_OUT_STR]
        diff = self.subtract_time(sign_out_time, sign_in_time)
        prior_total = self.str_to_timedelta(
            self.info[username + TOTAL_TIME_STR])
        self.info[username + TOTAL_TIME_STR] = str(diff + prior_total)

    def get_total_time(self, username):
        if self.info[username + USER_STATE_STR]:
            warning='consider signing out for an updated total time'
        else:
            warning = ''
        return "{}\n{}".format(self.info[username + TOTAL_TIME_STR], warning)

    def subtract_time(self, newer_time, older_time):
        diff = datetime.strptime(newer_time, DATETIME_FORMAT) \
               - datetime.strptime(older_time, DATETIME_FORMAT)
        # diff is in a 'timedelta' datatype, which dosen't print to a JSON
        return diff
    
    def str_to_timedelta(self, s):
        """take a timedelta that was a string back"""
        try: 
            t = datetime.strptime(s,"%H:%M:%S")
            return timedelta( hours=t.hour, minutes=t.minute,
                             seconds=t.second)
        except ValueError:
            # if signed in for multiple days. longer than that is not supported
            t = datetime.strptime(s,"%d days, %H:%M:%S")
            #the returns CANNOT be combined because otherwise timedelta 
            #inherits a 1 day from the default time
            return timedelta(days = t.day, hours=t.hour, minutes=t.minute,
                             seconds=t.second)
   
    def get_all_attributes(self, key):
        dalist = "User      :{} \n".format(key)
        #to make temp_users a seperate object that's not bound
        temp_users = copy.copy(users.info)
        del temp_users['admin']
        for user in temp_users:
            dalist = "{}{:10}: {}\n".format(dalist,
                user, timesheet.info[user + key])
        del temp_users
        return dalist
    

def main():
    finished = False
    while not finished:
        username = input('username: ')
        password = input('password: ')
        if users.authenticate(username, password):
            print('Access Granted')
            if username == 'admin': 
                print("As Admin, would you like to 'show users','add user',",
                    "'remove user', 'change password', 'get all times',",
                    " or 'get all user states', or 'nothing'?")
                adminAction = input('admin action: ').lower()
                if adminAction == 'add user':
                    new_username= input("New Username: ")
                    print(users.add_key(new_username,
                        input("New Password: ")))
                    print(timesheet.add_key(new_username))
                elif adminAction == 'remove user':
                    former_username = input("Username to remove: ")
                    if input("are you sure? ") == 'yes':
                        print(users.remove_key(former_username))
                        print(timesheet.remove_key(former_username))
                elif adminAction == 'show users':
                    print (users.show_keys())
                elif adminAction == 'change password':
                    print(users.change_value(input("which username? "),
                        input('new password: ')))
                elif adminAction == 'get all times':
                    print(timesheet.get_all_attributes(TOTAL_TIME_STR))
                elif adminAction == 'get all user states':
                    print(timesheet.get_all_attributes(USER_STATE_STR))
                else:
                    print("that wasn't a recognized admin action. Try again.")
                    
            else:
                #everyone else does this:          
                print("Would you like to 'change password', 'sign in',",
                      "'sign out','get total time', or 'nothing'?")
                userAction = input('user action: ')
                if userAction == 'change password':
                    print(users.change_value(username, input('new password: ')))
                elif userAction == 'sign in':
                    if timesheet.check_signed_in(username): 
                        print("You're already signed in.")
                        if input("Want to sign in anyway? (yes/no) ").lower() == 'yes':
                            print(timesheet.sign_in(username))   
                        else:
                            print("ok. You weren't signed in")
                    else:
                        print(timesheet.sign_in(username))
                elif userAction == 'sign out':
                    print(timesheet.sign_out(username))
                elif userAction == 'get total time':
                    print(timesheet.get_total_time(username))
                else:
                    print("that wasn't a recognized action. Try again.")
            
        else: 
            print("Access Denied. Wrong username and/or password.")
        finished = (input("Are you done with me? (yes/no): ").lower() == 'yes')
    print('Goodbye!')
    
users = DataBase("users.json", default_dict = {'admin':'admin',})
timesheet = Timer("timesheet.json", 
                  default_dict = {'file created': datetime.now().strftime(
                                                          DATETIME_FORMAT),})

#Start automatically

main()