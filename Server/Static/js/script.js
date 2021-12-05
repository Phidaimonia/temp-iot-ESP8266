
function onSocketOpen() {
    console.log("WS Open");
    connected_to_server = true;
    requestData();  // hned po pripojeni pozada o data
    requestAimtecStatus();
    requestSensorStatus();
    getUsername();
}

function onSocketClose() {
    console.log("WS Close");
    connected_to_server = false;
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

    //console.log(data)

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
        
        if("temperature_min" in data)  // data contains max and min temperatures -> from DB
        {
            nowDate = new Date()
            
            updateChart()
            

            nowDate = nowDate.getTime() - nowDate.getTime() % timeframe


            measureDate = new Date(data.created_on)
            measureDate = measureDate.getTime() - measureDate.getTime() % timeframe  

            diff = Math.floor((nowDate - measureDate) / timeframe)  // in mins
            var t_index = chartCapacity - diff - 1
            t_index = Math.min(Math.max(t_index, 0), chartCapacity - 1)

            //charts[data.team_name].data.datasets.forEach((dataset) => {
                //dataset.data[t_index] = data.temperature;
            //});

            charts[data.team_name].data.datasets[0].data[t_index] = data.temperature_min
            charts[data.team_name].data.datasets[1].data[t_index] = data.temperature_max
            charts[data.team_name].update(null);
        } else
        {
            updateChart()
            for(i = 0; i < 2; i++)
                if(charts[data.team_name].data.datasets[i].data[chartCapacity-1] == null)
                    charts[data.team_name].data.datasets[i].data[chartCapacity-1] = data.temperature

            charts[data.team_name].data.datasets[0].data[chartCapacity-1] = Math.min(charts[data.team_name].data.datasets[0].data[chartCapacity-1], data.temperature)
            charts[data.team_name].data.datasets[1].data[chartCapacity-1] = Math.max(charts[data.team_name].data.datasets[1].data[chartCapacity-1], data.temperature)
         }
    }

    if (data["response_type"] == "sensor_status")
    {
        if("last_seen" in data)
        {
            lastSeenDate = new Date(data.last_seen);
            minutes_offline = Math.floor(Math.abs(lastSeenDate.getTime() - Date.now()) / 60000)
            
            document.getElementById(data.team_name + 'Status').innerText = minutes_offline <= 5 ? "Online" : "Last seen " + minutes_offline + " minutes ago"
            document.getElementById(data.team_name + 'Status').style.color = minutes_offline <= 5 ? "green" : "red"
            if (data.last_seen == null)
                document.getElementById(data.team_name + 'Status').innerText = "Offline"
            
        }
    }

    if (data["response_type"] == "aimtec_status")
    {
        if("status" in data)
        {
            document.getElementById('aimtecOnlineElement').innerText = data["status"] ? "Online" : "Offline"   // nastavi text, mozna predelej na barvu
            document.getElementById('aimtecOnlineElement').style.color = data["status"] ? "green" : "red"
        }
    }

    if (data["response_type"] == "get_username")
        if("username" in data)
            document.getElementById('usernameElement').innerText = data["username"]     // Neprihlaseenej -> Guest

 
}


function requestData() {
    var params = {
        "request_type": "temperature_data",
        "dt_from": startDate.toISOString().slice(0, 19) + ".000000",  // in UTC
        "dt_to": endDate.toISOString().slice(0, 19) + ".000000", 
        "interval": Math.max(1, Math.floor(timeframe / 60000))
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
const team_names = ["red", "black", "green", "blue", "pink"]
connected_to_server = false
charts = {}


function createCharts(chartWidth, tf)
{
    chartCapacity = chartWidth  // v bodech
    timeframe = tf   // interval mezi body v ms
    
    visible_chunk = chartCapacity * timeframe

    team_names.forEach((tm_name) => {                            
        charts[tm_name].destroy()
    });

    charts = {}

    lastIntervalEdge = null;

    startDate = new Date(Date.now() - visible_chunk )
    endDate = new Date();

    var x_data = new Array(chartCapacity).fill(null)       // vytvori casovou skalu pro vsechny grafy
    for(i = 0; i < chartCapacity; i++)
    {
        //new_min = (startDate.getMinutes() + i) % 60
        //new_hr =  (startDate.getHours() + Math.floor((startDate.getMinutes() + i) / 60)) % 24

        intervalStartDate = startDate.getTime() + i * timeframe
        tmpIntervalEdge = intervalStartDate - intervalStartDate % timeframe
        var intervalCenter = new Date(tmpIntervalEdge + timeframe / 2)

        x_data[i] = intervalCenter.getHours().toString().padStart(2, "0") + ":" + intervalCenter.getMinutes().toString().padStart(2, "0")
                                        
    }

    team_names.forEach((tm_name) => {                               // vytvori chart objekty
        var canv = document.getElementById("canvas_" + tm_name)

        charts[tm_name] = new Chart(canv,{
        type: 'line',
        data: {labels: x_data,
                datasets: [
                    {label: "Min temp",
                data: new Array(chartCapacity).fill(null),
                backgroundColor: 'transparent',
                borderColor: 'white',
                borderWidth: 4}, 
                    {label: "Max temp",
                data: new Array(chartCapacity).fill(null),
                backgroundColor: 'transparent',
                borderColor: 'pink',
                borderWidth: 4}] },
        options: { 
            responsive: true,
            elements:
            {
                line:{ tension: 0.5, }, 
            }, 
            scales: 
            {
                x: { type: 'timeseries', }
            }

        }});
    });
    if(connected_to_server)
        requestData()
}


createCharts(80, 120000)


ws = new WebSocket("wss://" + window.location.host + '/data')   
ws.onopen = onSocketOpen
ws.onmessage = onSocketMessage
ws.onclose = onSocketClose


function updateChart() {
    var d = new Date();

    if(connected_to_server)
    {
        //requestAimtecStatus();
        //requestSensorStatus();
    }

    ///////////////////////////////










    if(d.getTime() < lastIntervalEdge + timeframe)
        return

    lastIntervalEdge = d.getTime() - d.getTime() % timeframe

    var intervalCenter = new Date(lastIntervalEdge + timeframe / 2)

    ///////////////////////////////
    for (i = 1; i < chartCapacity; i++) 
        charts[team_names[0]].data.labels[i-1] = charts[team_names[0]].data.labels[i]
        
    charts[team_names[0]].data.labels[chartCapacity-1] = intervalCenter.getHours().toString().padStart(2, "0") + ":" + intervalCenter.getMinutes().toString().padStart(2, "0")

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
