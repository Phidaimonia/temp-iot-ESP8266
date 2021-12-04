var ctx = document.getElementById('canvas')

const labels = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    ];         


    var allChart = new Chart(ctx, {
        type:'line',
        data: {
           labels: labels,
           datasets: [{
               label: 'Team Red',
               data: [1, 2, 9, 3],
               backgroundColor: 'transparent',
               borderColor: 'red',
               borderWidth: 4
           },
           {
               label: 'Team Black',
               data: [1, 2, 3, 6, 10, 18],
               backgroundColor: 'transparent',
               borderColor: 'black',
               borderWidth: 4
           },
           {
               label: 'Team Green',
               data: [1, 8, 9, 3, 2, 3],
               backgroundColor: 'transparent',
               borderColor: 'green',
               borderWidth: 4
           },
           {
               label: 'Team Blue',
               data: [4, 2, 9, 3, 2],
               backgroundColor: 'transparent',
               borderColor: 'blue',
               borderWidth: 4
           },
           {
               label: 'Team Pink',
               data: [6, 3, 9, 3, 2],
               backgroundColor: 'transparent',
               borderColor: 'pink',
               borderWidth: 4
           }]
       },
       options: {
           elements:{
               line:{
               tension: 0,
               }
           }
       
       
       },
       
       
       });
var redctx = document.getElementById('canvasRed')
var redChart = new Chart(redctx,{
    type: 'line',
    data: {labels: labels,
    datasets: [{label: 'Team Red',
    data: [1, 2, 9, 3],
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



   function requestData() {
    var params = {
      "dt_from": "2021-12-01T12:58:01.000000",  // in UTC
       "dt_to": "2022-02-01T12:58:01.000000", 
         "cookie": "4jgk6s9d3dj57j4kgs3"
      }
      ws.send(JSON.stringify(params))
   }
  //zatim nefunguje
   function onSocketMessage(message) {
    //console.log(message.data);
    //console.log(message);
    var data = JSON.parse((message.data));
    console.log(data);
    
    time = data.time;
    temp = data.temp;
    team = data.team;
   }