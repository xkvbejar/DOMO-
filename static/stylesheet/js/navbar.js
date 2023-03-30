$('ul li a').hover(function() {
  var x = $(this);
  $('.menuUnderline').stop().animate({
     'width': x.width(),
     'left' : x.position().left
  }, 400);
});