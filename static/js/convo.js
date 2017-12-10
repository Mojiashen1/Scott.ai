var index = 0;
$('#next').click(function(e) {
  index++;
  var questions = $('h4').attr('data-question')
  $('h4').val(questions[index]['questionText'])
})
