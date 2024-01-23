from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse,HttpResponse
from .models import FinancialInstrument, HistoricalData
from datetime import datetime
from django.db import connection
import json
import numpy as np
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required  # Import login_required decorator
from django.contrib.auth import logout
from django.shortcuts import redirect

def home(request):
    return HttpResponse("welcome to home")


def login_view(request):
    error_message  = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print("this is a request", user)
        if user is not None:
            login(request, user)
            # Redirect to a success page or dashboard upon successful login
            return redirect('instrument_detail', instrument_id=1) # Change 'dashboard' to your desired URL name
        else:
            # Handle invalid login credentials
            error_message = "Invalid username or password."

    return render(request, 'login.html', {'error_message': error_message})


@login_required
def instrument_detail_pre(request,instrument_id):
    instruments = FinancialInstrument.objects.all()
    data = HistoricalData.objects.filter(instrument=instrument_id)

    # Extract and process data for Plotly traces
    traces = []
    previous_close = None
    previous_open = None
    previous_high = None
    previous_low = None
    mean_close_close_minus_1 = None
    median_close_close_minus_1 = None 
    std_dev_close_close_minus_1 = None
    sum_close_close_minus_1 = None
    count_close_close_minus_1 = None
    mean_high_low_diff = None
    median_high_low_diff = None
    std_dev_high_low_diff = None
    sum_high_low_diff = None
    count_high_low_diff = None
    mean_high_count = None
    median_high_count = None
    std_dev_high_count = None
    sum_high_count = None
    count_high_count = None
    mean_close_open_diff = None
    median_close_open_diff = None
    std_dev_close_open_diff = None
    sum_close_open_diff = None
    count_close_open_diff = None
    mean_low_count = None
    median_low_count = None
    std_dev_low_count = None
    sum_low_count = None
    count_low_count = None
    mean_high_low_sum = None
    median_high_low_sum = None
    std_dev_high_low_sum = None
    sum_high_low_sum = None
    count_high_low_sum = None

    for entry in data:
        dt_obj = datetime.combine(entry.date, entry.time)
        
        # Calculate metrics
        close = float(entry.closing_price)
        open_price = float(entry.opening_price)
        high = float(entry.max_price)
        low = float(entry.min_price)
         # Check if any of the data values is NaN
        if np.isnan(close) or np.isnan(open_price) or np.isnan(high) or np.isnan(low):
        # Skip this data point if any value is NaN
            continue

        if previous_close is not None:
            close_close_minus_1 = close - previous_close
            if close_close_minus_1 is not None:
                mean_close_close_minus_1 = np.nanmean(close_close_minus_1)
                median_close_close_minus_1 = np.nanmedian(close_close_minus_1)
                std_dev_close_close_minus_1 = np.nanstd(close_close_minus_1)
                sum_close_close_minus_1 = np.nansum(close_close_minus_1)
                count_close_close_minus_1 = np.count_nonzero((close_close_minus_1))

        else:
            close_close_minus_1 = None

        close_open_diff = close - open_price
        mean_close_open_diff = np.nanmean(close_open_diff)
        median_close_open_diff = np.nanmedian(close_open_diff)
        std_dev_close_open_diff = np.nanstd(close_open_diff)
        sum_close_open_diff = np.nansum(close_open_diff)
        count_close_open_diff = np.count_nonzero(close_open_diff)

        if previous_high is not None and previous_low is not None:
            high_low_diff = high - low
            mean_high_low_diff = np.nanmean(high_low_diff)
            median_high_low_diff = np.nanmedian(high_low_diff)
            std_dev_high_low_diff = np.nanstd(high_low_diff)
            sum_high_low_diff = (np.nansum(high_low_diff)).tolist()
            count_high_low_diff = (np.count_nonzero(high_low_diff))

            high_count = 1 if high == previous_high else 0
            mean_high_count = np.nanmean(high_count)
            median_high_count = np.nanmedian(high_count)
            std_dev_high_count = np.nanstd(high_count)
            sum_high_count = np.nansum(high_count).tolist()
            count_high_count = np.count_nonzero(high_count)
            low_count = 1 if low == previous_low else 0
            mean_low_count = np.nanmean(low_count)
            median_low_count = np.nanmedian(low_count)
            std_dev_low_count = np.nanstd(low_count)
            sum_low_count = np.nansum(low_count).tolist()
            count_low_count = np.count_nonzero(low_count)
            high_low_sum = high_count + low_count
            mean_high_low_sum = np.nanmean(high_low_sum)
            median_high_low_sum = np.nanmedian(high_low_sum)
            std_dev_high_low_sum = np.nanstd(high_low_sum)
            sum_high_low_sum = np.sum(high_low_sum).tolist()
            count_high_low_sum = np.count_nonzero(high_low_sum)
        else:
            high_low_diff = None
            high_count = None
            low_count = None
            high_low_sum = None

        #mean_close_close_minus_1 = np.nanmean(close_close_minus_1_values)    

        trace = {
            'x': dt_obj.strftime("%Y-%m-%d %H:%M"),
            'y': close,
            'name': entry.date.strftime("%Y-%m-%d %H:%M"),
            'opening_price': open_price,
            'high_price': high,
            'low_price': low,
            'volume': entry.volume,
            'close_close_minus_1': close_close_minus_1,
            'close_open_diff': close_open_diff,
            'high_low_diff': high_low_diff,
            'high_count': high_count,
            'low_count': low_count,
            'high_low_sum': high_low_sum,
            'mean_close_close_minus_1':mean_close_close_minus_1,
            'median_close_close_minus_1':median_close_close_minus_1,
            'std_dev_close_close_minus_1':std_dev_close_close_minus_1,
            'sum_close_close_minus_1':sum_close_close_minus_1,
            'count_close_close_minus_1':count_close_close_minus_1,
            'mean_high_low_diff':mean_high_low_diff,
            'median_high_low_diff':median_high_low_diff,
            'std_dev_high_low_diff':std_dev_high_low_diff,
            'sum_high_low_diff':sum_high_low_diff,
            'count_high_low_diff':count_high_low_diff,
            'mean_high_count':mean_high_count,
            'median_high_count':median_high_count,
            'std_dev_high_count':std_dev_high_count,
            'sum_high_count':sum_high_count,
            'mean_close_open_diff':mean_close_open_diff,
            'median_close_open_diff':median_close_open_diff,
            'std_dev_close_open_diff':std_dev_close_open_diff,
            'sum_close_open_diff':sum_close_open_diff,
            'count_close_open_diff':count_close_open_diff,
            'mean_low_count':mean_low_count,
            'median_low_count':median_low_count,
            'std_dev_low_count':std_dev_low_count,
            'sum_low_count':sum_low_count,
            'count_low_count':count_low_count,
            'mean_high_low_sum':mean_high_low_sum,
            'median_high_low_sum':median_high_low_sum,
            'std_dev_high_low_sum':std_dev_high_low_sum,
            'sum_high_low_sum':sum_high_low_sum,
            'count_high_low_sum':count_high_low_sum,
        }

        traces.append(trace)

        previous_close = close
        previous_open = open_price
        previous_high = high
        previous_low = low

    serialized_traces = json.dumps(traces)  # Serialize traces to JSON

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

    return render(request, 'instrument_detail.html', {
        'days_of_month': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
        'days_of_week': ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],
        'instrument_id': instrument_id,
        'instruments': instruments,
        'data': data,
        'traces': serialized_traces,  # Pass serialized traces to the template
        'statistics': statistics,  # Pass calculated statistics to the template
    })


