from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class AddCafeForm(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    location = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Cafe Image URL", validators=[URL()])
    map_url = StringField("Map in URL", validators=[DataRequired(), URL()])

    has_sockets = SelectField('Has Sockets?', validators=[DataRequired()],
                              choices=[True,False]
                              )
    has_toilet = SelectField('Has Toilet?', validators=[DataRequired()],
                             choices=[True,False]
                             )
    has_wifi = SelectField('Has Wifi?', validators=[DataRequired()],
                           choices=[True,False]
                           )
    can_take_calls = SelectField('Take Calls ?', validators=[DataRequired()],
                                 choices=[True,False]
                                 )
    seats = SelectField('No: of Seats?', validators=[DataRequired()],
                                 choices=['10+','20+','30+','40+','50+' ]
                                 )
    coffee_price = StringField("Coffee Price?", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name = StringField('Your name', validators=[DataRequired()])
    email = EmailField('Your email', validators=[DataRequired(), Email(message='Input valid Email.')])
    password = PasswordField('Set password', validators=[DataRequired()])
    submit = SubmitField('Register')


# TODO: Create a LoginForm to login existing users

class LoginForm(FlaskForm):
    email = EmailField('Your email', validators=[DataRequired(), Email(message='Input valid Email.')])
    password = PasswordField('Set password', validators=[DataRequired()])
    submit = SubmitField('Login')


# TODO: Create a CommentForm so users can leave comments below posts

class CommentForm(FlaskForm):
    comment = CKEditorField('Write your comment', validators=[DataRequired()])
    add_comment = SubmitField('Add Comment')
