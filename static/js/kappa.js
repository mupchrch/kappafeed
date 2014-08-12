var kappaRegex = /\bKappa\b/g;
var kappaCount = 0;
var kpmArray = []

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
            kappaCount = 0;
            kpmArray = [];
            window.setInterval(kappaPerMin, 3000);
            printer.append('Connection open.');
            scrollBottom();
        };
        ws.onmessage = function (evt) {
            var jsonMsg = JSON.parse(evt.data);
            var indices = findKappas(jsonMsg.msg);
            kappaCount += indices.length;

            var kappaMsg = '<span class="channel">' + jsonMsg.channel + '</span>';
            kappaMsg += '<span class="user">' + jsonMsg.user + ':</span>';
            kappaMsg += '<span class="message">';
            //kappaMsg += jsonMsg.channel + ' -> ' + jsonMsg.user +': ';
            var currentIndex = 0;
            $.each(indices, function(index, value){
               kappaMsg += jsonMsg.msg.substring(currentIndex,value);
               kappaMsg += '<span class="emoticon kappa"></span>';
               currentIndex = value+5;
            });
            kappaMsg += jsonMsg.msg.substring(currentIndex) + '</span>';
            printer.append('<div>' + kappaMsg + '</div>');
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

function kappaPerMin(){
   var kpm = kappaCount * 20;
   kpmArray.push(kpm);
   if(kpmArray.length > 5){
      kpmArray.shift();
   }
   var avgKpm = 0;
   for(var i=0; i<kpmArray.length; i++){
      avgKpm += kpmArray[i];
   }
   avgKpm /= kpmArray.length;
   $('div.kpm').text(avgKpm + 'kpm');
   console.log(avgKpm + 'kpm');
   kappaCount = 0;
}
