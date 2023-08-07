from flask import Flask, render_template, request, session, redirect, url_for, flash
from functools import wraps
from get_db import get_database
from user.models import User
import query

app = Flask(__name__)
app.secret_key = b'ae0aabb7bd128fded731bbf2'

# Decorator for limiting certain pages to authenticated users
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'logged_in' in session:
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def start_session():
    # print("HERE BOI")
    # return
    if not session:
        session['active'] = True

# TODO: add login required to pages that need it


"""
Landing page for when users are not logged in and go to website.
Users are also redirected here when they log out of the application.
"""
@app.route("/")
def default():
    return render_template('index.html')

# routes for jobs
@app.route("/jobs/add", methods=['POST', 'GET'])
@login_required
def add_job():
    if request.method == 'GET':
        return render_template('addJobs.html')

    if request.method == 'POST':
        User().add_new_job()

        return redirect(url_for("get_jobs"))

@app.route('/jobs/', methods=['GET'])
@login_required
def get_jobs():
    results = User().get_jobs()
    return render_template('jobs.html', results=results)

@app.route('/jobs/<_id>', methods=['GET'])
@login_required
def specific_job(_id):
    results = User().find_job(_id)
    if results is None:
        return "Error: Job Not Found"
    else:
        return render_template('job.html', job=results)

@app.route('/jobs/edit/<_id>', methods=['GET'])
@login_required
def edit_job(_id):
    results = User().find_job(_id)
    if results is None:
        return "Error: Job Not Found"
    else:
        options = ["Applied", "OA", "Recruiter Screen", "Interview 1",
                   "Interview 2", "Interview 3", "Offer Extended", "Rejected"]
        options.remove(results["status"])                                         # TODO: caused error for me, try to repro
        return render_template('editJob.html', job=results, options=options)


# TODO: move this to where skills are --------------------------------------->
@app.route('/skills/edit/<_id>', methods=['GET', 'POST'])
@login_required
def edit_skill(_id):
    results = User().find_skill(_id)
    
    if request.method == 'GET':
        if results is None:
            return "Error: Skill Not Found"
        else:
            options = ["Never Used", "Beginner", "Intermediate", "Advanced"]
            return render_template('editSkill.html', skills=results, comfort=options)

@app.route('/skills/delete/<_id>', methods=['POST', 'GET'])
@login_required
def delete_skill(_id):
    User().delete_skill(_id)
    return redirect('/jobs/skills')

# TODO: move this to where skills are --------------------------------------- END>
# END

@app.route('/jobs/edit/<_id>/skills', methods=['GET','POST'])
@login_required
def add_skill_to_job(_id):
    results = User().get_skills()
    job = User().find_job(_id)
    x = job['skills']

    if request.method == 'GET':
        if results is None:
            # return "Blank"
            # TODO: make a prompt that tells user they haven't tracked any skills
             return render_template('skillsForJob.html', skills=None, x=None, job=_id)
        else:
            return render_template('skillsForJob.html', skl=results, x=x, job=_id)
    
    if request.method == 'POST':
        User().update_skill(_id)
        # return render_template('skillsForJob.html', skl=results, x=x)
        return redirect(f'/jobs/{_id}')

@app.route('/jobs/update/<_id>', methods=['POST'])
@login_required
def update_job(_id):
    User().edit_job(_id)
    url = "/jobs/" + _id
    return redirect(url, code=302)

@app.route('/jobs/<_id>/contacts/', methods=['GET', 'POST'])
@login_required
def display_contacts(_id):
    if request.method == 'GET':
        obj = User()
        job = obj.find_job(_id)
        contacts = []
        for cont_id in job["contacts"]:
            contacts.append(obj.find_contact(cont_id))
        return render_template('contactsForJob.html', results=contacts, job=job)

@app.route('/jobs/contacts/<_id>/', methods=['GET', 'POST'])
@login_required
def related_contacts(_id):
    usr = User()
    job = usr.find_job(_id)
    results = usr.find_related_contacts(job["company"], job["user"])
    return render_template('contactToJob.html', contacts=results, job=job)


@app.route('/jobs/connect/contacts/<_id>', methods=['GET', 'POST'])
@login_required
def connect_job_contact(_id):
    User().connect_job_contact(_id)
    url = "/jobs/" + _id + "/contacts/"
    return redirect(url, code=302)
    pass

@app.route('/delete/jobs/<_id>', methods=['GET'])
@login_required
def delete_job(_id):
    usr = User()
    job = usr.find_job(_id)
    if job is None:
        return "Error: Job Not Found"
    else:
        if len(job["contacts"]) != 0:
            for contact in job["contacts"]:
                usr.disconnect_contact_job(contact, _id)
        usr.delete_job(_id)
        return redirect(url_for('get_jobs'))

