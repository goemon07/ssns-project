'use strict';

$(function () {
    var envChart = Chart.Line($('#chart-environment'), {
        options: {
            responsive: true,
            hoverMode: 'index',
            stacked: false,
            scales: {
                xAxes: [{
                    type: 'time',
                }],
                yAxes: [{
                    type: 'linear',
                    display: true,
                    position: 'left',
                    id: 'y-axis-1',
                    ticks: {
                        beginAtZero: false
                    }
                }, {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    id: 'y-axis-2',
                    gridLines: {
                        drawOnChartArea: false, // only want the grid lines for one axis to show up
                    },
                }],
            }
        }
    });

    var nodes = new Map();
    var token = 0;

    function updateData(data) {
        for (let item of data.data) {
            var node = nodes.get(item.node_serial);
            if (node === undefined) {
                node = nodes.size;
                nodes.set(item.node_serial, node);

                envChart.data.datasets.push({label: item.node_serial + ' (°C)', yAxisID: 'y-axis-1', data: []});
                envChart.data.datasets.push({label: item.node_serial + ' (rel%)', yAxisID: 'y-axis-2', data: []});
            }

            switch (item.sensor) {
                case 0:
                case 1:
                    envChart.data.datasets[node * 2 + item.sensor].data.push({
                        t: Date.parse(item.timestamp),
                        y: item.value
                    });
                    break;
            }
        }
        token = data.token;
        envChart.update();

        setTimeout(function () {
            $.getJSON('/api/v1/measurement?token=' + token, updateData);
        }, 1000);
    }

    $.getJSON('/api/v1/measurement', updateData);
});
