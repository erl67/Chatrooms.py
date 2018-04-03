var timeoutID;
var timeout = 5000;
var room = 0;
var chats = [];
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
			}
		}
	}

	button = document.getElementsByTagName("button")[0];
	button.addEventListener("click", sendMsg, true);
	textarea = document.getElementsByTagName("textarea")[0];


	getChats();
	timeoutID = window.setTimeout(poller, timeout);

});

function getChats() {
	var httpRequest = new XMLHttpRequest();

	httpRequest.onreadystatechange = function() { 
		handleChat(httpRequest)
	};

	httpRequest.open("GET", "/chats");
	httpRequest.send();
}

function handleChat(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {
			chats[chats.length] = httpRequest.responseText;
			
			if (chats[chats.length-1] > chats[0]) {
				alert("New Chat");
			} else if (chats.length > 10) {
				chats = [chats[0]];
			}
		}
	}
}


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

function poller() {
	getChats();



	window.setTimeout(poller, timeout);
}



