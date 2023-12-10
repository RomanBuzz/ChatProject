// static/room.js

console.log("JS from room.js.");

const roomName = JSON.parse(document.getElementById("roomName").textContent);
const currentUser = JSON.parse(document.getElementById('user_pk').textContent);

let chatLog = document.querySelector("#chatLog");
let chatMessageInput = document.querySelector("#chatMessageInput");
let chatMessageSend = document.querySelector("#chatMessageSend");
let onlineUsersSelector = document.querySelector("#onlineUsersSelector");
let privateMessageInput = document.querySelector("#privateMessageInput");
let buttonArea = document.querySelector("#buttonArea");

document.querySelector("#onlineUsersSelector").onchange = function () {
    let userName = this.options[this.selectedIndex].text
    let value = document.querySelector("#onlineUsersSelector").value;
    privateMessageInput.placeholder = "Личное сообщение пользователю <" + userName + ">";
    buttonArea.innerHTML = "";
    let newOption = document.createElement("button");
    newOption.className = "btn btn-success";
    newOption.id = "privateMessageSend";
    newOption.type = "button";
    newOption.onclick = function () {
        if (privateMessageInput.value.length === 0) return;
        chatSocket.send(
        JSON.stringify({
            message: privateMessageInput.value,
            direction: value,
        })
        );
        privateMessageInput.value = "";
        };
    newOption.innerHTML = "Отправить";
    buttonArea.appendChild(newOption);
};

// adds a new list of options to 'onlineUsersSelector'
function usersOfRoom (userList) {
    onlineUsersSelector.options.length = 0;
    for (let value of userList) {
        let newOption = document.createElement("option");
        newOption.value = value[0];
        newOption.innerHTML = value[1];
        onlineUsersSelector.appendChild(newOption);
    }
}

// adds a new option to 'onlineUsersSelector'
function onlineUsersSelectorAdd(value) {
  if (document.querySelector("option[value='" + value + "']")) return;
  let newOption = document.createElement("option");
  newOption.value = value;
  newOption.innerHTML = value;
  onlineUsersSelector.appendChild(newOption);
}

// removes an option from 'onlineUsersSelector'
function onlineUsersSelectorRemove(value) {
  let oldOption = document.querySelector("option[value='" + value + "']");
  if (oldOption !== null) oldOption.remove();
}

// focus 'chatMessageInput' when user opens the page
chatMessageInput.focus();

// submit if the user presses the enter key
chatMessageInput.onkeyup = function (e) {
  if (e.keyCode === 13) {
    // enter key
    chatMessageSend.click();
  }
};

// clear the 'chatMessageInput' and forward the message
chatMessageSend.onclick = function () {
  if (chatMessageInput.value.length === 0) return;
  chatSocket.send(
    JSON.stringify({
        message: chatMessageInput.value,
        direction: 'room',
    })
  );
  chatMessageInput.value = "";
};


// WebSocket: static/room.js

let chatSocket = null;

function connect() {
  chatSocket = new WebSocket(
    "ws://" + window.location.host + "/ws/chat/" + roomName + "/"
  );
  console.log("ws://" + window.location.host + "/ws/chat/" + roomName + "/");

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

    switch (data.type) {
      case "chat_message":
          if (data.direction === 'room') {
                chatLog.value += data.date + " " + data.user + ": " + data.message + "\n";
            }
            else if (data.direction == currentUser) {
                chatLog.value += data.date + " <" + data.user + "> отправил вам личное сообщение: " + data.message + "\n";
            }
        break;
      case "connection_established":
        chatLog.value += data.message;
        break;
      case "connection_status":
        if (data.action === 'connected') {
            chatLog.value += data.date + " <" + data.user + "> connected!\n";
        }
        else {
            chatLog.value += data.date + " <" + data.user + "> disconnected!\n";
        }
        usersOfRoom (data.user_list);
        break;
      default:
        console.error("Unknown message type!");
        break;
    }

    // scroll 'chatLog' to the bottom
    chatLog.scrollTop = chatLog.scrollHeight;
  };

  chatSocket.onerror = function (err) {
    console.log("WebSocket encountered an error: " + err.message);
    console.log("Closing the socket.");
    chatSocket.close();
  };
}
connect();
