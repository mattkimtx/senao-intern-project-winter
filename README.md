# Title: Query Firmware Project Using MongoDB and S3 Bucket
## Contributors: Matthew Kim

## Description

#### What this application does
This project created a Django webapp that allows user to query firmware data for routers, switches, and access points on a MongoDB server and then deleted selected firmware versions on a separate AWS S3 server. Users will be able to query firmware data based on the following fields: `Model` (String), `Type`, and `Time`. While `Model` will be queried by typing a string, `Type` and `Time` will have dropdown menus where Type will choose from `alpha`, `beta`, or `release` and Time will choose from `ascending` or `descending` created time and modified time. 

This web application also implements a user authentication API with a login and signup page. When first opening the site at `localhost`, `http://127.0.0.1:8000`, or an additional chosen address, the user will be directed to a page where you can choose to login or create an account. This application will require the user to sign in to access the querying webpage, and the application will log out the user if they have been inactive for 15 minutes, or have clicked log out during their session.

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

## Usage: Login and Create Account
To use the querying feature, the user must login or create an account. This project uses an account creation and verification API.

#### Login/Verify Account
The user must only input uppercase and lowercase letters and numbers for the `username` and `password` fields. The `username` and `password` fields also require a minimum length of three and eight characters respectively. If the user fails to type in the correct password five times, the user will be unable to login for one minute, and the API will return an appropriate status code through HTTP.

#### Creating Account
Like logging in, the user must only input uppercase and lowercase letters and numbers for the `username` and `password` fields. The `username` and `password` fields also require a minimum length of three and eight characters respectively, and they both have a maximum length of 32 characters. The `password` has an additonal requirement where it must contain at least one uppercase letter, one lowercase letter, and one number. If any of these requirements are not met, the user will have to try again.

## Query: Input/Output Format
The model string textbox input must be a string, and the user can select any item from the selecting type or sorting by time dropdown boxes.

The output will be organized into seven columns where the first six columns represent fields, and each row represents one document. The last column contains the delete button for the document. If the user deletes a document, the page will refresh and display the remaining firmware versions of the same `model` name, and if there are no other matching `model` names remaining, there will be no output.