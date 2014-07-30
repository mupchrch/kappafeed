function WebSocketTest() {
    var messageContainer = $('#messages');

    if ("WebSocket" in window) {
		messageContainer.text("WebSocket is supported by your Browser!");
        var ws = new WebSocket("ws://localhost:8888/websock/?Id=123456789");
        ws.onopen = function() {
            ws.send("Message from client");
        };
        ws.onmessage = function (evt) { 
            var received_msg = evt.data;
            messageContainer.text("Message from server: " + received_msg);
        };
        ws.onclose = function() { 
            messageContainer.text("Connection is closed...");
        };
    } else {
        messageContainer.text("WebSocket NOT supported by your Browser!");
    }
}