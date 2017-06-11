// GLOBAL VARIABLES //
var activeUser

// display the messages on the screen
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


// Clear the text box and clear the messaage 
$("#send-button").click(function() {
	sendMessage()
	refreshMessages(activeUser)
	document.getElementById('clear').value='';
	});


// Send the file uppon request
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

//Search the users
function searchFunction() {
    // Declare variables
    var input, filter, ul, li, a, i;
    input = document.getElementById('search-name');
    filter = input.value.toUpperCase();
    ul = document.getElementById("search-users");
    li = ul.getElementsByTagName('li');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

// Refresh the user list
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

// Send the message to teh user
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


// Get the current status of the user
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

// refresh all the messages
function refreshMessages(user) {
    var message_request;
    message_request = "/getMessages?user=" + user;
	$.get(message_request, function(response) {
		$('.messages').html(response);
	});
}

// Send message on enter hit
document.getElementById("clear").addEventListener("keydown", function(e) {
	if (e.keyCode == 13) { 
		sendMessage();
		refreshMessages(activeUser)
		document.getElementById('clear').value='';
	}
}, false);

// At document ready do this:
$(document).ready(function() {
	// Starting
	refreshUsers()
	//setStatus()
	getStatus()
});
