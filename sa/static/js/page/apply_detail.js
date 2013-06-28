function get_sinfo(tr){
  hostname_obj = tr.children("td:nth-child(1)");
  ip_obj = tr.children("td:nth-child(2)");
  status_obj = tr.children("td:nth-child(3)");
  type_obj = tr.children("td:nth-child(4)");

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
      $(type_obj).html(data.type);
    }
  });
}

$(document).ready(function(){
  $("tr.getsinfo").each(function(){
    get_sinfo($(this));
  });
});
