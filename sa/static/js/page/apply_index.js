function sloading(tr){
  name_obj = tr.children("td:nth-child(1)");
  ip_obj = tr.children("td:nth-child(2)");
  state_obj = tr.children("td:nth-child(3)");

  $(name_obj).html("loading...");
  $(ip_obj).html("");
  $(state_obj).html("");
}

function get_sinfo(tr){
  name_obj = tr.children("td:nth-child(1)");
  ip_obj = tr.children("td:nth-child(2)");
  state_obj = tr.children("td:nth-child(3)");

  $.ajax({
    url: "/server/" + tr.attr("data-sid")  + "/getinfo",
    dataType: "json",
    async: false,
    success: function(data){
      ip = "";
      $.each(data.ip, function(i,item){ ip = ip + item + " "; });

      $(name_obj).html(data.name);
      $(ip_obj).html(ip);
      $(state_obj).html(data.state);
    }
  });
}

function get_tinfo(tr){
  hostname_obj = tr.children("td:nth-child(1)");
  ip_obj = tr.children("td:nth-child(2)");
  status_obj = tr.children("td:nth-child(3)");
  daysleft_obj = tr.children("td:nth-child(4)");

  $.ajax({
    url: "/server/" + tr.attr("data-sid")  + "/getinfo",
    dataType: "json",
    async: false,
    success: function(data){
      ip = "";
      $.each(data.ip, function(i,item){ ip = ip + item + " "; });

      $(hostname_obj).html(data.name);
      $(ip_obj).html(ip);
      $(status_obj).html(data.state);
      $(daysleft_obj).html(data.daysleft);
    }
  });
}


$(document).ready(function(){
  //get server info
  $("tr.getinfo").each(function(i){
    get_sinfo($(this));
  });

  //get test server info
  $("tr.tinfo").each(function(i){
    get_tinfo($(this));
  });

  //detail button click
  $(".detail a[data-action='toggle']").click(function(){
    $("." + $(this).attr("data-ele-id")).toggle();
    $(this).parent().children("a[data-action='refresh']").click();
    return false;
  });

  //refresh button click
  $(".detail a[data-action='refresh']").click(function(){
    $("tr[class*='" + $(this).attr("data-ele-id") + "']").each(function(){
      sloading($(this));
      get_sinfo($(this));
    });
    return false;
  });
});
