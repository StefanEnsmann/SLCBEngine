var image = null;
var container = null;

document.addEventListener("DOMContentLoaded", function() {
    // Connect if API_Key is inserted
    // Else show an error on the overlay
    if (typeof API_Key === "undefined") {
        document.body.innerHTML = "No API Key found or load!<br>Rightclick on the script in ChatBot and select \"Insert API Key\"";
    }
    else {
        connectWebsocket();
    }
})
  
// Connect to ChatBot websocket
// Automatically tries to reconnect on
// disconnection by recalling this method
function connectWebsocket() {
    image = document.getElementById("image");
    container = document.getElementById("container");

    //-------------------------------------------
    //  Create WebSocket
    //-------------------------------------------
    var socket = new WebSocket(API_Socket);

    //-------------------------------------------
    //  Websocket Event: OnOpen
    //-------------------------------------------
    socket.onopen = function() {

        // AnkhBot Authentication Information
        var auth = {
        author: "Zensmann",
        website: "https://twitch.tv/zensmann",
        api_key: API_Key,
        events: [
            "SHOWIMAGE_IMAGE_IN",
            "SHOWIMAGE_CONFIG"
        ]
        };

        // Send authentication data to ChatBot ws server
        socket.send(JSON.stringify(auth));
    };

    //-------------------------------------------
    //  Websocket Event: OnMessage
    //-------------------------------------------
    socket.onmessage = function (message) {

        // Parse message
        var socketMessage = JSON.parse(message.data);
        console.log(socketMessage);

        if (socketMessage.event === "SHOWIMAGE_IMAGE_IN") {
            var eventData = JSON.parse(socketMessage.data);
            console.log(eventData);
            image.src = eventData.url;
            image.style.visibility = "visible";
            container.style.backgroundColor = "#00000055";
        }
    };

    //-------------------------------------------
    //  Websocket Event: OnError
    //-------------------------------------------
    socket.onerror = function(error) {
        console.log("Error: " + error);
    };

    //-------------------------------------------
    //  Websocket Event: OnClose
    //-------------------------------------------
    socket.onclose = function() {
        // Clear socket to avoid multiple ws objects and EventHandlings
        socket = null;
        // Try to reconnect every 5s
        setTimeout(function(){connectWebsocket()}, 5000);
    }
};