import os
from flask import Flask, session,request,logging,url_for,redirect,render_template,flash,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt
import psycopg2
import requests
#Things to remember from one apprute function to another approute function use session to store information

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
app = Flask(__name__)


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
conn = psycopg2.connect(
    """postgres://sjgcgjtvhpbxfb:92820b851bb466fd170a93afaadfe34271651c9016bb90f461fa0dbc7a7cbd64@ec2-34-224-229-81.compute-1.amazonaws.com:5432/debu8o94v5beh2"""
)
cursor=conn.cursor()
#Home page
@app.route("/")
def home():
    return render_template("home.html")
#register form
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        secure_password = sha256_crypt.encrypt(str(password))#password get encrypted

        if password == confirm:
            cursor.execute("INSERT INTO users (name,username,password) VALUES (%s,%s,%s)", (name,username,secure_password))
            conn.commit()

            flash("you have successfully registered and you can now login","success")
            return redirect(url_for('login')) #redirect is different from render template  redirect will give you /(name) of other page where as render_temp will give /(name) of the page where you are rendered
        else:
            flash("password does not match","danger")
            return render_template("register.html")
    return render_template("register.html")

#login page
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")

        cursor.execute("SELECT username FROM users WHERE username=%(username)s",{"username":username})
        username_data = cursor.fetchone()

        cursor.execute("SELECT password FROM users WHERE username=%(username)s",{"username":username})
        password_data = cursor.fetchone()

        if username_data is None:
            flash("Username does not exists","danger")
            return render_template("login.html")
        else:
            for x in password_data:
                if sha256_crypt.verify(password,x):
                    session["log"] = username_data #here we create session this session also store the value until it is cleared and this value can be used anywhere else in the program and also in other function
                    flash("You have successfully logged in","success")
                    return redirect(url_for('searchbar'))

                else:
                    flash("incorrect password","danger")
                    return render_template("login.html")
    return render_template("login.html")
#searchbar
@app.route("/searchbar",methods=["GET","POST"])
def searchbar():
    if request.method=="POST":
        searchresult = request.form.get("searchresult")


        if len(searchresult)==0:
            flash("You need to enter something in the search box", "danger")
            return render_template("searchbar.html")

        searched_result = db.execute("SELECT * FROM books WHERE isbn LIKE :searchresult OR author LIKE :searchresult OR title LIKE :searchresult",{"searchresult": "%" + searchresult + "%"},).fetchall()
        if len(searched_result)==0 :
            flash("We could not find what you are searching for please be more specific", "danger")
            return render_template("searchbar.html")
        else:
            return render_template("searchbar.html",searched_result=searched_result)

    return render_template("searchbar.html")

@app.route("/searchbar/<int:result_id>",methods=["GET","POST"])
def bookinfo(result_id):
    bookinfo = db.execute("SELECT * FROM books WHERE id = :id", {"id": result_id}).fetchone()
    username_data= session.get("log",None)
    ##########################API#######################################
    isbn_api= db.execute("SELECT isbn FROM books WHERE id = :id", {"id": result_id}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json?key={ORPEp5oGbfOIODp3eWtu2Q}",params={"isbns": isbn_api})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    avg_rating = data["books"][0]['average_rating']
    rating_count = data["books"][0]['ratings_count']
    ###########################API#############################################
    cursor.execute("SELECT username FROM reviews WHERE username=%(username)s",{"username":username_data})
    user_check = cursor.fetchone()
    isbn = bookinfo[1]
    cursor.execute("SELECT isbn FROM reviews WHERE isbn=%(isbn)s", {"isbn": isbn})
    isbn_check=cursor.fetchone()

    if request.method == "POST":
        rating= request.form.get("rating")
        review=request.form.get("review")
        if len(review)==0 or rating==None:
            flash("You clicked Submit without giving your ratings or without entering comments , please select your ratings and also comment something and then click submit.", "danger")
            return render_template("bookinfo.html", bookinfo=bookinfo,avg_rating=avg_rating,rating_count=rating_count)
        elif user_check == None or isbn_check == None  :
            cursor.execute("INSERT INTO reviews (username,isbn,rating,comments) VALUES (%s,%s,%s,%s)",(username_data, isbn, rating,review))
            conn.commit()
            flash("you have successfully submitted your review", "success")
            return render_template("bookinfo.html", bookinfo=bookinfo,avg_rating=avg_rating,rating_count=rating_count)
        else:
            flash("You have already submitted rating for this book and hence you cannot submit another rating", "danger")
            return render_template("bookinfo.html", bookinfo=bookinfo,avg_rating=avg_rating,rating_count=rating_count)

    return render_template("bookinfo.html",bookinfo = bookinfo,avg_rating=avg_rating,rating_count=rating_count)

#here we create API which will return us the json string when we enter the url with isbn number
@app.route("/api/searchbar/<string:isbn>")
def bookinfo_api(isbn):
    cursor.execute("SELECT isbn,title,author,year FROM books WHERE isbn = %(isbn)s", {"isbn": isbn})
    isbn_check = cursor.fetchone()
    if isbn_check is None:
        return jsonify({"error": "Invalid ISBN number"}), 402
    else:
        cursor.execute("SELECT count(*) FROM reviews WHERE isbn = %(isbn)s", {"isbn": isbn})
        no_ratings = cursor.fetchone()
        cursor.execute("SELECT AVG(rating) FROM reviews WHERE isbn = %(isbn)s", {"isbn": isbn})
        avg_ratings = cursor.fetchone()
        avg_ratings=str(avg_ratings[0])
        return jsonify({
            "title": isbn_check[1],
            "author": isbn_check[2],
            "year": isbn_check[3],
            "isbn": isbn_check[0],
            "review_count": no_ratings[0],
            "average_score": avg_ratings
        })

@app.route("/logout",methods=["GET","POST"])
def logout():
    session.clear()#clear session 
    flash("You have successfully logged out", "success")
    return render_template("home.html")


if __name__=="__main__":
    app.secret_key = "r@lphw0rks77"
    app.run()
