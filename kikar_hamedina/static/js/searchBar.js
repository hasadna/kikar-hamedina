/* SearchBar.js - defines the behaviour of the search option that appears
 * in the navigation bar. It allows auto-suggest as you type (mk, party, tags)
 * and allows for free search.
 * */

function buildURI(SearchURI) {
//  This function receives target-uri for search,
//  extracts input text from search box, and returns a ready-to-execute uri
// path with search_str parameters.

    var inputText = $("#navbar-search-box").val();
    var value =  SearchURI + '?search_str=' + inputText.replace(/,(\s)+/gi,",");
    console.log(value);
    return value
}

function addDefaultBookMarks(count) {
    var result = {};
    result['count'] = count;
    var source = $("#result-default-link-all-mks-template").html();
    var template = Handlebars.compile(source);
    var html = template(result);
    $('#search-results-list').append(html);
}

$(document).ready(function () {

    // append default link to all-members on load
    var count = 0;
    addDefaultBookMarks(count);


    var resultList, // search results jQuery object
        selectedIndex = -1; // selected search result: -1 means nothing is selected.

    resultList = $('.result-container a');

    $("#navbar-search-box").bind({
        // event: When a letter is typed in, the auto-suggest updates
        input: function (event) {
            $('#search-results-dropdown').removeClass("open");
            this.removeAttribute('activedescendant');
            var inputText = $("#navbar-search-box").val();
            var url = $('body').data('lang') + "/search_bar/?text=" + inputText;
            if (inputText.length > 1) {
                $.ajax({
                    url: url,
                    contentType: "application/json",
                    success: function (data) {
                        var resultListDiv = $('#search-results-list');
                        resultListDiv.html('');
                        var source;
                        for (var i = 0; i < data['number_of_results']; i++) {
                            var result = data['results'][i];
                            if (result['type'] == "party") {
                                source = $("#result-party-list-item-template").html()
                            }
                            else if (result['type'] == "member") {
                                source = $("#result-member-list-item-template").html()
                            }
                            else if (result['type'] == "tag") {
                                // ignore these for now, they have not been updated for ages
                                continue;
                            }

                            result.count = i; // For Handlebars - id value on result output
                            var template = Handlebars.compile(source);
                            var html = template(result);
                            resultListDiv.append(html);

                        }
                        // append default link to all-members
                        count = data['number_of_results'].length;
                        addDefaultBookMarks(count);

                        if (data['number_of_results'] > 0) {
                            $('#search-results-dropdown').addClass("open");
                            resultList = $('.result-container a');
                            selectedIndex = -1;
                        }
                    }
                });
            } else {
                var resultListDiv = $('#search-results-list');
                resultListDiv.html('');
                count = 0;
                addDefaultBookMarks(count);
                resultList = $('.result-container a');
                selectedIndex = -1;
            }

        },

        // event: Enter-key pressed while typing - equivalent to submit-search.
        //        Enter-key pressed while selecting search result - go to search result
        //        Up / Down keys - navigation between search results

        keydown: function (event) {
            var uri, full_url;
            switch (event.which) {
                case 13:
                    if (selectedIndex > -1) {
                        full_url = $('.active-result').attr('href');
                    }
                    else {
                        uri = buildURI($("#search-bar-submit").data('target'));
                        full_url = window.location.origin + encodeURI(uri);
                    }
                    window.location.assign(full_url);
                    break;

                case 40:
                    setSelectedIndex(selectedIndex + 1);
                    break;

                case 38:
                    setSelectedIndex(selectedIndex - 1);
                    break;
            }
        }

    });


    // event: Click on submit search button
    $("#search-bar-submit").click(function () {
        var uri = buildURI($("#search-bar-submit").data('target'));
        window.location.assign(window.location.origin + encodeURI(uri))
    });

    // sets the focus on the next/previous search result
    function setSelectedIndex(i) {

        // if a result has been already selected
        if (selectedIndex > -1) {
            resultList[selectedIndex].className = '';
        }

        // end of result list - set to first result
        if (i == resultList.length) {
            i = 0;
        }

        // first result - set to last result
        if (i < 0) {
            i = resultList.length - 1;
        }

        resultList[i].className = 'active-result';
        $("#navbar-search-box").attr('activedescendant', 'option-' + i);
        selectedIndex = i;
    }
});
