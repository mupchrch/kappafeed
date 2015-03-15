//var kappaRegex = /\bKappa\b/g;
//var kappaCount = 0;
//var kpmArray = []
var msgCount = 0;
var maxNumMsg = 40;
var channelNameLen = 10;

$(function() {
    var chat = $('.chat');
    var printer = $('.messages', chat);
    var preventNewScroll = false;

    function scrollBottom(){
        var printerH = printer.innerHeight();

        if(!preventNewScroll){
            printer.stop().animate( {scrollTop: printer[0].scrollHeight - printerH  }, 600, 'swing', function(){
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

    //if mouse over chat, stop scrolling
    printer.hover(function( e ) {
        preventNewScroll = e.type=='mouseenter' ? true : false ;
        if(!preventNewScroll){ scrollBottom(); }
    });

    //check for websocket support
    if ("WebSocket" in window) {
        var wsPath = 'ws://kappafeed.tv/feed';
        var ws = new WebSocket(wsPath);

        ws.onopen = function() {
            msgCount = 0;
            //kappaCount = 0;
            //kpmArray = [];
            //window.setInterval(kappaPerMin, 3000);
            printer.append('<div class="msgDiv">Welcome to kappafeed.</div>');
            scrollBottom();
        };

        ws.onmessage = function (evt) {
            msgCount++;
            var jsonMsg = JSON.parse(evt.data);

            var channel = jsonMsg.channel.substring(1);
            var shortChannel = channel;

            if(shortChannel.length > channelNameLen){
                shortChannel = shortChannel.substring(0, channelNameLen) + '...';
            }

            //build the html for channel link
            var kappaMsg = '<div class="channelDiv"><span class="channel"><a class="channelLink" href="http://www.twitch.tv/' +
	            channel + '" target="_blank">' + shortChannel + '</a></span></div>';
            //build the user link
            kappaMsg += '<div class="userMsgDiv"><span class="user"><a class="userLink" style="color:' + jsonMsg.user.color + ';" href="http://www.twitch.tv/' +
                jsonMsg.user.name + '/profile" target="_blank">' + jsonMsg.user.name + '</a>';

            //if this is an action message, color it green
            if(jsonMsg.msg.substring(1,7) == 'ACTION'){
                kappaMsg += ' </span><span class="action">';
                jsonMsg.msg = jsonMsg.msg.substring(7);
            }
            else{
                kappaMsg += ': </span><span class="message">';
            }

            kappaMsg += jsonMsg.msg;
            printer.append('<div class="msgDiv">' + kappaMsg + '</div>');

            scrollBottom();
        };

        ws.onclose = function() {
            printer.append('Connection closed.');
            scrollBottom();
        };

    }
    else{
        alert('websocket not supported');
    }
});

/*
 * Calculates the KPM in chat.
 */
/*function kappaPerMin(){
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
}*/
