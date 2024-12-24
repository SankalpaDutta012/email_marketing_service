# routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from .forms import UserRegistrationForm, EmailListForm, RecipientForm, EmailTemplateForm, CampaignForm
from .db import db
from .models import User, EmailList, Recipient, EmailTemplate, Campaign
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import send_email
from datetime import datetime

routes_bp = Blueprint('routes', __name__)

# User Registration
@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Successfully created new user {form.username.data}')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form = form)

# User Login
@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            flash('Login Successful!')
            return redirect(url_for('routes.dashboard'))
        else:
            flash('Login Unsuccessful! Check your username or password.')
            return render_template('login.html')
    return render_template('login.html')

@routes_bp.route('/logout')
def logout():
    flash('Successfully logged out!')
    return redirect(url_for('routes.login'))

# Dashboard
@routes_bp.route('/dashboard')
def dashboard():
    email_lists = EmailList.query.all()
    templates = EmailTemplate.query.all()
    campaigns = Campaign.query.all()
    return render_template('dashboard.html', email_lists=email_lists, templates=templates, campaigns=campaigns)

# List CRUD
@routes_bp.route('/lists', methods = ['GET', 'POST'])
def lists():
    form = EmailListForm(request.form)
    if request.method == "POST" and form.validate():
        new_list = EmailList(name = form.name.data)
        db.session.add(new_list)
        db.session.commit()
        flash(f'Email list with name {form.name.data} successfully created!')
        return redirect(url_for('routes.lists'))
    all_lists = EmailList.query.all()
    return render_template('lists.html', form=form, email_lists=all_lists)

@routes_bp.route('/lists/<int:list_id>', methods=['GET', 'POST'])
def edit_list(list_id):
    edit_list = EmailList.query.get_or_404(list_id)
    form = EmailListForm(request.form, obj=edit_list)
    if request.method == 'POST' and form.validate():
        form.populate_obj(edit_list)
        db.session.commit()
        flash(f'Email list with name {edit_list.name} successfully updated!')
        return redirect(url_for('routes.lists'))
    return render_template('edit_list.html', form=form, edit_list = edit_list)

@routes_bp.route('/lists/<int:list_id>/delete', methods=['POST'])
def delete_list(list_id):
    delete_list = EmailList.query.get_or_404(list_id)
    db.session.delete(delete_list)
    db.session.commit()
    flash(f"Email list with name {delete_list.name} successfully deleted!")
    return redirect(url_for('routes.lists'))

# Recipient CRUD
@routes_bp.route('/lists/<int:list_id>/recipients', methods = ['GET','POST'])
def recipients(list_id):
    form = RecipientForm(request.form)
    email_list = EmailList.query.get_or_404(list_id)
    if request.method == "POST" and form.validate():
        new_recipient = Recipient(email = form.email.data, email_list= email_list)
        db.session.add(new_recipient)
        db.session.commit()
        flash(f'Recipient with email {form.email.data} successfully added to {email_list.name} list!')
        return redirect(url_for('routes.recipients', list_id = list_id))
    return render_template('recipients.html', form = form, email_list=email_list, recipients=email_list.recipients)

@routes_bp.route('/lists/<int:list_id>/recipients/<int:recipient_id>/delete', methods = ['POST'])
def delete_recipient(list_id, recipient_id):
    delete_recipient = Recipient.query.get_or_404(recipient_id)
    db.session.delete(delete_recipient)
    db.session.commit()
    flash(f"Recipient with email {delete_recipient.email} successfully deleted!")
    return redirect(url_for('routes.recipients', list_id = list_id))

# Template CRUD
@routes_bp.route('/templates', methods=['GET', 'POST'])
def templates():
    form = EmailTemplateForm(request.form)
    if request.method == 'POST' and form.validate():
        new_template = EmailTemplate(name = form.name.data, html=form.html.data)
        db.session.add(new_template)
        db.session.commit()
        flash(f"Email template with name {form.name.data} successfully created!")
        return redirect(url_for('routes.templates'))
    all_templates = EmailTemplate.query.all()
    return render_template('templates.html', form = form, email_templates = all_templates)

@routes_bp.route('/templates/<int:template_id>', methods=['GET', 'POST'])
def edit_template(template_id):
    edit_template = EmailTemplate.query.get_or_404(template_id)
    form = EmailTemplateForm(request.form, obj = edit_template)
    if request.method == 'POST' and form.validate():
        form.populate_obj(edit_template)
        db.session.commit()
        flash(f"Email template with name {edit_template.name} successfully updated!")
        return redirect(url_for('routes.templates'))
    return render_template('edit_template.html', form = form, edit_template = edit_template)

@routes_bp.route('/templates/<int:template_id>/delete', methods = ['POST'])
def delete_template(template_id):
    delete_template = EmailTemplate.query.get_or_404(template_id)
    db.session.delete(delete_template)
    db.session.commit()
    flash(f"Email template with name {delete_template.name} successfully deleted!")
    return redirect(url_for('routes.templates'))

#Campaign Creation
@routes_bp.route('/campaigns', methods = ['GET', 'POST'])
def campaigns():
    form = CampaignForm(request.form)
    if request.method == 'POST' and form.validate():
        new_campaign = Campaign(name=form.name.data,
                                subject=form.subject.data,
                                email_list_id = form.email_list_id.data,
                                template_id = form.template_id.data,
                                scheduled_at=form.scheduled_at.data)
        db.session.add(new_campaign)
        db.session.commit()
        flash(f"New campaign with name {form.name.data} successfully created")
        return redirect(url_for('routes.dashboard'))
    return render_template('campaigns.html', form = form)

# Email Sending
@routes_bp.route('/send-campaign/<int:campaign_id>', methods = ['POST'])
def send_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sent:
        flash(f'Campaign with name {campaign.name} has already been sent')
        return redirect(url_for('routes.dashboard'))
    email_list = EmailList.query.get_or_404(campaign.email_list_id)
    template = EmailTemplate.query.get_or_404(campaign.template_id)
    subject = campaign.subject
    for recipient in email_list.recipients:
        send_email(recipient.email, subject, template.html, is_html=True)
        campaign.recipients.append(recipient)
    campaign.sent = True
    db.session.commit()
    flash(f'Successfully sent email campaign with name {campaign.name}')
    return redirect(url_for('routes.dashboard'))

# Placeholder
@routes_bp.route('/email-template-editor')
def email_template_editor():
    return render_template('template_editor.html')