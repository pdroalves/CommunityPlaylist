//Load player api asynchronously.
            var tag = document.createElement('script');
            tag.src = "https://www.youtube.com/iframe_api";
            var firstScriptTag = document.getElementsByTagName('script')[5];
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
            var player;
            var default_start_video = 'dQw4w9WgXcQ'
            var default_next_video = 'F0BfcdPKw8E'
            var song_playing = default_start_video

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

            function updateStatus(song_title,status){
                $.getJSON( SCRIPT_ROOT + '/_set_playing',
                    {'now_playing':status,
                     'song_playing':song_title},
                     function(){

                     }
                    );
            }

            function onPlayerStateChange(evt) {
                console.log('new state '+evt.data)

                if(evt.data == YT.PlayerState.PLAYING){
                    get_video_data(song_playing,
                        function(data,status,xhr){
                            updateStatus(data.data.title,1);
                    });
                }else if (evt.data == YT.PlayerState.ENDED) {
                    playNextVideo();
                }else{
                    get_video_data(song_playing,
                        function(data,status,xhr){
                            updateStatus(data.data.title,0);
                    });
                }
            };
            function stopVideo() {
                player.stopVideo();
            };
