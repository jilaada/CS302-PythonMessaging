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
	alert(user)
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

$(document).ready(function() {
	// Starting
	updateWebpageProfile()
	getStatus()
});
