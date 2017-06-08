// GLOBAL VARIABLES //
var activeUser

function displayMessages(user) {
	$('.name-bar').html('');
	$(".name-bar").append(user);
	activeUser = user
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

$("#send-button").click(function() {
	sendMessage()
	refreshMessages(activeUser)
	document.getElementById('clear').value='';
	});


$('input[type=file]').change(function(){
		$(this).simpleUpload("/sendFile", {

			start: function(file){
				//upload started
				console.log("Logged File Uploaded");
			},
 
			progress: function(progress){
				//received progress 
			},
 
			success: function(data){
				//upload successful 
				console.log("Logged File Sent");
				refreshMessages(activeUser)
			},
 
			error: function(error){
				//upload failed 
				alert("File Upload Failed");
			}
 
		});
	});



function sendMessage() {
	var message_request;
	//Get the messages from the database somehow
	if ($('.write-message').is(':empty')){
		message_request = "/sendMessage?message=" + $(".write-message").val();
		$.get(message_request, function(response) {
			console.log("Logged Message Sent - " + response + "");
		});
	}
}

function refreshMessages(user) {
    var message_request;
    message_request = "/getMessages?user=" + user;
	$.get(message_request, function(response) {
		$('.messages').html(response);
	});
}

// Need a function to refresh the user list
function refreshUsers() {

}

$(document).ready(function() {
	// Starting
});
