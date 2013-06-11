$(document).ready(function(){
  $("input[type='checkbox']").click(function(){
    obj = $(this)
    $.getJSON("/user/" + obj.val() + "/" + obj.attr("data-role") + "/" + obj.prop('checked'), function(data){
        if(data.status != "ok"){ alert("修改失败！"); }
    });
  });
});
