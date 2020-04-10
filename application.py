from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, session
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import NumberRange

# import helper functions
from readScale import *
from barcode2Weight import *
from barcode2OrderQuantity import *
from submit_to_wms import *
from check_employee_id import *
from retrieve_order import *

# Configure application see here for details:
# https://flask.palletsprojects.com/en/0.12.x/quickstart/#a-minimal-application
app = Flask(__name__)

# Configure session to use filesystem (https://pythonhosted.org/Flask-Session/#quickstart)
app.config["SESSION_TYPE"] = "filesystem"  # this needs to be set to use a secret key, which is required to use wtforms
app.secret_key = 'supersecretkey'
host_address = '127.0.0.1'
Session(app)

# store these as global variables and update later
MOVE_number_psoft = 0
current_target_qty = 0
current_product_weight = 0
current_weight_unit = 0
manual_order = False
employee_id = 0
scanner_id = 0
dc_id = 0

# these variables are used to indicate error messages, if the submission to the WMS was impossible
wms_submit_unsuccessful = False


# classes for the form validation
class employee_login(FlaskForm):
    # these determine the visual appearance of the forms
    style_EID = {'class': 'form-control', 'autofocus': 'true', 'placeholder': 'Employee ID'}
    style_RFID = {'class': 'form-control', 'placeholder': 'Scanner ID'}
    style_DCID = {'class': 'form-control', 'placeholder': 'DC ID'}

    # these define the field types in this form, and include some validators to make sure the input is acceptable.
    # More info here: https://wtforms.readthedocs.io/en/stable/crash_course.html
    employee_id_wtf = IntegerField("Employee ID ",  # this is the label of this field
                                   [NumberRange(min=0, max=10 ** 10, message="This ID is too long or too short")],  #
                                   # these are validators and a customized error message
                                   render_kw=style_EID)  # this specifies some of the visual appearance of the field
    rf_scanner_id_wtf = IntegerField("RF Scanner ID ",
                                     [NumberRange(min=0, max=10 ** 10, message="This ID is too long or too short")],
                                     render_kw=style_RFID)
    dc_id = IntegerField("DC ID ",
                         [NumberRange(min=0, max=10 ** 10, message="This ID is too long or too short")],
                         render_kw=style_DCID)
    submit = SubmitField("Submit")


class manual_entry(FlaskForm):
    # these determine the visual appearance of the forms
    style_pw = {'class': 'form-control', 'placeholder': 'Product Weight'}
    style_tc = {'class': 'form-control', 'placeholder': 'Target Count'}
    style_drop_down = {'class': 'custom-select'}

    # these define the field types in this form, and include some validators to make sure the input is acceptable.
    # More info here: https://wtforms.readthedocs.io/en/stable/crash_course.html
    product_weight = FloatField("Product Weight ",
                                [NumberRange(min=0, max=10 ** 10, message="This weight is invalid")],
                                render_kw=style_pw)
    target_count = IntegerField("Target Count ", [NumberRange(min=0, max=10 ** 10, message="This quantity is invalid")],
                                render_kw=style_tc)
    weight_unit = SelectField(u'Weight Unit ',
                              choices=[('g', 'Grams'), ('kg', 'Kilograms'), ('oz', 'Ounces'), ('lbs', 'Pounds')],
                              render_kw=style_drop_down)
    submit = SubmitField("Submit")


# Define confidence interval (the percentage of the weight within which you want the desired scale reading)
within_target_count = 0.5  # this means that if the count is within .5 of the target, the count is assumed to be


# see https://flask.palletsprojects.com/en/0.12.x/quickstart/#a-minimal-application for more info on the function
# setup essentially the next line defines the url of the function after that, and the methods allowed for the url (
# form submission - post, simple load - get)
@app.route("/", methods=['GET', 'POST'])
def begin():
    # set up the wtform for later evaluation, csrf token turned off for convenience:
    # https://flask-wtf.readthedocs.io/en/latest/csrf.html
    login_form = employee_login(meta={'csrf': False})
    global employee_id
    global scanner_id
    global dc_id
    global wms_submit_unsuccessful

    # if the employee login form was successfully submitted, without errors in the wtf validations
    if login_form.validate_on_submit():

        # get the data from the forms
        employee_id = login_form.employee_id_wtf.data
        scanner_id = login_form.rf_scanner_id_wtf.data
        dc_id = login_form.dc_id.data
        check_id_val = check_employee_id(employee_id, scanner_id, dc_id)

        # check whether the employee id is correct using wms system and matches rf id and dc id
        if check_id_val != 'successful':
            employee_id = 0
            scanner_id = 0
            dc_id = 0

            if check_id_val == 'no connection':
                return render_template("begin.html", form=login_form, first_load=True, employee_id=employee_id,
                                       connection=False, ID_found=True)
            if check_id_val == 'employee not found':
                return render_template("begin.html", form=login_form, first_load=True, employee_id=employee_id,
                                       connection=True, ID_found=False)

        # if the credentials are correct, redirect to the next page to start order selection
        return redirect(url_for("setup_count"))

    # if the form was incorrectly filled out, first_load=False indicates to the wtform html to show the appropriate
    # errors
    elif request.method == "POST":

        # flash is a way of showing messages to the user, they are not necessary, but can be helpful
        flash("Please login")
        return render_template("begin.html", form=login_form, first_load=False, employee_id=employee_id,
                               connection=True, ID_found=True)

    # else if user reached route via GET (after logging out), first_load shows the html to hide wtforms errors
    else:
        # flash is a way of showing messages to the user, they are not necessary, but can be helpful
        flash("Please login")

        # reset credentials
        employee_id = 0
        scanner_id = 0
        dc_id = 0
        wms_submit_unsuccessful = False
        return render_template("begin.html", form=login_form, first_load=True, employee_id=employee_id,
                               connection=True, ID_found=True)


