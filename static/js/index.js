// static/index.js

console.log("JS from index.js.");

let roomSelect = document.querySelector("#roomSelect");

// adds a new list of options to 'roomSelect'
function roomList (roomList) {
    roomSelect.options.length = 0;
    for (let value of roomList) {
        let newOption = document.createElement("option");
        newOption.value = value;
        newOption.innerHTML = value;
        roomSelect.appendChild(newOption);
    }
}

// focus 'roomInput' when user opens the page
document.querySelector("#roomInput").focus();

// submit if the user presses the enter key
document.querySelector("#roomInput").onkeyup = function (e) {
  if (e.keyCode === 13) {
    // enter key
    document.querySelector("#roomConnect").click();
  }
};

// redirect to '/room/<roomInput>/'
document.querySelector("#roomConnect").onclick = function () {
  let roomName = document.querySelector("#roomInput").value;
  window.location.pathname = "chat/" + roomName + "/";
};

// redirect to '/room/<roomSelect>/'
document.querySelector("#roomSelect").onchange = function () {
  let roomName = document.querySelector("#roomSelect").value.split(" (")[0];
  window.location.pathname = "chat/" + roomName + "/";
};

// WebSocket: static/index.js

let chatSocket = null;

function connect() {
  chatSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/room-list/"
  );
  console.log("ws://" + window.location.host + "/ws/room-list/");

  chatSocket.onopen = function (e) {
    console.log("Successfully connected to the WebSocket.");
  };

  chatSocket.onclose = function (e) {
    console.log(
      "WebSocket connection closed unexpectedly. Trying to reconnect in 2s..."
    );
    setTimeout(function () {
      console.log("Reconnecting...");
      connect();
    }, 2000);
  };

  chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);

    switch (data.action) {
        case "first_connect":
            roomList (data.message);
            break;
        case "connected":
            console.log("<" + data.user + "> connected!");
            break;
        case "disconnected":
            console.log("<" + data.user + "> disconnected!");
            break;
        case 'refresh_rooms':
            console.log("Refreshing rooms...");
            roomList (data.message);
            break;
        default:
            console.error("Unknown message type!");
            break;
    }
  };

  chatSocket.onerror = function (err) {
    console.log("WebSocket encountered an error: " + err.message);
    console.log("Closing the socket.");
    chatSocket.close();
  };
}
connect();
