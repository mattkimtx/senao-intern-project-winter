from dotenv import load_dotenv
from pymongo import MongoClient
from api_account_password.mongo import cleanOutput, mongoDB
import S3Bucket.bucket
import api_account_password.mongo
import os

load_dotenv

def query_sort(model, type, time):
     secret = os.environ.get("CONNECTION_STRING")
     client = MongoClient(host=secret, directconnection=True)
     dbName = os.environ.get("MONGO_DB_NAME")
     colName = os.environ.get("MONGO_COLLECTION_FW")

     # select fields from MongoDB to be returned
     fields = {
          "_id": 1,
          "model": 1,
          "type": 1,
          "platform": 1,
          "created_time": 1,
          "modified_time": 1,
     }

     db = client[dbName]
     collection = db[colName]
     
     # returns all data
     if type == "none" and time == "none" and model == "":
          query_result = collection.find({}, fields)
     # this is to sort the data by time and also limit data to certain qualities.
     elif type == "none" and time == "none" and model != "":
          query_result = collection.find({"model": model}, fields)
     # type selected but not time, so show all of the times sorted by type
     elif type != "none" and time == "none":
          # if model is empty
          if model == "":
               query_result = collection.find({"type": type}, fields)
          else:
               query_result = collection.find({"model": model, "type": type}, fields)
     # time selected but not type, so show all of the types sorted by time
     elif type == "none" and time != "none":
          if model == "":
               if time == "ctasc":
                    query_result = collection.find({}, fields).sort("created_time", 1)    
               if time == "ctdec":
                    query_result = collection.find({}, fields).sort("created_time", -1)
               if time == "mtasc":
                    query_result = collection.find({}, fields).sort("modified_time", 1)
               if time == "mtdec":
                    query_result = collection.find({}, fields).sort("modified_time", -1)
          else:
               if time == "ctasc":
                    query_result = collection.find({"model": model}, fields).sort("created_time", 1)
               if time == "ctdec":
                    query_result = collection.find({"model": model}, fields).sort("created_time", -1)
               if time == "mtasc":
                    query_result = collection.find({"model": model}, fields).sort("modified_time", 1)
               if time == "mtdec":
                    query_result = collection.find({"model": model}, fields).sort("modified_time", -1)
     else:  # all are selected, so we must sort by time
          if model == "":     
               if time == "ctasc":
                    query_result = collection.find({"type": type}, fields).sort("created_time", 1)
               if time == "ctdec":
                    query_result = collection.find({"type": type}, fields).sort("created_time", -1)
               if time == "mtasc":
                    query_result = collection.find({"type": type}, fields).sort("modified_time", 1)
               if time == "mtdec":
                    query_result = collection.find({"type": type}, fields).sort("modified_time", -1)
          else:
               if time == "ctasc":
                    query_result = collection.find({"model": model, "type": type}, fields).sort("created_time", 1) # sorting created_time by ascending
               if time == "ctdec":
                    query_result = collection.find({"model": model, "type": type}, fields).sort("created_time", -1)
               if time == "mtasc":
                    query_result = collection.find({"model": model, "type": type}, fields).sort("modified_time", 1)
               if time == "mtdec":
                    query_result = collection.find({"model": model, "type": type}, fields).sort("modified_time", -1)

     # turn collection dictionary into list that is easier to read
     list = []
     for x in query_result:
          converted_data = cleanOutput(x)
          list.append(converted_data)
     all_data = {'list': list, 'query': model, 'type': type, 'time': time}

     return all_data

def query_delete(object_id, mdb):
     # create objects to connect to S3
     bucket = S3Bucket.bucket.Bucket()

     # variable to check if exists in bucket
     bucket_exist = False

     # getting mongoDB document from object_id using function in mongo.py
     document = mdb.get_doc_with_id(object_id)
     if document == None:
          print("document not found")
          return False

     file_key = str(document["file_key"])
     is_latest = document["is_latest"]
     is_previous = document["is_previous"]

     # cases for deleting files...
     ### does not exist in bucket
     try:
          if bucket.object_exists(file_key) == True:
               bucket_exist = True
     # when throwing error since bucket is not existing
     except:
          print("file not found in bucket")
          if mdb.delete_with_id(object_id) == True:
               print("document deleted from mongoDB")
          else:
               print("error deleting doc in mongoDB")
          # returning false bc objectdoes not exist in S3 bucket
          return False

     ### case for both False, can delete without modifying
     if is_latest == False and is_previous == False:
          # delete file in bucket
          if bucket_exist == True:
               bucket.delete_fk(file_key)
               print("file deleted from bucket")
          else:
               print("file not found in bucket")
               return False
          # delete document in mongoDB
          mdb.delete_with_id(object_id)
          print("document deleted from mongoDB")
          return True
     
     ### case for latest is true, need to set a new Firmware as "is_latest == True"
     elif is_latest == True and is_previous == False:
          return False
     
     ### case for is previous is True, do not need to worry
     elif is_latest == False and is_previous == True:
          return False
     
     ### case for both are True, need to set a new Firmware as "is_latest == True", otherwise this is the last firmware data for the model
     elif is_latest == True and is_previous == True:
          return True
     
     ### In case some other type of data besides "True" or "False" is read
     else:
          print("error deleting file")
          return False