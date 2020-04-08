// these two variables indicate whether the counting process is paused or ongoing, and whether the javasccript is
// currently waiting for the python backend to return weight data from the scale
counting_process_active = 0
weight_retrieval_in_process = 0

// as the page is loaded, the global variables are initialized, and an event listener is added to the existing html
// check box to confirm that the scale has been tared and connected etc
window.onload = function setup() {

    document.getElementById ("confirm_tare").addEventListener ("click", confirm_tare_clicked)
    counting_process_active = 0
    weight_retrieval_in_process = 0
}

// this function is called when the confirm tare check box that exists on the initially loaded page is clicked
// it removes the checkbox and creates a button to start the counting process, and an event listener to trigger the
// start_button_clicked function when this button is clicked
function confirm_tare_clicked() {
    document.getElementById("confirm_tare").remove();
    document.getElementById("label_tare").remove();

    button = document.createElement("button")
    button.setAttribute("class", "btn btn-dark");
    button.setAttribute("id", "start_button"); // this is necessary to be able to remove the button again later
    button.innerHTML = "Start Count";
    document.getElementById("start_stop_buttons").appendChild(button);
    document.getElementById ("start_button").addEventListener ("click", start_button_clicked);
}


// this function is called when the start button has been clicked. it changes the global variables to indicate that the
// count process is active. it then starts the function that retrieves weight readings from the python backend, and it
// creates a stop button to stop the counting process
function start_button_clicked()
{
    counting_process_active = 1

    // remove any old html checkboxes and messages that may still exist due to different previous actions by the user
    document.getElementById('start_button').remove();
    try {document.getElementById('count_status').remove();}
    catch {}
    try {
        document.getElementById("check_box").remove();
        document.getElementById("label_box").remove();
    } catch {}
    try {document.getElementById('submit_to_wms').remove();
        document.getElementById('submit_paragraph').remove()} catch {}

    // create stop button with an event listener to trigger the stop_button_clicked function and add it to the page
    button = document.createElement("button");
    button.setAttribute("class", "btn btn-dark");
    button.setAttribute("id", "stop_button");
    button.innerHTML = "Stop Count";
    document.getElementById("start_stop_buttons").appendChild(button);
    document.getElementById ("stop_button").addEventListener ("click", stop_button_clicked)

    // trigger the function to retrieve the readout from the python backend
    retrieve_readings()
}


// this function is clicked when the stop button is clicked. it changes the global variables to reflect this,
// waits for the current weight readings to complete and update the count messages, before stopping the weight readings
// it then creates a new start button. it also checks whether the count is complete. if the count is complete,
// it creates another checkbox to make sure the user did not add or remove any items. if that check box is clicked
// confirm_check_box_clicked() is called. if the count is not complete
function stop_button_clicked()
{
    // stop the counting process
    counting_process_active = 0

    // wait for the current weight_retrieval to complete
    if (weight_retrieval_in_process) {
        setTimeout(function() {
            stop_button_clicked() // recall this function until the weight reading functions have completed
        }, 100);
        return
    }

    // create a new start button and add it to the page with an event listener
    document.getElementById('stop_button').remove()
    button = document.createElement("button");
    button.setAttribute("class", "btn btn-dark");
    button.setAttribute("id", "start_button");
    button.innerHTML = "Continue count";
    document.getElementById("start_stop_buttons").appendChild(button);
    document.getElementById ("start_button").addEventListener ("click", start_button_clicked)

    // check whether count is correct
    if (document.getElementById("count_status").innerHTML == "Count Complete!") {

        // create a confirm check box
        box = document.createElement("input");
        box.setAttribute("type", "checkbox");
        box.setAttribute("id", "check_box");
        box.setAttribute("name", "check_box");

        // create a label for the confirm check box, add the checkbox to the page and create an event listener for the box
        label = document.createElement("label");
        label.setAttribute("for", "check_box");
        label.setAttribute("id", "label_box");
        label.setAttribute("class", "ml-2 stop_check");
        label.innerHTML = "Please check that you did not add or remove items after clicking stop";
        document.getElementById("submit_form").appendChild(box);
        document.getElementById("submit_form").appendChild(label);

        document.getElementById ("check_box").addEventListener ("click", confirm_check_box_clicked)

    // if the count was not complete, show a message to the user to complete count, or abort
    } else {
        // creating and appending new count message
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_incomplete");
        paragraph.innerHTML = "Please continue counting or cancel process";
        document.getElementById("count_messages").appendChild(paragraph);
    }
}


