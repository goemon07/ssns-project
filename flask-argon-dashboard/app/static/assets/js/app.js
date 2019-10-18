'use strict';

$(function () {
    var envChart = Chart.Line($('#chart-environment'), {
        options: {
            hoverMode: 'index',
            stacked: false,
            scales: {
                xAxes: [{
                    type: 'time',
                }],
                yAxes: [{
                    type: 'linear',
                    display: true,
                    labelString: '°C',
                    position: 'left',
                    id: 'y-axis-1',
                    ticks: {
                        beginAtZero: false,
                        callback: function(value, index, values) { return Math.round(value * 10) / 10 + ' °C'; },
                        precision: 1,
                    },
                }, {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    id: 'y-axis-2',
                    ticks: {
                        callback: function(value, index, values) { return Math.round(value * 10) / 10 + ' %'; },
                    },
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    }
                }],
            }
        }
    });

    var motionChart = Chart.Line($('#chart-motion'), {
        options: {
            hoverMode: 'index',
            stacked: false,
            scales: {
                xAxes: [{
                    type: 'time',
                    time: {
                        tooltipFormat: 'HH:mm:ss.SSS (Z)'
                    },
                }],
                yAxes: [{
                    id: 'y-axis-1',
                    type: 'linear',
                    display: true,
                    labelString: 'g',
                    position: 'left',
                    ticks: {
                        min: 0, max: 1,
                        callback: function(value, index, values) { return Math.round(value * 10) / 10 + ' g'; },
                        precision: 1,
                    }
                }],
            }
        }
    });

    var nodes = new Map();
    var token = 0;

    var colors = [
        ['#C25F9A', '#bc5090', '#ab4983'],
        ['#ffae17', '#ffa600', '#e89700'],
        ['#FF716F', '#ff6361', '#e85a59'],
        ['#17506A', '#003f5c', '#003a54'],
        ['#675F97', '#58508d', '#504981'],
    ];

    function updateData(data) {
        let t = null, v = [];
        for (let item of data.data) {
            var node = nodes.get(item.node_serial);
            if (node === undefined) {
                node = nodes.size;
                nodes.set(item.node_serial, node);

                envChart.data.datasets.push({
                    label: 'Node ' + (node + 1) + ' (°C)',
                    borderColor: colors[node][0],
                    yAxisID: 'y-axis-1',
                    data: []
                });
                envChart.data.datasets.push({
                    label: 'Node ' + (node + 1) + ' (rel %)',
                    borderColor: colors[node][1],
                    yAxisID: 'y-axis-2',
                    data: []
                });

                motionChart.data.datasets.push({
                    label: 'Node ' + (node + 1),
                    yAxisID: 'y-axis-1',
                    borderColor: colors[node][0],
                    data: []
                });
            }

            let timestamp = item.timestamp;
            if (timestamp !== t) {
                if (t && v.length === 3) {
                    let val = Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) - 1;
                    motionChart.data.datasets[node].data.push({
                        t: t,
                        y: val
                    });
                }

                t = timestamp;
                v = [];
            }

            switch (item.sensor) {
                case 0:
                case 1:
                    envChart.data.datasets[node * 2 + item.sensor].data.push({
                        t: timestamp,
                        y: item.value
                    });
                    break;
                case 2:
                case 3:
                case 4:
                    v.push(item.value);
                    break;
            }
        }
        token = data.token;
        envChart.update();
        motionChart.update();

        setTimeout(function () {
            $.getJSON('/api/v1/measurements?token=' + token, updateData);
        }, 1000);
    }

    $.getJSON('/api/v1/measurements', updateData);
});
