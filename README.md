# This project has been created with the specifications of CS50 2018 project 1


Web Programming with Python and JavaScript

1: Hello I have named my Web app KITAB-SAMEEKSHA which means BOOK-REVIEW in 
Hindi language which is the language of my Country India.
2:In the TEMPLATES folder you will find all HTML code webpages and inside the
TEMPLATES folder there is also one INCLUDES folder which has the code for alert messages.
3:In Flask_sessions folder all the flask sessions cache is stored.
4: application.py is the main file and I have also include the import.py file
which imports the books to the database.
5:My Web-APP's functionality is exactly designed as per the requirement.

Below i have mentioned the SQL code and the environment variables that I had det



please refer this to create sql tables and to set necessary env variables


###############SQL TABLES################################
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
     year VARCHAR NOT NULL
);


CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    isbn VARCHAR NOT NULL,
    rating INTEGER NOT NULL,
    comments VARCHAR NOT NULL	
);
#######################################################


###########environment variables###################
DATABASE_URL=[Your URL]
FLASK_APP=application.py
FLASK_DEBUG=1
###################################################
