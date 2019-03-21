# Project 1

## Web Programming with Python and JavaScript

Website with some examples about HTML5, CSS, SCSS, Bootstrap elements and techniques for the frontend, Python and SQL code for the backend.

##### Description of static HTML files:
- *index.html*: homepage with a Welcome message
- *login.html*: page where users can login to the website providing username and password
- *books.html*: page listing all the books, eventually filtered for search parameter
- *layout.html*: layout page with a navbar, including libraries. Is extended by all the other pages
- *registration.html*: page where users can register to the website providing username and password
- *search.html*: page where users can search for books, eventually choosing a text filter parameter
- *single_book.html*: page where a single book is completely described, with list of reviews, infos from Goodreads and a form where users can submit teir own review (if not already done)

##### Description of Python files

- *application.py*: script containing all the backend operations invoked using the frontend. Is the core of the entire application
- *import.py*: script with whom is possible to import all the books entries fron the file books.csv

##### Functionalities of the website

**Registration**: Users can register on the website, providing a username and password.
**Login**: Users, once registered, can log in on the website with their username and password.
**Logout**: Logged in users can log out of the site.
**Search**: Once a user has logged in, can search for a book. Users can type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, the website display a list of possible matching results. If the user typed in only part of a title, ISBN, or author name, search page should find matches as well.
**Book Page**: When users click on a book from the results of the search page, he goes to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews users have left for the book on the website.
**Review Submission**: On the book page, users can submit a review: consisting of a rating on a scale of 1 to 5 and a free text area where the user can write their opinion about a book. Users can submit a review for a book at least once.
**Goodreads Review Data**: On the book page, the website displays (if available) the average rating and number of ratings the work has received from Goodreads.
**API Access**: If users make a GET request to website’s /api/<isbn> route, where <isbn> is an ISBN number, website return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.
