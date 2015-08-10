/**
 * Created by Maxime on 8/9/2015.
 */


var ws,                 // websocket
    prev_data,          // remember data fetched last time
    ticker;

function establish_websocket(port, _ticker) {
    ticker = _ticker;
    if ("WebSocket" in window) {
        ws = new WebSocket("ws://" + document.domain + ":" + port.toString() + "/updated");
        ws.onstart = function() {
            ws.send('started');
        }
        ws.onmessage = function (msg) {
            $('div#nbconnect').html(msg['data']);
            load_data();

        };
        ws.onclose = function (msg) {
            $("#updated").html('SERVER DISCONNECT');
            $("#updated").css('backgroundColor', '#FFCCFF');
            $("#updated").fadeIn('fast');

        };

        // load the initial data
        load_data();
    } else {
        alert("WebSocket not supported");
    }
}

function load_data() {
    // load data from /data, optionally providing a query parameter read from
    // the #format select

    var url = '/data/' + ticker;
    $.ajax({ url: url,
        success: function(data) {
            display_data(data);
        }
    });
    return true;
}

function display_data(data) {
    // show the data acquired by load_data()

    if (data && (data != prev_data)) {      // if there is data, and it's changed

        // compute a message to display comparing current data with previous data
        var delta_value;
        if (prev_data) {
            console.log("data.value:", data.value, "prev_data.value:", prev_data.value);
        }
        else {
            console.log("data.value:", data.value, "no prev_data");
        }

        // update the contents of several HTML divs via jQuery
        $('div#ticker').html(data.ticker);
        $('div#value').html(data.value);
        $('div#change').html(data.change);

        // remember this data, in case want to compare it to next update
        prev_data = data;

        // a little UI sparkle - show the #updated div, then after a little
        // while, fade it away
        $("#updated").fadeIn('fast');
        setTimeout(function() {  $("#updated").fadeOut('slow');  }, 2500);
    }
}

$(document).ready(function() {
    // inital document setup - hide the #updated message, and provide a
    // "loading..." message
    $("div#updated").fadeOut(0);
    $("div#contents").append("awaiting data...");
    $("select#format").on('change', load_data);
    $("div#contents, div#value").on('click', load_data);
});
