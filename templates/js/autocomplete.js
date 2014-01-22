///////////////////////
// Autocomplete
///////////////////////

function convert_time(value){
  //var sInHour = 3600;
  var sInMinute = 60;

  var minutos = parseInt(value/sInMinute);
  var segundos =parseInt(value)%parseInt(sInMinute);
  if(minutos < 10){
    if(segundos < 10){
      var time = '0'+minutos + ':0'+segundos;
    }else{
      var time = '0'+minutos + ':'+segundos;
    }
  }else if(segundos < 10){
      var time = minutos + ':0'+segundos;
    }else{
      var time = minutos + ':'+segundos;
    }
  return time;
};
$( "#newSongUrl" ).autocomplete({
    source: function( request, response ) {
    var query = encodeURIComponent($("#newSongUrl").val());
    console.log("opa");
    $.ajax({
      url: "https://gdata.youtube.com/feeds/api/videos/-/"+query+"?v=2&alt=jsonc&orderby=viewCount",
      dataType: "jsonp",
      success: function( data ) {
          response( $.map( data['data']['items'], function( item ) {
                return {
                  //id:item['id'],title:item['title'],duration:item['duration'],thumbnail:item['thumbnail']['sqDefault']
                  label:item['title']+' ('+convert_time(item['duration'])+')',
                  value:'http://www.youtube.com/watch?v='+item['id'],
                  image:item['thumbnail']['sqDefault'],
                  stars:parseInt(item['rating'])
                }
              }));
          }
      });
    },
    minLength: 2,
    html: true,
    open: function() {
    $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
    },
    close: function() {
    $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
    }
}).data("uiAutocomplete")._renderItem = function (ul, item) {
    var stars = "";
    var count = 0;
    while(count < item.stars){
      stars = stars.concat("<img src=\"/static/images/star.png\" class=\"star-filled\" />");
      count += 1;
    }
    while(count < 5){      
      stars = stars.concat("<img src=\"/static/images/star.png\" class=\"star-unfilled\" />");
      count += 1;
    }
    var element = "<a><div class=\"row\">"
                    +"<div class=\"col-md-4\"><img src='" + item.image + "' alt='no thumbnail'/></div>"
                      +"<div class=\"col-md-8\"><p align=\"center\">"+item.label+"</p></div>"
                    +"<div class=\"row\">"
                      +"<div class=\"col-md-8 stars\">"+stars+"</div>"
                    +"</div>"
                  +"</div></a>"
    return $("<li></li>").data("item.autocomplete", item).append(element).appendTo(ul);
  };;