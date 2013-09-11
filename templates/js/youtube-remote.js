//Load player api asynchronously.
            var tag = document.createElement('script');
            tag.src = "https://www.youtube.com/iframe_api";
            var firstScriptTag = document.getElementsByTagName('script')[5];
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
            var player;
            var default_start_video = 'dQw4w9WgXcQ'
            var default_next_video = 'F0BfcdPKw8E'
            var song_playing = default_start_video
            var current_time = 0
            var maxDelay = 10


            function onYouTubeIframeAPIReady() {
                player = new YT.Player('player', {
                  height: '100%',
                  width: '100%',
                  videoId: default_start_video,
                  events: {
                    'onReady': onPlayerReady,
                    'onStateChange': onPlayerStateChange
                  }
                });
                ;
            }
            var update_status_function = function(){
                $.getJSON(SCRIPT_ROOT + '/_get_playing',
                    {},
                    function(status){
                        //console.log(status.now_playing)
                        if(song_playing != status.song_id){
                            player.loadVideoById(status.song_id);
                            player.seekTo(status.current_time,false);
                            song_playing = song_id;
                        }

                        if(player.getCurrentTime() - status.current_time > maxDelay){
                            player.seekTo(status.current_time,false);
                        }

                        if(status.now_playing == 1){
                           player.playVideo();
                        }else{
                           player.pauseVideo();
                        }
                    });
                };

            function periodicStatusUpdate(){
                update_status_function();
                setTimeout(periodicStatusUpdate,1000);
            }

            periodicStatusUpdate();