from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterUserForm, UserLoginForm, CommentForm, ContactForm
from flask_gravatar import Gravatar
from functools import wraps
from dotenv import load_dotenv
import os
import smtplib

app = Flask(__name__)
load_dotenv('.env')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY_BLOG')
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)

email_password = os.environ.get('PASSWORD')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CONFIGURE TABLES OF DATABASE
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship('Comments', back_populates='author')


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    comments = relationship('Comments', back_populates='blog_post')


class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = relationship('User', back_populates='comments')

    blog_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    blog_post = relationship('BlogPost', back_populates='comments')

# db.create_all()


# Gravatar setup Used for logos for the comment section in below the posts
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# Decorator to allow only the admin to access certain routes
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1 :
            return abort(403)
        else:
            return f(*args, **kwargs)
    return decorated_function

# Home route, shows the home page
@app.route('/')
def get_all_posts():

    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


# Register route used by the user to register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        password = form.password.data
        email = form.email.data
        already_exists = User.query.filter_by(email=email).first()
        if not already_exists:
            hashed_salted_password = generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=10)
            new_user = User(
                email=request.form.get('email'),
                password=hashed_salted_password,
                name=request.form.get('name')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
        else:
            flash('This email address is already registered. Please log in')
            return redirect(url_for('login'))
    return render_template("register.html", form=form)


# Login route used by the user to login
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            hashed_salted_password = user.password
            if check_password_hash(hashed_salted_password, form.password.data):
                login_user(user)
                return redirect(url_for('get_all_posts'))

            else:
                flash('The password entered is wrong. Please try again.')
                return redirect(url_for('login'))
        else:
            flash('That email does not exist. Please try again.')
            return redirect(url_for('login'))

    return render_template("login.html", form=form)


# Logout route used by the user to logout of their account
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


# Post route, returns the blog post selected by the user
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash(message='To comment please login.')
            return redirect(url_for('login'))
        else:
            new_comment = Comments(
                text=form.comment.data,
                author=current_user,
                blog_post=requested_post

            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('get_all_posts'))
    comments = Comments.query.filter_by(blog_id=requested_post.id).all()
    return render_template("post.html", post=requested_post, form=form, comments=comments)


# About route, shows the about page
@app.route("/about")
def about():
    return render_template("about.html")


# Contact route, show the contact me page
@app.route("/contact", methods=['POST', 'GET'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        pass
        # The SMTP LIBRARY does not work on heroku. It is suggested to use third party email service which unfortunately are priced.
        email = form.email.data
        name = form.name.data
        message = form.message.data
        connection = smtplib.SMTP("smtp.gmail.com", 587)
        connection.starttls()
        connection.login("yashcode.wiz1@gmail.com", email_password)
        connection.sendmail(from_addr="yashcode.wiz1@gmail.com", to_addrs="kumar.yashrana1718@gmail.com",
                            msg=f"Subject: New blog message\n\nemail: {email}\nname: {name}\n{message}")
        connection.close()
        return redirect(url_for('get_all_posts'))
    return render_template("contact.html", form=form)


# new-post route, allows the admin to add a new post
@app.route("/new-post", methods=['GET', 'POST'])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# edit-post route, allows the admin to edit a post
@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True)


# delete route, allows the admin to delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
