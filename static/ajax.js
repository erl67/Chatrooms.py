var timeoutID;
var timeout = 15000;
var room = 0;
var chats = 0;
var button;
var textarea;

document.addEventListener("DOMContentLoaded", function() {
	var httpRequest = new XMLHttpRequest();
	httpRequest.onreadystatechange = function() { 
		handleRoom(httpRequest)
	};

	httpRequest.open("GET", "/r");
	httpRequest.send();
	function handleRoom(httpRequest) {
		if (httpRequest.readyState === XMLHttpRequest.DONE) {
			if (httpRequest.status === 200) {
				room = httpRequest.responseText;
				//alert("Room located" + room);
			}
		}
	}


	button = document.getElementsByTagName("button")[0];
	button.addEventListener("click", sendMsg, true);
	textarea = document.getElementsByTagName("textarea")[0];

	timeoutID = window.setTimeout(poller, timeout);
});

function sendMsg() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}
	
	var msg = document.getElementsByTagName("textarea")[0].value;

	httpRequest.onreadystatechange = function() { handleSendMsg(httpRequest, msg) };

	httpRequest.open("POST", "/new_msg");
	httpRequest.setRequestHeader('Content-Type', 'application/json');

   var data = new Object();
   data.msg = textarea.value;
   data = JSON.stringify(data);

   httpRequest.send(data);
}

function handleSendMsg(httpRequest, msg) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 204) {
			alert(msg);
			 textarea.value = "";
			 //add something here to call function that gets new messages
		} else {
			alert("There was a problem with the post request.");
		}
	}
}

function makePost() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { handlePost(httpRequest) };

	httpRequest.open("POST", "/chat");
	httpRequest.setRequestHeader('Content-Type', 'application/json');

	httpRequest.send();
}

function handlePost(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			room = httpRequest.responseText;
			alert("Room located" + room);
		} else {
			alert("There was a problem with the room request.");
		}
	}
}

function poller() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { 
		handlePoll(httpRequest)
	};

	httpRequest.open("GET", "/r");
	httpRequest.send();
}

function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			room = httpRequest.responseText;
//			alert("Room located" + room);
		}
//		} else {
//		alert("There was a problem with the room request.");
//		}
//		} else {
//		alert("There was a problem with the poll request.");
	}
}


