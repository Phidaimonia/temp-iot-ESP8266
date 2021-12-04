function onSocketOpen() {
    console.log("WS Open")
}

function onSocketMessage(message) {
  
    var data = JSON.parse(message.data);
    //console.log(data);
    
    t = new Date(data.created_on);
    temp = data.temperature;
    team = data.team_name; 
    //
    //console.log(time);

    //if(team=="red") {
    if(true) {
 
        redChart.data.labels.push(t.getHours() + ":" + t.getMinutes());
        redChart.data.datasets.forEach((dataset) => {
            dataset.data.push(temp);
        });
        redChart.update();
    }
 
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
    //ws = new WebSocket('wss://sulis48.zcu.cz/data')     
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

//window.addEventListener('load', onLoad, false);


const x_data = [];  
const y_data = [];

var redctx = document.getElementById('canvasRed')
var redChart = new Chart(redctx,{
    type: 'line',
    data: {labels: x_data,
    datasets: [{label: 'Team Red',
    data: y_data,
    backgroundColor: 'transparent',
    borderColor: 'red',
    borderWidth: 4}]
},
    options: {
        elements:{
            line:{
            tension: 0,
            }
        }

    }});
    onLoad()

function requestData() {
    var params = {
      "dt_from": "2021-12-01T12:58:01.000000",  // in UTC
       "dt_to": "2022-02-01T12:58:01.000000", 
         "cookie": "4jgk6s9d3dj57j4kgs3"
      }
      ws.send(JSON.stringify(params))
   }
  

   // onmessage
   