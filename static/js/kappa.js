var kappaCount;
var kpmArray;
var msgCount;
var maxNumMsg;
var channelNameLen;
var kappaPollRate;
var selectedEmote;
var selectedEmoteId = '25';

$(function() {
    var autoScrolling = false;
    var emotesOpen = false;
    var infoOpen = false;
    var topChannelsOpen = false;

    $.getJSON("https://api.twitch.tv/kraken/chat/emoticon_images?emotesets=0", function(data) {
        var rawEmotes = data['emoticon_sets']['0'];
        for (var e in rawEmotes) {
            if (rawEmotes[e]['id'] == '25') {
                var dString = '<div class="emoticonHolder selected" style="background-image: url(\'http://static-cdn.jtvnw.net/emoticons/v1/' + rawEmotes[e]['id'] + '/1.0\')" data-hover="' + rawEmotes[e]['code'] + '">' + rawEmotes[e]['id'] + '</div>';
                $('div.kpm').empty().append('0 <img class="emoticon" src="http://static-cdn.jtvnw.net/emoticons/v1/' + selectedEmoteId + '/1.0" ></img> /min');
            } else
                var dString = '<div class="emoticonHolder" style="background-image: url(\'http://static-cdn.jtvnw.net/emoticons/v1/' + rawEmotes[e]['id'] + '/1.0\')" data-hover="' + emoteCodeCleaner(rawEmotes[e]['code']) + '">' + rawEmotes[e]['id'] + '</div>';
            $('.twitchEmotes').append(dString);
        }
    });

    /******************************* LISTENERS *******************************/
    $('.twitchSmile').on('click', function(e) {
        e.stopPropagation();
        $('.twitchEmotes').toggleClass('popupShow');
        $('.emotePopup > .popupArrow').toggleClass('emotePopupArrowShow');
        //jquery cannot toggle class of SVG
        if (emotesOpen) {
            $('.twitchSmile').attr('class', 'twitchSmile');
            emotesOpen = false;
        } else {
            $('.twitchSmile').attr('class', 'twitchSmile twitchSmileHover');
            emotesOpen = true;
        }
    });

    $('.infoIcon').on('click', function(e) {
        e.stopPropagation();
        $('.info').toggleClass('popupShow');
        $('.infoPopup > .popupArrow').toggleClass('infoPopupArrowShow');
        //jquery cannot toggle class of SVG
        if (infoOpen) {
            $('.infoIcon').attr('class', 'infoIcon');
            infoOpen = false;
        } else {
            $('.infoIcon').attr('class', 'infoIcon infoIconHover');
            infoOpen = true;
        }

        if (topChannelsOpen) {
            $('.topChannels').toggleClass('popupShow');
            $('.topChannelsPopup > .popupArrow').toggleClass('topChannelsPopupArrowShow');
            $('.topChannelsIcon').attr('class', 'topChannelsIcon');
            topChannelsOpen = false;
        }
    });

    $('.topChannelsIcon').on('click', function(e) {
        e.stopPropagation();
        $('.topChannels').toggleClass('popupShow');
        $('.topChannelsPopup > .popupArrow').toggleClass('topChannelsPopupArrowShow');
        //jquery cannot toggle class of SVG
        if (topChannelsOpen) {
            $('.topChannelsIcon').attr('class', 'topChannelsIcon');
            topChannelsOpen = false;
        } else {
            $('.topChannelsIcon').attr('class', 'topChannelsIcon topChannelsIconHover');
            topChannelsOpen = true;
        }

        if (infoOpen) {
            $('.info').toggleClass('popupShow');
            $('.infoPopup > .popupArrow').toggleClass('infoPopupArrowShow');
            $('.infoIcon').attr('class', 'infoIcon');
            infoOpen = false;
        }
    });

    $('.noDismiss').on('click', function(e) {
        e.stopPropagation();
    })

    $(window).on('click', function() {
        if (emotesOpen) {
            $('.twitchEmotes').toggleClass('popupShow');
            $('.emotePopup > .popupArrow').toggleClass('emotePopupArrowShow');
            $('.twitchSmile').attr('class', 'twitchSmile');
            emotesOpen = false;
        }
        if (infoOpen) {
            $('.info').toggleClass('popupShow');
            $('.infoPopup > .popupArrow').toggleClass('infoPopupArrowShow');
            $('.infoIcon').attr('class', 'infoIcon');
            infoOpen = false;
        }
        if (topChannelsOpen) {
            $('.topChannels').toggleClass('popupShow');
            $('.topChannelsPopup > .popupArrow').toggleClass('topChannelsPopupArrowShow');
            $('.topChannelsIcon').attr('class', 'topChannelsIcon');
            topChannelsOpen = false;
        }
    });

    $('.scrollPopup').on('click', function() {
        $(this).css('opacity', 0);
        $(this).css('z-index', -1);
        preventNewScroll = false;
        scrollBottom();
    });

    $('.messages').on('scroll', function() {
        if (!autoScrolling) {
            if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
                $('.scrollPopup').css('opacity', 0);
                $('.scrollPopup').css('z-index', -1);
                preventNewScroll = false;
            } else {
                $('.scrollPopup').css('z-index', 1);
                $('.scrollPopup').css('opacity', 1);
                preventNewScroll = true;
            }
        }
    });
    /***************************** END LISTENERS *****************************/

    var chat = $('.chat');
    var printer = $('.messages', chat);
    var preventNewScroll = false;

    /*
     * Scrolls the chat to the bottom automatically.
     */
    function scrollBottom() {
        if (!preventNewScroll) {
            autoScrolling = true;
            printer.stop().animate({
                scrollTop: printer[0].scrollHeight - printer.innerHeight()
            }, 200, 'swing', function() {
                if (msgCount > maxNumMsg) {
                    for (var i = maxNumMsg; i < msgCount; i++) {
                        $(printer).find('div').first().remove();
                    }
                    msgCount -= (i - maxNumMsg);
                }
                autoScrolling = false;
            });
        }
    }

    selectedEmote = $('.selected');

    //check for websocket support
    if ("WebSocket" in window) {
        var wsPath = 'ws://kappafeed.com/feed';
        var ws = new WebSocket(wsPath);

        $(document).on('click', '.emoticonHolder', function(event) {
            var nSelectedEmote = $(this);
            if (selectedEmote != nSelectedEmote) {
                $('.selected').removeClass("selected");
                nSelectedEmote.addClass("selected");

                kappaCount = 0;
                selectedEmote = nSelectedEmote;
                selectedEmoteId = $(this).text()

                printer.empty();
                msgCount = 0;
                printer.append('<div class="msgDiv"><div class="serverMsgDiv">searching for <img class="emoticon" src="http://static-cdn.jtvnw.net/emoticons/v1/' + selectedEmoteId + '/1.0" /></div></div>');

                ws.send(JSON.stringify({
                    emoteId: selectedEmoteId
                }));
            }
        });


        ws.onopen = function() {
            kappaCount = 0;
            msgCount = 0; //number of messages in chat
            maxNumMsg = 40; //number of messages chat will hold before removal
            kpmArray = []; //keeps a few kpm measurements for smooth averaging
            channelNameLen = 10; //max length of a channel name before shortened
            kappaPollRate = 1.7; //seconds between each poll

            window.setInterval(kappaPerMin, kappaPollRate * 1000);
            printer.append('<div class="msgDiv"><div class="serverMsgDiv" style="font-weight: bold;">welcome to kappafeed</div></div>');
            printer.append('<div class="msgDiv"><div class="serverMsgDiv">searching for <img class="emoticon" src="http://static-cdn.jtvnw.net/emoticons/v1/' + selectedEmoteId + '/1.0" /></div></div>');
            scrollBottom();
        };

        ws.onmessage = function(evt) {
            msgCount++;
            var jsonMsg = JSON.parse(evt.data);

            if (jsonMsg.channel) {
                var parsedMsg = parseKappaMsg(jsonMsg);
                printer.append(parsedMsg);
                scrollBottom();
            } else if (jsonMsg.serverMsg) {
                var serverMsg = '<div class="msgDiv"><div class="serverMsgDiv">' + jsonMsg.serverMsg + '</div></div>'
                printer.append(serverMsg);
                scrollBottom();
            } else if (jsonMsg.topChannels) {
                var topChannelsUl = $('.topChannels > ol');
                topChannelsUl.empty();
                for (var i = 0; i < jsonMsg.topChannels.length; i++) {
                    topChannelsUl.append('<li><a href="http://www.twitch.tv/' +
                        jsonMsg.topChannels[i].channel + '" target="_blank">' + jsonMsg.topChannels[i].channel + '</a></li>');
                }
            }
        };

        ws.onclose = function() {
            printer.append('<div class="msgDiv"><div class="serverMsgDiv">Connection closed.</div></div>');
            scrollBottom();
        };

    } else {
        alert('websocket not supported');
    }
});

