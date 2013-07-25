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
  //get test server info
  $("tr.tinfo").each(function(i){
    get_tinfo($(this));
  });

  $("a[href='#renew']").click(function(){
    $('#renewUrl').val(($(this).attr('data-renew-url')));
  });

  $("#renewSubmit").click(function(){
    window.location.href = $('#renewUrl').val() + "?days=" + $('#renewDays').val();
  });

  setupVNC();
});
