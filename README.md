# Blog site

This is my personal blog website built with the flask framework of python. 

# Builiding it

I programmed the entire Backend in python and used a template for the Frontend. Using the templating language Jinja I was able to modify the template to create different pages.
The program makes use of a SQL-Light database to store blog information such as title, post, etc. 
The website is being hosted on Heroku and you can find it at https://yashrana-blog.herokuapp.com/.

# Functionality 

The website is able to display a list of the blogs posted along with the date, subtitle, and poster name. If the user decides to click and select a certain blog, the program goes to the actual post page where it displays the entire post.
There is a 'register' page where the user is asked to register and a 'login' page where an existing user can log back in. 
The user is able to comment under each post, if not logged they will be prompted to do so. There is also a contact me page which makes use of the SMTP library to send the user message as an email.

# Admin Access

There are more things that can be done on this blog site if logged in as an admin. Indeed, if you are an admin you can see an 'edit post' button to change posts, a 'new post' button to create new posts and a '✗' cross symbol to delete a post.


# Issues
* In order for the database to work on Heroku it was necessary to upgrade to PostgreSQL. 
* Due to Heroku's restrictions the SMTP library does not work thus it is not possible for the user to send any message.
