$(document).ready(function(){
  $("h5").hover(
    function() {
      $(this).children("a").fadeIn();
    },
    function() {
      $(this).children("a").fadeOut();
    }
  );

  $("a[href='#templateModal']").click(function(){
    $("#templateModal .modal-body").load($(this).attr("data-url"));
  });
});
