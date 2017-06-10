function updateWebpageProfile() {
	var message_request;
	message_request = "/getUserProfile";
	$.get(message_request, function(profileData) {
		data = JSON.parse(profileData)
		replaceProfile = "<h2>" + data['fullname'] + '</h2><div class="imgcontainer"><img src="' + data['picture'] + '" alt="Avatar" class="avatar"></div><h3>Position: ' + data['position'] + '</h3><h3>Location: ' + data['location'] + '</h3><h3>Description: ' + data['description'] + '</h3>'
		$(".profile").html(replaceProfile)
	});
}

function editProfile() {
	var message_request;
	message_request = "/getUserProfile";
	$.get(message_request, function(profileData) {
		data = JSON.parse(profileData)
		replaceProfile = '<form action="/saveProfile" method="post" enctype="multipart/form-data" class="editProfile">Name: <input type="text" name="fullname" value="' + data['fullname'] + '"/><br/>Picture: <input type="text" name="picture" value="' + data['picture'] + '"/><br/>Location: <input type="text" name="location" value="' + data['location'] + '"/><br/>Position: <input type="text" name="position" value="' + data['position'] + '"/><br/>Description:<br/> <textarea name="description">' + data['description'] + '</textarea><br/><button type="submit">Save Profile</button></form>'
		$(".profile").html(replaceProfile)
	});
}


function viewProfiles() {
	var message_request;
	message_request = "/getAllUsers";
	$.get(message_request, function(userNames) {
		users = JSON.parse(userNames)
		replaceText = '<ul class="side-nav"><li style="width:100% id="Home" float:center"><a class="active" href="/">Home</a></li>'
		for (var items in users) {
			replaceText += '<li style="width:100%"><a class="side" id="' + users[items]['upi'] + '" href="javascript:displayProfile(\'' + users[items]['upi'] + '\')">' + users[items]['upi'] + '</a></li>'
		}
		$(".dash").html(replaceText)
	});
}


function displayProfile(user) {
	var message_request;
	message_request = "/userProfile?user=" + user;
	$.get(message_request, function(profileData) {
		data = JSON.parse(profileData)
		replaceProfile = "<h2>" + data['fullname'] + '</h2><div class="imgcontainer"><img src="' + data['picture'] + '" alt="Avatar" class="avatar"></div><h3>Position: ' + data['position'] + '</h3><h3>Location: ' + data['location'] + '</h3><h3>Description: ' + data['description'] + '</h3>'
		$(".profile").html(replaceProfile)
	});
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


function editEvent() {
	replaceProfile = '<form action="/createEvent" method="post" enctype="multipart/form-data" class="editProfile">Event Name: <input type="text" name="name" value=""/><br/>Guest: <input type="text" name="guest" value=""/><br/>Start Time: <input type="text" name="start" value=""/><br/>End Time: <input type="text" name="end" value=""/><br/>Event Location: <input type="text" name="loc" value=""/><br/>Event Description:<br/> <textarea name="desc"></textarea><br/><button type="submit">Save Event</button></form>'
	$(".profile").html(replaceProfile)
}


function viewEvent() {
	var message_request;
	message_request = "/getEvents";
	$.get(message_request, function(eventList) {
		events = JSON.parse(eventList)
		replaceText = '<div class="upcoming-event">Upcoming events</div><ul class="event-header">'
		for (var item in events) {
			alert
			replaceText += 	'<ul><li style="width:100%">' + events[item]['event_name'] + '</li> \
							<li class="desc">Host: ' + events[item]['host'] + '</li> \
							<li class="desc">Location: ' + events[item]['location'] + '</li> \
							<li class="desc">Start Time: ' + events[item]['start_time'] + '</li> \
							<li class="desc">End Time: ' + events[item]['end_time'] + '</li> \
							<li class="desc">Description: ' + events[item]['description'] + '</li> \
							<li class="desc">Acknowledge: </li> \
							<select class="status" id="' + events[item]['id'] + '" onChange="setEvent(this.value, ' + events[item]['id'] + ')" >'
			if (events[item]['attendance'] == 2) {
				replaceText += '<option value="2" selected>Going</option><option value="1">Maybe</option><option value="0">Not Going</option></select></ul>'
			} else if (events[item]['attendance'] == 1) {
				replaceText += '<option value="2" >Going</option><option value="1" selected>Maybe</option><option value="0">Not Going</option></select></ul>'
			} else {
				replaceText += '<option value="2" >Going</option><option value="1" >Maybe</option><option value="0" selected>Not Going</option></select></ul>'
			}
		} 
		$(".profile").html(replaceText)
	});
	
}

function setEvent(value, id) {
	var message_request;
	message_request = "/acknowledgeHost?attendance=" + value + "&row_id=" + id;
	$.get(message_request)
}


$(document).ready(function() {
	// Starting
	updateWebpageProfile()
	getStatus()
});
