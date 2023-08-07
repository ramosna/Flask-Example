from flask import Flask, request, session
import query

class User:
    """
    Model for our application users.
    """

    def signup(self):
        """
        Responsible for account creation. 
        TODO: add more detail such as result of successful creation and failed creation.
        """
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        reset_pin = request.form['reset-pin']

        # after successful insertion, should get user_id
        user_id = query.add_new_user(username, password, firstname, lastname, reset_pin)
        if not user_id:
            return False
        else:
            user = query.login_user(username, password)
            self.init_session(user, username)
        

        # TODO: we might not need to return user anymore since their info is stored in the session.
        # return query.get_user(user_id)

    def login(self):
        """
        Method for logging a user into the application.
        TODO: add detail for successful login and failed login.
        TODO: also look into doing reset password
        """

        username = request.form['username']
        password = request.form['password']

        user = query.login_user(username, password)
        if user:
            print("Login method in User model successful")
            self.init_session(user, username)
            return user
        else:
            print("Login method in User model NOT successful.")
            return

    def logout(self):
        """
        Logs user out of applciation.
        """
        del session['username']
        del session['user']
        del session['logged_in']


    def init_session(self, user, username):
        """
        Starts the session for a user in order to give access to user-only content.
        """
        session['logged_in'] = True
        session['username'] = username
        session['user'] = user

    # methods for job interactions
    def add_new_job(self):
        """
        Allows a user to add a new job.

        TODO: do we want to return anything after insertion?
        """
        # TODO: come back here when have contact/skills figured out

        company = request.form['company']
        position = request.form['position']
        date = request.form['date']
        status = request.form['status']
        username = session['username']

        new_job = query.add_new_job(company, position, date, status, username)

    def get_jobs(self):
        results = query.get_jobs(session['username'])
        return results

    def find_job(self, _id):
        result = query.find_job(_id)
        return result

    def edit_job(self, _id):
        company = request.form['company']
        position = request.form['position']
        date = request.form['date']
        status = request.form['status']
        query.update_job(_id, company, position, date, status)

    def delete_job(self, _id):
        query.delete_job(_id)

    def find_related_contacts(self, job_name, user):
        contacts = query.get_contacts(user)
        complete = []
        for contact in contacts:
            if contact["company"].lower() == job_name.lower():
                if contact["job"] is None:
                    complete.append(contact)
        return complete

    def connect_job_contact(self, job_id):
        contact_id = request.form['contact']
        query.add_job_contact(job_id, contact_id)
        query.update_contact_job(contact_id, job_id)

    # methods for contact interactions
    def add_new_contact(self):
        """
        Allows user to store a new contact.

        TODO: same as add_new_job
        """
        # TODO: figure way to connect this to jobs or display contacts that belong to certain companies

        name = request.form['name'].title()
        company = request.form['company']
        email = request.form['email']
        phone = request.form['phone']
        username = session['username']

        new_contact = query.add_new_contact(name, company, email, phone, username)

    def get_contacts(self):
        results = query.get_contacts(session['username'])
        return results

    def find_contact(self, _id):
        result = query.find_contact(_id)
        return result

    def edit_contact(self, _id):
        name = request.form['name']
        company = request.form['company']
        email = request.form['email']
        phone = request.form['phone']
        query.update_contact(_id, name, company, email, phone)

    def delete_contact(self, _id):
        query.delete_contact(_id)

    def find_related_jobs(self, company, user):
        jobs = query.get_jobs(user)
        complete = []
        for job in jobs:
            if job["company"].lower() == company.lower():
                complete.append(job)
        return complete

    def connect_contact_job(self, contact_id):
        job_id = request.form['job']
        query.add_job_contact(job_id, contact_id)
        query.update_contact_job(contact_id, job_id)

    def disconnect_contact_job(self, contact_id, job_id):
        query.update_contact_job(contact_id, None)
        query.remove_job_contact(job_id, contact_id)

    # methods for skill interactions
    def add_new_skill(self):
        """
        Allows user to add skills for all users of app.
        """
        user = session['username']
        skill = request.form['skill'].title()
        comfort = request.form['comfort']

        skill = query.add_skill(user, skill, comfort)

        if skill == 1:
            print("Skill already exists")

    def get_skills(self):
        result = query.get_skills(session['username'])
        return result

    def update_skill(self, _id):
        x = request.form.getlist('updated-skills')
        print(x)
        updated = query.update_skill(_id, x)
        
    def find_skill(self, _id):
        result = query.find_skill(_id)
        return result
    
    def delete_skill(self, _id):
        query.delete_skill(_id)