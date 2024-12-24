# forms.py
from wtforms import Form, StringField, IntegerField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, Length

class UserRegistrationForm(Form):
    username = StringField('Username', validators=[DataRequired(), Length(min = 3, max = 80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = StringField('Password', validators=[DataRequired(), Length(min = 8, max = 128)])

class EmailListForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=80)])

class RecipientForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])

class EmailTemplateForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=80)])
    html = TextAreaField('HTML Content', validators=[DataRequired()])

class CampaignForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=80)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max = 200)])
    email_list_id = IntegerField('Email List ID', validators=[DataRequired()])
    template_id = IntegerField('Template ID', validators=[DataRequired()])
    scheduled_at = DateTimeField('Scheduled Time', validators=[DataRequired()])