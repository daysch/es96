from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, session
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import NumberRange

# import helper functions
from readScale import *
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
task_id = 0
current_target_qty = 0
current_product_weight = 0
current_weight_unit = 0
current_lp = 0

# will continue to contain all orders available at a given DC with weight data
all_current_orders_at_location = []

# specifies the DC considered
dc_id = 0


# classes for the form validation
class select_dc_id(FlaskForm):
    style_drop_down = {'class': 'custom-select'}
    dc_id_entry = SelectField(u'Please select your Distribution Center ID ',
                             choices=[('DC001', 'DC001'),
                                      ('DC002', 'DC002'),
                                      ('DC003', 'DC003'),
                                      ('DC004', 'DC004'),
                                      ('DC005', 'DC005')],
                             render_kw=style_drop_down)
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


# this means that if the count is within .5 (e.g. 3.4 is acutal count, when target count is 3) of the target,
# the count is assumed to be correct
within_target_count = 0.5


# see https://flask.palletsprojects.com/en/0.12.x/quickstart/#a-minimal-application for more info on the function
# setup essentially the next line defines the url of the function after that, and the methods allowed for the url (
# form submission - post, simple load - get)

# this page will redirect to the setup_count page
@app.route("/", methods=['GET', 'POST'])
def setup_dc_id():
    # set up the dc_id form, no csrf token (would provide more security, which is not required here),
    # info here: https://flask-wtf.readthedocs.io/en/latest/csrf.html
    dc_form = select_dc_id(meta={'csrf': False})

    # if a submission was posted
    if request.method == "POST":

        # if the form validated, adapt global variables and redirect user to setup_count page
        if dc_form.validate_on_submit():
            global dc_id
            dc_id = dc_form.dc_id_entry.data
            return redirect(url_for("setup_count"))

        # if the form was incorrectly filled out (almost impossible)
        else:
            return render_template("setup_dc_id.html", dc_form=dc_form, first_load=False)

    # if the page was retrieved using a GET method (just retrieving the page)
    # first_load = True will suppress form related error messages
    else:
        dc_id = 0
        return render_template("setup_dc_id.html", dc_form=dc_form, first_load=True)


# this page is intended to set up the counting process, by either retrieving the current order, or entering a manual
# order form
@app.route("/setup_count", methods=['GET', 'POST'])
def setup_count():
    # check credentials have been entered
    if not dc_id:
        return redirect(url_for("setup_dc_id"))

    global all_current_orders_at_location

    # set up the manual order form, again no csrf token, info here: https://flask-wtf.readthedocs.io/en/latest/csrf.html
    manual_entry_form = manual_entry(meta={'csrf': False})

    # if some submission happened
    if request.method == "POST":

        # check whether the user selected a order based on a license plate
        global task_id
        global current_weight_unit
        global current_product_weight
        global current_target_qty
        global current_lp
        task_id = request.form.get("task_id")

        # this means an order needs to be retrieved. this can only be reached, if no errors occurred previously
        if task_id:
            # get the required info by from the list of all orders
            for orders in all_current_orders_at_location:
                if str(orders['task_id']) == str(task_id):
                    order = orders

            # reassign global variables
            current_product_weight = float(order['product_weight'][0])
            current_weight_unit = str(order['uom'][0])
            current_target_qty = int(order['quantity_requested'][0])
            current_lp = str(order['license_plates_contained'][0])

            return redirect(url_for("count"))

        # if user filled out the manual entry form
        if manual_entry_form.validate_on_submit():
            # retrieve data from submission form and redefine global variables
            current_weight_unit = manual_entry_form.weight_unit.data
            current_product_weight = manual_entry_form.product_weight.data
            current_target_qty = manual_entry_form.target_count.data
            current_lp = 0

            # lead the user to the actual count site
            return redirect(url_for("count"))

        # this means that the manual entry form was incorrectly filled out, reload the page and show error messages
        else:
            return render_template("setup_count.html", manual_form=manual_entry_form, first_load=False, dc_id=dc_id)

    # else if user reached route via GET (as after completing the count)
    else:

        # update the current orders for typeahead.
        return_tasks = retrieve_all_tasks(dc_id)

        # retrieve weight database update indicator and then retrieve list with all orders
        time_weight_database_updated = return_tasks[-1]
        all_current_orders_at_location = return_tasks[0:-1]

        # accounting for error messages
        all_order_gen_error_val = False
        no_orders_error_val = False
        retrieval_error_val = False
        connection_unavailable_error_val = False

        # if there was some general error (specific error messages printed in retrieve_order.py)
        if all_current_orders_at_location == 'General Error':
            all_order_gen_error_val = True
        # if no orders with weight data were found
        elif all_current_orders_at_location == 'No orders' or len(all_current_orders_at_location) == 0:
            no_orders_error_val = True
        # if there was a retrieval error
        elif all_current_orders_at_location == 'Retrieval error':
            retrieval_error_val = True
        # if no connection could be established
        elif all_current_orders_at_location == 'No connection':
            connection_unavailable_error_val = True
        # if the return val is not a list something else went wrong
        elif type(all_current_orders_at_location) != list:
            all_order_gen_error_val = True

        # return html
        return render_template("setup_count.html", manual_form=manual_entry_form,
                               all_order_gen_error=all_order_gen_error_val, no_orders=no_orders_error_val,
                               first_load=True, retrieval_error=retrieval_error_val, dc_id=dc_id,
                               database_connection_unavailable=connection_unavailable_error_val,
                               time_weight_update=time_weight_database_updated[0:19])


