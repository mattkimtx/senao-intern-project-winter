from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import timedelta
from .bcrypt import hash_password, verify_password
import os

load_dotenv()

# Create a connection with the MongoDB database
class mongoDB:
     def __init__(self):
          secret = os.environ.get("CONNECTION_STRING")
          MONGO_DB = os.environ.get("MONGO_DB_NAME")
          self.client = MongoClient(host=secret, directconnection=True)
          self.db = self.client["cloud6_intern"]

     def get_collection(self, collection_name):     
          return self.db[collection_name]
     
     # close the mongoDB connection
     def close(self):
          self.client.close()

     # checks to see if the username exists in the database
     def user_exists(self, username):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
          user_col = self.db.get_collection(COLLECTION_NAME)
          account = user_col.find_one({"user": username})
          if account == None:
               return False
          else:
               return True
          
     # checks to see if the hashed password exists in the database
     def password_exists(self, username, password):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
          user_col = self.db.get_collection(COLLECTION_NAME)
          account = user_col.find_one({"user": username})
          if verify_password(password, account["password"]):
               return True
          else:
               return False
          
     # creates the new account (does not check if account was created)
     def create_account(self, username, password):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
          user_col = self.db.get_collection(COLLECTION_NAME)
          hash_pass = hash_password(password)
          user_col.insert_one({"user": username, "password": hash_pass})
     
     # Counts failed login attempts
     def failed_login(self, username, timestamp):
          # get both collections from the database
          fail_col = self.db.get_collection('failed_login')
          # get account and update the failed login
          fail_col.insert_one({"user": username, "timestamp": timestamp})

     # flaw in design, it uses timezone of the user. what happens when 2+ people with same account log in from different timezones?
     def check_failed_login_attempts(self, username, timestamp):
          counter = 0
          login_attempt_duration = timedelta(minutes=1)
          fail_col = self.db.get_collection('failed_login')
          # a list of failed attempts
          attempts = fail_col.find({"user": username})
          for attempt in attempts:
               # if the timestamp is within 1 minute of the current time, add to counter
               if (timestamp - attempt["timestamp"]) < login_attempt_duration:
                    counter += 1
               # if there have already been too many attempts
               if counter >= 5:
                    return False
          return True
     
     # deletes the account
     def delete_account(self, username):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
          user_col = self.db.get_collection(COLLECTION_NAME)
          user_col.delete_one({"user": username})