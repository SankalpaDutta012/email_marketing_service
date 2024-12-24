# models.py
from datetime import datetime
from .db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable = False)

class EmailList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipients = db.relationship('Recipient', backref='email_list', cascade="all, delete-orphan", lazy=True)

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('email_list.id'), nullable=False)

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    html = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    email_list_id = db.Column(db.Integer, db.ForeignKey('email_list.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, default = False)
    recipients = db.relationship('Recipient', secondary = 'campaign_recipient', backref=db.backref('campaigns', lazy='dynamic'))

class CampaignRecipient(db.Model):
    __tablename__ = 'campaign_recipient'
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'), primary_key=True)