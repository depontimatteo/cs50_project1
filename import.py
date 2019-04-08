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

    db.execute("create table books (isbn varchar(50), title varchar(1000), author varchar(500), year integer)")

    f = open("books.csv")
    reader = csv.reader(f);
    for isbn, title, author, year in reader:
        db.execute("insert into books (isbn, title, author, year) values (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year })
        print(f"inserting book ({isbn}) {title} written by {author} in {year}")

    db.commit();

if __name__ == '__main__':
    main()
