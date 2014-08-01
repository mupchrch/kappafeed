$(function() {
    var chat = $('.chat'),
    printer = $('.messages', chat),
    printerH = printer.innerHeight(),
    preventNewScroll = false;

    function scrollBottom(){
        if(!preventNewScroll){
            printer.stop().animate( {scrollTop: printer[0].scrollHeight - printerH  }, 600);
        }
    }

    scrollBottom();

    printer.hover(function( e ) {
        preventNewScroll = e.type=='mouseenter' ? true : false ;
        if(!preventNewScroll){ scrollBottom(); }
    });

    if ("WebSocket" in window) {
        var ws = new WebSocket("ws://ec2-54-88-109-228.compute-1.amazonaws.com:80/feed");
        ws.onopen = function() {
            printer.append('Connection open.');
            scrollBottom();
        };
        ws.onmessage = function (evt) {
            var received_msg = evt.data;
            printer.append('<div>' + received_msg + '</div>');
            scrollBottom();
        };
        ws.onclose = function() {
            printer.append('Connection closed.');
            scrollBottom();
        };
    } else {
        alert('websocket not supported');
    }
});
