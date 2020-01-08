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
    addMessage(data);

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

    var data_values = document.getElementById("values");

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
        sendWSMessage(message)
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