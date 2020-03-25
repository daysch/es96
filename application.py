from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from readScale import *
from barcode2Weight import *
from barcode2OrderQuantity import *
from submit_to_wms import *
from functools import wraps

from flask_jsglue import JSGlue

# Configure application
app = Flask(__name__)
JSGlue(app)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

Session(app)

# store these as global variables and update later
current_barcode = 0
current_target_qty = 0
current_product_weight = 0
current_weight_unit = 0
employee_id = 0
scanner_id = 0

# Define confidence interval (the percentage of the weight within which you want the desired scale reading)
conf_int = .5  # can also define this as an absolute value if that works better
within_target_count = 0.5  # this means that if the count is within .5 of the target, the count is assumed to be


@app.route("/", methods=['GET', 'POST'])
def begin():
    # if user reached route via POST (as by submitting a user id)
    if request.method == "POST":
        global employee_id
        global scanner_id
        employee_id = request.form.get("employee_id")
        scanner_id = request.form.get("scanner_id")

        if not employee_id or not scanner_id:
            return redirect(url_for("begin"))

        employee_id = float(employee_id)
        scanner_id = float(scanner_id)

        return redirect(url_for("enter_product_number"))

    # else if user reached route via GET (after logging out)
    else:
        return render_template("begin.html", employee_id=employee_id)


@app.route("/enter_product_number", methods=['GET', 'POST'])
def enter_product_number():
    if not employee_id:
        return redirect(url_for("begin"))

    # if user reached route via POST (as by submitting a barcode)
    if request.method == "POST":
        global current_weight_unit
        global current_product_weight
        global current_barcode
        global current_target_qty

        # get the current barcode from the submitted html form
        barcode = request.form.get("barcode")

        # if no barcode was supplied, then that means that either nothing was filled out, or the manual barcode input
        # was used
        if not barcode:
            barcode_manual = request.form.get("barcode_manual")

            # nothing was supplied
            if not barcode_manual:
                return redirect(url_for("enter_product_number"))
            else:
                current_barcode = int(barcode_manual)
                current_target_qty = float(request.form.get("target_count"))
                current_product_weight = float(request.form.get("product_weight"))
                current_weight_unit = (request.form.get("weight_unit"))

        else:
            current_barcode = int(barcode)
            """
            [current_product_weight, current_weight_unit] = barcode2Weight(barcode)
            current_target_qty = barcode2OrderQuantity(barcode)
            """

            # retrieve and assign global variables for this order
            [current_product_weight, current_weight_unit] = [8, 'g']
            current_target_qty = 2
            print(current_product_weight)

        return redirect(url_for("count"))

    # else if user reached route via GET (as after completing the count)
    else:
        return render_template("enter_barcode.html", employee_id=employee_id)


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
            submit_to_wms(current_barcode)
            print("submitted to wms")

        return redirect(url_for("enter_product_number"))

    # else if user reached route via GET (after entering the product barcode)
    else:
        return render_template("count.html", barcode=current_barcode, prod_weight=current_product_weight,
                               target_count=current_target_qty, target_weight=current_product_weight*current_target_qty,
                               employee_id=employee_id)


# this function serves the javascript on /count, it returns the current weight, the current count, and whether the
# target has been reached
@app.route("/check_weight")
def check_weight():
    if not employee_id:
        return redirect(url_for("begin"))

    current_reading = accurate_reading(current_weight_unit)
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
