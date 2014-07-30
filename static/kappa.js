$(function(){
	$('input.hello').on('click', function(){
		$('p.kappa').text('kappa');
	});
});

var messageContainer = document.getElementById("messages");
function WebSocketTest() {
    if ("WebSocket" in window) {
		messageContainer.innerHTML = "WebSocket is supported by your Browser!";
        var ws = new WebSocket("ws://localhost:8888/?Id=123456789");
        ws.onopen = function() {
            ws.send("Message to send");
        };
        ws.onmessage = function (evt) { 
            var received_msg = evt.data;
            messageContainer.innerHTML = "Message is received...";
        };
        ws.onclose = function() { 
            messageContainer.innerHTML = "Connection is closed...";
        };
    } else {
        messageContainer.innerHTML = "WebSocket NOT supported by your Browser!";
    }
}