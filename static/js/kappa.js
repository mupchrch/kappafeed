var kappaCount;
var kpmArray;
var msgCount;
var maxNumMsg;
var channelNameLen;
var kappaPollRate;

$(function() {
    var autoScrolling = false;
    var emotesOpen = false;

    $.getJSON("https://api.twitch.tv/kraken/chat/emoticon_images?emotesets=0", function( data ){
        var rawEmotes = data['emoticon_sets']['0'];
        for(var e in rawEmotes){
            var dString = '<div class="emoticonHolder" style="background-image: url(\'http://static-cdn.jtvnw.net/emoticons/v1/' + rawEmotes[e]['id'] + '/1.0\')" >'+rawEmotes[e]['id']+'</div>'
            $('#twitchEmotes').append(dString);
        }
    });

    $('#twitchSmile').on('click', function(){
        if(emotesOpen)
        {
            $('#twitchEmotes').css('opacity', 0);
            $('#twitchEmotes').css('z-index', -1);
            emotesOpen = false;
        }
        else
        {
            $('#twitchEmotes').css('opacity', 1);
            $('#twitchEmotes').css('z-index', 1);
            emotesOpen = true;
        }
    });


    $('.scrollPopup').on('click', function(){
        $(this).css('opacity', 0);
        $(this).css('z-index', -1);
        preventNewScroll = false;
        scrollBottom();
    });

    $('.messages').on('scroll', function(){
        if(!autoScrolling){
            if($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight){
                $('.scrollPopup').css('opacity', 0);
                $('.scrollPopup').css('z-index', -1);
                preventNewScroll = false;
            }
            else{
                $('.scrollPopup').css('z-index', 1);
                $('.scrollPopup').css('opacity', 1);
                preventNewScroll = true;
            }
        }
    });

    var chat = $('.chat');
    var printer = $('.messages', chat);
    var preventNewScroll = false;

    /*
     * Scrolls the chat to the bottom automatically.
     */
    function scrollBottom(){
        if(!preventNewScroll){
            autoScrolling = true;
            printer.stop().animate( {scrollTop: printer[0].scrollHeight - printer.innerHeight()  }, 200, 'swing', function(){
                if(msgCount > maxNumMsg){
                    for(var i=maxNumMsg; i<msgCount; i++){
                        $(printer).find('div').first().remove();
                    }
                    msgCount -= (i-maxNumMsg);
                }
                autoScrolling = false;
            });
        }
    }

    //check for websocket support
    if ("WebSocket" in window) {
        var wsPath = 'ws://kappafeed.com/feed';
        var ws = new WebSocket(wsPath);

        $(document).on('click', '.emoticonHolder', function(event){
            $('#twitchEmotes').css('opacity', 0);
            emotesOpen = false;

            ws.send(JSON.stringify({emoteId : $(this).text()}));
        });


        ws.onopen = function() {
            kappaCount = 0;
            msgCount = 0; //number of messages in chat
            maxNumMsg = 40; //number of messages chat will hold before removal
            kpmArray = []; //keeps a few kpm measurements for smooth averaging
            channelNameLen = 10; //max length of a channel name before shortened
            kappaPollRate = 1.7; //seconds between each poll

            window.setInterval(kappaPerMin, kappaPollRate * 1000);
            printer.append('<div class="msgDiv"><div class="serverMsgDiv">Welcome to kappafeed.</div></div>');
            scrollBottom();
        };

        ws.onmessage = function (evt) {
            msgCount++;
            var jsonMsg = JSON.parse(evt.data);
            var parsedMsg = '';
            
            if(jsonMsg.channel){
            	parsedMsg = parseKappaMsg(jsonMsg);
            }
            else if(jsonMsg.serverMsg){
            	parsedMsg = '<div class="msgDiv"><div class="serverMsgDiv">' + jsonMsg.serverMsg + '</div></div>'
            }
            
            printer.append(parsedMsg);
            scrollBottom();
        };

        ws.onclose = function() {
            printer.append('<div class="msgDiv"><div class="serverMsgDiv">Connection closed.</div></div>');
            scrollBottom();
        };

    }
    else{
        alert('websocket not supported');
    }
});

/*
 * Parses a kappa-filled json message from server.
 */
function parseKappaMsg(jsonMsg){
    var channel = jsonMsg.channel.substring(1);
    var shortChannel = channel;

    if(shortChannel.length > channelNameLen){
        shortChannel = shortChannel.substring(0, channelNameLen) + '...';
    }

    //build the html for channel link
    var kappaMsg = '<div class="channelDiv"><span class="channel"><a class="channelLink" href="http://www.twitch.tv/' +
         channel + '" target="_blank">' + shortChannel + '</a></span></div>';
    //build the user link
    kappaMsg += '<div class="userMsgDiv"><span class="user"><a class="userLink" style="color:'+
        jsonMsg.user.color + ';" href="http://www.twitch.tv/' +
        jsonMsg.user.name + '/profile" target="_blank">' + jsonMsg.user.name +
        '</a>';

    //if this is an action message, color it green
    if(jsonMsg.msg.content.substring(0,6) == 'ACTION'){
        kappaMsg += ' </span><span class="action" style="color:' +
            jsonMsg.user.color + '">';
        jsonMsg.msg.content = jsonMsg.msg.content.substring(7);
    }
    else{
        kappaMsg += ': </span><span class="message">';
    }
    kappaMsg += jsonMsg.msg.content;
    kappaCount += jsonMsg.msg.emoteCount;
    
    return '<div class="msgDiv">' + kappaMsg + '</div>';
}

/*
 * Calculates the KPM in chat.
 */
function kappaPerMin(){
    var kpm = kappaCount * (60/kappaPollRate);
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

    var curKpm = parseInt($('div.kpm').text().replace('kpm', ''));
    gradualIncrease(curKpm, avgKpm, (kappaPollRate-0.2)*1000, 100);
    kappaCount = 0;
}

/*
 * Animates the kpm meter in between updates.
 */
function gradualIncrease(startNum, endNum, time, updateRate){
    //number of times to update value in time frame:
    var numUpdates = Math.ceil(time / updateRate);
    //amount to increase value by each update:
    var increaseAmt = (endNum - startNum) / numUpdates;

    var value = startNum;
    var numIncreases = 0;        
    var intervalId = window.setInterval(updateValue, updateRate);

    function updateValue(){
        value += increaseAmt;
        numIncreases++;
        $('div.kpm').text(value.toFixed(0) + 'kpm');

        if(numIncreases >= numUpdates){
            window.clearInterval(intervalId);
        }
    }
}
