// GLOBAL VARIABLES //

function displayMessages(user) {
	$('.name-bar').html('');
	$(".name-bar").append(user);
	var message_request;
	// Get the messages from the database somehow
	message_request = "/getMessages?user=" + user;
	$.get(message_request, function(response) {
		$('.messages').html(response);
	});
	var toggle_request;
	toggle_request = "/toggleActiveUser?user=" + user;
	$.get(toggle_request, function(response) {
	});
}

function sendMessage() {
	$(".form-box").ajaxForm(function() {
	    refreshMessages(activeUser);
	});
}

function refreshMessages(user) {
    var message_request;
    message_request = "/getMessages?user=" + user;
	$.get(message_request, function(response) {
		$('.messages').html(response);
	});
}

$(document).ready(function() {
	// Starting
});
