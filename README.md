# Query Firmware Project
## MatthewKim

This project created a Django webapp that allows user to query firmware data from a MongoDB server and then modify the data on an AWS S3 server. The web app also implements a user authentication API with a login and signup page.

## Usage

To use the querying feature, the user must login and go to /selectApp/query/. The user then must type in the firmware model string and can choose whether to furhter specify the query by selecting a type or sorting the results by time.

## Input/Output Format

The model string textbox input must be a string, and the user can select any item from the selecting type or sorting by time dropdown boxes.

The output will be organized into four columns where each column represents a field, and each row represents one document.