// when the user confirms that he did not add or remove any items after clicking stop, it becomes possible to post to the WMS
// this function sets up the submit button to the main page and adds an event listener to that button. it does not
// actually submit, but rather triggers another function submit_to_wms(), which is necessary to indicate to the
// python whether the submission was successful
function confirm_check_box_clicked() {
    document.getElementById("check_box").removeEventListener("click", confirm_check_box_clicked)
    button = document.createElement("button");
    button.setAttribute("class", "btn btn-dark");
    button.setAttribute("id", "submit_to_wms");
    button.innerHTML = "Submit to WMS and Start New Count";
    paragraph = document.createElement("p")
    paragraph.setAttribute("id", "submit_paragraph")
    document.getElementById("submit_form").appendChild(paragraph)
    document.getElementById("submit_form").appendChild(button);
    document.getElementById ("submit_to_wms").addEventListener ("click", submit_to_wms)
}

// this function submits the count to the python script, which can then communicate with the WMS
function submit_to_wms() {
    // remove the cancel button
    document.getElementById("cancel_count").remove();

    // create a hidden field to contain a value that shows the python backend, that the count has been completed
    // the field is hidden to the user, since the type="hidden"
    hiddenField = document.createElement('input');
    hiddenField.type = 'hidden';
    hiddenField.name = "wms_submit";
    hiddenField.value = "1";

    // add the hidden field to the page in the lower part of the page
    document.getElementById("buttons").appendChild(hiddenField);
    document.getElementById("submit_form").submit()
}


// this function will retrieve the current reading from the page, by calling another function update_displays().
// It will do so only if the counting process is set to active.
// it is called when the start button is clicked, and re-called when the displays are successfully updated
function retrieve_readings()
{
    if (counting_process_active) {

        // update the page content
        update_displays()
    }
}


// this function retrieves the current readings from the python backend, and recalls retrieve_readings when that is completed
// if it cannot retrieve the readings it will display an error message to the user, since most errors in normal
// operation are caused by incorrect scale setup, the message includes that
function update_displays()
{
    // get updated weight data from python backend, reflect this in the global variables
    // this uses jquery. more info here: https://flask.palletsprojects.com/en/1.1.x/patterns/jquery/
    weight_retrieval_in_process = 1
    $.getJSON("/check_weight")

    // when the info has been retrieved successfully, update the displays and recall the retrieve_readings function
    .done(function(data, textStatus, jqXHR) {

    // update current count and current weight, data[0] denotes the current count, data[1] indicates the current weight
    //, data[3] indicates the current unit
    if (data[0] == 1) {
        document.getElementById("current_count").innerHTML=data[0] + " part";
    } else {
        document.getElementById("current_count").innerHTML=data[0] + " parts";
    }
    document.getElementById("current_weight").innerHTML=data[1] + " " + data[3];

    // indicate whether count is complete after removing current count messages
    try {
            document.getElementById("count_status").remove();

        } catch (err) {}

    // if the count is too high
    if (data[2] == 1) {
        // creating and appending new count message & recall retrieve_readings() & indicate weight retrieval is complete
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_over");
        paragraph.innerHTML = "You have counted too many items";
        document.getElementById("count_messages").appendChild(paragraph);
        weight_retrieval_in_process = 0
        retrieve_readings()

    // if the count is correct
    } else if (data[2] == 0) {
        // creating and appending new count message
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_right");
        paragraph.innerHTML = "Count Complete!";
        document.getElementById("count_messages").appendChild(paragraph);
        weight_retrieval_in_process = 0
        retrieve_readings()

    // if the count is low
    } else if (data[2] == -1) {
        // creating and appending new count message
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_low");
        paragraph.innerHTML = "You have counted too few items";
        document.getElementById("count_messages").appendChild(paragraph);
        weight_retrieval_in_process = 0
        retrieve_readings()
        }


    })

    // if the function failed, this usually because the scale is not connected properly, or because there is an error in the backend
    // this error will be shown in the console.
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());
        if (errorThrown.toString() == "INTERNAL SERVER ERROR") {
            paragraph = document.createElement("p");
            paragraph.setAttribute("id", "count_status");
            paragraph.setAttribute("class", "count_low");
            paragraph.innerHTML = "Please check that the scale is connected and <br> turned on, and restart the count";
            document.getElementById("count_messages").appendChild(paragraph);

            // create a new start button, add it and setup an event listener
            document.getElementById('stop_button').remove()
            button = document.createElement("button");
            button.setAttribute("class", "btn btn-dark");
            button.setAttribute("id", "start_button");
            button.innerHTML = "Continue Count";
            document.getElementById("start_stop_buttons").appendChild(button);
            document.getElementById ("start_button").addEventListener ("click", start_button_clicked)
        }
        return 0
    });

}
