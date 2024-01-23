$.ajaxSetup({
  headers: { 'X-CSRFToken': $('meta[name="X-CSRF-TOKEN"]').attr('content') },
});

var yearSliderRange = $('#year-slider-range');
var hourSliderRange = $('#hour-slider-range');
var startDate = '2005.01.01';
var endDate = '2005.04.01';
var startTime = '00:00';
var endTime = '23:59';
var selectedMonths = [];
var selectedDates = [];
var selectedWeekDays = [];
var selectedChartType = "line";
var chartContainer = document.getElementById('selected-chart');

var groupingOptions = {
  "HH.MM": {
    units: [
      ["hour", [1]]
    ]
  },
  "day_of_month,HH.MM": {
    units: [
      ["day", [1]]
    ]
  },
  "month_of_year,HH.MM": {
    units: [
      ["month", [1]]
    ]
  },
  "year,HH.MM": {
    units: [
      ["year", [1]]
    ]
  },
  "day_of_week,day": {
    units: [
      ["week", [1]]
    ]
  },
  "day_of_month,day": {
    units: [
      ["month", [1]]
    ]
  },
  "month_of_year,day": {
    units: [
      ["year", [1]]
    ]
  },
  "day,HH": {
    units: [
      ["day", [1]]
    ]
  },
  "day,day": {
    units: [
      ["day", [1]]
    ]
  }
};



function time2str(time) {
  var hour = Math.floor(time / 60);
  var minute = time % 60;
  if (hour < 10) {
    hour = '0' + hour;
  }

  if (minute < 10) {
    minute = '0' + minute;
  }
  return hour + ":" + minute;
}

var Splash = (function () {
  return {
    show: function () {
      $('body').append('<div id="loading_splash" class="d-flex justify-content-center">\
                          <h3>Loading...</h3>\
                        </div>');
    },
    hide: function () {
      $('#loading_splash').remove();
    }
  }
})();

var StockStatistic = (function () {

  var instrumentId = $('body').data('instrument_id') || 1;
  

  var loadStatisticData = function () {

    console.log("Date range: ", startDate, " - " + endDate);
    console.log("Selected Months: ", selectedMonths);
    console.log("Selected dates: ", selectedDates);
    console.log("Selected Week days: ", selectedWeekDays);
    console.log("Selected hour range: ", startTime + " - " + endTime);

    $.ajax({
      type: 'POST',
      url: "/api/statistics",
      data: {
        instrumentId: instrumentId,
        startDate: startDate,
        endDate: endDate,
        selectedMonths: selectedMonths,
        selectedWeekDays: selectedWeekDays,
        selectedDates: selectedDates,
        startTime: startTime,
        endTime: endTime
      },
      beforeSend: function () {
        Splash.show();
      },
      success: function (data) {
        initChart(data.traces || []);
      },
      error: function () {

      },
      complete: function () {
        Splash.hide();
      }
    });
  };

  var initChart = function (traces) {
    
    chartContainer.innerHTML = "";

    var selectedChartType = $('#chart-type').val() || "line";
    var selectedAggregationInterval = parseInt($('#aggregation-interval').val());
    var selectedGroupingCriteria = $('#grouping-criteria').val();
    var selectedStatistic = $('#statistic-selector').val();
    var selectedMetric = $('#metric-selector').val();

    var offset = new Date().getTimezoneOffset() * 60 * 1000;

    var chart = new Highcharts.stockChart(chartContainer, {
      chart: {
        type: selectedChartType || 'line',
        time: {
          useUTC: false,
          timezoneOffset: new Date().getTimezoneOffset()
        }
      },
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
        name : "Series Name",
          data : traces.map(function(trace) {
            return [
              new Date(trace.x).getTime() - offset, // Convert to milliseconds
              trace.mean_close_close_minus_1,
            ];
          })
      }],
      // Add Highcharts stock tools (range selector, navigation buttons, etc.)
      rangeSelector: {
        enabled: true, // Enable the range selector
      },
      navigator: {
        enabled: true, // Enable the navigator for zooming
      },
      scrollbar: {
        enabled: true, // Enable the scrollbar for scrolling
      },
      legend: {
        enabled: true, // Enable the legend
      },
    });

    if(selectedMetric) {
      // Example for 'std_deviation' series:
      var newData = traces.map(function (trace) {
        return [new Date(trace.x).getTime(), trace['std_dev_' + selectedMetric]];
      });

      // Add or update the series data
      // Example for 'sum' series:
      var sumSeriesData = traces.map(function (trace) {
        return [new Date(trace.x).getTime() - offset, trace['sum_' + selectedMetric]];
      });

      // Example for 'count' series:
      var countSeriesData = traces.map(function (trace) {
        return [new Date(trace.x).getTime() - offset, trace['count_' + selectedMetric]];
      });

      // Example for 'mean' series:
      var meanSeriesData = traces.map(function (trace) {
        return [new Date(trace.x).getTime() - offset, trace['mean_' + selectedMetric]];
      });

      // Example for 'median' series:
      var medianSeriesData = traces.map(function (trace) {
        return [new Date(trace.x).getTime() - offset, trace['median_' + selectedMetric]];
      });
      // Example for 'std_deviation' series:
      var stdDevSeriesData = traces.map(function (trace) {
        return [new Date(trace.x).getTime() - offset, trace['std_dev_' + selectedMetric]];
      });

      chart.addSeries({
        name: 'Standard Deviation Series',
        data: stdDevSeriesData,
        color: 'red'
      }, false);

      chart.addSeries({
        name: 'Sum Series',
        data: sumSeriesData,
        color: 'orange'
      }, false);

      chart.addSeries({
        name: 'Count Series',
        data: countSeriesData,
        color: 'purple'
      }, false);

      chart.addSeries({
        name: 'Mean Series',
        data: meanSeriesData,
        color: 'blue'
      }, false);

      chart.addSeries({
        name: 'Median Series',
        data: medianSeriesData,
        color: 'green'
      }, false); // true to redraw the chart after adding series

      chart.redraw();
    }
  };

  return {
    init: function () {
      loadStatisticData();
    }
  };
})();

