(function() {
function onSocketOpen() {
    console.log("WS Open")
}

function onSocketMessage(message) {
  
    console.log("JSON data received:", message)
    //msg = JSON.parse(message.data)
}

function onSocketClose() {
    console.log("WS Close")
}

function requestData() {
    var params = {
        "request_type": "temperature_data",
        "dt_from": "2021-12-01T12:58:01.000000",  // in UTC
        "dt_to": "2022-02-01T12:58:01.000000", 
        "cookie": "4jgk6s9d3dj57j4kgs3"
    }
    ws.send(JSON.stringify(params))
}

function requestSensorStatus() {
    var params = {
        "request_type": "sensor_status"
    }
    ws.send(JSON.stringify(params))
}

function onLoad() {
	console.log("Ahoj world")
    //document.getElementById('dict').innerText = loadJsonHandler()

    ws = new WebSocket("wss://" + window.location.host + '/data')     
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

window.addEventListener('load', onLoad, false);
})();