from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_paginate import Pagination, get_page_args
# Import your forms from the forms.py
# from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from typing import List
from hashlib import md5
from sqlalchemy.ext.declarative import declarative_base
from flask_migrate import Migrate
from forms import AddCafeForm, LoginForm, CommentForm, RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Put Secret Key'
ckeditor = CKEditor(app)
Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# TODO: Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return func(*args, **kwargs)
        else:
            return abort(403)

    return decorated_function

    # return the_wrapper_around_the_original_function


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False, unique=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

class Cafe(db.Model):
    __tablename__ = "cafe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.String(250), nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)
    comments = db.relationship('Comment', backref='cafe', lazy=True)

class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'), nullable=False)



@app.route('/')
def home_page():
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page', default_per_page=10)
    total = Cafe.query.count()
    cafes = Cafe.query.offset(offset).limit(per_page).all()

    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('front_webpage.html', cafes=cafes, page=page,
                           per_page=per_page,
                           pagination=pagination,
                           current_user = current_user
                           )

@app.route('/cafe/<int:cafe_id>', methods=['GET','POST'])
def show_info(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    comment_form = CommentForm()
    comments = Comment.query.filter_by(cafe_id=cafe_id).all()
    user = User.query.filter_by(id=cafe_id)

    if comment_form.validate_on_submit():

        add_comment(cafe_id, text=comment_form.comment.data, name = current_user.name)

    return render_template('show_info.html', cafe=cafe,form = comment_form,
                           current_user = current_user,
                           comments = comments,
                           user = user
                           )

@app.route('/addcafe', methods=['GET','POST'])
def add_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
        cafe_name = request.form['name']
        cafe_map_url = request.form['map_url']
        cafe_img_url = request.form['img_url']
        cafe_location = request.form['location']
        has_sockets = bool(request.form.get('has_sockets'))
        has_toilet = bool(request.form.get('has_toilet'))
        has_wifi = bool(request.form.get('has_wifi'))
        can_take_calls = bool(request.form.get('can_take_calls'))
        cafe_seats = request.form['seats']
        cafe_coffee_price = request.form['coffee_price']
        new_cafe = Cafe(
            name=cafe_name,
            map_url=cafe_map_url,
            img_url=cafe_img_url,
            location=cafe_location,
            has_sockets=has_sockets,
            has_toilet=has_toilet,
            has_wifi=has_wifi,
            can_take_calls=can_take_calls,
            seats=cafe_seats,
            coffee_price=cafe_coffee_price
        )
        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for('home_page'))

    return render_template('addcafe.html', form=form)


@admin_only
@app.route('/delete_cafe/<int:cafe_id>', methods=['GET','POST'])
def delete_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('home_page'))


@app.route('/update_cafe/<int:cafe_id>', methods=['GET', 'POST'])
def update_cafe(cafe_id):
    form = AddCafeForm()
    if form.validate_on_submit():
        cafe = Cafe.query.get_or_404(cafe_id)
        cafe.name = request.form['name']
        cafe.map_url = request.form['map_url']
        cafe.img_url = request.form['img_url']
        cafe.location = request.form['location']
        cafe.has_sockets = bool(request.form.get('has_sockets'))
        cafe.has_toilet = bool(request.form.get('has_toilet'))
        cafe.has_wifi = bool(request.form.get('has_wifi'))
        cafe.can_take_calls = bool(request.form.get('can_take_calls'))
        cafe.seats = request.form['seats']
        cafe.coffee_price = request.form['coffee_price']
        db.session.commit()
        return redirect(url_for('home_page'))

    return render_template('addcafe.html', form=form)



@app.route('/add_comment/<int:cafe_id>', methods=['GET','POST'])
def add_comment(cafe_id, text, name):
    comment_text = text
        # request.form['comment_text']
    user_id = current_user.id
        # cafe_id
    new_comment = Comment(name=name,text=comment_text, user_id=user_id, cafe_id=cafe_id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('show_info', cafe_id=cafe_id))



@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == register_form.email.data)).scalar()
        if not user:
            new_user = User(
                name=register_form.name.data,
                email=register_form.email.data,
                password=generate_password_hash(register_form.password.data,
                                                salt_length=8
                                                )
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home_page', logged_in=current_user.is_authenticated))
        else:
            flash(message='Email is already registered. Login instead.')
            return redirect(url_for('login'))

    return render_template("register.html", form=register_form)


@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        login_email = login_form.email.data
        login_passowrd = login_form.password.data
        user = db.session.execute(db.select(User).where(User.email == login_email)).scalar()
        if user and check_password_hash(password=login_passowrd, pwhash=user.password):
            login_user(user)
            return redirect(url_for('home_page'))
        elif not user:
            flash(message='Email is not registered.')
            return redirect(url_for('register'))
        elif not check_password_hash(password=login_passowrd, pwhash=user.password):
            flash(message='Incorrect Password')
            return redirect(url_for('login'))

    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)