$(document).ready(function () {

  /** Bind events on ui   */
  $('#symbol-selector').on("change", function () {
    var val = this.value;
    location.href = "/instrument/" + val + "/";
  });

  yearSliderRange.slider({
    range: true,
    min: new Date('2000-01-01').getTime() / 1000,
    max: new Date('2023-12-31').getTime() / 1000,
    step: 86400,
    values: [new Date(startDate).getTime() / 1000, new Date(endDate).getTime() / 1000],
    slide: function (event, ui) {
      startDate = moment(ui.values[0] * 1000).format('yyyy-MM-DD');
      endDate = moment(ui.values[1] * 1000).format('yyyy-MM-DD');
      $("#year-range-label").val(startDate + " - " + endDate);
    }
  });

  $("#year-range-label").val(startDate + " - " + endDate);

  $("#month_filter_all").change(function () {
    selectedMonths = new Array;
    if (this.checked) {
      $("input[name='month_filter']").each(function () {
        this.checked = true;
        selectedMonths.push(parseInt(this.value));
      });
    } else {
      $("input[name='month_filter']").each(function () {
        this.checked = false;
      });
    }
  });

  $("input[name='month_filter']").on("change", function () {
    var thisMonth = this.value;
    if (this.checked) {
      selectedMonths.push(parseInt(this.value));
    } else {
      selectedMonths = selectedMonths.filter(function (month) {
        return thisMonth != month;
      });
    }
  });


  $("#days_of_month_filter_all").click(function () {
    selectedDates = new Array;
    if (this.checked) {
      $("input[name='days_of_month_filter']").each(function () {
        this.checked = true;
        selectedDates.push(parseInt(this.value));
      });
    } else {
      $("input[name='days_of_month_filter']").each(function () {
        this.checked = false;
      });
    }
  });

  $("input[name='days_of_month_filter']").change(function () {
    var thisValue = parseInt(this.value);
    if (this.checked) {
      selectedDates.push(thisValue);
    } else {
      selectedDates = selectedDates.filter(function (val) {
        return val != parseInt(thisValue);
      });
    }
  });

  $("#days_of_week_filter_all").click(function () {
    selectedWeekDays = new Array;
    if (this.checked) {
      $("input[name='days_of_week_filter']").each(function () {
        this.checked = true;
        selectedWeekDays.push(parseInt(this.value) + 1);
      });
    } else {
      $("input[name='days_of_week_filter']").each(function () {
        this.checked = false;
      });
    }
  });

  $("input[name='days_of_week_filter']").change(function () {
    var thisValue = parseInt(this.value) + 1;
    if (this.checked) {
      selectedWeekDays.push(parseInt(this.value) + 1);
    } else {
      selectedWeekDays = selectedWeekDays.filter(function (val) {
        return val != thisValue;
      });
    }
  });

  hourSliderRange.slider({
    range: true,
    min: 0,
    max: 1439,
    step: 1,
    values: [0, 1439],
    slide: function (event, ui) {
      startTime = time2str(ui.values[0]);
      endTime = time2str(ui.values[1]);
      $("#hour-range-label").val(startTime + " - " + endTime);
    }
  });

  $("#hour-range-label").val(startTime + " - " + endTime);

  $('#chart-type').on("change", function () {
    selectedChartType = this.value || "line";
  });

  $('#run-statistics').on("click", function () {
    StockStatistic.init();
  });

  // StockStatistic.init();
});