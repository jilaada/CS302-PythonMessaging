function displayMessages(user) {
	$('.name-bar').html('');
	$(".name-bar").append(user);
	// Get the messages from the database somehow
	message_request = "/getMessages?user=" + user;
	$.get(message_request, function(response) {
		$('.messages').html(response);
	});
}

function sendMessage(message, file) {
	

$(document).ready(function() {
	// Staring
});
