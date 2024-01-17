from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from dotenv import load_dotenv
from .query_edit import query_sort, query_delete
from api_account_password.mongo import cleanOutput, mongoDB
import api_account_password.mongo
import os

load_dotenv

def index(request):
     # verify the user has logged in
     return render(request, 'selectApp/index.html')

# query and sort FW data
def query(request):
     try:
          model = request.GET.get('q')
          type = request.GET.get('sortType')
          time = request.GET.get('sortTime')
          # select fields from MongoDB to be returned
          all_data = query_sort(model, type, time)
          # Render the template with the data)
          return render(request, 'selectApp/index.html', all_data)
     
     except:
          # Handle exceptions (e.g., connection errors)
          raise Http404("No data found")

# delete firmware data
def delete(request):
     try:
          if request.method == 'POST':
               # Get the item_data from the POST request
               item_data = request.POST.get('item_data')
               object_id = item_data.strip("[]").split(',')[0].strip()
               # remove "object_id" from the string
               object_id = object_id.replace("ObjectId('", "").replace("')", "")
               # using function from query_edit.py to delete the data from mongoDB and S3
               mdb = api_account_password.mongo.mongoDB()
               # To return the model
               model = mdb.get_model_with_id(object_id)
               result = query_delete(object_id, mdb)
               # query delete successfuly ran
               if result == True:
                    print("successful")
                    # print out all data again
                    all_data = query_sort("", "none", "none")
                    return render(request, 'selectApp/index.html', all_data)
               if result == False:
                    print("successful, but S3 object does not exist")
                    # if model exists, display other models that exist
                    all_data = query_sort(model, "none", "none")
                    # add error message to all_data
                    all_data["no_input"] = "S3 object does not exist, but document deleted from MongoDB."
                    return render(request, 'selectApp/index.html', all_data)
          else:
               # Handle GET requests or other cases
               return HttpResponse('Invalid request method')
     except Exception as e:
          # Handle exceptions (e.g., connection errors)
          print(f"An error occurred: {str(e)}")  # Print the error for debugging
          return HttpResponse('An error occurred')