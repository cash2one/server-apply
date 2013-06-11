function if_days_show() {
  $.getJSON("/smodel/" + $("#s_id").val() + "/getinfo", function(data){
    if(data.if_t){ $(".days").show(); }else{ $(".days").hide(); }
  });
}

$(document).ready(function(){
  if_days_show();

  $("#s_id").click(function(){
    if_days_show();
  });
});
