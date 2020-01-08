var ctx = document.getElementById('myChart');
var data = [{
    x: 10,
    y: 20
}, {
    x: 15,
    y: 10
}];

var myLineChart = new Chart(ctx, {
type: 'scatter',
  data: {
    datasets: [{
        data: [],
        label: "Position Data"
      }
    ]
  },
  options: {
    animation: {
        duration:1,
        easing:'linear'
    },
    title: {
      display: false,
      text: 'Steering'
    },
    scales: {
            xAxes: [{
                type: 'linear',
                position: 'bottom',
                ticks: {
                    beginAtZero: true,
                    suggestedMax:5
                }
            }],
            yAxes: [{
                    type: 'linear',
                    position: 'left',
                    ticks: {
                        beginAtZero: true,
                        suggestedMax:5
                    }
                }]
        }
  }
});
