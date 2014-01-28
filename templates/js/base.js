window.URL = window.URL || window.webkitURL;

var playing = 0;
var SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
//var SCRIPT_ROOT = ""
var itemList = $('#show-items');
var lockBackground = false;
var backgroundDir = '/static/images/';
var currentBG = ''


function periodic_updates(){    
    update_function();
    update_status_function();
    setTimeout(periodic_updates,1000);
};

$(document).ready(function() {
    periodic_updates();
    setTimeout(periodic_updates,1000);
});


var update_index = function(){
    $("span.index").each(function (index){
        $(this).text(index+1);
    });
};

var check_index_and_sort = function(base){
    if(base.length == 0){
        return;
    };
    $("tr").each(function (index,item){

        if(index == 0 && item.getAttribute("id") != base[0].url){
            $("tr#"+base[0].url).insertBefore($("tr")[0]);
        }else if(index < base.length){
            if(item.getAttribute("id") != base[index].url){
                $("tr#"+base[index].url).insertAfter($("tr")[index-1]);            
            }
        }
    });
};

var cmp = function(listA,listB){
    if(listA.length != listB.length){
        return false;
    }
    for(var index=0;index<listA.length;index++){
        if(listA[index].url != listB[index].url){
            return false;
        }
    }
    return true;
};

var update_status_function = function(){
    $.getJSON(SCRIPT_ROOT + '/_get_playing',
        {},
        function(status){
	   try{
            //console.log(status.now_playing)
            if(status.song_playing == '0'){
                update_status_function();
            }else if(status.now_playing == 1){
                $("span.now_playing").html('Now playing: <b>'+status.song_playing+'</b>')
            }else if(status.now_playing == 2){
                $("span.now_playing").html('Now paused: <b>'+status.song_playing+'</b>')
            }else{
                $("span.now_playing").html('<b>Not playing...</b>')
            }
	   }catch(err){
		console.log("Exception! "+String(err));
	   }
        });
};

var get_video_container = function(id,title,duration,vpositive,vnegative){
    var txt_title = "Carregando..."
    var txt_duration = "?"

    if(id != title){
        txt_title = title
    }
    if(duration != '?'){
        var time_duration = new Date((duration*1000));
        if(time_duration.getMinutes() < 9){
            txt_duration = ''+"0"+time_duration.getMinutes();
        }else{
            txt_duration = ''+time_duration.getMinutes();
        }
        txt_duration = txt_duration+":";
        if(time_duration.getSeconds() < 9){
            txt_duration = txt_duration + "0"+time_duration.getSeconds();
        }else{
            txt_duration = txt_duration+time_duration.getSeconds();
        }

    }

    var container =
        "<tr id='"+id+"' style='display:none;' valign='middle'>"
            +"<td>"
                +"<span class='index'>1</span>"
            +"</td>"
            +"<td>"
                +"<div class='video'>"
                    +"<span class='videoitem'>"
                    +txt_title+" ("+txt_duration+")"
                     +"</span>"                    
                 +"</div>"
            +"</td>"
            +"<td>"
                +"<div  class='vote'>"
                    +"<a >"
                        +"<img src={{ url_for('static', filename='like.png')}} alt='Next' id='like' />"
                    +"</a>"
                    +"<span class='votepos'>"+vpositive+"</span>"
                +"</div>"
              
            +"</td>"
            +"<td>"  
                +"<a href='#' class='remove'>  x</a>"
            +"</td>"
         +"</tr>";
    return container;
};

