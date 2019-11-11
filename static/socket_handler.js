var connected = false;
var ws;

function addMessage(message_content) {
    var message_holder = document.getElementById("messages"),
        message = document.createElement('p'),
        content = document.createTextNode(message_content);
    message.id = "message";
    message.appendChild(content);
    message_holder.appendChild(message);
    message_holder.scrollTop = message_holder.scrollHeight
}

function eventHandler(event) {
    addMessage(event.data);
    var data = JSON.parse(event.data);
    myLineChart.data.labels.push(data.x);
    myLineChart.data.datasets[0].data.push(data.y);
    myLineChart.update()
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
        message.x = formData.get("x_destination");
        message.y = formData.get("y_destination");
        sendWSMessage(message)
    } else {
        console.log("WebSocket not connected!")
    }
}

function stop() {
    var message = {};
    message.type = "car_control";
    message.speed = 0.5;
    message.angle = 0.5;
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