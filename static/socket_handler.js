var ws = new WebSocket("ws://" + location.hostname + ":5678/");

ws.onmessage = function (event) {
    var message_holder = document.getElementById("messages"),
        message = document.createElement('p'),
        content = document.createTextNode(event.data);
    message.id = "message";
    message.appendChild(content);
    message_holder.appendChild(message);
};

function sendOrder() {
    var formData = new FormData(document.querySelector('form'));
    var destination = {};
    destination.x = formData.get("x_destination");
    destination.y = formData.get("y_destination");
    destination.speed = formData.get("drive_speed");
    destination.angle = formData.get("wheel_angle");
    let json = JSON.stringify(destination);
    ws.send(json)
}