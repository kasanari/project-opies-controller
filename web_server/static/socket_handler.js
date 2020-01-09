var connected = false;
var ws;
var graph_index = 0;

function addMessage(message_content) {
    var message_holder = document.getElementById("messages"),
        message = document.createElement('p'),
        content = document.createTextNode(message_content);
    message.id = "message";
    message.appendChild(content);
    message_holder.appendChild(message);
    message_holder.scrollTop = message_holder.scrollHeight
}


function dataHandler(data) {
    //addMessage(data.toString());

    var measurement = data.measurement;
    var imu_data = measurement.result_imu;

    var lines = [
        "x, y: " + measurement.result_tag.x + ", " + measurement.result_tag.y + "\n",
        "x_est, y_est: " + data.location_est.x + ", " + data.location_est.y + "\n",
        "v_x_est, v_x_est: " + data.x_v_est + ", " + data.y_v_est + "\n",
        "a_y_est, a_y_est: " + data.x_acc_est.x + ", " + data.y_acc_est + "\n",
        "a_real_x, a_real_y: " + imu_data.real_acceleration.x + ", " + imu_data.real_acceleration.y + "\n",
        "a_world_x, a_world_y: " + imu_data.world_acceleration.x + ", " + imu_data.world_acceleration.y + "\n",
        "yaw: " + imu_data.rotation.yaw + "\n"
    ];

    var data_values = document.getElementById("values_data");

    var new_data = document.createElement("div");

    for (let line of lines) {
        var content = document.createElement("p");
        content.innerHTML = line;
        new_data.appendChild(content)
    }

    data_values.replaceChild(new_data, data_values.firstChild);

    position = {'x':data.location_est.x, 'y':data.location_est.y};


    if (graph_index % 40 === 0) {
        graph_index = 0;
        myLineChart.data.datasets[0].data[graph_index] = position;
        graph_index++;
    } else {
        myLineChart.data.datasets[0].data[graph_index] = position;
        graph_index++;
    }

    //myLineChart.data.datasets[0].data.push(position)
    myLineChart.update()
}

function eventHandler(event) {
    var data = JSON.parse(event.data);
    var type = data.type;
    if (type === "measurements") {
        dataHandler(data.estimation);
    } else if (type === "movie") {
        console.log("movie ready");
        var video = document.getElementById("path_movie");
        var source = document.getElementById("movie_source");//document.createElement('source');
        source.setAttribute('src', 'static/movie.mp4');
        video.load();
        video.play()
    }
}

function sendWSMessage(message) {
    let json = JSON.stringify(message);
    console.log(json);
    ws.send(json)
}

function sendCarControl() {
    if (connected) {
        var formData = new FormData(document.getElementById('form-carcontrol'));
        var message = {};
        message.type = "car_control";
        message.speed = formData.get("drive_speed");
        message.angle = formData.get("wheel_angle");
        sendWSMessage(message)
    } else {
        console.log("WebSocket not connected!")
    }
}

function sendDestination() {
    if (connected) {
        var formData = new FormData(document.getElementById('form-destination'));
        var message = {};
        message.type = "destination";
        message.x = [formData.get("x_destination")];
        message.y = [formData.get("y_destination")];
        message.filename = "movie";
        sendWSMessage(message);

        let x_points = [1.1, 2.5, 2.5, 1.1, 1,1];
        let y_points = [1.1, 1.1, 5.0, 5.0, 1.1];

        let p = x_points.map(function(e, i) {
            return {'x':e, 'y':y_points[i]};
        });

        myLineChart.data.datasets[1].data = p;

    } else {
        console.log("WebSocket not connected!")
    }
}

var arr_index = 0;
var array_x = Array();
var array_y = Array();

function add_element_to_array()
{
    array_x[arr_index] = document.getElementById("x_destination").value;
    array_y[arr_index] = document.getElementById("y_destination").value;
    arr_index++;
    document.getElementById("x_destination").value = "";
    document.getElementById("y_destination").value = "";
    display_array();
}

function erase_array()
{
    array_x = Array();
    array_y = Array();
    arr_index = 0;
    display_array();
}

function erase_last_element()
{
    let new_array_x = Array();
    let new_array_y = Array();
    for (let index=0; index<array_x.length-1; index++)
    {
        new_array_x[index] = array_x[index];
        new_array_y[index] = array_y[index];
    }
    array_x = new_array_x;
    array_y = new_array_y;
    arr_index = array_x.length;
    display_array();
}

function display_array()
{
    let path_status = "<hr/>";

    for (let disp_index=0; disp_index<array_x.length; disp_index++)
    {
        path_status += "Point " + disp_index + ": (" + array_x[disp_index] + ", " + array_y[disp_index] + ") <br/>"
    }
    document.getElementById("Array_res").innerHTML = path_status;
}


function sendPath() {
    if (connected) {
        var message = {};
        message.type = "path";
        message.x = array_x;
        message.y = array_y;
        message.filename = "movie";

        let path_status = document.getElementById("Array_res").innerHTML;
        path_status += "Path sent! <br/>";
        document.getElementById("Array_res").innerHTML = path_status;
        sendWSMessage(message);

        let p = array_x.map(function(e, i) {
            return {'x':parseFloat(e), 'y':parseFloat(array_y[i])};
        });

        myLineChart.data.datasets[1].data = p;
    } else {
        console.log("WebSocket not connected!")
    }
}

function stop() {
    var message = {};
    message.type = "stop";
    message.speed = 0;
    message.angle = -0.2;
    resetSliders();
    sendWSMessage(message)
}

function connect() {
    ws = new WebSocket("ws://" + location.hostname + ":5678/");
    connected = true;
    ws.onmessage = eventHandler;
    addMessage("Connected to host.")
}

function disconnect() {
    if (connected) {
        ws.close();
        connected = false;
        addMessage("Disconnected from host.")
    } else {
        console.log("WebSocket not connected!")
    }
}