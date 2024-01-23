    function displaySelectedMetric() {
      // Get the selected metric value from the dropdown
      var selectedMetric = metricSelector.value;

      // Compute the selected metric (replace this with your actual computation logic)
      var computedMetric = computeMetric(selectedMetric);

      // Display the computed metric value
      selectedMetricValue.textContent = computedMetric;
    }

    // Attach an event listener to the metric selector to trigger the computation when the selection changes
    metricSelector.addEventListener('change', displaySelectedMetric);

    // Example computation function (replace with your actual computation logic)
    function computeMetric(selectedMetric) {
    // Replace this with your actual computation logic based on the selected metric
      switch (selectedMetric) {
        case 'close_close_minus_1':
          return 'Computed Value for Close - Close (-1)';
        case 'close_open_diff':
          return 'Computed Value for Close - Open';
        case 'high_low_diff':
          return 'Computed Value for High - Low';
        case 'high_count':
          return 'Computed Value for High Count';
        case 'low_count':
          return 'Computed Value for Low Count';
        case 'high_low_sum':
          return 'Computed Value for High + Low Sum';
          default:
          return 'Unknown Metric';
       }
      }
    }); 
    

    from django.shortcuts import render, get_object_or_404
from .models import FinancialInstrument, HistoricalData
from datetime import datetime
import csv
import json
import numpy as np
from django.http import JsonResponse

def index(request):
    instruments = FinancialInstrument.objects.all()
    return render(request, 'index.html', {'instruments': instruments})

def instrument_detail(request, instrument_id):
    instrument = get_object_or_404(FinancialInstrument, pk=instrument_id)
    data = HistoricalData.objects.filter(instrument=instrument)

    # Extract and process data for Plotly traces
    traces = []


    for entry in data:
        dt_obj = datetime.combine(entry.date, entry.time)
        trace = {
            'x':  dt_obj.strftime("%Y-%m-%d %H:%M"),
            'y': float(entry.closing_price),
            'name': entry.date.strftime("%Y-%m-%d %H:%M"),
            'opening_price': float(entry.opening_price),
            'high_price': float(entry.max_price),
            'low_price': float(entry.min_price),
            'volume': entry.volume,
        }
        traces.append(trace)

        # Calculate metrics
        close = float(entry.closing_price)
        if close_prev is not None:
            close_close_minus_1 = close - close_prev
            close_open_diff.append(close - float(entry.opening_price))
            high_low_diff.append(float(entry.max_price) - float(entry.min_price))
        close_prev = close

        # Calculate high and low counts and sum
        if float(entry.max_price) == close:
            high_count += 1
        if float(entry.min_price) == close:
            low_count += 1
        high_low_sum += float(entry.max_price) + float(entry.min_price)

    serialized_traces = json.dumps(traces)  # Serialize traces to JSON

    # Calculate statistics
    closing_prices = [float(entry.closing_price) for entry in data]
    mean_price = np.mean(closing_prices)
    median_price = np.median(closing_prices)
    std_dev = np.std(closing_prices)

    metrics = {
        'close_close_minus_1': close_close_minus_1,
        'close_open_diff': close_open_diff,
        'high_low_diff': high_low_diff,
        'high_count': high_count,
        'low_count': low_count,
        'high_low_sum': high_low_sum,
    }

    statistics = {
        'mean_price': mean_price,
        'median_price': median_price,
        'std_dev': std_dev,
        # Add more statistics as needed
    }

    return render(request, 'instrument_detail.html', {
        'instrument': instrument,
        'data': data,
        'traces': serialized_traces,
        'metrics': metrics,  # Pass calculated metrics to the template
        'statistics': statistics,  # Pass calculated statistics to the template
    })

def get_chart_data(request, instrument_id, chart_type):
    instrument = get_object_or_404(FinancialInstrument, pk=instrument_id)
    data = HistoricalData.objects.filter(instrument=instrument)

    chart_data = []
    for entry in data:
        dt_obj = datetime.combine(entry.date, entry.time)
        chart_data.append({
            'x': dt_obj.strftime("%Y-%m-%d %H:%M"),
            'y': entry.closing_price,
            'name': entry.date.strftime("%Y-%m-%d %H:%M"),
            'opening_price': entry.opening_price,
            'high_price': entry.max_price,
            'low_price': entry.min_price,
            'up': entry.up,
            'down': entry.down,
        })

    return JsonResponse(chart_data, safe=False)


# Add more metrics calculation functions as needed

def calculate_statistics(request, instrument_id):
    instrument = get_object_or_404(FinancialInstrument, pk=instrument_id)
    data = HistoricalData.objects.filter(instrument=instrument)
    
    # Calculate statistics
    closing_prices = [float(entry.closing_price) for entry in data]
    mean_price = np.mean(closing_prices)
    median_price = np.median(closing_prices)
    std_dev = np.std(closing_prices)

    statistics = {
        'mean_price': mean_price,
        'median_price': median_price,
        'std_dev': std_dev,
        # Add more statistics as needed
    }

    return JsonResponse(statistics)