@app.route("/db/")
@login_required
def testdb():
    """
    Test method to see what the database holds.
    """
    db = get_database()
    jobs = db["jobs"]
    items = jobs.find()
    for item in items:
        print(item)
    return render_template('addJobs.html', text="Hello World How You Doin")

# routes for skills
@app.route('/jobs/skills', methods=['POST','GET'])
@login_required
def get_skills():
    """
    A page that lists skills added by a user.
    You can add skills to individual jobs.
    """

    if request.method == 'GET':
        results = User().get_skills()
        return render_template('skills.html', results=results, function=query.skill_appears)

    if request.method == 'POST':
        add_skill = User().add_new_skill()

        return redirect(url_for("get_skills"))

# routes for contacts
# TODO: this doesn't do anything.
@app.route('/contacts/', methods=['GET'])
@login_required
def get_contacts():
    """
    Returns all the contacts stored by a user.
    """
    if request.method == 'GET':
        results = User().get_contacts()
        return render_template('contacts.html', results=results)

@app.route('/contacts/add', methods=['POST', 'GET'])
@login_required
def add_contact():
    """
    Allows a user to add contact.
    TODO: figure out schmea for this
    TODO: 
    """
    if request.method == 'GET':
        return render_template('addContact.html')
    
    if request.method == 'POST':
        User().add_new_contact()
        return redirect(url_for('get_contacts'))

@app.route('/contacts/<_id>', methods=['GET'])
@login_required
def view_contact(_id):
    results = User().find_contact(_id)
    if results is None:
        return "Error: Contact Not Found"
    else:
        return render_template('contact.html', contact=results)

@app.route('/contacts/edit/<_id>', methods=['GET'])
@login_required
def edit_contact(_id):
    results = User().find_contact(_id)
    if results is None:
        return "Error: Job Not Found"
    else:
        return render_template('editContact.html', contact=results)

@app.route('/contacts/update/<_id>', methods=['POST'])
@login_required
def update_contact(_id):
    User().edit_contact(_id)
    url = "/contacts/" + _id
    return redirect(url, code=302)

@app.route('/contacts/jobs/<_id>', methods=['GET'])
@login_required
def related_jobs(_id):
    usr = User()
    contact = usr.find_contact(_id)
    results = usr.find_related_jobs(contact["company"], contact["user"])
    return render_template('jobToContact.html', jobs=results, contact=contact)

@app.route('/contacts/connect/job/<_id>', methods=['GET'])
@login_required
def connect_contact_job(_id):
    User().connect_contact_job(_id)
    url = "/contacts/" + _id
    return redirect(url, code=302)

@app.route('/contacts/disconnect/<contact_id>/<job_id>', methods=['GET'])
@login_required
def disconnect_contact_job(contact_id, job_id):
    User().disconnect_contact_job(contact_id, job_id)
    url = "/contacts/" + contact_id
    return redirect(url, code=302)

@app.route('/delete/contacts/<_id>', methods=['GET'])
@login_required
def delete_contact(_id):
    usr = User()
    contact = usr.find_contact(_id)
    if contact is None:
        return "Error: Contact Not Found"
    else:
        if contact["job"] is not None:
            usr.disconnect_contact_job(_id, contact["job"])
        usr.delete_contact(_id)
        return redirect(url_for('get_contacts'))

# routes for user
@app.route('/user/signup/', methods=['POST', 'GET'])
def user_signup():
    """
    Responsible for the creation of a new user. It checks to see whether or not if a username is taken.
    In the event that a username is not taken, a new account is created. 
    In the event that username is taken, prevents user from creating an account.
    """
    
    # check to see if a user is already logged in
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('home'))

    if request.method == 'POST':
        new_user = User().signup()

        # in the event a username is already taken
        if new_user == False:
            flash('Username already taken, please try again')
            return render_template("signup.html")

        return redirect(url_for("home"))
    
    if request.method == 'GET':
        return render_template("signup.html")

@app.route('/user/login/', methods=['POST', 'GET'])
def user_login():
    """
    Used for authenticating a user and giving them access to the application.
    """

    # check to see if a user is already logged in
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template("login.html")
    
    if request.method == 'POST':
        user = User().login()

        # login failed
        if not user:
            flash("Invalid login. Please try again.")
            return render_template("login.html")

        return redirect(url_for('home'))

@app.route('/user/logout')
@login_required
def user_logout():
    User().logout()
    # return 'you have successfully logged out'
    # return redirect(url_for('user_login'))
    return render_template('logout.html')


@app.route('/home')
@login_required
def home():
    """
    Upon successful login/account creation, default landing page for users.
    """
    return render_template("home.html", username=f"{session['username']}")


if __name__ == '__main__':
    app.run(port=8000, debug=True)