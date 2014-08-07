var kappaRegex = /\bKappa\b/g;

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
        var pathname = window.location.href;
        var wsPath = 'ws' + pathname.substr(4) + 'feed';
        var ws = new WebSocket(wsPath);
        ws.onopen = function() {
            printer.append('Connection open.');
            scrollBottom();
        };
        ws.onmessage = function (evt) {
            var received_msg = evt.data;
            var indices = findKappas(received_msg);

            var kappaMessage = '<span class="message">';
            var currentIndex = 0;
            $.each(indices, function(index, value){
               kappaMessage += received_msg.substring(currentIndex,value);
               kappaMessage += '<span class="emoticon kappa"></span>';
               currentIndex = value+5;
            });
            kappaMessage += received_msg.substring(currentIndex) + '</span>';
            printer.append('<div>' + kappaMessage + '</div>');
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

function findKappas(s){
   var match, indices = [];
   while(match = kappaRegex.exec(s)){
      indices.push(match.index);
   }
   return indices;
}
