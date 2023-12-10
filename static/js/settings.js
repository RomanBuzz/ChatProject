// static/settings.js

console.log("JS from settings.js.");

let roomSelect = document.querySelector("#roomSelect");
let roomInput = document.querySelector("#roomInput")
let roomRename = document.querySelector("#roomRename")

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

document.querySelector("#sendNewName").onclick = function () {
  if (roomInput.value.length === 0) return;
  if (roomRename.value.length === 0) return;
  chatSocket.send(
    JSON.stringify({
        room: roomInput.value,
        rename: roomRename.value,
        description: 'room-rename',
    })
  );
  roomInput.value = "";
  roomRename.value = "";
};

document.querySelector("#roomDelete").onclick = function () {
  if (roomInput.value.length === 0) return;
  chatSocket.send(
    JSON.stringify({
        room: roomInput.value,
        description: 'room-delete',
    })
  );
  roomInput.value = "";
};

document.querySelector("#roomSelect").onchange = function () {
  let roomName = document.querySelector("#roomSelect").value.split(" (")[0];
  let userCount = document.querySelector("#roomSelect").value.split(/ \(|\)/, 2)[1];
  if (userCount > 0) {
    alert("Нельзя редактировать чат с активными пользователями!");
    roomInput.value = '';
    return;
  }
  roomInput.value = roomName;
};

// WebSocket: static/settings.js

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
