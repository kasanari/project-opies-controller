var ctx = document.getElementById('myChart');
var data = [{
    x: 10,
    y: 20
}, {
    x: 15,
    y: 10
}];

var myLineChart = new Chart(ctx, {
type: 'line',
  data: {
    labels: [0],
    datasets: [{
        data: [0],
        label: "Steering",
        borderColor: "#3e95cd",
        fill: false
      }
    ]
  },
  options: {
    title: {
      display: false,
      text: 'Steering'
    }
  }
});
