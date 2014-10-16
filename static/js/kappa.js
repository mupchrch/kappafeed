var kappaRegex = /\bKappa\b/g;
var kappaCount = 0;
var kpmArray = []
var msgCount = 0;
var maxNumMsg = 40;

$(function() {
    var chat = $('.chat'),
    printer = $('.messages', chat),
    printerH = printer.innerHeight(),
    preventNewScroll = false;

    function scrollBottom(){
        if(!preventNewScroll){
            printer.stop(/*false,true*/).animate( {scrollTop: printer[0].scrollHeight - printerH  }, 600, 'swing', function(){
               if(msgCount > maxNumMsg){
                  for(var i=maxNumMsg; i<msgCount; i++){
                     $(printer).find('div').first().remove();
                  }
                  msgCount -= (i-maxNumMsg);
               }
            });
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
            msgCount = 0;
            kappaCount = 0;
            kpmArray = [];
            window.setInterval(kappaPerMin, 3000);
            printer.append('Welcome to kappafeed.');
            scrollBottom();
        };

        ws.onmessage = function (evt) {
            msgCount++;
            var jsonMsg = JSON.parse(evt.data);
            //var indices = findKappas(jsonMsg.msg);
            //kappaCount += indices.length;

            var kappaMsg = '<div class="channelDiv"><span class="channel"><a class="channelLink" href="http://www.twitch.tv/' +
                jsonMsg.channel.substring(1)  + '" target="_blank">' + jsonMsg.channel + '</a></span></div>';
            kappaMsg += '<div class="userMsgDiv"><span class="user">' + jsonMsg.user;

            if(jsonMsg.msg.substring(1,7) == 'ACTION'){
               kappaMsg += ' </span><span class="action">';
               jsonMsg.msg = jsonMsg.msg.substring(7);
            }
            else{
               kappaMsg += ': </span><span class="message">';
            }

            var indices = findKappas(jsonMsg.msg);
            kappaCount += indices.length;

            var currentIndex = 0;
            $.each(indices, function(index, value){
               kappaMsg += jsonMsg.msg.substring(currentIndex,value);
               kappaMsg += '<span class="emoticon kappa"></span>';
               currentIndex = value+5;
            });

            kappaMsg += jsonMsg.msg.substring(currentIndex) + '</span></div>';
            printer.append('<div class="msgDiv">' + kappaMsg + '</div>');
            //fitText('div.msg'+msgCount);

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
   avgKpm = Math.round(avgKpm);
   $('div.kpm').text(avgKpm + 'kpm');
   kappaCount = 0;
}

/*function fitText(msgDiv) {
    var span = $(msgDiv).find('span.channel');
    var fontSize = parseInt(span.css('font-size'));

    do {
        fontSize -= 2;
        span.css('font-size', fontSize.toString() + 'px');
    } while (span.width() >= 80);
}*/