var update_function = function(){
           $.getJSON( SCRIPT_ROOT+'/_update',
                {},
                function(data){
                    var items = data.queue;
                    var videos = document.getElementsByClassName('video');

                    var urls = new Array();
                    Array.prototype.forEach.call(items,function(item){
                        urls.push(item.url);
                    });

                    // Checks if any item was removed
                    Array.prototype.forEach.call(videos, function(video) {
                        if(urls.indexOf(video.parentNode.parentNode.getAttribute('id')) == -1){
                            console.log("removing "+video.innerText);
                            $("#"+video.parentNode.parentNode.getAttribute('id')).fadeOut("fast",function(){
                                $("#"+video.parentNode.parentNode.getAttribute('id')).remove();
                                update_index();
                            }                            
                            );
                        }
                    }); 

                    // Add new items
                    for (item in items){                    
                        var url_item = get_video_container(items[item].url,items[item].title,items[item].duration,items[item].positive,items[item].negative);
                        if($("#"+items[item].url).size() == 0){
                            itemList.append(url_item);                            
                            $("#"+items[item].url).fadeIn(function(){});   
                        }                        
                    }

                    // Update votes
                    Array.prototype.forEach.call(items,function(item){
                        $("tr#"+item.url+" td span.votepos").text(item.positive);
                        $("tr#"+item.url+" td span.voteneg").text(item.negative);
                    });

                    // Reorder items
                    var queue = new Array();
                    $("tr").each(function(index,item){
                        queue.push({"url":item.getAttribute("id")});
                    });     
                    if(!cmp(queue,items)){
                        //console.log("Sorting");
                        check_index_and_sort(items)
                    };

                    update_index();

                    // Change background
                    if(data.backgrounds_directory != backgroundDir){
                        backgroundDir = data.backgrounds_directory;
                    }
                    if(data.current_background && !lockBackground){
                        currentBG = data.current_background;
                        change_background(data.current_background); 
                    }
                } 
            );                
        };
