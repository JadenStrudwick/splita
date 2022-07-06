from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
import datetime

# Create the SQL database
db = SQLAlchemy()

# User class
class User(UserMixin, db.Model):
    __tablename__ = 'USERS'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text)
    email = db.Column(db.Text, unique = True)
    hashedpassword = db.Column(db.Text)
    lastLogout = db.Column(db.DateTime)
    themeColor = db.Column(db.Text)

    def __init__(self, name, email, hashedpassword):
        self.name = name
        self.email = email
        self.hashedpassword = hashedpassword
        self.lastLogout = datetime.datetime.now()
        self.themeColor = "#ffa6ff"

# Household class that contains bills
class Household(db.Model):
    __tablename__ = 'HOUSEHOLDS'
    id = db.Column(db.Integer, primary_key = True)
    owner_id = db.Column(db.Integer)
    name = db.Column(db.Text)

    def __init__(self, owner_id, name):
        self.owner_id = owner_id
        self.name = name

# Householdmember class which stores User IDs and the Household IDs they're part of
class Householdmember(db.Model):
    __tablename__ = 'HOUSEHOLDMEMBERS'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    household_id = db.Column(db.Integer)

    def __init__(self, user_id, household_id):
        self.user_id = user_id
        self.household_id = household_id

# Bill class
class Bill(db.Model):
    __tablename__ = 'BILLS'
    id = db.Column(db.Integer, primary_key = True)
    household_id = db.Column(db.Integer)
    name = db.Column(db.Text)
    amount = db.Column(db.Float)
    date_added = db.Column(db.DateTime)
    added_by = db.Column(db.Integer)

    def __init__(self, household_id, name, amount, date_added, added_by):
        self.household_id = household_id
        self.name = name
        self.amount = amount
        self.date_added = date_added
        self.added_by = added_by

# billPayment class which stores the User IDs and the Bill IDs they've paid for
class billPayment(db.Model):
    __tablename__ = 'BILLPAYMENTS'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    bill_id = db.Column(db.Integer)

    def __init__(self, user_id, bill_id):
        self.user_id = user_id
        self.bill_id = bill_id

# Init the database with a single Household and some example Users and Bills
def dbinit():
    # Create Users who are members of a Household
    user_list = [
        User("Jaden", "jaden@gmail.com", generate_password_hash("jaden")),
        User("Tyson", "tyson@gmail.com", generate_password_hash("tyson")),
        User("Jacob", "jacob@gmail.com", generate_password_hash("jacob")),
        User("Arnav", "arnav@gmail.com", generate_password_hash("arnav"))
    ]
    db.session.add_all(user_list)

    # Get user of "jaden@gmail.com"
    jaden = User.query.filter_by(email="jaden@gmail.com").first()

    # Create Household
    jadenHouseHold = Household(jaden.id, "House1")
    db.session.add(jadenHouseHold)

    # Get Household created by Jaden
    house1 = Household.query.filter_by(owner_id=jaden.id).first()

    # Add the Users to the Household
    members = [
        Householdmember(User.query.filter_by(email="jaden@gmail.com").first().id, house1.id),
        Householdmember(User.query.filter_by(email="tyson@gmail.com").first().id, house1.id),
        Householdmember(User.query.filter_by(email="jacob@gmail.com").first().id, house1.id),
        Householdmember(User.query.filter_by(email="arnav@gmail.com").first().id, house1.id),
    ]
    db.session.add_all(members)

    # Add Bills to the Household
    bill_list = [
        Bill(house1.id, "Water", 250.40, datetime.datetime.now(), jaden.id),
        Bill(house1.id, "Gas", 375.80, datetime.datetime.now(), jaden.id),
        Bill(house1.id, "Dinner", 50.90, datetime.datetime.now(), jaden.id)
    ]
    db.session.add_all(bill_list)

    # Commit changes to database file
    db.session.commit()