# set up website for the actual counting process
@app.route("/count", methods=["GET", "POST"])
def count():
    # check credentials have been entered
    if not dc_id:
        return redirect(url_for("setup_dc_id"))

    # if user completed count
    if request.method == "POST":
        return redirect(url_for("setup_count"))

    # else if user reached route via GET (after entering the product barcode or retrieving order)
    else:
        # include information to display to user
        return render_template("count.html", prod_weight=current_product_weight, weight_unit=current_weight_unit,
                               target_count=current_target_qty,
                               target_weight=current_product_weight * current_target_qty,
                               dc_id=dc_id, lp=current_lp)


# this function serves the javascript on /count, it returns the current weight, the current count, and whether the
# target has been reached
@app.route("/check_weight")
def check_weight():
    # ensure credentials are correctly set
    if not dc_id:
        return redirect(url_for("setup_dc_id"))

    # retrieve the current weight, and calculate the current count
    current_reading = accurate_reading(current_weight_unit)
    if current_reading == 'Not connected':
        return jsonify('Not connected')
    if current_reading == 'Other error':
        return jsonify('Other error in readScale()')
    if current_reading == 'Unsupported UOM':
        return jsonify('Unsupported UOM')
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
    if not dc_id:
        return redirect(url_for("setup_dc_id"))

    # retrieve the id entered so far and determine whether just the license plate is requested, or the full order info
    start_id = request.args.get("q")
    return_orders = []

    # check which ids start the same as the id entered so far
    for order in all_current_orders_at_location:
        for current_id in order['license_plates_contained']:
            # split the current_id into chunks with the same length of the input so far
            len_chunks = len(start_id)

            # convert the integer current_id to a string
            current_id = str(current_id)

            # split current id into chunks of same length as input supplied, iterating though all digits in current_id
            chunks = set([current_id[i:i + len_chunks] for i in range(0, len(current_id) - len_chunks + 1)])

            if start_id in chunks and not any(item['license_plate'] == current_id for item in return_orders):
                return_orders.append({'license_plate': current_id})

    # return data to json request page
    if len(return_orders) == 0:
        return jsonify([{'license_plate': 'no orders available for this LP'}])

    # prepare info for the json request, for more info on JSON and AJAX:
    # https://api.jquery.com/jQuery.getJSON/
    # return data to json request page
    return jsonify(return_orders)


# this function serves the javascript on /setup_count, it compares the id entered so far with all the ids at the
# current location, and returns the matches
@app.route("/get_full_orders")
def get_full_orders():
    # ensure credentials are correctly set
    if not dc_id:
        return redirect(url_for("setup_dc_id"))

    # retrieve the id entered so far and determine whether just the license plate is requested, or the full order info
    license_plate_requested = request.args.get("q")
    return_orders = []

    # check which ids start the same as the id entered so far
    for order in all_current_orders_at_location:
        for current_id in order['license_plates_contained']:
            if license_plate_requested == current_id:
                # determine which position the license plate has within the order's license plate list to find
                # the corresponding quantity
                quantity_index = order['license_plates_contained'].index(current_id)
                return_orders.append({'task_id': order['task_id'], 'license_plate': current_id,
                                      'quantity_requested': order['quantity_requested'][quantity_index]})

    # return data to json request page
    if len(return_orders) == 0:
        return jsonify([{'task_id': 'no orders available for this LP', 'license_plates_contained': 0,
                         'quantity_requested': 0}])

    return jsonify(return_orders)


# start up the application when python application.py is executed
app.run(host=host_address)
