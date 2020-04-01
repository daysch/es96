counting_process_active = 0
weight_retrieval_in_process = 0


window.onload = function setup() {

    document.getElementById ("confirm_tare").addEventListener ("click", confirm_tare_clicked)
    console.log('here')
    counting_process_active = 0
    weight_retrieval_in_process = 0
}

function confirm_tare_clicked() {
    document.getElementById("confirm_tare").remove()
    document.getElementById("label_tare").remove()

    button = document.createElement("button")
    button.setAttribute("class", "btn btn-dark");
    button.setAttribute("id", "start_button");
    button.innerHTML = "Start Count";
    document.getElementById("start_stop_buttons").appendChild(button);
    document.getElementById ("start_button").addEventListener ("click", start_button_clicked)
}

function start_button_clicked()
{
    console.log('Start button clicked')
    counting_process_active = 1

    // remove any old stuff
    document.getElementById('start_button').remove();
    try {document.getElementById('count_status').remove();
         console.log('removed')} catch {console.log('couldnt remove count status')}
    try {
        document.getElementById("check_box").remove();
        document.getElementById("label_box").remove();
    } catch {}
    try {document.getElementById('submit_to_wms').remove();
        document.getElementById('submit_paragraph').remove()} catch {}

    // create stop button
    button = document.createElement("button");
    button.setAttribute("class", "btn btn-dark");
    button.setAttribute("id", "stop_button");
    button.innerHTML = "Stop count";
    document.getElementById("start_stop_buttons").appendChild(button);
    document.getElementById ("stop_button").addEventListener ("click", stop_button_clicked)
    main_function()
}

function stop_button_clicked()
{
    // stop the counting process
    counting_process_active = 0

    console.log(weight_retrieval_in_process)
    console.log()
    console.log(counting_process_active)

    // wait for the current weight_retrieval to complete
    if (weight_retrieval_in_process) {
        setTimeout(function() {
            stop_button_clicked()
        }, 100);
        return
    }

    // create a new start button
    document.getElementById('stop_button').remove()
    button = document.createElement("button");
    button.setAttribute("class", "btn btn-dark");
    button.setAttribute("id", "start_button");
    button.innerHTML = "Continue count";
    document.getElementById("start_stop_buttons").appendChild(button);
    document.getElementById ("start_button").addEventListener ("click", start_button_clicked)

    // check whether count is correct
    console.log(document.getElementById("count_status").innerHTML)
    if (document.getElementById("count_status").innerHTML == "Count complete") {
        console.log("count right")

        // create a confirm check box
        box = document.createElement("input");
        box.setAttribute("type", "checkbox");
        box.setAttribute("id", "check_box");
        box.setAttribute("name", "check_box");

        label = document.createElement("label");
        label.setAttribute("for", "check_box");
        label.setAttribute("id", "label_box");
        label.innerHTML = "Please check that you did not add or remove items after clicking stop";
        document.getElementById("submit_form").appendChild(box);
        document.getElementById("submit_form").appendChild(label);

        document.getElementById ("check_box").addEventListener ("click", confirm_check_box_clicked)

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
function confirm_check_box_clicked() {
    button = document.createElement("button");
    button.setAttribute("class", "btn btn-dark");
    button.setAttribute("id", "submit_to_wms");
    button.innerHTML = "Submit to WMS and start new count";
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

    hiddenField = document.createElement('input');
    hiddenField.type = 'hidden';
    hiddenField.name = "wms_submit";
    hiddenField.value = "1";

    // add the hidden field
    document.getElementById("buttons").appendChild(hiddenField);
    document.getElementById("submit_form").submit()



}

const main_function = async () => {
    if (counting_process_active) {
        console.log(counting_process_active)
        // update the page content
        const result = await update_displays()
    }
}

function update_displays()
{
    // get updated weight data from python backend
    weight_retrieval_in_process = 1
    $.getJSON("/check_weight")
    .done(function(data, textStatus, jqXHR) {

    // update current count and current weight
    document.getElementById("current_count").innerHTML=data[0] + " parts";
    document.getElementById("current_weight").innerHTML=data[1] + " " + data[3];

    // indicate whether count is complete after removing current messages
    try {
            document.getElementById("count_status").remove();

        } catch (err) {}

    // if the count is too high
    if (data[2] == 1) {
        // creating and appending new count message
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_over");
        paragraph.innerHTML = "You have counted too many items";
        document.getElementById("count_messages").appendChild(paragraph);
        weight_retrieval_in_process = 0
        main_function()

    // if the count is correct
    } else if (data[2] == 0) {
        // creating and appending new count message
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_right");
        paragraph.innerHTML = "Count complete";
        document.getElementById("count_messages").appendChild(paragraph);
        weight_retrieval_in_process = 0
        main_function()

    // if the count is low
    } else if (data[2] == -1) {
        // creating and appending new count message
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_low");
        paragraph.innerHTML = "You have counted too few items";
        document.getElementById("count_messages").appendChild(paragraph);
        weight_retrieval_in_process = 0
        main_function()
        }


    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());
        if (errorThrown.toString() == "INTERNAL SERVER ERROR") {
            paragraph = document.createElement("p");
            paragraph.setAttribute("id", "count_status");
            paragraph.setAttribute("class", "count_low");
            paragraph.innerHTML = "Please check that the scale is connected and turned on, and restart the count";
            document.getElementById("count_messages").appendChild(paragraph);

            // create a new start button
            document.getElementById('stop_button').remove()
            button = document.createElement("button");
            button.setAttribute("class", "btn btn-dark");
            button.setAttribute("id", "start_button");
            button.innerHTML = "Continue count";
            document.getElementById("start_stop_buttons").appendChild(button);
            document.getElementById ("start_button").addEventListener ("click", start_button_clicked)
        }
        return 0
    });

}