# this page is intended to set up the counting process, by either retrieving the current order, or entering a manual
# order form
@app.route("/setup_count", methods=['GET', 'POST'])
def setup_count():
    # set up the manual order form, again no csrf token, info here: https://flask-wtf.readthedocs.io/en/latest/csrf.html
    manual_entry_form = manual_entry(meta={'csrf': False})

    # ensure user credentials are validated
    if not employee_id:
        return redirect(url_for("begin"))

    # if user filled out the manual entry form
    if manual_entry_form.validate_on_submit():
        # retrieve data from submission form and redefine global variables
        global current_weight_unit
        global current_product_weight
        global current_target_qty
        global manual_order

        current_weight_unit = manual_entry_form.weight_unit.data
        current_product_weight = manual_entry_form.product_weight.data
        current_target_qty = manual_entry_form.target_count.data
        manual_order = True

        # lead the user to the actual count site
        return redirect(url_for("count"))

    # if the user submitted just the button
    if request.method == "POST":

        # determine whether a manual order is placed, or whether an order is retrieved
        count_type = request.form.get("count_type")

        # if the user clicked the button to retrieve the order on their RF scanner
        if count_type == "retrieve_order":
            # get the required info from the WMS
            global MOVE_number_psoft
            order = retrieve_order(scanner_id)

            # check whether there are any errors with the request
            if order == 'Database Error':
                return render_template("setup_count.html", form=manual_entry_form, employee_id=employee_id,
                                       first_load=True, no_orders=False, database_connection_available=False,
                                       general_order_error=False, wms_submit_error=wms_submit_unsuccessful)
            elif order == 'No orders':
                return render_template("setup_count.html", form=manual_entry_form, employee_id=employee_id,
                                       first_load=True, no_orders=True, database_connection_available=True,
                                       general_order_error=False, wms_submit_error=wms_submit_unsuccessful)
            elif type(order) != list or len(order) != 4:  # this indicates the return value is not a correct list, so there is some other error
                return render_template("setup_count.html", form=manual_entry_form, employee_id=employee_id,
                                       first_load=True, no_orders=False, database_connection_available=True,
                                       general_order_error=True, wms_submit_error=wms_submit_unsuccessful)

            # no errors
            [MOVE_number_psoft, current_product_weight, current_weight_unit, current_target_qty] = order

            return redirect(url_for("count"))

        # this means that the manual entry form was incorrectly filled out, reload the page and show error messages
        else:
            return render_template("setup_count.html", form=manual_entry_form, employee_id=employee_id,
                                   first_load=False, no_orders=False, database_connection_available=True,
                                   general_order_error=False, wms_submit_error=wms_submit_unsuccessful)

    # else if user reached route via GET (as after completing the count)
    elif request.method == "GET":
        return render_template("setup_count.html", form=manual_entry_form, employee_id=employee_id, first_load=True,
                               no_orders=False, database_connection_available=True,
                               general_order_error=False, wms_submit_error=wms_submit_unsuccessful)

    # this should not be reachable
    else:
        return render_template("setup_count.html", form=manual_entry_form, employee_id=employee_id, no_orders=False,
                               database_connection_available=True,
                               general_order_error=False, wms_submit_error=wms_submit_unsuccessful)


# set up website for the actual counting process
@app.route("/count", methods=["GET", "POST"])
def count():
    global wms_submit_unsuccessful

    # check credentials have been entered
    if not employee_id:
        return redirect(url_for("begin"))

    # if user completed count
    if request.method == "POST":
        global manual_order
        # check whether the count was completed successfully, if submit_condition is 0, the count was cancelled,
        # otherwise it was completed. Also do not submit manual orders
        submit_condition = request.form.get("count_complete")
        if submit_condition == "1" and not manual_order:
            # call the function to submit completed count to the WMS and check whether an error message is needed
            submit_return_val = submit_to_wms(MOVE_number_psoft)
            if not submit_return_val:
                wms_submit_unsuccessful = True
            else:
                wms_submit_unsuccessful = False

        # redirect user to page to retrieve next order
        manual_order = False
        return redirect(url_for("setup_count"))

    # else if user reached route via GET (after entering the product barcode or retrieving order)
    else:
        # include information to display to user
        return render_template("count.html", prod_weight=current_product_weight, weight_unit=current_weight_unit,
                               target_count=current_target_qty,
                               target_weight=current_product_weight * current_target_qty,
                               employee_id=employee_id)


# this function serves the javascript on /count, it returns the current weight, the current count, and whether the
# target has been reached
@app.route("/check_weight")
def check_weight():
    # ensure credentials are correctly set
    if not employee_id:
        return redirect(url_for("begin"))

    # retrieve the current weight, and calculate the current count
    current_reading = accurate_reading(current_weight_unit)
    if current_reading == 'Not connected':
        return jsonify('Not connected')
    current_count = current_reading / current_product_weight

    # counting status is -1 if the count is under, 0 if its correct, 1 if its over
    # again, the count needs to be correct to within within_target_count, default set to 0.5
    counting_status = -1
    if current_target_qty - within_target_count <= current_count <= current_target_qty + within_target_count:
        counting_status = 0
    if current_count > current_target_qty + within_target_count:
        counting_status = 1

    # prepare info for the json request, for more info on JSON and AJAX:
    # https://api.jquery.com/jQuery.getJSON/
    return_list = [round(current_count), current_reading, counting_status, current_weight_unit]

    # return data to json request page
    return jsonify(return_list)


# start up the application when python application.py is executed
app.run(host=host_address)