function change_background(background){
    var current_background = $('body').css('background-image');
    var new_background = 'url(/'+backgroundDir+'/'+background+')';
    if(new_background != current_background){
        //console.log(new_background);
        $('body').css('background-image',new_background);
        return true;
    }else{
        return false;
    }
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
var rm_function = function(id){
    console.log(id);
            $.getJSON( SCRIPT_ROOT+'/_rm_url',
                {element:id},
                function(n){
                    update_function()
                }
            )            
        };

var get_video_data = function(id,calllback_function){
    if(calllback_function == null){
        $.getJSON('http://gdata.youtube.com/feeds/api/videos/'+id+'?v=2&alt=jsonc',
           // Método que atualiza o nome do vídeo na lista
             function(data,status,xhr){
                    if(document.getElementById(id) != null && data.data.title != 'NaN'){
                        $("#"+id+" > td > div.video > span.videoitem").text(data.data.title);
                        //document.getElementById(id).children[0].innerHTML = id;
                    }
                }
            );
    }else{
        $.getJSON('http://gdata.youtube.com/feeds/api/videos/'+id+'?v=2&alt=jsonc',calllback_function);
    }
}

$("#upd").click(function(){
            console.log('update');
            update_function();
        });

$("#addNewSong").click(function(){
        var button = document.getElementById("newSongUrl");
        console.log(button.value);
        add_function(button.value);
      //  update_function();
        button.value = "";
    });

// Votes
$("*").delegate("tr div.vote a","click",function(e){
    var type = $(this).children().attr("id");
    var id = $(this).parent().parent().parent().attr("id");

    if(type == "like"){
        var positive = 1;
        var negative = 0;
    }else{
        var positive = 0;
        var negative = 1;        
    }

    $.getJSON(SCRIPT_ROOT+'/_vote',
                {"url":id,"positive":positive,"negative":negative},
                update_function()    
            );
});

// Remove todo
$("*").delegate("tr a.remove", "click", function(e) {
    var id = $(this).parent().parent().attr("id");
    console.log("Tchau "+id);
    rm_function(id);
});

$("#clear-all").click(function(){
     $.getJSON(    SCRIPT_ROOT+'/_clear-all',
                    {},
                    update_function()    
                );
});


 $('#login-trigger').click(function(){
            $(this).next('#login-content').slideToggle();
            $(this).toggleClass('active');          
            
            // Inverte a seta
            if ($(this).hasClass('active'))$(this).find('span').html('&#x25B2;')
              else $(this).find('span').html('&#x25BC;')
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


///////////////////////
// Player controls
///////////////////////
$('#startPL').bind('mouseover',function(e){
    if($("#startPL img").attr("state") == "playing"){
        $('#startPL img').attr("src","{{ url_for('static', filename='pause_mouse_over.png')}}");
    }else{
        if($("#startPL img").attr("state") == "paused"){
            $('#startPL img').attr("src","{{ url_for('static', filename='play_mouse_over.png')}}");
        }
    }
});

$('#startPL').bind('mouseleave',function(e){
    if($("#startPL img").attr("state") == "playing"){
        $('#startPL img').attr("src","{{ url_for('static', filename='pause.png')}}");
    }else{
        if($("#startPL img").attr("state") == "paused"){
            $('#startPL img').attr("src","{{ url_for('static', filename='play.png')}}");
        }
    }
});

$('#startPL').bind('click',function(e){
    if($("#startPL img").attr("state") == "paused"){
        $('#startPL img').attr("src","{{ url_for('static', filename='pause_mouse_over.png')}}");
    }else{
        if($("#startPL img").attr("state") == "playing"){
            $('#startPL img').attr("src","{{ url_for('static', filename='play_mouse_over.png')}}");
        }
    }
});


$('#next').bind('mouseover',function(e){
    $('#next img').attr("src","{{ url_for('static', filename='next_mouse_over.png')}}");
});

$('#next').bind('mouseleave',function(e){
    $('#next img').attr("src","{{ url_for('static', filename='next.png')}}");
});

$('#revert').bind('mouseover',function(e){
    $('#revert img').attr("src","{{ url_for('static', filename='previous_mouse_over.png')}}");
});

$('#revert').bind('mouseleave',function(e){
    $('#revert img').attr("src","{{ url_for('static', filename='previous.png')}}");
});

function set_vinheta1(files){
    window.URL.revokeObjectURL($("#player_vinheta1").attr("src"));
    $("#player_vinheta1").attr("src",window.URL.createObjectURL(files[0]));
    $("#txt_vinheta1").text(files[0].name);
};

function set_vinheta2(files){
    window.URL.revokeObjectURL($("#player_vinheta2").attr("src"));
    $("#player_vinheta2").attr("src",window.URL.createObjectURL(files[0]));
    $("#txt_vinheta2").text(files[0].name);
};

function set_vinheta3(files){
    window.URL.revokeObjectURL($("#player_vinheta3").attr("src"));
    $("#player_vinheta3").attr("src",window.URL.createObjectURL(files[0]));
    $("#txt_vinheta3").text(files[0].name);
};

function get_vinheta1(){
    $("#input_vinheta1").click();
};

function get_vinheta2(){
    $("#input_vinheta2").click();
};

function get_vinheta3(){
    $("#input_vinheta3").click();
};

function play_vinheta1(){
    if(document.getElementById("player_vinheta1").paused){
        document.getElementById("player_vinheta1").play();
    }else{
        document.getElementById("player_vinheta1").pause();        
    }
};

function play_vinheta2(){
    if(document.getElementById("player_vinheta2").paused){
        document.getElementById("player_vinheta2").play();
    }else{
        document.getElementById("player_vinheta2").pause();        
    }
};

function play_vinheta3(){
    if(document.getElementById("player_vinheta3").paused){
        document.getElementById("player_vinheta3").play();
    }else{
        document.getElementById("player_vinheta3").pause();        
    }
};

$("#background-chooser a").click(function(){
    var choose = $(this).text()
    lockBackground = true;
    if(change_background(choose)){
        currentBG = choose;
        $("#save-background").prop("disabled",false);
    }else{
        lockBackground = false;
    }
});

$("#save-background").click(function(){
    console.log("Saving...")
    $.getJSON( SCRIPT_ROOT+'/_set_background',
                {new_background:currentBG},
                function(data){
                    //A funcao de callback nao funciona!
                    console.log("Done!");
                    $("#save-background").prop("disabled",true);
                    lockBackground = false;
                });
});