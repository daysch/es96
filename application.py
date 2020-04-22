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
from SetupConn import *

# Configure application see here for details:
# https://flask.palletsprojects.com/en/0.12.x/quickstart/#a-minimal-application
app = Flask(__name__)

# Configure session to use filesystem (https://pythonhosted.org/Flask-Session/#quickstart)
app.config["SESSION_TYPE"] = "filesystem"  # this needs to be set to use a secret key, which is required to use wtforms
app.secret_key = 'supersecretkey'
host_address = '127.0.0.1'
Session(app)

# store these as global variables and update later
order_id = 0
current_target_qty = 0
current_product_weight = 0
current_weight_unit = 0
manual_order = False
employee_id = 0
scanner_id = 0
dc_id = 0
all_current_orders_at_location = []

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


# this label creates an input such that the employee can enter the order id number they are currently picking for
class enter_order_id_current_order(FlaskForm):
    style_order_id = {'class': 'form-control', 'autofocus': 'true', 'id': 'q',
                   'placeholder': 'Enter current Order ID # and select', 'autocomplete':"off"} # turn off autocomplete
                                                                                            # to not have any
                                                                                            # suggestions on type ahead
    order_id_label = IntegerField("RF Scanner ID ",
                               [NumberRange(min=0, max=10 ** 10, message="This ID is too long or too short")],
                               render_kw=style_order_id)
    submit = SubmitField("Submit")


# this means that if the count is within .5 (e.g. 3.4 is acutal count, when target count is 3) of the target,
# the count is assumed to be correct
within_target_count = 0.5


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

            if check_id_val == 'No connection':
                return render_template("begin.html", form=login_form, first_load=True, employee_id=employee_id,
                                       connection=False, ID_not_found=False, retrieval_error=False, gen_error=False)
            elif check_id_val == 'employee not found':
                return render_template("begin.html", form=login_form, first_load=True, employee_id=employee_id,
                                       connection=True, ID_found=False, retrieval_error=False, gen_error=False)
            elif check_id_val == 'Retrieval Error':
                return render_template("begin.html", form=login_form, first_load=True, employee_id=employee_id,
                                       connection=True, ID_not_found=False, retrieval_error=True, gen_error=False)
            else:
                return render_template("begin.html", form=login_form, first_load=True, employee_id=employee_id,
                                       connection=True, ID_not_found=False, retrieval_error=False, gen_error=True)

        # if the credentials are correct, redirect to the next page to start order selection
        return redirect(url_for("setup_count"))

    # if the form was incorrectly filled out, first_load=False indicates to the wtform html to show the appropriate
    # errors
    elif request.method == "POST":

        # flash is a way of showing messages to the user, they are not necessary, but can be helpful
        flash("Please login")
        return render_template("begin.html", form=login_form, first_load=False, employee_id=employee_id,
                               connection=True, ID_not_found=False, retrieval_error=False, gen_error=False)

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
                               connection=True, ID_not_found=False, retrieval_error=False, gen_error=False)


