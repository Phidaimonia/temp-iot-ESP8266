
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

    if (data.response_type == "temperature_data")
    {
        if(!("team_name" in data))
        {
            console.log("Wrong data format: ")
            console.log(data)
            return
        }
        

        if(!team_names.find(item => { return item === data.team_name } ))
        {
            console.log("Team: " + data.team_name + " is not on the team list")
            console.log(team_names)
            return
        }
   
        nowDate = new Date()
        if(lastChartUpdateMin != nowDate.getMinutes())
            updateChart()

        nowDate = nowDate.getTime() - nowDate.getSeconds() * 1000


        measureDate = new Date(data.created_on)
        measureDate = measureDate.getTime() - measureDate.getSeconds() * 1000  

        diff = Math.floor((nowDate - measureDate) / timeframe)  // in mins
        var t_index = chartCapacity - diff - 1
        t_index = Math.min(Math.max(t_index, 0), chartCapacity - 1)

        charts[data.team_name].data.datasets.forEach((dataset) => {
            dataset.data[t_index] = data.temperature;
        });
        charts[data.team_name].update(null);
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

var chartCapacity = 80  // v minutach
var timeframe = 60000   // interval mezi body v ms
var lastChartUpdateMin = 0



const team_names = ["red", "black", "green", "blue", "pink"]
charts = {}

var endDate = new Date();
var startDate = new Date(Date.now() - chartCapacity * timeframe )

var x_data = new Array(chartCapacity).fill(endDate)       // vytvori casovou skalu pro vsechny grafy
for(i = 0; i < chartCapacity; i++)
{
    //new_min = (startDate.getMinutes() + i) % 60
    //new_hr =  (startDate.getHours() + Math.floor((startDate.getMinutes() + i) / 60)) % 24
    //x_data[i] = new_hr.toString().padStart(2, "0") + ":" + new_min.toString().padStart(2, "0")

    x_data[i] = new Date(endDate.getTime() + (i-chartCapacity) * timeframe )
}

team_names.forEach((tm_name) => {                               // vytvori chart objekty
    var canv = document.getElementById("canvas_" + tm_name)

    charts[tm_name] = new Chart(canv,{
    type: 'line',
    data: {labels: x_data,
            datasets: [{label: "Team " + tm_name,
            data: new Array(chartCapacity).fill(null),
            backgroundColor: 'transparent',
            borderColor: tm_name,
            borderWidth: 4}] },
    options: { 
        responsive: true,
        elements:
        {
            line:{ ension: 0.5, }, 
        }, 
        scales: 
        {
            x: { type: 'timeseries', }, 
            time: { minUnit: 'minute', }
        }

    }});
});

time.minUnit

ws = new WebSocket("wss://" + window.location.host + '/data')   
ws.onopen = onSocketOpen
ws.onmessage = onSocketMessage
ws.onclose = onSocketClose


function updateChart() {
    var d = new Date();

    if(lastChartUpdateMin == d.getMinutes())
        return

    lastChartUpdateMin = d.getMinutes()

    for (i = 1; i < chartCapacity; i++) 
        charts[team_names[0]].data.labels[i-1] = charts[team_names[0]].data.labels[i]
        
    //charts[team_names[0]].data.labels[chartCapacity-1] = d.getHours().toString().padStart(2, "0") + ":" + d.getMinutes().toString().padStart(2, "0")
    charts[team_names[0]].data.labels[chartCapacity-1] = new Date(charts[team_names[0]].data.labels[chartCapacity-2].getTime() + timeframe)
    


    team_names.forEach((tm_name) => 
    {
        charts[tm_name].data.datasets.forEach((dataset) => {
            for (i = 1; i < chartCapacity; i++) {
                dataset.data[i-1] = dataset.data[i]
            }
            dataset.data[chartCapacity-1] = null
    });
    charts[tm_name].update(null);});
  }

d = new Date();
setTimeout(startUpdateTimer, (60 - d.getSeconds()) * 1000);  // time to until new minute begins

function startUpdateTimer(){
    d = new Date();
    lastChartUpdateMin = d.getMinutes()
    setInterval(updateChart, Math.max(1, 60 - d.getSeconds() - 1) * 1000);        // kazdou minutu prida novy bod
    updateChart();
}
