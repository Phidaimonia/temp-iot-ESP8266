
function onSocketOpen() {
    console.log("WS Open")
}

function onSocketMessage(message) {
  
    console.log("JSON data received:", message)    
}

function onSocketClose() {
    console.log("WS Close")
}

function sendToServer() {
    var params = {
        topic: "tempServer/broker1",
        temperatures: ["123.4"]
    }
    ws.send(JSON.stringify(params))
}

function onLoad() {
	console.log("Ahoj world")
    document.getElementById('dict').innerText = loadJsonHandler()

    ws = new WebSocket('/data')     
    ws.onopen = onSocketOpen
    ws.onmessage = onSocketMessage
    ws.onclose = onSocketClose
}


function loadJsonHandler() {
    if (window.XMLHttpRequest) {
        xmlhttp = new XMLHttpRequest();
    }
    xmlhttp.open('GET', '/json/', false);
    xmlhttp.send(null);

    return  xmlhttp.responseText;
}