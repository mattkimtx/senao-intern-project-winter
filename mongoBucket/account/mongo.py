from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import timedelta
from .bcrypt import hash_password, verify_password
import os
import time

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
          user_col.insert_one({"user": username, "password": hash_pass, "session_token": ""})
     
     # Counts failed login attempts
     def failed_login(self, username, timestamp):
          # get both collections from the database
          fail_col = self.db.get_collection("failed_login")
          # get account and update the failed login
          fail_col.insert_one({"user": username, "timestamp": timestamp})

     # flaw in design, it uses timezone of the user. what happens when 2+ people with same account log in from different timezones?
     def check_failed_login_attempts(self, username, timestamp):
          login_attempt_duration = timedelta(minutes=1)
          fail_col = self.db.get_collection("failed_login")

          # Use the index to filter failed attempts within the last minute
          query = {
               "user": username,
               "timestamp": {"$gt": timestamp - login_attempt_duration},
               "session_token": ""
          }
          count = fail_col.count_documents(query)

          # Check if there have already been too many attempts
          return count < 5
     
     # deletes the account
     def delete_account(self, username):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
          user_col = self.db.get_collection(COLLECTION_NAME)
          user_col.delete_one({"user": username})

     # checks if the session token exists
     def session_token_exists(self, session_token):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
          session_col = self.db.get_collection(COLLECTION_NAME)
          session = session_col.find_one({"session_token": session_token})
          return session is not None
          
     # creates a new session token
     def create_session_token(self, username, session_token):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
          session_col = self.db.get_collection(COLLECTION_NAME)
          try:
               start_start = time.time()
               session_col.update_one(
                    {"user": username},
                    {"$set": {"session_token": session_token}},
                    upsert=False
               )
               end_start = time.time()
               print("mongo.py: create_session_token time: " + str(end_start - start_start))
               return True  # Successfully created/updated the session token
          except Exception as e:
               print(f"Error creating session token: {str(e)}")
               return False  # Failed to create/update the session token
          
     # deletes the session token
     def delete_session_token(self, session_token):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_NAME")
          session_col = self.db.get_collection(COLLECTION_NAME)
          try:
               session_col.update_one({"session_token": session_token}, {"$unset": {"session_token": ""}})
               return True
          except Exception as e:
               print(f"Error creating session token: {str(e)}")
               return False  # Failed to create/update the session token