/*
 * Parses a kappa-filled json message from server.
 */
function parseKappaMsg(jsonMsg) {
    var channel = jsonMsg.channel.substring(1);

    //build the html for channel link
    var kappaMsg = '<div class="channelDiv"><span class="channel"><a class="channelLink" href="http://www.twitch.tv/' +
        channel + '" target="_blank">' + channel + '</a></span></div>';
    //build the user link
    kappaMsg += '<div class="userMsgDiv"><span class="user"><a class="userLink" style="color:' +
        jsonMsg.user.color + ';" href="http://www.twitch.tv/' +
        jsonMsg.user.name + '/profile" target="_blank">' + jsonMsg.user.name +
        '</a>';

    //if this is an action message, color it the color of user name
    if (jsonMsg.msg.content.substring(0, 6) == 'ACTION') {
        kappaMsg += ' </span><span class="action" style="color:' +
            jsonMsg.user.color + '">';
        jsonMsg.msg.content = jsonMsg.msg.content.substring(7);
    } else {
        kappaMsg += ': </span><span class="message">';
    }
    kappaMsg += jsonMsg.msg.content;

    var emoteArray = jsonMsg.msg.emoteList;
    for (var i = 0; i < emoteArray.length; i++) {
        if (emoteArray[i] == selectedEmoteId)
            kappaCount++;
    }
    //kappaCount += jsonMsg.msg.emoteCount;

    return '<div class="msgDiv">' + kappaMsg + '</div>';
}

