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
        var ws = new WebSocket("ws://www.kappafeed.tv/feed");
        ws.onopen = function() {
            printer.append('Connection open.');
            scrollBottom();
        };
        ws.onmessage = function (evt) {
            var received_msg = evt.data;
            var indices = findKappas(received_msg);

            var kappaMessage = '<div><span class="message">';
            $.each(indices, function(index, value){
               kappaMessage += received_msg.substring(0,value);
               kappaMessage += '<span class="emoticon kappa"></span>';
               received_msg = received_msg.substr(value+5);
            });
            kappaMessage += '</span></div>';
            printer.append(kappaMessage);
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