<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Highcharts Stock Chart Example</title>
  <!-- Include Bootstrap CSS -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/14.6.4/nouislider.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/ion-rangeslider/2.3.1/css/ion.rangeSlider.min.css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/14.6.4/nouislider.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/ion-rangeslider/2.3.1/js/ion.rangeSlider.min.js"></script>

  <!-- Include Bootstrap and jQuery JavaScript -->
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"></script>
  <!-- Include Highcharts library -->
  <script src="https://code.highcharts.com/highcharts.js"></script>
  <script src="https://code.highcharts.com/modules/stock.js"></script>
  <!-- Custom CSS -->
  <style>
    /* Custom styling for better organization */
    .left-column, .right-column {
      padding: 10px;
      font-size: 14px;
    }

    .data-visualization, .statistics, .filters {
      margin-bottom: 10px;
    }

    .filter-group {
      margin-bottom: 10px;
    }

    /* Minimize left column's screen occupation */
    .left-column {
      flex: 1;
      max-width: 300px;
    }

    /* Style the track and thumb of the range slider */
    .hour-range-filter {
      -webkit-appearance: none;
      width: 100%;
      height: 5px;
      background: #d3d3d3; /* Gray track */
      outline: none;
    }

    .hour-range-filter::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 20px;
      height: 20px;
      background: #4caf50; /* Green thumb */
      cursor: pointer;
      border-radius: 50%;
    }

    /* Style the selected range display */
    #selected-hours-range {
      margin-top: 5px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="container-fluid">
    <div class="row">
      <div class="col-md-4 left-column">
        <div class="data-visualization">
          <label for="chart-type" class="form-label">Chart Type:</label>
          <select id="chart-type" class="form-select mb-3">
            <option value="line">Line Chart</option>
            <option value="area">Area Chart</option>
            <option value="column">Column Chart</option>
            <!-- Add more chart types as needed -->
          </select>
        </div>

        <div class="statistics">
          <label for="statistic-selector" class="form-label">Select a Statistic:</label>
          <select id="statistic-selector" class="form-select mb-3">
            <option value="volume">Volume</option>
            <option value="mean">Mean</option>
            <option value="median">Median</option>
            <option value="std_deviation">Standard Deviation</option>
            <option value="variance">Variance</option>
            <option value="price_range">Price Range</option>
            <!-- Add more statistics options here if needed -->
          </select>
        </div>

        <div class="metrics">
          <label for="metric-selector" class="form-label">Select a Metric:</label>
          <select id="metric-selector" class="form-select mb-3">
            <option value="close_close_minus_1">Close - Close (-1)</option>
            <option value="close_open_diff">Close - Open</option>
            <option value="high_low_diff">High - Low</option>
            <option value="high_count">High Count</option>
            <option value="low_count">Low Count</option>
            <option value="high_low_sum">High + Low</option>
            <!-- Add more metrics options here if needed -->
          </select>
        </div>

        <div class="filters">
          <div class="filter-group">
            <label class="form-label">Months:</label>
            <div class="mb-3"> <!-- Add the 'mb-3' class for margin-bottom -->
              <select class="form-select month_filter">
                <option value="1">January</option>
                <option value="2">February</option>
                <option value="3">March</option>
                <option value="4">April</option>
                <option value="5">May</option>
                <option value="6">June</option>
                <option value="7">July</option>
                <option value="8">August</option>
                <option value="9">September</option>
                <option value="10">October</option>
                <option value="11">November</option>
                <option value="12">December</option>
                <!-- Add options for the rest of the months -->
              </select>
            </div>
          </div>

          <div class="filter-group">
            <label class="form-label">Years:</label>
            <div class="input-group">
              <input type="range" class="form-range year-filter" min="2000" max="2020" step="1" value="2000">
              <span class="input-group-text" id="selected-year">2000</span>
            </div>
          </div>

          <div class="filter-group">
            <label class="form-label">Days of the Week:</label>
            <div class="mb-3"> <!-- Add the 'mb-3' class for margin-bottom -->
              <select class="form-select day-filter">
                <option value="0">Sunday</option>
                <option value="1">Monday</option>
                <option value="2">Tuesday</option>
                <option value="3">Wednesday</option>
                <option value="4">Thursday</option>
                <option value="5">Friday</option>
                <option value="6">Saturday</option>
                <!-- Add options for the rest of the days -->
              </select>
            </div>
          </div>

          <div class="filter-group">
            <label class="form-label">Hours:</label>
            <div>
              <input type="range" class="hour-range-filter" min="0" max="23" step="1" value="0" />
              <span id="selected-hours-range">0 - 23</span>
            </div>
          </div>
        </div>
        <button id="run-statistics" class="btn btn-primary">Run Statistics</button>
      </div>

      <div class="col-md-8 right-column">
        <div class="top-section" style="height: 10%;">
          <!-- Metric Chart Type Selection -->
          <div class="metric-chart-type">
            <label class="form-label">Metric Chart Type:</label>
            <select id="metric-chart-type" class="form-select">
              <option value="line">Line Chart</option>
              <option value="column">Column Chart</option>
              <option value="column3d">3D Column Chart</option>
            </select>
          </div>

 
          <!-- Placeholder for displaying the selected metric -->
            <div id="selected-metric-display">
              Selected Metric: <span id="selected-metric-value">-</span>
            </div>
        </div>

        <div class="bottom-section" style="height: 90%;">
          <!-- Bottom Section Content -->
          <!-- Chart goes here -->
          <div class="chart" id="selected-chart"></div>
          <!-- Information display -->
          <div id="info-div"></div>
          <!-- Metric Line Chart Container -->
          <div class="chart" id="line-chart"></div>

          <!-- Metric Column Chart Container -->
          <div class="chart" id="column-chart"></div>

          <!-- Metric 3D Column Chart Container -->
          <div class="chart" id="column3d-chart"></div>
        </div>
      </div>
    </div>
  


  <script>
    // JavaScript code goes here
    var metrics = {{ metrics | safe }};
    var traces = {{ traces | safe }};
    var selectedMonths = [];
    var selectedYear = 2005; // Default selected year
    var selectedDays = [];
    var selectedHours = [];
    var selectedMinutes = [];
    var selectedSeconds = [];
    var chart = null; // Store the chart instance

    // Function to generate a Highcharts Line chart
    function generateHighchartsLineChart() {
      var selectedChartContainer = document.getElementById('selected-chart');
      selectedChartContainer.innerHTML = '';

      var filteredTraces = filterTracesBySelection();

      chart = new Highcharts.stockChart(selectedChartContainer, {
        title: {
          text: 'Line Chart',
        },
        xAxis: {
          type: 'datetime',
        },
        yAxis: {
          title: {
            text: 'Y-Axis Title',
          },
        },
        series: [{
          name: 'Series Name',
          type: 'line',
          data: filteredTraces.map(function(trace) {
            return [
              new Date(trace.x).getTime(), // Convert to milliseconds
              trace.y,
            ];
          }),
        }],
      });
    }

    // Function to generate a Highcharts Area chart
    function generateHighchartsAreaChart() {
      var selectedChartContainer = document.getElementById('selected-chart');
      selectedChartContainer.innerHTML = '';

      var filteredTraces = filterTracesBySelection();

      chart = new Highcharts.stockChart(selectedChartContainer, {
        title: {
          text: 'Area Chart',
        },
        xAxis: {
          type: 'datetime',
        },
        yAxis: {
          title: {
            text: 'Y-Axis Title',
          },
        },
        series: [{
          name: 'Series Name',
          type: 'area',
          data: filteredTraces.map(function(trace) {
            return [
              new Date(trace.x).getTime(), // Convert to milliseconds
              trace.y,
            ];
          }),
        }],
      });
    }

    // Function to generate a Highcharts Column chart with minute-level granularity
    function generateHighchartsColumnChart() {
      var selectedChartContainer = document.getElementById('selected-chart');
      selectedChartContainer.innerHTML = '';

      var filteredTraces = filterTracesBySelection();

      chart = new Highcharts.stockChart(selectedChartContainer, {
        title: {
          text: 'Column Chart',
        },
        xAxis: {
          type: 'datetime',
        },
        yAxis: {
          title: {
            text: 'Y-Axis Title',
          },
        },
        series: [{
          name: 'Series Name',
          type: 'column',
          pointInterval: 60 * 1000, // 1 minute in milliseconds
          pointStart: filteredTraces[0].x, // Use the earliest time as the starting point
          data: filteredTraces.map(function(trace) {
            return trace.y; // Use the value directly for the column height
          }),
        }],
      });
    }

    // Function to run statistics
    function runStatistics() {
      // Calculate and display statistics based on 'traces' data
    }

    // Filter traces based on selected months, year, days, hours, minutes, and seconds
    function filterTracesBySelection() {
      return traces.filter(function(trace) {
        var date = new Date(trace.x);
        var month = date.getMonth() + 1; // Adding 1 to adjust to 1-based indexing
        var year = date.getFullYear();
        var dayOfWeek = date.getDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday;
        var hour = date.getHours();
        var minute = date.getMinutes();
        var second = date.getSeconds();

        return (selectedMonths.length === 0 || selectedMonths.includes(month)) &&
          (year === selectedYear) &&
          (selectedDays.length === 0 || selectedDays.includes(dayOfWeek)) &&
          (selectedHours.length === 0 || selectedHours.includes(hour)) &&
          (selectedMinutes.length === 0 || selectedMinutes.includes(minute)) &&
          (selectedSeconds.length === 0 || selectedSeconds.includes(second));
      });
    }

    // Listen for changes in the chart type dropdown
    var chartTypeSelector = document.getElementById('chart-type');
    chartTypeSelector.addEventListener('change', function() {
      var selectedChartType = chartTypeSelector.value;
      if (selectedChartType === 'line') {
        generateHighchartsLineChart();
      } else if (selectedChartType === 'area') {
        generateHighchartsAreaChart();
      } else if (selectedChartType === 'column') {
        generateHighchartsColumnChart();
      }
    });

    // Listen for the "Run Statistics" button click
    var runStatisticsButton = document.getElementById('run-statistics');
    runStatisticsButton.addEventListener('click', runStatistics);

    // Listen for changes in the month select element
    var monthFilterSelect = document.querySelector('.month_filter');
    monthFilterSelect.addEventListener('change', function() {
    selectedMonths = Array.from(monthFilterSelect.options)
    .filter(function(option) { return option.selected; })
    .map(function(option) { return parseInt(option.value); });
    chart.redraw(); // Update the chart
    });
    // Listen for changes in year slider
    var yearFilter = document.querySelector('.year-filter');
    yearFilter.addEventListener('input', function() {
      selectedYear = parseInt(yearFilter.value);
      document.getElementById('selected-year').textContent = selectedYear;
      chart.redraw(); // Update the chart
    });

    // Listen for changes in day of the week selection
    var dayFilterSelector = document.querySelector('.day-filter');
    dayFilterSelector.addEventListener('change', function() {
    selectedDays = Array.from(dayFilterSelector.selectedOptions).map(function(option) {
    return parseInt(option.value);
    });
    chart.redraw(); // Update the chart
    });

    // Listen for changes in the hour range slider
    var hourRangeFilter = document.querySelector('.hour-range-filter');
    hourRangeFilter.addEventListener('input', function() {
    var minHour = parseInt(hourRangeFilter.value);
    var maxHour = parseInt(document.getElementById('selected-hours-range').textContent.split(' - ')[1]);

    // Update the displayed selected range
    document.getElementById('selected-hours-range').textContent = minHour + ' - ' + maxHour;

    chart.redraw(); // Update the chart
    });
    // Listen for changes in minute checkboxes
    var minuteFilters = document.querySelectorAll('.minute-filter');
    minuteFilters.forEach(function(filter) {
      filter.addEventListener('change', function() {
        selectedMinutes = Array.from(minuteFilters)
          .filter(function(filter) { return filter.checked; })
          .map(function(filter) { return parseInt(filter.value); });
        chart.redraw(); // Update the chart
      });
    });

    // Listen for changes in second checkboxes
    var secondFilters = document.querySelectorAll('.second-filter');
    secondFilters.forEach(function(filter) {
      filter.addEventListener('change', function() {
        selectedSeconds = Array.from(secondFilters)
          .filter(function(filter) { return filter.checked; })
          .map(function(filter) { return parseInt(filter.value); });
        chart.redraw(); // Update the chart
      });
    });
    document.addEventListener("DOMContentLoaded", function() {
    var metricSelector = document.getElementById('metric-selector');
    var selectedMetricValue = document.getElementById('selected-metric-value');


    
    // Initialize the chart with the default selected chart type
    generateHighchartsLineChart(); // Default to Line Chart
  </script>

  <style>
  /* Add CSS styles for the layout here */
  .container {
    display: flex;
    width: 100%;
  }

  .left-column {
    flex: 0.24; /* Adjust the flex value as needed */
    padding: 20px;
    border-right: 1px solid #ccc;
  }

  .right-column {
    flex: 0.86;
    display: flex; /* Add this to enable nested flex layout */
    flex-direction: column; /* Create a column layout for the right column */
    padding: 20px;
  }

  .chart {
    flex: 1; /* The chart takes up all available space in the right column */
    width: 100%;
    height: 100%; /* Adjust the height as needed */
  }

  /* Add styles for the top section */
  .top-section {
    flex: 0.2; /* Adjust the flex value for the top section */
    /*background-color: lightgray; /* Add your background color */
  }

  /* Add styles for the bottom section */
  .bottom-section {
    flex: 0.8; /* Adjust the flex value for the bottom section */
    overflow: auto; /* Add overflow for scrolling if content overflows */
  }

  /* Adjust the styles as needed */
</style>

</body>
</html>
