function onSocketOpen() {
    console.log("WS Open")
}

function onSocketMessage(message) {
  
    console.log("JSON data received:", message)
    //msg = JSON.parse(message.data)

    //----------------added-------------
    var data = JSON.parse((message.data));
    console.log(data);
    
    time = data.time;
    temp = data.temp;
    team = data.team; 
    //
    console.log(time);
    console.log(temp);
    console.log(team);

    if(team=="red") {
        red_data.labels = time;
        red_data.datasets[0].data = temp;
        redChart.update();
    }
    if(team=="black") {
         black_data.labels = time;
         black_data.datasets[0].data = temp;
         blackChart.update();
    }
    if(team=="blue") {
        blue_data.labels = time;
        blue_data.datasets[0].data = temp;
        blueChart.update();
    }  
    if(team=="green") {
        green_data.labels = time;
        green_data.datasets[0].data = temp;
        greenChart.update();
    }
    if(team=="pink") {
        pink_data.labels = time;
        pink_data.datasets[0].data = temp;
        pinkChart.update();
    }
    console.log("data successfully parsed.")
    //------------------------------
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

window.addEventListener('load', onLoad, false);

//--------------------------------------------------------------------------
var ctx = document.getElementById('canvas')

const labels = ['1', '2', '3', '4', '5', '6'];         
    var red_data = {labels: labels,datasets: [{label: 'Temperature red', backgroundColor: 'white', borderColor: 'red', borderWidth: 4, data: [null],}]};

    var black_data = {labels: labels,datasets: [{label: 'Temperature black', backgroundColor: 'white',borderColor: 'black', borderWidth: 4, data: [null],}]};

    var blue_data = {labels: labels,datasets: [{label: 'Temperature blue', backgroundColor: 'white',borderColor: 'blue', borderWidth: 4, data: [null],}]};

    var green_data = {labels: [null],datasets: [{label: 'Temperature green', backgroundColor: 'white', borderColor: 'green', borderWidth: 4, data: [null],}]};
        
    var pink_data = {labels: labels,datasets: [{label: 'Temperature pink', backgroundColor: 'white',borderColor: 'pink', borderWidth: 4, data: [null],}]};

    var redctx = document.getElementById('canvasRed')
    var blackctx = document.getElementById('canvasBlack')
    var bluectx = document.getElementById('canvasBlue')
    var greenctx = document.getElementById('canvasGreen')
    var pinkctx = document.getElementById('canvasPink')

    var redChart = new Chart(redctx,{
    type: 'line',
    data: {red_data
},
    options: {
        elements:{
            line:{
            tension: 0,
            }
        }

    }});
    
    var blackChart = new Chart(blackctx,{
        type: 'line',
        data: {black_data       
    },
        options: {
            elements:{
                line:{
                tension: 0,
                }
            }
    
    }});
        
    var blueChart = new Chart(bluectx,{
            type: 'line',
            data: {blue_data
        },
            options: {
                elements:{
                    line:{
                    tension: 0,
                    }
                }
        
    }}); 
            
    var greenChart = new Chart(greenctx,{
                type: 'line',
                data: {green_data
            },
                options: {
                    elements:{
                        line:{
                        tension: 0,
                        }
                    }
            
    }});

    var pinkChart = new Chart(pinkctx,{
                    type: 'line',
                    data: {pink_data
                },
                    options: {
                        elements:{
                            line:{
                            tension: 0,
                            }
                        }
                
    }});

   function requestData() {
    var params = {
      "dt_from": "2021-12-01T12:58:01.000000",  // in UTC
       "dt_to": "2022-02-01T12:58:01.000000", 
         "cookie": "4jgk6s9d3dj57j4kgs3"
      }
      ws.send(JSON.stringify(params))
   }
  

   // onmessage
   