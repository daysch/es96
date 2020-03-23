


const main_function = async () => {
    // update the page content
    const result = await update_displays()
}

function update_displays()
{
    // get updated weight data from python backend
    $.getJSON("/check_weight")
    .done(function(data, textStatus, jqXHR) {

    // update current count and current weight
    document.getElementById("current_count").innerHTML="Current Count:  " + data[0];
    document.getElementById("current_weight").innerHTML="Current Weight:  " + data[1];

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
        main_function()

    // if the count is correct
    } else if (data[2] == 0) {
        // creating and appending new count message
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_right");
        paragraph.innerHTML = "Count complete";
        document.getElementById("count_messages").appendChild(paragraph);

        // create a submit button
        button = document.createElement("button");
        button.setAttribute("class", "btn btn-default");
        button.setAttribute("type", "submit");
        button.innerHTML = "Start new count";
        document.getElementById("buttons").appendChild(button);

    // if the count is low
    } else if (data[2] == -1) {
        // creating and appending new count message
        paragraph = document.createElement("p");
        paragraph.setAttribute("id", "count_status");
        paragraph.setAttribute("class", "count_low");
        paragraph.innerHTML = "You have counted too few items";
        document.getElementById("count_messages").appendChild(paragraph);
        main_function()
        }


    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());
        return 0
    });

}
