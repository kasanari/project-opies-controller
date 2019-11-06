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

function sendOrder() {
    if (connected) {
        var formData = new FormData(document.querySelector('form'));
        var destination = {};
        destination.x = formData.get("x_destination");
        destination.y = formData.get("y_destination");
        destination.speed = formData.get("drive_speed");
        destination.angle = formData.get("wheel_angle");
        let json = JSON.stringify(destination);
        ws.send(json)
    } else {
        console.log("WebSocket not connected!")
    }
}

function connect() {
    ws = new WebSocket("ws://" + location.hostname + ":5678/");

    connected = true;

    ws.onmessage = eventHandler;
    addMessage("Connected to host.")
}

function disconnect() {
    ws.close();
    connected = false;
    addMessage("Disconnected from host.")
}