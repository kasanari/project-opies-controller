var ws = new WebSocket("ws://127.0.0.1:5678/");

ws.onmessage = function (event) {
    var message = document.getElementById("text");
    message.textContent = event.data
};

function sendOrder() {
    var formData = new FormData(document.querySelector('form'));
    var destination = {};
    destination.x = formData.get("x_destination");
    destination.y = formData.get("y_destination");
    let json = JSON.stringify(destination);
    ws.send(json)
}