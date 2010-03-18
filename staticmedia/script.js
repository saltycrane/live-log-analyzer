// TODO: columns and keys should not be hard-coded
// Need to send separate data for initialization and update
var columns = [0, 1]
var keys = ['rpm', 'cache0', 'cache1', 'http_status', 'aurt', 'mysql',
            ];

var init_all = function() {
    for (var i=0; i<columns.length; i++) {
        init_column(i);
        for (var j=0; j<keys.length; j++) {
            init_graph(i, keys[j]);
        }
    }
    var lastcol = columns.length;
    init_column(lastcol);
    for (var j=0; j<keys.length; j++) {
        init_values(lastcol, keys[j]);
    }
};

var init_column = function(index) {
    var container = document.getElementById('container');
    var column = document.createElement('div');
    column.className = 'column';
    column.id = 'column-' + index;
    container.appendChild(column);
}

var init_graph = function(col, key) {
    var column = document.getElementById('column-' + col);
    var plot = document.createElement('div');
    plot.className = 'plot';
    plot.id = 'plot-' + col + '-' + key;
    plot.style.width = column.style.width;
    plot.innerHTML = plot.id;
    column.appendChild(plot);
};

var init_values = function(col, key) {
    var column = document.getElementById('column-' + col);
    var value = document.createElement('div');
    value.className = 'value';
    value.id = 'value-' + key;
    value.innerHTML = key;
    column.appendChild(value);
};

var update_all = function(body) {
    var data = JSON.parse(body);
    var labels = data['labels'];
    var history = data['history'];
    var history_length = data['history_length'];
    var options_list = data['flot_options'];
    var column = data['index'];
    for (var i=0; i<keys.length; i++) {
        var key = keys[i];
        var values = history[key];
        var label = labels[key];
        var options = options_list[key];
        update_graph(column, key, values, label, history_length, options);
    }
};

var update_graph = function(col, key, values, label, history_length, options) {
    // plot
    var css_id = '#plot-' + col + '-' + key;
    $.plot($(css_id), values, options);

    // print value
    var value = document.getElementById('value-'+key);
    value.innerHTML = label;
    // value.innerHTML = label + "<br>" + values[history_length-1][1];
    // value.innerHTML = "<br>" + values[history_length-1][1];
};

// run when DOM is ready
$(function () {
    init_all();

    stomp = new STOMPClient();
    stomp.onopen = function() {
    };
    stomp.onclose = function(c) { alert('Lost Connection, Code: ' + c);};
    stomp.onerror = function(error) {
        alert("Error: " + error);
    };
    stomp.onerrorframe = function(frame) {
        alert("Error: " + frame.body);
    };
    stomp.onconnectedframe = function() {
        stomp.subscribe("/topic/graph");
    };
    stomp.onmessageframe = function(frame) {
        update_all(frame.body);
    };
    stomp.connect('localhost', 61613);
});
