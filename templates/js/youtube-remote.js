//Load player api asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
var player;
//var default_start_video = 'dQw4w9WgXcQ'
//var default_next_video = 'F0BfcdPKw8E'
var song_playing = ''
var current_time = 0
var maxDelay = 5.0


function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
      height: '100%',
      width: '100%',
      //videoId: default_start_video,      
      events: {
        'onReady': onPlayerReady
      }
    });
    ;
}

function onPlayerReady(evt) {
    console.log('playing '+song_playing)
    //if(playing)
    evt.target.playVideo();
};

var update_status_function = function(){
    $.getJSON(SCRIPT_ROOT + '/_get_playing',
        {},
        function(status){
            //console.log(status.now_playing)
            if(song_playing != status.song_id){
                console.log(status.song_id)
                player.loadVideoById(status.song_id);
                player.seekTo(status.current_time);
                song_playing = status.song_id;
            }

            if(player.getPlayerState() == YT.PlayerState.PLAYING || 
                player.getPlayerState() == YT.PlayerState.PAUSED){
                var diff = Math.abs(player.getCurrentTime() - status.current_time);
                if(diff > maxDelay){
                    player.seekTo(status.current_time);
                }
            }

            if(status.now_playing == YT.PlayerState.PLAYING){
               player.playVideo();
               console.log("Play");
            }else if(status.now_playing == YT.PlayerState.PAUSED){
               player.pauseVideo();
               console.log("Pause");
            }else{
                player.stopVideo();
               console.log("End");
            }
        });
    };

function periodicGetStatusUpdate(){
    update_status_function();
    setTimeout(periodicGetStatusUpdate,1000);
}

periodicGetStatusUpdate();