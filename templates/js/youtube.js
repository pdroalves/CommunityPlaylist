//Load player api asynchronously.
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[5];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
var player;
var default_start_video = 'dQw4w9WgXcQ'
var default_next_video = 'F0BfcdPKw8E'
var song_playing = default_start_video
var song_title = ""
var status = 0
var current_time = 0

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
      height: '390',
      width: '640',
      videoId: default_start_video,
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
    ;
}
function checkValidUrl(url){
    if(url == null){
        return 0;
    }else{
        return 1;
    }
}
$("#startPL").click(function(){
    if(player.getPlayerState() == YT.PlayerState.PAUSED){
        player.playVideo();
    }
});

$("#pausePL").click(function(){
    player.pauseVideo();
});

$("#next").click(function(){
    playNextVideo();
});

$("#revert").click(function(){
    player.seekTo(0);
});

function playVideoByUrl(url){
    player.loadVideoByUrl(url);
};

function playNextVideo(){
    $.getJSON( SCRIPT_ROOT + '/_next',
            {},
            function(item){
                console.log("Proximo video "+item);
                if(item != null){
                    song_playing = item;
                }else{
                    song_playing = default_next_video
                }
                    player.loadVideoById(song_playing)
                    update_status_function();
                    update_function();
            })
};
function onPlayerReady(evt) {
    console.log('playing '+playing)
    //if(playing)
    evt.target.playVideo();
};

function updateStatus(){
    var current_time = 0;

    if(status == 1){
        current_time = player.getCurrentTime();
    }


    $.getJSON( SCRIPT_ROOT + '/_set_playing',
        {'now_playing':status,
          'song_id':song_playing,
         'song_playing':song_title,
          'current_time':current_time},
         function(s){
            console.log(s)
         }
        );
}


function periodicStatusUpdate(){
    if(document.getElementById('player') != null){
        updateStatus();
    }
    setTimeout(periodicStatusUpdate,1000);
}

periodicStatusUpdate();

function onPlayerStateChange(evt) {
    console.log('new state '+evt.data)

    if (evt.data == YT.PlayerState.ENDED) {
        playNextVideo();
    }else{
        get_video_data(song_playing,
            function(data,stats,xhr){
                //updateStatus(data.data.title,1);
                song_title = data.data.title;
                status = evt.data;
            }
        );
    }
};
function stopVideo() {
    player.stopVideo();
};
