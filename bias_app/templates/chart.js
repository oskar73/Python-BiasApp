document.addEventListener('DOMContentLoaded', function () {
    // Sample data (replace with your own data)
    const rawData = [
        const rawData = [
    [1631464800000, 100, 110, 90, 105],
    [1631465100000, 105, 115, 100, 112],
    [1631465400000, 112, 118, 105, 108],
    [1631465700000, 108, 115, 105, 113],
    [1631466000000, 113, 120, 110, 118],
    [1631466300000, 118, 125, 115, 123],
    [1631466600000, 123, 130, 120, 128],
    // ... Add more data points here

    ];

    // Initialize the chart with a default aggregation interval (1 minute)
    let selectedInterval = 1;

    const chart = Highcharts.stockChart('container', {
        rangeSelector: {
            selected: 1
        },
        title: {
            text: 'Candlestick Chart with Aggregation'
        },
        series: [{
            type: 'candlestick',
            name: 'Candlesticks',
            data: aggregateData(rawData, selectedInterval)
        }]
    });

    // Function to aggregate data based on the selected interval
    function aggregateData(rawData, interval) {
        const aggregatedData = [];
        let startTime = rawData[0][0];
        let open = rawData[0][1];
        let high = open;
        let low = open;
        let close = open;

        for (const dataPoint of rawData) {
            const timestamp = dataPoint[0];

            if (timestamp - startTime >= interval * 60 * 1000) {
                aggregatedData.push([startTime, open, high, low, close]);
                startTime = timestamp;
                open = dataPoint[1];
                high = open;
                low = open;
            }

            high = Math.max(high, dataPoint[2]);
            low = Math.min(low, dataPoint[3]);
            close = dataPoint[4];
        }

        return aggregatedData;
    }

    // Event listener for aggregation dropdown change
    document.getElementById('aggregation-select').addEventListener('change', function () {
        selectedInterval = parseInt(this.value);
        chart.series[0].setData(aggregateData(rawData, selectedInterval));
    });
});
