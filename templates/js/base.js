var playing = 0;
var SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
var itemList = $('#show-items');
var removeLink =$('#show-items li span a');

function periodic_updates(){    
    update_function();
    update_status_function();
    setTimeout(periodic_updates,3000);
};

$(document).ready(function() {
    periodic_updates();
});

var update_status_function = function(){
    $.getJSON(SCRIPT_ROOT + '/_get_playing',
        {},
        function(status){
            console.log(status.now_playing)
            if(status.now_playing == 1){
                document.getElementById('now_playing').innerHTML='Now playing: <b>'+status.song_playing+'</b>'
            }else{
                document.getElementById('now_playing').innerHTML='<b>Not playing...</b>'    
            }
        });
};

var update_function = function(){
           $.getJSON( SCRIPT_ROOT+'/_update',
                {},
                function(items){
                    itemList.children().remove()
                    for (item in items){
                        var callback_function = function(data,status,xhr){
                            localStorage.setItem(data.data.title,items[item])
                            itemList.append(
                                    "<li class='video'>"
                                    + "<span class='editable'>"
                                    + data.data.title
                                     + " </span><a href='#'>x</a></li>"
                                    );
                            // data contains the JSON-Object below

                    $.publish('/regenerate-list/', []); 
                        };

                        get_video_data(items[item],callback_function);
                      
                    }} 
                    );                
        };

var add_function = function(newItem){
            var len = 0
            if(newItem.length > 0){
                 $.getJSON( SCRIPT_ROOT+'/_add_url',
                    {element:newItem},
                    function(n){
                        queue_size = n
                        update_function()
                    }
                )
             }
             return len
        };
var rm_function = function(item){
            $.getJSON( SCRIPT_ROOT+'/_rm_url',
                {element:localStorage.getItem(item)},
                function(n){
                    update_function()
                }
            )            
        };

var get_video_data = function(id,callback_function){
    $.getJSON('http://gdata.youtube.com/feeds/api/videos/'+id+'?v=2&alt=jsonc',
        callback_function);
}

$("#upd").click(function(){
            console.log('update');
            update_function();
        });

    // Fade In and Fade Out the Remove link on hover
    itemList.delegate('li', 'mouseover mouseout', function(event) {
        var $this = $(this).find('a');
         
        if(event.type === 'mouseover') {
            $this.stop(true, true).fadeIn();
        } else {
            $this.stop(true, true).fadeOut();
        }
    });

$("#addNewSong").click(function(){
        var button = document.getElementById("newSongUrl");
        console.log(button.value);
        add_function(button.value);
      //  update_function();
        button.value = "";
    });

// Remove todo
itemList.delegate("a", "click", function(e) {
    var $this = $(this);
 
    remove_item($this);
});

var remove_item = function($this){
    rm_function($this.parent().text().replace(' x',''));
};

$("#clear-all").click(function(){
     $.getJSON(    SCRIPT_ROOT+'/_clear-all',
                    {},
                    update_function()    
                );
});

// Fade In and Fade Out the Remove link on hover
itemList.delegate('li', 'mouseover mouseout', function(event) {
    var $this = $(this).find('a');
    
    if(event.type === 'mouseover') {
        $this.stop(true, true).fadeIn();
    } else {
        $this.stop(true, true).fadeOut();
    }
});

  function youtubeFeedCallback(data) {
    var s = '';
    s += '<img src="' + data.entry.media$group.media$thumbnail[0].url + '" width="' + data.entry.media$group.media$thumbnail[0].width + '" height="' + data.entry.media$group.media$thumbnail[0].height + '" alt="' + data.entry.media$group.media$thumbnail[0].yt$name + '" align="right"/>';
    s += '<b>Title:</b> ' + data.entry.title.$t + '<br/>';
    s += '<b>Author:</b> ' + data.entry.author[0].name.$t + '<br/>';
    s += '<b>Published:</b> ' + new Date(data.entry.published.$t).toLocaleDateString() + '<br/>';
    s += '<b>Duration:</b> ' + Math.floor(data.entry.media$group.yt$duration.seconds / 60) + ':' + (data.entry.media$group.yt$duration.seconds % 60) + ' (' + data.entry.media$group.yt$duration.seconds + ' seconds)<br/>';
    if (data.entry.gd$rating) {
      s += '<b>Rating:</b> ' + data.entry.gd$rating.average.toFixed(1) + ' out of ' + data.entry.gd$rating.max + ' (' + data.entry.gd$rating.numRaters + ' ratings)<br/>';
    }
    s += '<b>Statistics:</b> ' + data.entry.yt$statistics.favoriteCount + ' favorite(s); ' + data.entry.yt$statistics.viewCount + ' view(s)<br/>';
    s += '<br/>' + data.entry.media$group.media$description.$t.replace(/\n/g, '<br/>') + '<br/>';
    s += '<br/><a href="' + data.entry.media$group.media$player.url + '" target="_blank">Watch on YouTube</a>';
    document.write(s);
  };


