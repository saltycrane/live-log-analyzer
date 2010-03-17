var keys = ['rpm', 'cache0', 'cache1', 'http_status', 'aurt',
            ];

var init_all = function() {
   for (var i=0; i<keys.length; i++) {
      init_graph(keys[i]);
   }
};

var init_graph = function(key) {
   var container1 = document.getElementById('container1');

   var plot = document.createElement('div');
   plot.className = 'plot';
   plot.id = 'plot-' + key;
   container1.appendChild(plot);

   var value = document.createElement('div');
   value.className = 'value';
   value.id = 'value-' + key;
   value.innerHTML = key;
   container1.appendChild(value);
};

var update_all = function(body) {
    var data = JSON.parse(body);
    var labels = data['labels'];
    var history = data['history'];
    var history_length = data['history_length'];
    var options_list = data['flot_options'];
    for (var i=0; i<keys.length; i++) {
        var key = keys[i];
        var values = history[key];
        var label = labels[key];
        var options = options_list[key];
        update_graph(key, values, label, history_length, options);
    }
};

var update_graph = function(key, values, label, history_length, options) {
    // plot
    var css_id = '#plot-' + key;
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