# def gravatar_url(email, size=100, rating='g', default='retro', force_default=False):
#     hash_value = md5(email.lower().encode('utf-8')).hexdigest()
#     return f"https://www.gravatar.com/avatar/{hash_value}?s={size}&d={default}&r={rating}&f={force_default}"
#
#

# class BlogPost(db.Model):
#     __tablename__ = "blog_posts"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
#     subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
#     date: Mapped[str] = mapped_column(String(250), nullable=False)
#     body: Mapped[str] = mapped_column(Text, nullable=False)
#     img_url: Mapped[str] = mapped_column(String(250), nullable=False)
#
#     # Create Foreign Key, "users.id" the users refers to the tablename of User.
#     # Create reference to the User object. The "posts" refers to the posts property in the User class.
#
#     author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
#     author = relationship("User", back_populates="posts")
#
#     # ***************Parent Relationship*************#
#     comments = relationship("Comment", back_populates="parent_post")


# TODO: Use Werkzeug to hash the user's password when creating a new user.

#
#
# # TODO: Retrieve a user from the database based on their email.

#
#
# @app.route('/')
# def get_all_posts():
#     result = db.session.execute(db.select(BlogPost))
#     posts = result.scalars().all()
#     return render_template("index.html", all_posts=posts, current_user=current_user)
#
#
# # TODO: Allow logged-in users to comment on posts
# @app.route("/post/<int:post_id>", methods=['GET', 'POST'])
# def show_post(post_id):
#     requested_post = db.get_or_404(BlogPost, post_id)
#     comment_form = CommentForm()
#     if comment_form.validate_on_submit():
#         if not current_user.is_authenticated:
#             flash('Login or Register to Comment.')
#         else:
#             new_comment = Comment(
#                 comment_author=current_user,
#                 text=comment_form.comment.data,
#                 parent_post=requested_post
#             )
#             db.session.add(new_comment)
#             db.session.commit()
#
#     return render_template("post.html", post=requested_post, current_user=current_user,
#                            comment=comment_form
#                            , gravatar_url=gravatar_url)
#
#

#
#
# # TODO: Use a decorator so only an admin user can create a new post
# @app.route("/new-post", methods=["GET", "POST"])
# @admin_only
# def add_new_post():
#     form = CreatePostForm()
#     if form.validate_on_submit():
#         new_post = BlogPost(
#             title=form.title.data,
#             subtitle=form.subtitle.data,
#             body=form.body.data,
#             img_url=form.img_url.data,
#             author=current_user,
#             date=date.today().strftime("%B %d, %Y")
#         )
#         db.session.add(new_post)
#         db.session.commit()
#         return redirect(url_for("get_all_posts"))
#     return render_template("make-post.html", form=form, current_user=current_user)
#
#
# # TODO: Use a decorator so only an admin user can edit a post
# @app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
# @admin_only
# def edit_post(post_id):
#     post = db.get_or_404(BlogPost, post_id)
#     edit_form = CreatePostForm(
#         title=post.title,
#         subtitle=post.subtitle,
#         img_url=post.img_url,
#         author=post.author,
#         body=post.body
#     )
#     if edit_form.validate_on_submit():
#         post.title = edit_form.title.data
#         post.subtitle = edit_form.subtitle.data
#         post.img_url = edit_form.img_url.data
#         post.author = current_user
#         post.body = edit_form.body.data
#         db.session.commit()
#         return redirect(url_for("show_post", post_id=post.id))
#     return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)
#
#
# # TODO: Use a decorator so only an admin user can delete a post
# @app.route("/delete/<int:post_id>")
# @admin_only
# def delete_post(post_id):
#     post_to_delete = db.get_or_404(BlogPost, post_id)
#     db.session.delete(post_to_delete)
#     db.session.commit()
#     return redirect(url_for('get_all_posts'))
#
#
# @app.route("/about")
# def about():
#     return render_template("about.html")
#
#
# @app.route("/contact")
# def contact():
#     return render_template("contact.html")
