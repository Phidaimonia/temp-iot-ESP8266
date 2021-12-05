
function onSocketOpen() {
    console.log("WS Open");
    requestData();  // hned po pripojeni pozada o data
}

function onSocketMessage(message) {
  
    try {
        var data = JSON.parse(message.data);
    } catch (error) {
        console.error(error + " " + message.data);
        return
    }

    if (!("response_type" in data))
    {
        console.log(data)
        console.log("Bad response from the server")
        return
    }

    if ("error" in data)
    {
        console.log("Error: " + data.error)
        return
    }

    if (data["response_type"] == "temperature_data" && data["team_name"] in team_names)
    {
        nowDate = new Date()
        nowDate = nowDate.getTime() - nowDate.getSeconds() * 1000
        measureDate = new Date(data.created_on);
    
        measureDate = measureDate.getTime() - measureDate.getSeconds() * 1000


        diff = Math.floor((nowDate - measureDate) / 60000)  // in mins
        //console.log("Diff " + diff)

        var t_index = chartCapacity - diff - 1
        t_index = Math.min(Math.max(t_index, 0), chartCapacity - 1)

        //console.log("Saving index " + t_index)    

            charts[data["team_name"]].data.datasets.forEach((dataset) => {
                dataset.data[t_index] = data.temperature;
            });
            charts[data["team_name"]].update();
    }

    if (data["response_type"] == "sensor_status")
    {
        if("team_name" in data && "last_seen" in data)
        {
            //
        }
    }

    if (data["response_type"] == "aimtec_status")
    {
        if("status" in data)
            document.getElementById('aimtecOnlineElement').innerText = data["status"]   // nastavi text, mozna predelej na barvu
    }

    if (data["response_type"] == "get_username")
        if("username" in data)
            document.getElementById('usernameElement').innerText = data["username"]     // Neprihlaseenej -> Guest

 
}

function onSocketClose() {
    console.log("WS Close")
}

function requestData() {
    var params = {
        "request_type": "temperature_data",
        "dt_from": startDate.toISOString().slice(0, 19) + ".000000",  // in UTC
        "dt_to": endDate.toISOString().slice(0, 19) + ".000000"
    }
    ws.send(JSON.stringify(params))
}

function requestSensorStatus() {
    var params = {
        "request_type": "sensor_status"
    }
    ws.send(JSON.stringify(params))
}

function requestAimtecStatus() {
    var params = {
        "request_type": "aimtec_status"
    }
    ws.send(JSON.stringify(params))
}

function getUsername() {
    var params = {
        "request_type": "get_username"
    }
    ws.send(JSON.stringify(params))
}



//window.addEventListener('load', onLoad, false);

var chartCapacity = 320  // v minutach

var endDate = new Date();
var startDate = new Date((Date.now() - chartCapacity * 60 * 1000 ))


var x_data = new Array(chartCapacity).fill(null)
var y_data = new Array(chartCapacity).fill(null)

for(i = 0; i < chartCapacity; i++)
{
    new_min = (startDate.getMinutes() + i) % 60
    new_hr =  (startDate.getHours() + Math.floor((startDate.getMinutes() + i) / 60)) % 24
    x_data[i] = new_hr.toString().padStart(2, "0") + ":" + new_min.toString().padStart(2, "0")
}

team_names = ["red", "black", "green", "blue", "pink"]
charts = {}

team_names.forEach((tm_name) => {
    var canv = document.getElementById("canvas_" + tm_name)
    console.log(tm_name + " canv: " + canv)
    var chart = new Chart(canv,{
    type: 'line',
    data: {labels: x_data,
    datasets: [{label: "Team " + tm_name,
    data: y_data,
    backgroundColor: 'transparent',
    borderColor: tm_name,
    borderWidth: 4}]
},
    options: {
        responsive: true,
        elements:{
            line:{
            tension: 0.5,
            }
        }

    }});

    charts[tm_name] = chart
    console.log(chart)
});


ws = new WebSocket("wss://" + window.location.host + '/data')   
ws.onopen = onSocketOpen
ws.onmessage = onSocketMessage
ws.onclose = onSocketClose


function updateChart() {
    var d = new Date();

    for (i = 1; i < chartCapacity; i++) {
        redChart.data.labels[i-1] = redChart.data.labels[i]
    }
    redChart.data.labels[chartCapacity-1] = d.getHours().toString().padStart(2, "0") + ":" + d.getMinutes().toString().padStart(2, "0")

    redChart.data.datasets.forEach((dataset) => {
        for (i = 1; i < chartCapacity; i++) {
            dataset.data[i-1] = dataset.data[i]
        }
        dataset.data[chartCapacity-1] = null
    });
        redChart.update(null);
  }

d = new Date();
setTimeout(startUpdateTimer, (60 - d.getSeconds()) * 1000);  // time to until new minute begins

function startUpdateTimer(){
    setInterval(updateChart, 60000);        // kazdou minutu prida novy bod
    updateChart();
}
