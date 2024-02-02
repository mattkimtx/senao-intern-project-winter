# Title: Query Firmware Project Using MongoDB and S3 Bucket
## Contributors: Matthew Kim

## Description

#### What this application does
This project created a Django webapp that allows user to query firmware data for routers, switches, and access points on a MongoDB server and then deleted selected firmware versions on a separate AWS S3 server. Users will be able to query firmware data based on the following fields: `Model` (String), `Type`, and `Time`. While `Model` will be queried by typing a string, `Type` and `Time` will have dropdown menus where Type will choose from `alpha`, `beta`, or `release` and Time will choose from `ascending` or `descending` created time and modified time. Access to the querying page will be restricted to users who have active login sessions.

#### Technologies Used
- This project uses the program languages Python3 and HTML/CSS as well as JSON scripts.
- This project was made to run in a Linux System (in this case, Ubuntu).
- Built using `Django` web framework
- `MongoDB`, storing firmware data as documents
- `AWS S3 Bucket`, storing the firmware files 

## Setup
The first step is to clone the repository and cd into the project:

```sh
$ git clone https://github.com/mattkimtx/senao-mongo-bucket.git
$ cd senao-mongobucket
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python -m env /path/to/new/virtual/environment
$ source env/bin/activate
```

Install dependencies:
Note the `(env)` in front of the prompt. This indicates we have activated
the python virtual environment seen in the previous step.

```sh
(env)$ pip install -r requirements.txt
```

Once `pip` has finished downloading the dependencies:
```sh
(env)$ cd mongoBucket
(env)$ python manage.py runserver
```
Now open your browser and access `http://127.0.0.1:8000/`.

If you would like to change the IP address for running the website, go to senao-mongo-bucket/mongoBucket/mongoBucket/settings.py and change the following code.
```
ALLOWED_HOSTS = ['localhost', '127.0.0.1', <your_desired_ip_address>]
```
To change the desired port, navigate to the project's root directory (the one with manage.py) and run the following command
```sh
$ python manage.py runserver <your_desired_port>
```

#### Usage: Login and Create Account
To use the querying feature, the user must login or create an account. This project uses an account creation and verification API.

#### Login/Verify Account (./api_account_password)
The user must only input uppercase and lowercase letters and numbers for the `username` and `password` fields. The `username` and `password` fields also require a minimum length of three and eight characters respectively. If the user fails to type in the correct password five times, the user will be unable to login for one minute, and the API will return an appropriate status code through HTTP.

The login session data is also tracked within my code where I attach a cookie holding a `session_token` which is a 16 byte hexadecimal string (`secrets.token_hex(16)`). This cookie then gets stored into the MongoDB `users` database and inserted into the document that hold's the user's login information. When the user clicks logout, the `session_token` is then removed from the user's document.

#### Creating Account
Like logging in, the user must only input uppercase and lowercase letters and numbers for the `username` and `password` fields. The `username` and `password` fields also require a minimum length of three and eight characters respectively, and they both have a maximum length of 32 characters. The `password` has an additonal requirement where it must contain at least one uppercase letter, one lowercase letter, and one number. If any of these requirements are not met, the user will have to try again.

#### User Authentication Backend (./account/backend.py)
This web application also implements a user authentication API with a MongoDB backend and uses Django's authentication API `django.contrib.auth`. When first opening the site at `localhost`, `http://127.0.0.1:8000`, or an additional chosen address, the user will be directed the login page. I have created an extra python file (`backend.py`) with the `MyBackend` class and an `authenticate` method. This method calls methods in `mongo.py` to verify the account information. The `authenticate` method is called within `act_pw_api.py`.

#### Query: Input/Output Format
The model string textbox input must be a string, and the user can select any item from the selecting type or sorting by time dropdown boxes.

#### MongoDB: Indexes
Although it is not visible in the code, I have set up indexes in MongoDB to optimize querying speeds for larger volumes of data. This will be particularly helpful for expanding the website to potentially thousands of users and potentially even more firmware data. I created an index for each firmware model and for each user's username. I have also added a TTL index for the `failed_login` database because I do not want to store every single failed_login. This strategy also helps tracking failed logins and user information because it will automatically return how many documents there are within X seconds rather than my current strategy of counting the last 5 failed tries and calculating how recent they are.

## Assumptions
- When decided to choose a new `is_previous` firmware version, we assume that we used the most recent firmware version. For example, if we were removing firmware version `v1.1`, we would find the closest previous version, `v1.0`, the new `is_previous` rather than another version such as `v0.5`.
- We assume that the firmwares documents stored in MongoDB and in the S3 bucket do not have the following values: `is_previous` = `True` and `is_latest` = `True`.

The output will be organized into seven columns where the first six columns represent fields, and each row represents one document. The last column contains the delete button for the document. If the user deletes a document, the page will refresh and display the remaining firmware versions of the same `model` name, and if there are no other matching `model` names remaining, there will be no output.

## Potential Improvements
In my code, there are a lot of opportunities for more clear variable naming and more clear coding overall. I think my selectApp/views.py represents what I want my code to look like, but the reality is represented in selectapp/query_edit.py. There, my query_sort and query_delete has a lot of `if statements that I can turn into separate smaller functions.

#### Improvement with login
When logging in, I create a session token by creating a 16 byte hex string and store it in the account database in MongoDB. While this conveniently combines tracking login data with user information, it does not protect against a user closing the webpage and then reopening it later (or potentially a lot later). If I had more time, I would adapt my MongoDB storing failed logins to store all login information there and add an index with a TTL that automatically deletes a user's session after X amount of seconds (probably 3600 for 1 hour).