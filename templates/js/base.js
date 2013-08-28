var playing = 0;
var SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
var itemList = $('#show-items');


var update_function = function(){
           $.getJSON( SCRIPT_ROOT+'/_update',
                {},
                function(data){
                    itemList.children().remove()
                    console.log(data);
                    for (item in data){
                        console.log(data[item]);
                        itemList.append(
                                "<li class='video'>"
                                + "<span class='editable'>"
                                + data[item] 
                                 + " </span><a href='#'>x</a></li>"
                                );
                    $.publish('/regenerate-list/', []);  
                    }     
                }
            )
        };

update_function();

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
                {element:item},
                update_function()
            )            
        };

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

