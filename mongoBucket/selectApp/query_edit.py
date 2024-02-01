from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from .mongoHelper import mongoHelper, cleanOutput
import S3Bucket.bucket
import os

load_dotenv

def query_sort(model, type, time):
     # return all_data
     secret = os.environ.get("CONNECTION_STRING")
     client = MongoClient(host=secret, directconnection=True)
     dbName = os.environ.get("MONGO_DB_NAME")
     colName = os.environ.get("MONGO_COLLECTION_FW")

     # Define the fields to be returned
     fields = {
          "_id": 1,
          "model": 1,
          "type": 1,
          "platform": 1,
          "created_time": 1,
          "modified_time": 1,
     }

     db = client[dbName]
     collection: Collection = db[colName]

     # Define the filter criteria based on the input parameters
     filter_criteria = {}

     if model:
          filter_criteria["model"] = model

     if type != "none":
          filter_criteria["type"] = type

     if time != "none":
          sort_field = "created_time" if time.startswith("ct") else "modified_time"
          sort_order = 1 if time.endswith("asc") else -1

          # Sort by the specified time field and order
          query_result: Cursor = collection.find(filter_criteria, fields).sort(sort_field, sort_order)
     else:
          # No time-based sorting
          query_result: Cursor = collection.find(filter_criteria, fields)

     # Convert the cursor to a list of cleaned data
     data_list = [cleanOutput(doc) for doc in query_result]

     all_data = {'list': data_list, 'query': model, 'type': type, 'time': time}

     return all_data

def query_delete(object_id, mdb, bucket):
     print(0)
     # variable to check if exists in bucket
     bucket_exist = False
     # getting mongoDB document from object_id using function in mongo.py
     document = mdb.get_doc_with_id(object_id)
     if document == None:
          print("document not found")
          return False
     file_key = str(document["file_key"])
     model = str(document["model"])
     fw_type = str(document["type"])
     fw_platform = str(document["platform"])
     is_latest = document["is_latest"]
     is_previous = document["is_previous"]

     ### Does not have enough firmware documents
     # check to see if it satisfies the condition of having 2 or less documents
     # very redundant, but need bc i am passing in mdb
     if mdb.count_documents_func(object_id) == True:
          print("2 or less firmware files found, cannot delete")
          return "few"
     
     ### does not exist in bucket
     try:
          if bucket.object_exists(file_key) == True:
               bucket_exist = True
     except:
          print("bucket does not exist")

     ### case for both False, can delete without modifying
     if is_latest == False and is_previous == False:
          # delete file in bucket (if it exists)
          if bucket_exist == True:
               bucket.delete_fk(file_key)
               print("file deleted from bucket")
          else:
               print("file not found in bucket")
               return False
          if mdb.delete_with_id(object_id) == True:
               print("document deleted from mongoDB")
               return True
          else:
               print("error deleting doc in mongoDB")
               return False
          
     ### case for latest is true, need to set a new Firmware as "is_latest == True"
     elif is_latest == True and is_previous == False:
           ### find documents that match model, type, and platform
          sorted_fw = mdb.get_docs_from_model(model, fw_type, fw_platform, is_latest, is_previous)
          if sorted_fw == None:
               print("query_edit.py: no documents found")
               return "error"
          ### delete from bucket
          if bucket_exist == True:
               bucket.delete_fk(file_key)
               print("file deleted from bucket")
          else:
               print("file not found in bucket")
          # delete document in mongoDB
          if mdb.delete_with_id(object_id) == True:
               print("document deleted from mongoDB")
               return True
          else:
               print("error deleting doc in mongoDB")
               return False

     ### case for is previous is True, do not need to worry
     elif is_latest == False and is_previous == True:
          sorted_fw = mdb.get_docs_from_model(model, fw_type, fw_platform, is_latest, is_previous) 
          print("new", sorted_fw["version"])
          if sorted_fw == None:
               print("query_edit.py: no documents found")
               return False
          # ### delete from bucket
          if bucket_exist == True:
               bucket.delete_fk(file_key)
               print("file deleted from bucket")
          else:
               print("file not found in bucket")
          # delete document in mongoDB
          if mdb.delete_with_id(object_id) == True:
               print("document deleted from mongoDB")
               return True
          else:
               print("error deleting doc in mongoDB")
               return False
     ### In case some other type of data besides "True" or "False" is read
     else:
          print("error deleting file")
          return False  