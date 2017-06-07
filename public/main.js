// GLOBAL VARIABLES //
var activeUser = "";

function displayMessages(user) {
	$('.name-bar').html('');
	$(".name-bar").append(user);
	activeUser = user;
	// Get the messages from the database somehow
	message_request = "/getMessages?user=" + user;
	$.get(message_request, function(response) {
		$('.messages').html(response);
	});
}

function sendMessage() {
	$(".form-box").submit(function() {
		message_request = "/sendMessage?destination=" + activeUser + '&message=' + $(".write-message").val();
		$.get(message_request, function() {
			alert("messagesent");
		});
	})
}

$(document).ready(function() {
	// Staring
});
