import os
import hashlib
import sys
import requests
import json

from flask import Flask, session, render_template, request, flash, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def get_book_specs(book_isbn):
    books = db.execute("select isbn, title, author, year from books where isbn = :isbn ", { "isbn": book_isbn }).fetchall()

    book = {}

    for book_db in books:
        book["title"]=book_db.title
        book["isbn"]=book_db.isbn
        book["author"]=book_db.author
        book["year"]=book_db.year

    return book

def get_reviews_from_user(book_isbn):
    reviews_from_user = db.execute("select review_id, rating, review, userid from reviews where userid = :userid and isbn = :isbn", { "userid": session["userid"], "isbn": book_isbn }).fetchall()    

    already_reviewed=False
    for review_fu in reviews_from_user:
        if session["userid"] == review_fu.userid:
            already_reviewed=True
    
    return already_reviewed

def get_reviews_from_all(book_isbn):
    reviews_from_all = db.execute("select r.review_id, r.rating, r.review, u.username from reviews r left join users u on r.userid=u.userid where r.isbn = :isbn", { "isbn": book_isbn }).fetchall()    
    
    return reviews_from_all

def get_reviews_from_goodreads(book_isbn):
    reviews_from_goodreads_json = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "UYMkXV82q3xj7zy9rQaomg", "isbns": book_isbn})
    reviews_from_goodreads_parsed = json.loads(reviews_from_goodreads_json.text)
    reviews_from_goodreads_array=[]
    reviews_from_goodreads_array=reviews_from_goodreads_parsed['books']
    reviews_from_goodreads = {}

    for item in reviews_from_goodreads_array:
        if(item["isbn"] == book_isbn):
            reviews_from_goodreads["isbn"]=item["isbn"]
            reviews_from_goodreads["ratings_count"]=item["ratings_count"]
            reviews_from_goodreads["average_rating"]=item["average_rating"]
    
    return reviews_from_goodreads

@app.route('/')
def index():
    if not session.get('userid'):
        return render_template('login.html')
    else:
        return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return "Operation not allowed"
    else:
        username_p = request.form.get("username_p")
        password_p = request.form.get("password_p")

        hashpass_p = hashlib.md5(password_p.encode('utf8')).hexdigest()

        users=db.execute("select userid from users where username = :username and password = :password limit 1",{ "username": username_p, "password": hashpass_p }).fetchall()

        for user in users:
            if user.userid is None:
                flash("Wrong password!")
            else:
                session["userid"]=user.userid
        return index()

@app.route('/logout')
def logout():
    session.pop('userid', None)
    return index()

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/search_result", methods=["GET","POST"])
def search_result():
    search_p = request.form.get("search_p")
    books = db.execute("select isbn, title, author, year from books where upper(isbn) like '%" + search_p.upper() + "%' or upper(title) like '%" + search_p.upper() + "%' or upper(author) like '%" + search_p.upper() + "%'").fetchall()
    return render_template("books.html", books=books)

@app.route("/search_result/<string:book_isbn>", methods=["GET","POST"])
def search_single_book(book_isbn):

    book=get_book_specs(book_isbn)

    already_reviewed=get_reviews_from_user(book_isbn)

    reviews_from_all=get_reviews_from_all(book_isbn)

    reviews_from_goodreads=get_reviews_from_goodreads(book_isbn)
    
    return render_template("single_book.html", book=book, already_reviewed=already_reviewed, reviews_from_all=reviews_from_all, reviews_from_goodreads=reviews_from_goodreads, userid=session["userid"], number_of_reviews=len(reviews_from_all), isbn=book_isbn )

@app.route("/books")
def books():
    books = db.execute("select isbn, title, author, year from books").fetchall()
    return render_template("books.html", books=books)

@app.route("/send_review", methods=["GET","POST"])
def send_review():
    review_p = request.form.get("review_p")
    rating_p = request.form.get("rating_p")
    book_isbn_p = request.form.get("book_isbn_p")
    db.execute("insert into reviews (review_id, rating, review, userid, isbn) values (nextval('review_id_seq'), :rating, :review, :userid, :isbn)", { "rating": rating_p, "review": review_p, "userid": session["userid"], "isbn": book_isbn_p })
    db.commit();
    return search_single_book(book_isbn_p)

@app.route("/api/<string:book_isbn>")
def api(book_isbn):
    book=get_book_specs(book_isbn)

    book_api = {}

    if "isbn" in book.keys():
        if(book["isbn"] == book_isbn):

            reviews_from_goodreads=get_reviews_from_goodreads(book_isbn)

            book_api['title'] = book["title"]
            book_api['author'] = book["author"]
            book_api['year'] = book["year"]
            book_api['isbn'] = book_isbn
            book_api['review_count'] = reviews_from_goodreads["ratings_count"]
            book_api['average_score'] = reviews_from_goodreads["average_rating"]
            json_book_api = json.dumps(book_api)

            return json_book_api

        else:
            abort(404)
    else:
        abort(404)

