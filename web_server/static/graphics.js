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
      }, {
            label: 'Path',
            data: [
                {
                    'x': 1.1,
                    'y': 1.1
                },
                {
                    'x': 2.5,
                    'y': 1.1
                },
                {
                    'x': 2.5,
                    'y': 5
                },
                {
                    'x': 1.1,
                    'y': 5
                },
                {
                    'x': 1.1,
                    'y': 1.1
                },
            ],

            // Changes this dataset to become a line
            type: 'line',
            fill: false,
            cubicInterpolationMode: 'monotone',
            borderColor: '#FFBF00'

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
                    suggestedMax:6
                }
            }],
            yAxes: [{
                    type: 'linear',
                    position: 'left',
                    ticks: {
                        beginAtZero: true,
                        suggestedMax:6
                    }
                }]
        }
  }
});
