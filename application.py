from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.contrib import *
from readScale import *
from barcode2Weight import *
from barcode2OrderQuantity import *
from submit_to_wms import *
from check_employee_id import *
from retrieve_order import *
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import  NumberRange

from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# unit, remove submit button, positive numbers, non integer count values, check on the backend
# remove barcode entries

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'supersecretkey'
Session(app)

# store these as global variables and update later
MOVE_number = 0
current_target_qty = 0
current_product_weight = 0
current_weight_unit = 0
employee_id = 0
scanner_id = 0


# classes for the form validation
class employee_login(FlaskForm):
    employee_id_wtf = IntegerField("Employee ID ",
                                   [NumberRange(min=0, max=10**10, message="This ID is too long or too short")])
    rf_scanner_id_wtf = IntegerField("RF Scanner ID ",
                                     [NumberRange(min=0, max=10**10, message="This ID is too long or too short")])
    submit = SubmitField("Submit")


class manual_entry(FlaskForm):
    product_weight = FloatField("Product Weight ",
                                  [NumberRange(min=0, max=10**10, message="This weight is invalid")])
    target_count = IntegerField("Target Count ", [NumberRange(min=0, max=10**10, message="This quantity is invalid")])
    weight_unit = SelectField(u'Weight Unit ',
                              choices=[('g', 'Grams'), ('kg', 'Kilograms'), ('oz', 'Ounces'), ('lbs', 'Pounds')])
    submit = SubmitField("Submit")


# Define confidence interval (the percentage of the weight within which you want the desired scale reading)
conf_int = .5  # can also define this as an absolute value if that works better
within_target_count = 0.5  # this means that if the count is within .5 of the target, the count is assumed to be


@app.route("/", methods=['GET', 'POST'])
def begin():
    # if user reached route via POST (as by submitting a user id)
    login_form = employee_login(meta={'csrf': False})
    global employee_id
    global scanner_id

    if login_form.validate_on_submit():
        employee_id = login_form.employee_id_wtf.data
        scanner_id = login_form.rf_scanner_id_wtf.data

        # check whether the employee id is correct using wms system
        if not check_employee_id(employee_id, scanner_id):
            flash("Employee ID or Scanner ID are incorrect")
            return redirect(url_for("begin"))

        return redirect(url_for("enter_product_number"))

    # else if user reached route via GET (after logging out)
    elif request.method == "POST":
        flash("Please login")
        return render_template("begin.html", form=login_form, first_load=False, employee_id=employee_id)
    else:
        flash("Please login")
        return render_template("begin.html", form=login_form, first_load=True, employee_id=employee_id)


@app.route("/enter_product_number", methods=['GET', 'POST'])
def enter_product_number():
    manual_entry_form = manual_entry(meta={'csrf': False})
    if not employee_id:
        return redirect(url_for("begin"))

    # if user filled out the manual entry form
    if manual_entry_form.validate_on_submit():
        global current_weight_unit
        global current_product_weight
        global current_target_qty

        current_weight_unit = manual_entry_form.weight_unit.data
        current_product_weight = manual_entry_form.product_weight.data
        current_target_qty = manual_entry_form.target_count.data
        return redirect(url_for("count"))

    # if the user submitted just the button
    if request.method == "POST":
        global MOVE_number

        # determine whether a manual order is placed, or whether an order is retrieved
        count_type = request.form.get("count_type")

        if count_type == "retrieve_order":
            # get the required info from the WMS
            [MOVE_number, current_product_weight, current_weight_unit, current_target_qty] = retrieve_order(scanner_id)
            return redirect(url_for("count"))
        else:
            return render_template("enter_barcode.html", form=manual_entry_form, employee_id=employee_id)

    # else if user reached route via GET (as after completing the count)
    elif request.method == "GET":
        return render_template("enter_barcode.html", form=manual_entry_form, employee_id=employee_id, first_load=True)
    else:
        return render_template("enter_barcode.html", form=manual_entry_form, employee_id=employee_id)


# set up website for the actual counting process
@app.route("/count", methods=["GET", "POST"])
def count():
    if not employee_id:
        return redirect(url_for("begin"))

    # if user completed count
    if request.method == "POST":

        # check whether the count was completed successfully
        submit_condition = request.form.get("wms_submit")
        if submit_condition == "1":
            # call the function to submit completed count to the WMS
            submit_to_wms(MOVE_number)
            print("submitted to wms")

        return redirect(url_for("enter_product_number"))

    # else if user reached route via GET (after entering the product barcode)
    else:
        return render_template("count.html", prod_weight=current_product_weight, weight_unit=current_weight_unit,
                               target_count=current_target_qty,
                               target_weight=current_product_weight * current_target_qty,
                               employee_id=employee_id)


# this function serves the javascript on /count, it returns the current weight, the current count, and whether the
# target has been reached
@app.route("/check_weight")
def check_weight():
    if not employee_id:
        return redirect(url_for("begin"))

    #current_reading = accurate_reading(current_weight_unit)
    #current_reading = 16 #for testing purposes
    print(current_reading)
    current_count = current_reading / current_product_weight

    # counting status is -1 if the count is under, 0 if its correct, 1 if its over
    counting_status = -1
    if current_target_qty - within_target_count <= current_count <= current_target_qty + within_target_count:
        counting_status = 0
    if current_count > current_target_qty + within_target_count:
        counting_status = 1

    return_list = [round(current_count), current_reading, counting_status]

    return jsonify(return_list)


@app.route("/logout")
def logout():
    # Forget any id
    global employee_id
    global scanner_id

    employee_id = 0
    scanner_id = 0

    # Redirect user to begin
    return redirect(url_for("begin"))


app.run()
