 //Searches database for typeahead's suggestions.
 //
 // this uses jquery. more info here: https://api.jquery.com/jQuery.getJSON/
function get_ids(query, syncResults, asyncResults)
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
        source: get_ids, // use get_ids function to retrieve possible ids
        templates: {    // show retrieved suggestions to user
            suggestion: Handlebars.compile( // handlebars enables easier html processing of the returned json data
                "<div>" +
                "{{license_plate}}" +
                "</div>"
            )
        }
    })
})