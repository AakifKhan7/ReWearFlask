from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ItemForm(FlaskForm):
    c_title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    c_description = TextAreaField('Description', validators=[DataRequired()])
    condition = StringField('Condition', validators=[DataRequired(), Length(max=120)])
    genderSuited = SelectField('Gender Suited', choices=[('men', 'Men'), ('women', 'Women'), ('both', 'Both')])
    size = SelectField('Size', choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')])
    style = StringField('Style')  # for simplicity, just capture name & create if not exist
    type = StringField('Type')    # same as style
    image = FileField('Image')
    submit = SubmitField('Submit')
