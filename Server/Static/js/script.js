
function onSocketOpen() {
    console.log("WS Open");
    //requestData();
}

function onSocketMessage(message) {
  
    try {
        var data = JSON.parse(message.data);
    } catch (error) {
        console.error(error + " " + message.data);
        return
    }

    console.log(data)
    d = new Date()
    
    t = new Date(data.created_on);
    temp = data.temperature;
    team = data.team_name; 

    var t_index = chartCapacity + t.getMinutes() - d.getMinutes() - 1
    t_index = Math.min(Math.max(t_index, 0), chartCapacity - 1)

    

    if(team=="red") { 
        redChart.data.datasets.forEach((dataset) => {
            dataset.data[t_index] = temp;
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
        "dt_from": startDate.toISOString(),  // in UTC
        "dt_to": endDate.toISOString(), 
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

var chartCapacity = 130  // v minutach

var endDate = new Date();
var startDate = new Date((Date.now() - chartCapacity * 60 * 1000 ))



//new Date().toISOString();



var x_data = new Array(chartCapacity).fill(null)
var y_data = new Array(chartCapacity).fill(null)

for(i = 0; i < chartCapacity; i++)
{
    new_min = (startDate.getMinutes() + i) % 60
    new_hr =  (startDate.getHours() + Math.floor((startDate.getMinutes() + i) / 60)) % 24
    x_data[i] = new_hr.toString().padStart(2, "0") + ":" + new_min.toString().padStart(2, "0")
}



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
        responsive: true,
        elements:{
            line:{
            tension: 0,
            }
        }

    }});

onLoad()


function updateChart() {
    var d = new Date();
    //console.log("Update chart")

    //redChart.data.labels.push(d.getHours() + ":" + d.getMinutes());
    let len = redChart.data.labels.length;

    for (i = 1; i < len; i++) {
        redChart.data.labels[i-1] = redChart.data.labels[i]
    }
    redChart.data.labels[len-1] = d.getHours() + ":" + d.getMinutes()

    redChart.data.datasets.forEach((dataset) => {
        let len = dataset.data.length;
        for (i = 1; i < len; i++) {
            dataset.data[i-1] = dataset.data[i]
        }
        dataset.data[len-1] = null
        //dataset.data.push(null);
    });
        redChart.update(null);
  }

d = new Date();
setTimeout(startUpdateTimer, (60 - d.getSeconds()) * 1000);  // time to until new minute begins

function startUpdateTimer(){
    setInterval(updateChart, 60000);        // kazdou minutu prida novy bod
    updateChart();
}

    


   // onmessage
   