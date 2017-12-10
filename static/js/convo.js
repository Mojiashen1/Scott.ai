var index = 0;
$('#next').click(function(e) {
  index++;
  var questions = $('h4').attr('data-question')
  console.log(questions)
  $('h4').val(questions[index]['questionText'])
})
