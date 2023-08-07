# will be using this to house the methods that insert into our database
from get_db import get_database
from bson import ObjectId

db = get_database()

# job collection
jobs_db = db["jobs"]

def add_new_job(company, position, date, status, username):
    """
    Adds job to the job database.
    """
    # TODO: need to figure out how we want to add skills/contact
    # TODO: determine if we need to return new job ID for later use
    # TODO: do we want to return true if successful?
    # TODO: make dropdown for status, make applied default
    job = {
        "company": company, "position": position,
        "date": date, "status": status, "skills": [], "contacts": [], "user": username
    }

    new_job = jobs_db.insert_one(job)

def get_jobs(username):
    result = list(jobs_db.find({'user': username}))
    for jobs in result:
        jobs["_id"] = str(jobs["_id"])
    return result

def find_job(_id):
    job = jobs_db.find_one({"_id": ObjectId(_id)})
    return {
        "company": job['company'], "position": job['position'],
        "date": job['date'], "status": job['status'], "skills": job['skills'],
        "contacts": job['contacts'], "user": job['user'], "_id": str(job["_id"])
    }

def update_job(_id, company, position, date, status):
    jobs_db.update_one({"_id": ObjectId(_id)}, {"$set": {"company": company,
                                                         "date": date, "position": position, "status": status}})

def add_job_contact(_id, contact_id):
    job = find_job(_id)
    contacts = job["contacts"]
    contacts.append(contact_id)
    jobs_db.update_one({"_id": ObjectId(_id)}, {"$set": {"contacts": contacts}})

def remove_job_contact(job_id, contact_id):
    #TODO: test this for error like adding contact to job

    job = find_job(job_id)
    contacts = job["contacts"]
    contacts.remove(contact_id)
    jobs_db.update_one({"_id": ObjectId(job_id)}, {"$set": {"contacts": contacts}})

def delete_job(_id):
    jobs_db.delete_one({"_id": ObjectId(_id)})

# skills collection
skills_db = db["skills"]

def get_skills(username):
    result = list(skills_db.find({'user': username}))
    return result


def add_skill(user, skill, comfort):
    """
    Adds a skill to the skills database.
    """
    skill = skill.title()
    skill_to_add = {
        "user": user,
        "skill": skill,
        "comfort": comfort
    }

    if not skills_db.find_one(skill_to_add):
        skills_db.insert_one(skill_to_add)
    else:
        return 1

def update_skill(job_id, new_skills):
    job = find_job(job_id)
    old_skills = job["skills"]
    old_skills.clear()
    jobs_db.update_one({"_id": ObjectId(job_id)}, {"$set": {"skills": new_skills}})

def skill_appears(skill):
    """
    Returns the number of jobs that contain a skill
    TODO: count might not work
    """
    return jobs_db.count_documents({"skills": skill})

# TODO: find_skill, update_skill
def find_skill(_id):
    skill = skills_db.find_one({"_id": ObjectId(_id)})
    return { "skill": skill['skill'], "comfort": skill['comfort'], "_id": str(skill["_id"]) }

def delete_skill(_id):
    # TODO: change name of skill in other jobs with same skill
    skill_obj = skills_db.find_one({"_id": ObjectId(_id)})
    name = skill_obj['skill']
    print(name)

    jobs = list(jobs_db.find({'skills': name}))
    x = len(jobs)
    
    print(f"Jobs with {name} before deletion: {x}")

    for job in jobs:
        if name in job['skills']:
            updated_skill_list = []

            for skill in job['skills']:
                if skill != name:
                    updated_skill_list.append(skill)
                # print(f"Job: {job}")
            
            jobs_db.update_one({"_id": ObjectId(job['_id'])}, {"$set": {"skills":updated_skill_list}})

    jobs = list(jobs_db.find({'skills': name}))
    z = len(jobs)

    print(f"Jobs with {name} after deletion: {z}")

    # delete skill from database
    skills_db.delete_one({"_id": ObjectId(_id)})


# contact collection
contacts_db = db["contacts"]

def add_new_contact(name, company, email, phone, username):
    """
    Adds new contact to the database.
    """
    contact = {
        "name": name, "company": company, "email": email,
        "phone": phone, "user": username, "job": None
    }

    new_contact = contacts_db.insert_one(contact)

def get_contacts(username):
    result = list(contacts_db.find({'user': username}))
    return result

def find_contact(_id):
    contact = contacts_db.find_one({"_id": ObjectId(_id)})
    return {
        "name": contact["name"], "company": contact["company"], "email": contact["email"], "phone": contact["phone"],
        "_id": str(contact["_id"]), "user": contact["user"], "job": contact["job"]
    }

def update_contact(_id, name, company, email, phone):
    contacts_db.update_one({"_id": ObjectId(_id)}, {"$set": {"name": name, "company": company,
                                                             "email": email, "phone": phone}})

def update_contact_job(_id, job_id):
    contacts_db.update_one({"_id": ObjectId(_id)}, {"$set": {"job": job_id}})

def delete_contact(_id):
    contacts_db.delete_one({"_id": ObjectId(_id)})

# login collection
login = db['login']

def add_new_user(username, password, first_name, last_name, reset_pin):
    """
    Method to add a new user to the databse. Checks first to see if a desired username exists, if it does
    not already exist in our database then it will create the account. In the event that it does exist,
    it will not create a new account and tell the user to try again.
    """
    # TODO: guard clauses to be used for later
    # make sure username is not empty string
    # if len(username) < 1:
    #     print("Empty string passed for username")
    #     return False

    # make sure that password contains at least 5 characters
    # if len(password) < 5:
    #     print("Password needs at least 5 characters.")
    #     return False

    # make sure that a pin of at least 4 digits is passed
    # if len(reset_pin) < 4:
    #     print("Pin too short")
    #     return False

    # TODO: tell user when a username is taken to try again
    
    valid_username = username_available(username)

    if valid_username:
        new_user = {
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "reset_pin": reset_pin
        }

        new_login = login.insert_one(new_user)

        return new_login.inserted_id
    else:
        return False

def username_available(username):
    """
    Returns true if username is available, else returns false. This is a helper method to determine whether or not
    an account can be created.
    """
    result = login.find_one({'username':username})

    print(f"New login created: {result == None}")
    
    return result == None

def get_user(user_id):
    """
    Searches collection for a user via their ID. Returns a user and their information, this will be used for controlling
    sessions to only allow authenticated users to see the site.
    """

    user = login.find_one({'_id': user_id})

    return user['username']

def login_user(username, password):
    """
    Searches collection for matching username and password combo, if a match is found then user is loaded.
    
    TODO: determine whether or not to warn about invalid username/password combo. also decide whether to say if username doesn't exist.
    """
    user = login.find_one({'username': username, 'password': password})

    if user == None:
        print("No matches found in database.")
        return False

    print(f'{user}')
    print("User has been found!")
    return username
