import os
import csv
import hashlib

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    password="password"
    hashpass = hashlib.md5(password.encode('utf8')).hexdigest()

    #db.execute("create table reviews (review_id integer, rating integer, review varchar(2000), userid integer)")
    #db.execute("create sequence review_id_seq start 1000")
    #db.execute("insert into users (userid, username, password) values (nextval('userid_seq'), :username, :password)",
    #               {"username": "admin", "password": hashpass  })
    #print(f"inserting user admin with password 'password' (md5 {hashpass})")
    db.execute("alter table reviews add column isbn varchar(100)")

    print(f"table reviews created")

    db.commit();

if __name__ == '__main__':
    main()
