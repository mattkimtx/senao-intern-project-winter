from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import os

load_dotenv()

# Create a connection with the MongoDB database and define functions for MongoDB
class mongoHelper:
     def __init__(self):
          secret = os.environ.get("CONNECTION_STRING")
          MONGO_DB = os.environ.get("MONGO_DB_NAME")
          self.client = MongoClient(host=secret, directconnection=True)
          self.db = self.client["cloud6_intern"]

     # return collection name
     def get_collection(self, collection_name):     
          return self.db[collection_name]
     
     # close the mongoDB connection
     def close(self):
          self.client.close()

     # query all firmware document fields using the mongoDB document's ID.
     def get_doc_with_id(self, id):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_FW")
          fw_col = self.db.get_collection(COLLECTION_NAME)
          fields = {
               "_id": 1,
               "platform": 1,
               "version": 1,
               "is_latest": 1,
               "is_previous": 1,
               "file_key": 1,
               "model": 1,
               "type": 1,
               "created_time": 1,
               "modified_time": 1,
          }
          # convert parameter "id" from string to BSON.
          document_id = ObjectId(id)
          # find the firmware document in MongoDB
          fw_doc = fw_col.find_one({"_id": document_id}, fields)
          # check if doc exists and the file key exists
          if fw_doc and "file_key" in fw_doc:
               return fw_doc
          else:
               print("document not found or id incorrect")
               return None
     
     # query firmware "model" field using the mongoDB document's ID.
     def get_model_with_id(self, id):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_FW")
          fw_col = self.db.get_collection(COLLECTION_NAME)
          fields = {
               "_id": 1,
               "model": 1,
          }
          # convert parameter "id" from string to BSON.
          document_id = ObjectId(id)
          # find the document
          fw_doc = fw_col.find_one({"_id": document_id}, fields)
          # check if doc exists and the file key exists
          if fw_doc and "model" in fw_doc:
               model = str(fw_doc["model"])
               return model
          else:
               print("document not found or id incorrect")
               return None
     
     # query firmware documents and filter by the following fields: "model", "type", and "platform".
     def get_docs_from_model(self, model, type, platform, is_latest, is_previous):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_FW")
          fw_col = self.db.get_collection(COLLECTION_NAME)
          
          # case: deleting document that is the latest version. Will update is_previous to the new is_latest and select a new document to be is_previous
          if is_latest == True and is_previous == False:
               previous_doc = fw_col.find_one({"model": model, "type": type, "platform": platform, "is_previous": True})
               
               # check if there exists a previous version
               if previous_doc  == None:
                    print("mongo.py: no previous document found, returning None")
                    return None
               # update previous_doc to now be is_latest = True
               previous_doc["is_latest"] = True
               previous_doc["is_previous"] = False
               fw_col.update_one({"_id": previous_doc["_id"]}, {"$set": previous_doc})
               # query to find the new is_previous document, sorts by "version" field
               previous_doc_sort = fw_col.find({"model": model, 
                                               "type": type, 
                                               "platform": platform, 
                                               "is_previous": False, 
                                               "is_latest": False}).sort("version", -1).limit(1)
               
               # check if there exists a previous version
               if previous_doc_sort == None:
                    print("mongo.py: no new previous document found, returning None")
                    return None
               previous_new_version_str = next(previous_doc_sort, None)["version"]
               previous_doc_new = fw_col.find_one({"model": model, "type": type, "platform": platform, "version": previous_new_version_str})
               # update previous_doc_new to now be is_previous = True
               previous_doc_new["is_latest"] = False
               previous_doc_new["is_previous"] = True
               fw_col.update_one({"_id": previous_doc_new["_id"]}, {"$set": previous_doc_new})
               return fw_col.find_one({"model": model, "type": type, "platform": platform, "is_latest": True})
          
          # case: deleting document that is the previous version, no latest exists
          if is_latest == False and is_previous == True:
               version_recent = fw_col.find({"model": model, 
                                               "type": type, 
                                               "platform": platform, 
                                               "is_previous": False, 
                                               "is_latest": False}).sort("version", 1).limit(1)
              
               # check if there exists a previous version
               if version_recent == None:
                    print("mongo.py: no new previous document found, returning None")
                    return None
               version_previous_new = next(version_recent, None)["version"]
               previous_new = fw_col.find_one({"model": model, "type": type, "platform": platform, "version": version_previous_new})
               # update new version of previous to is_previous = True
               previous_new["is_latest"] = False
               previous_new["is_previous"] = True
               fw_col.update_one({"_id": previous_new["_id"]}, {"$set": previous_new})
               # return updated previous version
               return fw_col.find_one({"model": model, "type": type, "platform": platform, "is_previous": True})

     # deletes the firmware document using the mongoDB document's ID.
     def delete_with_id(self, id):
          COLLECTION_NAME = os.environ.get("MONGO_COLLECTION_FW")
          fw_col = self.db.get_collection(COLLECTION_NAME)
          # make ID back into a BSON file
          document_id = ObjectId(id)

          # check to make sure more than 2 documents exist for the same model, type, and platform
          document = fw_col.find_one({"_id": document_id})
          model = document["model"]
          type = document["type"]
          platform = document["platform"]
          # count how many documents exist for the same model, type, and platform
          count = fw_col.count_documents({"model": model, "type": type, "platform": platform})
          # if there are only 2 documents, return "only two documents"
          if count <= 2:
               return False
          # if there are more than 2 documents, delete the document
          else: 
               try:
                    fw_col.delete_one({"_id": document_id})
                    return True
               except:
                    return False
          

# creates a list that will be used to create a table on the index.html page
def cleanOutput(input):
     id = input["_id"]
     type = input["type"]
     model = input["model"]
     platform = input["platform"]
     created_time = input["created_time"]
     modified_time = input["modified_time"]

     # attempting to return a list instead of a string to make columns
     output = [id, model, type, platform, created_time, modified_time]

     return output
