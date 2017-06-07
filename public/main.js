function displayMessages(user) {
	$('.name-bar').html('');
	$(".name-bar").append(user);
	// Get the messages from the database somehow
	message_request = "/getMessages?user=" + user;
	$.get(message_request);
}


$(document).ready(function() {
    $("p").click(function(){
        $(this).append("Some appended text.");
    });
});
