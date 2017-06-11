// function that will update profile website
function updateWebpageProfile() {
	var message_request;
	message_request = "/getUserProfile";
	$.get(message_request, function(profileData) {
		data = JSON.parse(profileData)
		replaceProfile = "<h2>" + data['fullname'] + '</h2><div class="imgcontainer"><img src="' + data['picture'] + '" alt="Avatar" class="avatar"></div><h3>Position: ' + data['position'] + '</h3><h3>Location: ' + data['location'] + '</h3><h3>Description: ' + data['description'] + '</h3>'
		$(".profile").html(replaceProfile)
	});
}

// function that will displaty the edit profile page
function editProfile() {
	var message_request;
	message_request = "/getUserProfile";
	$.get(message_request, function(profileData) {
		data = JSON.parse(profileData)
		replaceProfile = '<form action="/saveProfile" method="post" enctype="multipart/form-data" class="editProfile">Name: <input type="text" name="fullname" value="' + data['fullname'] + '"/><br/>Picture: <input type="text" name="picture" value="' + data['picture'] + '"/><br/>Location: <input type="text" name="location" value="' + data['location'] + '"/><br/>Position: <input type="text" name="position" value="' + data['position'] + '"/><br/>Description:<br/> <textarea name="description">' + data['description'] + '</textarea><br/><button type="submit">Save Profile</button></form>'
		$(".profile").html(replaceProfile)
	});
}

// function that displays all the users on the dash and updates the profiles
function viewProfiles() {
	var message_request;
	message_request = "/getAllUsers";
	$.get(message_request, function(userNames) {
		users = JSON.parse(userNames)
		replaceText = '<ul class="side-nav"><input type="text" id="search-name" onkeyup="searchFunction()" placeholder="Search for names.."><ul class="side-nav" id="search-users">'
		for (var items in users) {
			replaceText += '<li class="search-users" style="width:100%"><a class="side" id="' + users[items]['upi'] + '" href="javascript:displayProfile(\'' + users[items]['upi'] + '\')">' + users[items]['upi'] + '</a></li>'
		}
		replaceText += '</ul></ul>'
		$(".dash").html(replaceText)
	});
}


// Search function for the user list
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


// display the profile of the current user
function displayProfile(user) {
	var message_request;
	message_request = "/userProfile?user=" + user;
	$.get(message_request, function(profileData) {
		data = JSON.parse(profileData)
		replaceProfile = "<h2>" + data['fullname'] + '</h2><div class="imgcontainer"><img src="' + data['picture'] + '" alt="Avatar" class="avatar"></div><h3>Position: ' + data['position'] + '</h3><h3>Location: ' + data['location'] + '</h3><h3>Description: ' + data['description'] + '</h3>'
		$(".profile").html(replaceProfile)
	});
}

// Get the status of the current user
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

// Display the edit form for the events
function editEvent() {
	replaceProfile = 	'<div class="create-event">Create New Event</div>'
	replaceProfile += 	'<form action="/createEvent" method="post" enctype="multipart/form-data" class="editProfile"> \
						Event Name: <input type="text" name="name" value=""/><br/> \
						Guest: <input type="text" name="guest" value=""/><br/> \
						Start Time: (DD-MM-YYYY HH:MM:SS) <input type="text" name="start" value=""/><br/> \
						End Time: (DD-MM-YYYY HH:MM:SS) <input type="text" name="end" value=""/><br/> \
						Event Location: <input type="text" name="loc" value=""/><br/> \
						Event Description:<br/> <textarea name="desc"></textarea><br/> \
						<button type="submit">Save Event</button></form>'
	$(".profile").html(replaceProfile)
}

// View all the events for this 
function viewEvent() {
	var message_request;
	message_request = '/getEvents?toggle=0';
	$.get(message_request, function(eventList) {
		events = JSON.parse(eventList)
		replaceText = '<div class="event-crate"><div class="upcoming-event">Upcoming events</div>'
		for (var item in events) {
			replaceText += 	'<ul class="event-header"><li style="width:100%">' + events[item]['event_name'] + '</li> \
							<li class="desc">Host: ' + events[item]['host'] + '</li> \
							<li class="desc">Location: ' + events[item]['location'] + '</li> \
							<li class="desc">Start Time: ' + events[item]['start_time'] + '</li> \
							<li class="desc">End Time: ' + events[item]['end_time'] + '</li> \
							<li class="desc">Description: ' + events[item]['description'] + '</li> \
							<li class="desc">Status:  \
							<select id="' + events[item]['id'] + '" onChange="setEvent(this.value, ' + events[item]['id'] + ')" >'
			if (events[item]['attendance'] == 1) {
				replaceText += '<option value="1" selected>Going</option><option value="2">Maybe</option><option value="0">Not Going</option></select></li></ul>'
			} else if (events[item]['attendance'] == 2) {
				replaceText += '<option value="1" >Going</option><option value="2" selected>Maybe</option><option value="0">Not Going</option></select></li></ul>'
			} else {
				replaceText += '<option value="1" >Going</option><option value="2" >Maybe</option><option value="0" selected>Not Going</option></select></li></ul>'
			}
		}
	});
	
	message_request = '/getEvents?toggle=1';
	$.get(message_request, function(eventList) {
		events = JSON.parse(eventList)
		replaceText += '<div class="upcoming-event">My Events</div>'
		for (var item in events) {
			replaceText += 	'<ul class="event-header"><li style="width:100%">' + events[item]['event_name'] + '</li> \
							<li class="desc">Host: ' + events[item]['guest'] + '</li> \
							<li class="desc">Location: ' + events[item]['location'] + '</li> \
							<li class="desc">Start Time: ' + events[item]['start_time'] + '</li> \
							<li class="desc">End Time: ' + events[item]['end_time'] + '</li> \
							<li class="desc">Description: ' + events[item]['description'] + '</li>'
			if (events[item]['attendance'] == 1) {
				replaceText += '<li class="desc">Status: Going </li></ul>'
			} else if (events[item]['attendance'] == 2) {
				replaceText += '<li class="desc">Status: Maybe </li></ul>'
			} else {
				replaceText += '<li class="desc">Status: Not Going </li></ul>'
			}
		}
	});
	
	replaceText += '</div>'
	
	$(".profile").html(replaceText)
}

// Set an acknowledgement for the event to the user
function setEvent(value, id) {
	var message_request;
	message_request = "/acknowledgeHost?attendance=" + value + "&row_id=" + id;
	$.get(message_request)
}

// At document ready do this:
$(document).ready(function() {
	// Starting
	updateWebpageProfile()
	getStatus()
});
