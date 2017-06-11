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
 
			success: function(data){
				//upload successful
				alert("File Upload Success!");
				console.log("Logged File Sent");
			},
 
			error: function(error){
				//upload failed 
				alert("File Upload Failed!");
			}
 
		});
		
		refreshMessages(activeUser)
	});


$(".message-box-user").click(function(){
    $("span").fadeIn();
});



function refreshUsers() {
	var message_request;
	message_request = "/refreshUserList";
	$.get(message_request, function(response) {
		$('.dash').html(response);
	});
	setTimeout(function() {
		refreshUsers()
	}, 25000);
}


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

function getStatus() {
	var state
	state = document.getElementById('status').value;
	message_request = "/storeStatus?status=" + state
	$.get(message_request, function(response) {
		
	});
	setTimeout(function() {
		getStatus()
	}, 20000);
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
	refreshUsers()
	//setStatus()
	getStatus()
});
