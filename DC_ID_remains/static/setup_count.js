// this is the minimum length of a correct license plate
min_length_correct_LP = 3

// this function retrieves the entered license plate from the text input field
function get_task_ids() {

    // try to remove any existing error messages
    try {document.getElementById("incomplete_LP").remove()} catch{}

    // get the ID entered
    id_entered = document.getElementById('q').value;

    // check whether the LP is long enough
    if (id_entered.length < min_length_correct_LP) {
        incomplete_id()
    }
    else {
        // retrieve full order info for the LP entered
        results = get_full_orders(id_entered);
     }
}

// this function creates an error message if the user entered an LP that is too short to be correct
function incomplete_id() {
    paragraph = document.createElement("p");
    paragraph.setAttribute("id", "incomplete_LP");
    paragraph.setAttribute("class", "errors");
    paragraph.innerHTML = "Please enter a valid license plate";
    document.getElementById("errors").appendChild(paragraph);
}


// this function retrieves orders with the license plate passed in as an argument
function get_full_orders(query) {
    // get IDs matching query
    var parameters = {
        q: query
    };
    $.getJSON("/get_full_orders", parameters)
    .done(function(data, textStatus, jqXHR) {

        // call table creator with data retrieved
        create_table_from_order_info(data);

    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());

        // call table creator with error message
        create_table_from_order_info([{'task_id': 'no orders available check command line and console', 'license_plates_contained': 0,
                         'quantity_requested': 0}]);
    });
}


function create_table_from_order_info(data) {
    // remove any existing table content
    document.getElementById("table_holder").innerHTML=''
    document.getElementById("confirmation_quantity").innerHTML=''

    // create title
    title = document.createElement("p");
    title.setAttribute("id", "title");
    title.setAttribute("class", "count_titles");
    title.innerHTML = "Orders containing this license plate";
    document.getElementById("table_holder").appendChild(title);

    // create table
    table = document.createElement("table");
    table.setAttribute("class", "table table-bordered bg-white")
    table.setAttribute("id", "table")
    document.getElementById("table_holder").appendChild(table)

    // create header for table
    header = document.createElement("thead");
    header.setAttribute("id", "header");
    header.setAttribute("class", "table_header");
    document.getElementById("table").appendChild(header);

    // add content to the header
    row = document.createElement("tr");
    row.setAttribute("id", "header_row");
    document.getElementById("header").appendChild(row)

    // create row content with headers
    content_for_row = document.createElement("td");
    content_for_row.innerHTML = "Order ID"
    document.getElementById("header_row").appendChild(content_for_row)

    content_for_row = document.createElement("td");
    content_for_row.innerHTML = "License plate"
    document.getElementById("header_row").appendChild(content_for_row)

    content_for_row = document.createElement("td");
    content_for_row.innerHTML = "Order quantity"
    document.getElementById("header_row").appendChild(content_for_row)

    content_for_row = document.createElement("td");
    content_for_row.innerHTML = "Submit?"
    document.getElementById("header_row").appendChild(content_for_row)

    // create body
    body = document.createElement("tbody")
    body.setAttribute("id", "body")
    document.getElementById("table").appendChild(body)

    // fill body
    for (i = 0; i < data.length; i++) {
        // create row
        row = document.createElement("tr");
        row.setAttribute("id", "body_row"+i);
        document.getElementById("body").appendChild(row)

        // add order id to row
        content_for_row = document.createElement("td");
        content_for_row.innerHTML = data[i].task_id
        document.getElementById("body_row"+i).appendChild(content_for_row)

        // add license plate to row
        content_for_row = document.createElement("td");
        content_for_row.innerHTML = data[i].license_plate
        document.getElementById("body_row"+i).appendChild(content_for_row)

        // add quantity requested to row
        content_for_row = document.createElement("td");
        content_for_row.innerHTML = data[i].quantity_requested
        document.getElementById("body_row"+i).appendChild(content_for_row)

        // add button to submit to row with a listener
        // create table entry
        content_for_row = document.createElement("td");
        content_for_row.setAttribute("id", "button_row"+i)
        document.getElementById("body_row"+i).appendChild(content_for_row)

        // create button
        button = document.createElement("button");
        button.setAttribute("class", "btn btn-dark");
        button.setAttribute("id", "button"+i);
        button.setAttribute("onclick", "table_button_clicked("+data[i].quantity_requested+',"'+data[i].task_id+'")')
        button.innerHTML = "Start Count";
        document.getElementById("button_row"+i).appendChild(button)
    }
}


// create a checkbox to confirm the target count
function table_button_clicked(quantity_requested, task_id) {
    // remove any existing checkbox and it's label
    try{
        document.getElementById("label_box").remove()
        document.getElementById("check_box").remove()
        } catch {}

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
    label.innerHTML = "Confirm that your target count is " + quantity_requested + " and submit. <br> Otherwise please retrieve your license plate again <br> or select a different order from the table";
    document.getElementById("confirmation_quantity").appendChild(box);
    document.getElementById("confirmation_quantity").appendChild(label);

    // add event listener to checkbox to call confirm_check_box_clicked
    document.getElementById ("check_box").addEventListener ("click", function() {confirm_check_box_clicked(task_id)}, false)
}


// this function will submit the selected order id
function confirm_check_box_clicked(task_id) {

    // create a hidden field to contain a value that shows the python backend, that the count has been completed
    // the field is hidden to the user, since the type="hidden"
    hiddenField = document.createElement('input');
    hiddenField.type = 'hidden';
    hiddenField.name = "task_id";
    hiddenField.value = task_id;
    document.getElementById("confirmation_quantity").appendChild(hiddenField);

    // submit
    document.getElementById("retrieve_order_form").submit()
}


//Searches database for typeahead's suggestions.
 //
 // this uses jquery. more info here: https://api.jquery.com/jQuery.getJSON/
function get_license_plates(query, syncResults, asyncResults)
{
    // get IDs matching query (asynchronously)
    var parameters = {
        q: query
    };
    $.getJSON("/get_ids", parameters)
    .done(function(data, textStatus, jqXHR) {

        // call typeahead's callback with search results (i.e., IDs)
        asyncResults(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());

        // call typeahead's callback with no results
        asyncResults([]);
    });
}

// configure typeahead when the site is ready
$(document).ready(function() {
    $("#q").typeahead({
        highlight: true, // highlight where input matches suggestions
        minLength: 3 // at least three numbers need to be entered for the typeahead to start searching for suggestions
    },
    {
        display: function(suggestion) { return suggestion["license_plate"]; }, // fill the input, once a suggestion is selected
        limit: 10, // max number of suggestions
        source: get_license_plates, // use get_ids function to retrieve possible ids
        templates: {    // show retrieved suggestions to user
            suggestion: Handlebars.compile( // handlebars enables easier html processing of the returned json data
                "<div>" +
                "{{license_plate}}" +
                "</div>"
            )
        }
    })
})