def logout_view(request):
    logout(request)
    return redirect('/login')  # Redirect to your home page or any other page after logout

@login_required
def instrument_detail(request, instrument_id):

    instruments = FinancialInstrument.objects.all();

    return render(request, 'instrument_detail.html', {
        'days_of_month': [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
        'days_of_week': ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],
        'instrument_id': instrument_id,
        'instruments': instruments,
    })


def api_statistics(requset):
    instrumentId = requset.POST.get("instrumentId")
    startDate = requset.POST.get("startDate")
    endDate = requset.POST.get("endDate")
    selectedMonths = requset.POST.getlist("selectedMonths[]")
    selectedWeekDays = requset.POST.getlist("selectedWeekDays[]")
    selectedDates = requset.POST.getlist("selectedDates[]")
    startTime = requset.POST.get("startTime")
    endTime = requset.POST.get("endTime")

    selectedMonths = '{}'.format(','.join(str(x) for x in selectedMonths))
    selectedWeekDays = '{}'.format(','.join(str(x) for x in selectedWeekDays))
    selectedDates = '{}'.format(','.join(str(x) for x in selectedDates))

    query = "SELECT * FROM `bias_app_historicaldata` WHERE DATE BETWEEN '{}' AND '{}' AND TIME BETWEEN '{}' AND '{}'".format(startDate, endDate, startTime, endTime)
    nMonths = len(selectedMonths)
    if nMonths > 0 and nMonths < 12:
        query += " AND MONTH(date) IN ({})".format(selectedMonths)
    
    nWeekDays = len(selectedWeekDays)
    if nWeekDays > 0 and nWeekDays < 7:
        query += " AND DAYOFWEEK(date) IN ({})".format(selectedWeekDays)
    
    nDates = len(selectedDates)
    if nDates > 0 and nDates < 31:
        query += " AND DAYOFMONTH(date) IN ({})".format(selectedDates)

    query += " ORDER BY date ASC, time ASC"

    data = HistoricalData.objects.raw(query)    

    traces = []
    previous_close = None
    previous_open = None
    previous_high = None
    previous_low = None
    mean_close_close_minus_1 = None
    median_close_close_minus_1 = None 
    std_dev_close_close_minus_1 = None
    sum_close_close_minus_1 = None
    count_close_close_minus_1 = None
    mean_high_low_diff = None
    median_high_low_diff = None
    std_dev_high_low_diff = None
    sum_high_low_diff = None
    count_high_low_diff = None
    mean_high_count = None
    median_high_count = None
    std_dev_high_count = None
    sum_high_count = None
    count_high_count = None
    mean_close_open_diff = None
    median_close_open_diff = None
    std_dev_close_open_diff = None
    sum_close_open_diff = None
    count_close_open_diff = None
    mean_low_count = None
    median_low_count = None
    std_dev_low_count = None
    sum_low_count = None
    count_low_count = None
    mean_high_low_sum = None
    median_high_low_sum = None
    std_dev_high_low_sum = None
    sum_high_low_sum = None
    count_high_low_sum = None

    for entry in data:
        dt_obj = datetime.combine(entry.date, entry.time)
        
        # Calculate metrics
        close = float(entry.closing_price)
        open_price = float(entry.opening_price)
        high = float(entry.max_price)
        low = float(entry.min_price)
         # Check if any of the data values is NaN
        if np.isnan(close) or np.isnan(open_price) or np.isnan(high) or np.isnan(low):
        # Skip this data point if any value is NaN
            continue

        if previous_close is not None:
            close_close_minus_1 = close - previous_close
            if close_close_minus_1 is not None:
                mean_close_close_minus_1 = np.nanmean(close_close_minus_1)
                median_close_close_minus_1 = np.nanmedian(close_close_minus_1)
                std_dev_close_close_minus_1 = np.nanstd(close_close_minus_1)
                sum_close_close_minus_1 = np.nansum(close_close_minus_1)
                count_close_close_minus_1 = np.count_nonzero((close_close_minus_1))

        else:
            close_close_minus_1 = None

        close_open_diff = close - open_price
        mean_close_open_diff = np.nanmean(close_open_diff)
        median_close_open_diff = np.nanmedian(close_open_diff)
        std_dev_close_open_diff = np.nanstd(close_open_diff)
        sum_close_open_diff = np.nansum(close_open_diff)
        count_close_open_diff = np.count_nonzero(close_open_diff)

        if previous_high is not None and previous_low is not None:
            high_low_diff = high - low
            mean_high_low_diff = np.nanmean(high_low_diff)
            median_high_low_diff = np.nanmedian(high_low_diff)
            std_dev_high_low_diff = np.nanstd(high_low_diff)
            sum_high_low_diff = (np.nansum(high_low_diff)).tolist()
            count_high_low_diff = (np.count_nonzero(high_low_diff))

            high_count = 1 if high == previous_high else 0
            mean_high_count = np.nanmean(high_count)
            median_high_count = np.nanmedian(high_count)
            std_dev_high_count = np.nanstd(high_count)
            sum_high_count = np.nansum(high_count).tolist()
            count_high_count = np.count_nonzero(high_count)
            low_count = 1 if low == previous_low else 0
            mean_low_count = np.nanmean(low_count)
            median_low_count = np.nanmedian(low_count)
            std_dev_low_count = np.nanstd(low_count)
            sum_low_count = np.nansum(low_count).tolist()
            count_low_count = np.count_nonzero(low_count)
            high_low_sum = high_count + low_count
            mean_high_low_sum = np.nanmean(high_low_sum)
            median_high_low_sum = np.nanmedian(high_low_sum)
            std_dev_high_low_sum = np.nanstd(high_low_sum)
            sum_high_low_sum = np.sum(high_low_sum).tolist()
            count_high_low_sum = np.count_nonzero(high_low_sum)
        else:
            high_low_diff = None
            high_count = None
            low_count = None
            high_low_sum = None

        #mean_close_close_minus_1 = np.nanmean(close_close_minus_1_values)    

        trace = {
            'x': dt_obj.strftime("%Y-%m-%d %H:%M"),
            'y': close,
            'name': entry.date.strftime("%Y-%m-%d %H:%M"),
            'opening_price': open_price,
            'high_price': high,
            'low_price': low,
            'volume': entry.volume,
            'close_close_minus_1': close_close_minus_1,
            'close_open_diff': close_open_diff,
            'high_low_diff': high_low_diff,
            'high_count': high_count,
            'low_count': low_count,
            'high_low_sum': high_low_sum,
            'mean_close_close_minus_1':mean_close_close_minus_1,
            'median_close_close_minus_1':median_close_close_minus_1,
            'std_dev_close_close_minus_1':std_dev_close_close_minus_1,
            'sum_close_close_minus_1':sum_close_close_minus_1,
            'count_close_close_minus_1':count_close_close_minus_1,
            'mean_high_low_diff':mean_high_low_diff,
            'median_high_low_diff':median_high_low_diff,
            'std_dev_high_low_diff':std_dev_high_low_diff,
            'sum_high_low_diff':sum_high_low_diff,
            'count_high_low_diff':count_high_low_diff,
            'mean_high_count':mean_high_count,
            'median_high_count':median_high_count,
            'std_dev_high_count':std_dev_high_count,
            'sum_high_count':sum_high_count,
            'mean_close_open_diff':mean_close_open_diff,
            'median_close_open_diff':median_close_open_diff,
            'std_dev_close_open_diff':std_dev_close_open_diff,
            'sum_close_open_diff':sum_close_open_diff,
            'count_close_open_diff':count_close_open_diff,
            'mean_low_count':mean_low_count,
            'median_low_count':median_low_count,
            'std_dev_low_count':std_dev_low_count,
            'sum_low_count':sum_low_count,
            'count_low_count':count_low_count,
            'mean_high_low_sum':mean_high_low_sum,
            'median_high_low_sum':median_high_low_sum,
            'std_dev_high_low_sum':std_dev_high_low_sum,
            'sum_high_low_sum':sum_high_low_sum,
            'count_high_low_sum':count_high_low_sum,
        }

        traces.append(trace)

        previous_close = close
        previous_open = open_price
        previous_high = high
        previous_low = low

        
    
    return JsonResponse({'traces' : traces})
