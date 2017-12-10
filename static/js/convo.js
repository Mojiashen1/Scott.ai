var index = 0;
$('#next').click(function(e) {
  index++;
  var questions = $('h4').attr('data-question');
  console.log(Object(questions));
  questions = JSON.parse(questions.slice(1,questions.length-2));
  $('h4').val(questions[index]['questionText']);
})