# this page is intended to set up the counting process, by either retrieving the current order, or entering a manual
# order form
@app.route("/setup_count", methods=['GET', 'POST'])
def setup_count():
    # set up the manual order form, again no csrf token, info here: https://flask-wtf.readthedocs.io/en/latest/csrf.html
    manual_entry_form = manual_entry(meta={'csrf': False})
    order_id_label_form = enter_order_id_current_order(meta={'csrf': False})

    # ensure user credentials are validated
    if not employee_id:
        return redirect(url_for("begin"))

    # if some submission happened
    if request.method == "POST":

        # checking whether both forms were filled out, in that case, show error message to user
        if manual_entry_form.validate_on_submit() and order_id_label_form.validate_on_submit():
            return render_template("setup_count.html", manual_form=manual_entry_form,
                                   order_id_form=order_id_label_form, employee_id=employee_id,
                                   first_load=True, both_forms_filled_out=True,
                                   wms_submit_error=wms_submit_unsuccessful)

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

        # if the user submitted just the order_id, this means they are trying to retrieve the order they are picking for
        if order_id_label_form.validate_on_submit():

            # retrieve the entered order_id number
            global order_id
            order_id = order_id_label_form.order_id_label.data

            # get the required info from the WMS
            order = retrieve_specific_order_info(scanner_id, order_id)

            # if no connection to the database could be established
            if order == 'No connection':
                return render_template("setup_count.html", manual_form=manual_entry_form,
                                       order_id_form=order_id_label_form, employee_id=employee_id,
                                       database_connection_unavailable=True,
                                       first_load=True, wms_submit_error=wms_submit_unsuccessful)

            # check whether there are any errors with the retrieval
            elif order == 'Retrieval Error':
                return render_template("setup_count.html", manual_form=manual_entry_form,
                                       order_id_form=order_id_label_form, employee_id=employee_id,
                                       first_load=True, retrieval_error=True, wms_submit_error=wms_submit_unsuccessful)

            # if no errors are assigned to the location
            elif order == 'No orders':
                return render_template("setup_count.html", manual_form=manual_entry_form,
                                       order_id_form=order_id_label_form, employee_id=employee_id,
                                       first_load=True, no_orders=True, wms_submit_error=wms_submit_unsuccessful)

            # this indicates the return value is not a correct list, so there is some other error
            elif type(order) != list or len(order) != 4:
                return render_template("setup_count.html", manual_form=manual_entry_form,
                                       order_id_form=order_id_label_form, employee_id=employee_id,
                                       first_load=True,
                                       general_order_error=True, wms_submit_error=wms_submit_unsuccessful)

            # no errors
            [order_id, current_product_weight, current_weight_unit, current_target_qty] = order

            return redirect(url_for("count"))

        # this means that the manual entry form was incorrectly filled out, reload the page and show error messages
        else:
            return render_template("setup_count.html", manual_form=manual_entry_form,
                                   order_id_form=order_id_label_form, employee_id=employee_id,
                                   first_load=False, wms_submit_error=wms_submit_unsuccessful)

    # else if user reached route via GET (as after completing the count)
    else:

        # update the current orders for typeahead.
        global all_current_orders_at_location
        all_current_orders_at_location = retrieve_all_order_ids(scanner_id)
        if all_current_orders_at_location == 'General Error':
            return render_template("setup_count.html", manual_form=manual_entry_form, all_order_retrieval_error=True,
                                   order_id_form=order_id_label_form, employee_id=employee_id, first_load=True,
                                   wms_submit_error=wms_submit_unsuccessful)


        # return html
        return render_template("setup_count.html", manual_form=manual_entry_form,
                               order_id_form=order_id_label_form, employee_id=employee_id, first_load=True,
                               wms_submit_error=wms_submit_unsuccessful)


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
            submit_return_val = submit_to_wms(order_id)

            # evaluate whether submission was successful and create indicator to be shown on the setup_count page
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
    if current_reading == 'Other error':
        return jsonify('Other error in readScale()')
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

# this function serves the javascript on /setup_count, it compares the id entered so far with all the ids at the
# current location, and returns the matches
@app.route("/get_ids")
def get_ids():

    # ensure credentials are correctly set
    if not employee_id:
        return redirect(url_for("begin"))

    # retrieve the id entered so far
    start_id = request.args.get("q")
    return_ids = []

    # if no orders could be retrieved
    if type(all_current_orders_at_location) != list:
        return jsonify({'order_id': 'no orders available, check command line'})

    # check which ids start the same as the id entered so far
    for current_id in all_current_orders_at_location:

        # split the current_id into chunks with the same length of the input so far
        len_chunks = len(start_id)

        # convert the integer current_id to a string
        current_id = str(current_id)

        # split current id into chunks of same length as the input supplied, iterating though all digits in current_id
        chunks = set([current_id[i:i + len_chunks] for i in range(0, len(current_id)-len_chunks+1)])

        if start_id in chunks:
            return_ids.append({'order_id': current_id})

    # prepare info for the json request, for more info on JSON and AJAX:
    # https://api.jquery.com/jQuery.getJSON/
    # return data to json request page
    return jsonify(return_ids)


# start up the application when python application.py is executed
app.run(host=host_address)
