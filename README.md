# DjangoUsers
A simple user creation and search API with Admin Interface

Requirements:

1. Python2
2. Django version <2 -- pip install django==1.11
3. Pillow module for ImageField -- pip install Pillow
4. pip install future

Steps to install.
1. Clone the Directory.
2. run migrate.sh (Please give execution permissions to this file (chmod +x migrate.sh))
3. Ready to USE -- python manage.py runserver

Admin User:
username: flo
password: asdf1234

API's
1. /user/create/
2. /login/
3. /user/search/ (optional params status,company)
4. /logout/

Stats to be viewed in Admin Panel Under "Search Summary".

Details about API:
1. /user/create/
   Method: POST
   Request Body: {"username":<username>, "password": <password>, "email":<email>, "first_name":<first_name>,
                  "last_name": <last_name>, "phone":<phone>, "company":<companyname>, "position": <position>}
   Response:
   a. Success:
      {"status": "success", "message": "(Created new user <username>) or (User details updated for username(except passwrod))"}
   b. Failure:
      {"status": "error", "message": <errorString>}
2. /login/
   Method: POST
   Request Body: {"username":<username>, "password":<password>}
   Response:
   a. Success:
      {"status":"success", "message": "User is Logged in. Username:<username>"}
   b. Failure:
      {"status": "error", "message": <errorString>}
   
3. /user/search/
   Method: GET
   Parameters:
    a. status -- active,inactive,archived
    b. company -- <company name>
   Sample Response:
   api: /users/search/?company=new
   {
    count: 1,
    users: [
      {
        username: "firstuser",
        user_status: "active",
        first_name: "",
        last_name: "",
        company: "New Company 1",
        phone: "",
        position: "" ,
        email: "firstuser@gmail.com"
      }
    ]
   }
 
 4. /logout/
    Method: GET
    Response:
    {
    "status": "success",
    "message": "Successfully Logged out user:<username>"
    }
