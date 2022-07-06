from flask import Flask, render_template, request, redirect, session, flash
from werkzeug import security
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import datetime

# Create the flask app and configure
app = Flask(__name__)
app.secret_key = "JADENSTRUDWICK"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///todo.sqlite'
app.config['SQLALCHMEY_TRACK_MODIFICATIONS'] = False

# Set up database and init
from db_schema import Householdmember, billPayment, db, User, Household, Bill, dbinit
db.init_app(app)

# Change to True to reset the database everytime the server is started
resetdb = False
if resetdb:
    with app.app_context():
        db.drop_all()
        db.create_all()
        dbinit()

# Setup LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    # If user is authenticated, redirect to their dashboard
    if current_user.is_authenticated:
        return redirect('/dashboard')
    
    # Otherwise, redirect to registration page
    return redirect('/register')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Clear previous flashes
    session.pop('_flashes', None)

    # If user is authenticated, redirect to their dashboard
    if current_user.is_authenticated:
        return redirect('/dashboard')

    # If GET request, render the registration template
    if request.method == "GET":
        return render_template('register.html')

    # If POST request, attempt to register the User
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"]

        hashedpassword = security.generate_password_hash(password)

        if password != confirmPassword:
            flash("Passwords do not match. Please try again")
            return render_template('register.html')

        # Create the new user
        newUser = User(name, email, hashedpassword)
        db.session.add(newUser)
        db.session.commit()
        
        # Log in the new user
        user = User.query.filter_by(email=email).first()
        login_user(user)
        return redirect('/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear previous flashes
    session.pop('_flashes', None)

    # If user is authenticated, redirect to their dashboard
    if current_user.is_authenticated:
        return redirect('/dashboard')

    # If GET request, render the login template
    if request.method == "GET":
        return render_template('login.html')

    # If POST request, attempt to login User
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Get the user with this email
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("No account registered with this email. Please register instead")
            print("1")
            return render_template('login.html')
        elif not security.check_password_hash(user.hashedpassword, password):
            flash("Incorrect password. Please try again")
            print("2")
            return render_template('login.html')

        login_user(user)
        return redirect('/dashboard')

@app.route('/logout')
def logout():
    user = User.query.filter_by(id=current_user.id).first()
    user.lastLogout = datetime.datetime.now()
    db.session.commit()

    logout_user()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    # Clear previous flashes
    session.pop('_flashes', None)

    # Get the IDs of each household the user is a member of
    userHouseholdPairs = Householdmember.query.filter_by(user_id=current_user.id).all()

    # Get the bills and households for the current user
    currentUserHouseHolds = []
    currentUserBills = []
    for userHouseholdPair in userHouseholdPairs:
        currentUserHouseHolds.append(Household.query.filter_by(id=userHouseholdPair.household_id).first())
        currentUserBills.append(Bill.query.filter_by(household_id=userHouseholdPair.household_id).all())

    # Get the Ids of all the bills the current user has paid for    
    currentUserPaidBills = billPayment.query.filter_by(user_id=current_user.id).all()
    currentUserPaidBillsIds = []
    for paidBill in currentUserPaidBills:
        currentUserPaidBillsIds.append(paidBill.bill_id)

    # Get the members and owners for currentUserHouseHolds
    membersOfCurrentUserHouseHolds = []
    ownersOfCurrentUserHouseHolds = []
    for household in currentUserHouseHolds:
        ownersOfCurrentUserHouseHolds.append(household.owner_id)

        membersOfSingularHouseHold = []
        houseHoldMembers = Householdmember.query.filter_by(household_id=household.id).all()
        for houseHoldMember in houseHoldMembers:
            membersOfSingularHouseHold.append(User.query.filter_by(id=houseHoldMember.user_id).first())
        membersOfCurrentUserHouseHolds.append(membersOfSingularHouseHold)

    # Get all the bill payments relevant to the current user (includes their own payments and payments of their house mates)
    currentUserBillPayments = []
    for houseHoldBills in currentUserBills:
        householdBillPayments = []
        for bill in houseHoldBills:
            usersThatHavePaidCurrentBill = []
            billPaymentsForCurrentBill = billPayment.query.filter_by(bill_id=bill.id).all()
            for billpayment in billPaymentsForCurrentBill:
                usersThatHavePaidCurrentBill.append(User.query.filter_by(id=billpayment.user_id).first())
            householdBillPayments.append(usersThatHavePaidCurrentBill)
        currentUserBillPayments.append(householdBillPayments)
    
    # Handle notification flashing for new bills that have been added the last time the user logged in
    for householdBills in currentUserBills:
        for individualBill in householdBills:
            if individualBill.date_added > current_user.lastLogout and individualBill.added_by != current_user.id :
                formatedAmount = "£{:,.2f}".format(individualBill.amount / len(membersOfCurrentUserHouseHolds[currentUserBills.index(householdBills)]))                
                flash(f"{individualBill.name} in {Household.query.filter_by(id=individualBill.household_id).first().name} ({formatedAmount})")

    # If bill has been paid by everyone, then we can delete it
    # Delete bills if they have been paid by everyone in a household
    for household in currentUserHouseHolds:
        houseHoldMembers = Householdmember.query.filter_by(household_id=household.id).all()
        houseHoldBills = Bill.query.filter_by(household_id=household.id).all()
        for bill in houseHoldBills:
            # If the length of bill payments for the current bill is equal to number of members in the household
            # Then the bill has been fully paid and should be removed
            if (len(billPayment.query.filter_by(bill_id=bill.id).all()) == len(houseHoldMembers)):
                    billPayment.query.filter_by(bill_id=bill.id).delete()
                    Bill.query.filter_by(id=bill.id).delete()
                    db.session.commit()
        
    # If currentUserHouseHolds is empty, User should be redirect to addHouseHold page to prevent a blank dashboard from being displayed
    if len(currentUserHouseHolds) == 0:
        return redirect('/addHouseHold')

    # Get user's theme
    hex = current_user.themeColor

    return render_template('dashboard.html', hex=hex[1:], households=currentUserHouseHolds, bills=currentUserBills, members=membersOfCurrentUserHouseHolds, user=current_user, owners=ownersOfCurrentUserHouseHolds, paidBillsId=currentUserPaidBillsIds, allBillPayments=currentUserBillPayments)

@app.route('/addBill/<userId>/<householdId>', methods=['GET', 'POST']) 
@login_required
def addBill(userId, householdId):
    # If the userId from the URL does not match the current user, do not add the bill
    if int(current_user.id) != int(userId):
        return redirect('/dashboard')

    # Check that the user is a member of the household
    userHouseholdPair = Householdmember.query.filter_by(user_id=userId, household_id=householdId)
    if userHouseholdPair is None:
        return redirect('/dashboard')

    db.session.add(Bill(householdId,request.form["billName"],float(request.form["amount"]),datetime.datetime.now(), userId))
    db.session.commit()
    return redirect('/dashboard')

@app.route('/payBill', methods=["POST"])
@login_required
def payBill():
    # Get input data from POST request
    userId = request.form["userId"]
    houseHoldId = request.form["houseHoldId"]
    billId = request.form["billId"]

    # If the userId from URL does not match the current user, do not pay the bill
    if int(current_user.id) != int(userId):
        return "ERROR: REQUEST NOT FROM CURRENT USER"

    # Check that the bill being paid is from the current household
    bill = Bill.query.filter_by(id=billId).first()
    if int(bill.household_id) != int(houseHoldId):
        return "ERROR: BILL IS NOT IN THIS HOUSEHOLD"

    # Now we can safely pay the pill
    db.session.add(billPayment(userId, billId))
    db.session.commit()

    return "OK"

@app.route('/deleteBill', methods=["POST"])
@login_required
def deleteBill():
    # Get input data from POST request
    userId = request.form["userId"]
    houseHoldId = request.form["houseHoldId"]
    billId = request.form["billId"]

    # If the userId from URL does not match the current user, do not delete
    if int(current_user.id) != int(userId):
        return "ERROR: REQUEST NOT FROM CURRENT USER"

    # Check that the household is being deleted by the owner
    household = Household.query.filter_by(owner_id=current_user.id, id=houseHoldId)
    if household is None:
        return "ERROR: USER IS NOT OWNER OF THE HOUSEHOLD"

    # Check that the bill being deleted is from the current household
    bill = Bill.query.filter_by(id=billId).first()
    if int(bill.household_id) != int(houseHoldId):
        return "ERROR: BILL IS NOT IN THIS HOUSEHOLD"

    # Now we can safely delete the bill and all payments
    billPayment.query.filter_by(bill_id=billId).delete()
    Bill.query.filter_by(id=billId).delete()
    db.session.commit()
    return "OK"

@app.route('/addHouseHold', methods=["GET", "POST"])
@login_required
def addHouseHold():
    if request.method == "POST":
        # Create the new Household
        db.session.add(Household(current_user.id,request.form["name"]))
        db.session.commit()

        # Add owner to household
        newHouseHold = Household.query.filter_by(owner_id=current_user.id, name=request.form["name"]).all()[-1] # Get the last added household that matches
        db.session.add(Householdmember(current_user.id,newHouseHold.id))
        db.session.commit()

        # Add household members
        emails = request.form["emails"].split(',')
        for email in emails:
            # Get User for respective email if the account exists
            userToAdd = User.query.filter_by(email=email).first()
            
            # If account exists, add the account to the household
            if userToAdd is not None:
                db.session.add(Householdmember(userToAdd.id,newHouseHold.id))
                db.session.commit()

        return redirect('/dashboard')

    # Get user's theme
    hex = current_user.themeColor

    return render_template('addHouseHold.html', hex=hex[1:])

@app.route('/deleteHouseHold', methods=["POST"])
@login_required
def deleteHouseHold():
    # Get input data from POST request
    userId = request.form["userId"]
    houseHoldId = request.form["houseHoldId"]

    # Check that the request is comming from the current user
    if int(current_user.id) != int(userId):
        return "ERROR: REQUEST NOT FROM CURRENT USER"

    # Check that the household is being deleted by the owner
    household = Household.query.filter_by(owner_id=current_user.id, id=houseHoldId)
    if household is None:
        return "ERROR: USER IS NOT OWNER OF THE HOUSEHOLD"

    # Get all the bills associated with the household
    bills = Bill.query.filter_by(household_id=houseHoldId).all()

    # Delete paid bills related to the household
    for bill in bills:
        billPayment.query.filter_by(bill_id=bill.id).delete()

    # Delete bills related to the household
    Bill.query.filter_by(household_id=houseHoldId).delete()

    # Delete household member relationships related to the household
    Householdmember.query.filter_by(household_id=houseHoldId).delete()

    # Delete the household itself
    Household.query.filter_by(id=houseHoldId).delete()

    # Commit changes
    db.session.commit()
    return "OK"

@app.route('/leaveHouseHold', methods=["POST"])
@login_required
def leaveHouseHold():
    # Get input data from POST request
    userId = request.form["userId"]
    houseHoldId = request.form["houseHoldId"]

    # If the userId from URL does not match the current user, do not delete
    if int(current_user.id) != int(userId):
        return "ERROR: REQUEST NOT FROM CURRENT USER"

    # Delete household membership entry for current user
    Householdmember.query.filter_by(user_id=userId, household_id=houseHoldId).delete()
    db.session.commit()

    return "OK"

@app.route('/settings')
@login_required
def settings():
    # Get user's theme
    hex = current_user.themeColor

    return render_template('settings.html', hex=hex[1:])

@app.route('/changeColor', methods=["POST"])
@login_required
def changeColor():
    # Get new theme color
    colorHex = request.form["color"]
    
    # Update user's theme
    current_user.themeColor = colorHex
    db.session.commit()

    return redirect('/settings')

@app.route('/changePassword', methods=["POST"])
@login_required
def changePassword():
    # Clear previous flashes
    session.pop('_flashes', None)

    # Get form data
    oldPassword = request.form["oldPassword"]
    newPassword = request.form["newPassword"]
    confirmNewPassword = request.form["confirmNewPassword"]

    # If password hashes don't match, flash the user
    if not security.check_password_hash(current_user.hashedpassword, oldPassword):
        flash("Incorrect password. Please try again")

        # Get user's theme
        hex = current_user.themeColor
        return render_template('settings.html', hex=hex[1:])

    # If new passwords don't match, flash the user
    if newPassword != confirmNewPassword:
        flash("Passwords do not match. Please try again")
        
        # Get user's theme
        hex = current_user.themeColor
        return render_template('settings.html', hex=hex[1:])

    current_user.hashedpassword = security.generate_password_hash(newPassword)
    db.session.commit()

    # Get user's theme
    hex = current_user.themeColor
    return render_template('settings.html', hex=hex[1:])