from django.shortcuts import render
from django.http import Http404
from dotenv import load_dotenv
from pymongo import MongoClient
from mongo import cleanOutput
import os

load_dotenv

def index(request):
     return render(request, 'selectApp/index.html')

# Create your views here.
def query(request):
     try:
          model = request.GET.get('q')
          type = request.GET.get('sortType')
          time = request.GET.get('sortTime')
          if model == "":
               message = "please enter a model"
               return render(request, 'selectApp/index.html', {'no_input': message})
          else:
               secret = os.environ.get("CONNECTION_STRING")
               client = MongoClient(host=secret, directconnection=True)
               dbName = os.environ.get("MONGO_DB_NAME")
               colName = os.environ.get("MONGO_COLLECTION_FW")

               # select fields from MongoDB to be returned
               fields = {
                    "_id": 0,
                    "model": 1,
                    "type": 1,
                    "created_time": 1,
                    "modified_time": 1,
               }

               db = client[dbName]
               collection = db[colName]
               
               # this is to sort the data by time and also limit data to certain qualities.
               if type and time == "none":
                    query_result = collection.find({"model": model}, fields)
               elif type != "none selected" and time == "none selected":
                    query_result = collection.find({"model": model, "type": type}, fields)
               else:  # all are selected, so we must sort by time
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

               # Render the template with the data)
               return render(request, 'selectApp/index.html', all_data)
     
     except:
          # Handle exceptions (e.g., connection errors)
          raise Http404("No data found")