/*
 * Calculates the KPM in chat.
 */
function kappaPerMin() {
    var kpm = kappaCount * (60 / kappaPollRate);
    kpmArray.push(kpm);
    if (kpmArray.length > 5) {
        kpmArray.shift();
    }

    var avgKpm = 0;
    for (var i = 0; i < kpmArray.length; i++) {
        avgKpm += kpmArray[i];
    }
    avgKpm /= kpmArray.length;
    avgKpm = Math.round(avgKpm);

    var curKpm = parseInt($('div.kpm').text().replace(' <img class="emoticon" src="http://static-cdn.jtvnw.net/emoticons/v1/' + selectedEmoteId + '/1.0" ></img> /min', ''));
    gradualIncrease(curKpm, avgKpm, (kappaPollRate - 0.2) * 1000, 100);
    kappaCount = 0;
}

/*
 * Animates the kpm meter in between updates.
 */
function gradualIncrease(startNum, endNum, time, updateRate) {
    //number of times to update value in time frame:
    var numUpdates = Math.ceil(time / updateRate);
    //amount to increase value by each update:
    var increaseAmt = (endNum - startNum) / numUpdates;

    var value = startNum;
    var numIncreases = 0;
    var intervalId = window.setInterval(updateValue, updateRate);

    function updateValue() {
        value += increaseAmt;
        numIncreases++;
        $('div.kpm').empty().append(value.toFixed(0) + ' <img class="emoticon" src="http://static-cdn.jtvnw.net/emoticons/v1/' + selectedEmoteId + '/1.0" ></img> /min');

        if (numIncreases >= numUpdates) {
            window.clearInterval(intervalId);
        }
    }
}

function emoteCodeCleaner(code) {
    switch (code) {
        case 'B-?\\)':
            return 'B)';
        case '\\:-?[z|Z|\\|]':
            return ':|';
        case '\\:-?\\)':
            return ':)';
        case '\\:-?\\(':
            return ':(';
        case '\\:-?(p|P)':
            return ':P';
        case '\\;-?(p|P)':
            return ';P';
        case '\\&lt\\;3':
            return '<3';
        case '\\;-?\\':
            return ':\\';
        case 'R-?\\)':
            return 'R)';
        case '\\:-?D':
            return ':D';
        case '[oO](_|\\.)[oO]':
            return 'O_o';
        case '\\&gt\\;\\(':
            return '>(';
        case '\\:-?(o|O)':
            return ':O';
        case '\\:-?[\\\\/]':
            return ':/';
        case '\\;-?\\)':
            return ';)';
        default:
            return code;
    }
}
