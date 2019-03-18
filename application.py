import os
import hashlib
import sys
import requests

from flask import Flask, session, render_template, request, flash
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
    books = db.execute("select isbn, title, author, year from books where isbn = :isbn ", { "isbn": book_isbn }).fetchall()
    reviews_from_user = db.execute("select review_id, rating, review from reviews where userid = :userid and isbn = :isbn", { "userid": session["userid"], "isbn": book_isbn });
    reviews_from_all = db.execute("select r.review_id, r.rating, r.review, u.username from reviews r left join users u on r.userid=u.userid and r.isbn = :isbn", { "isbn": book_isbn });
    reviews_from_goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "UYMkXV82q3xj7zy9rQaomg", "isbns": book_isbn})
    return render_template("single_book.html", books=books, reviews_from_user=reviews_from_user, reviews_from_all=reviews_from_all, reviews_from_goodreads=reviews_from_goodreads)

@app.route("/books")
def books():
    books = db.execute("select isbn, title, author, year from books").fetchall()
    return render_template("books.html", books=books)

@app.route("/send_review", methods=["GET","POST"])
def send_review():
    review_p = request.form.get("review_p")
    rating_p = request.form.get("rating_p")
    book_isbn_p = request.form.get("book_isbn_p")
    print("insert into reviews (review_id, rating, review, userid, isbn) values (nextval('review_id_seq'), " + str(rating_p) + " " + str(review_p) + " " + str(session["userid"]) + " " + str(book_isbn_p), file=sys.stdout)
    db.execute("insert into reviews (review_id, rating, review, userid, isbn) values (nextval('review_id_seq'), :rating, :review, :userid, :isbn)", { "rating": rating_p, "review": review_p, "userid": session["userid"], "isbn": book_isbn_p })
    db.commit();
    return search_single_book(book_isbn_p)
