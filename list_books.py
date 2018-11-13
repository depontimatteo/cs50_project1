import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    books = db.execute("select isbn, title, author, year from books").fetchall()
    for book in books:
        print(f" ({book.isbn}) {book.title} written by {book.author} in {book.year}")

    if books is None:
        print("no books")
        return

if __name__ == '__main__':
    main()
