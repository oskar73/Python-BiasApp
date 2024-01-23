from dash import Dash, html, dcc, callback, Output, Input, dash_table
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .models import *
import pandas as pd

stocks=FinancialInstrument.objects.all().values('symbol')
# print(stocks)
# exit()
df=pd.DataFrame.from_records(stocks)

sheet=[dbc.themes.COSMO]
load_figure_template('COSMO')
app = DjangoDash(name='dash_app', external_stylesheets=sheet)
app.layout = dbc.Container(
    [
    dbc.Row([
            dbc.Col([
                dcc.Dropdown(df.symbol, 'Select Stock', id="select_stock",persistence=True),
                dcc.RangeSlider(2000, 2023, 1, value=[2007, 2008], id='date_range',marks=None,tooltip={"placement": "bottom", "always_visible": True}, persistence=True),
                dcc.RangeSlider(
                                min=0,
                                max=24 * 60,  # 24 hours * 60 minutes
                                step=1,
                                value=[10 * 60, 15 * 60],  # Default range from 10:00 to 15:00
                                id='hour_range',
                                marks=None,  # Marks every hour
                                persistence=True
                                ,className="py-0"
                            ),
                html.Div(id='output',className="py-0"),
                ]),
            dbc.Col([
                dcc.Checklist(
                    options={
                            '1': 'Jan','2': 'Feb','3': 'Mar','4': 'Apr','5': 'May','6': 'Jun',
                            '7': 'Jul','8': 'Aug','9': 'Sep','10': 'Ouc','11': 'Nov','12': 'Dec'
                    },
                    value=['1','2','3','4','5','6','7','8','9','10','11','12'],
                    id="months",
                    inline=True,
                    className="pb-2",persistence=True),
                dcc.Checklist(
                    options={
                            'mon': 'Mon','tue': 'Tue','wed': 'Wed','thu': 'Thu','fri': 'Fri','sun': 'Sun','sut': 'Sut',
                    },
                    value=['mon','tue','wed','thu','fri','sun','sut'],
                    id="week_days",
                    inline=True,persistence=True
                    ),]),
            dbc.Col([
                dcc.Checklist(
                    options={
                            '1': '1st','2': '2nd','3': '3rd','4': '4th','5': '5th','6': '6th','7': '7th','8': '8th','9': '9th','10': '10th','11': '11th','12': '12th','13': '13th','14': '14th','15': '15th',
                            '16': '16th','17': '17th','18': '18th','19': '19th','20': '20th','21': '21th','22': '22th','23': '23th','24': '24th','25': '25th','26': '26th','27': '27th','28': '28th','29': '29th','30': '30th','31': '31th',
                    },
                    value=[ '1','2','3','4','5','6','7','8','9','10','11','12','13','14','15',
                            '16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31'],
                    id="days",
                    inline=True,persistence=True
                    ),
                ], width=5),
            ],
        className="d-flex justify-content-between"),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(['Line', 'Bar','Histogram'], 'Line',id="select_chart",searchable=False,clearable=False,persistence=True),
            dcc.Dropdown(['All Series', 'One Per Chart',], 'All Series',id="select_series", className="pt-2",searchable=False,clearable=False,persistence=True),
            dcc.Dropdown(['Year, HH:MM', 'Month of Year, Day', 'Month of Year, HH:MM','Days of the Week, Day','Day of the Week, HH:MM','Days of Month, Day','Day of Month, HH:MM','Day, Day','D.HH'],'Year, HH:MM',id="select_group", className="pt-2",searchable=False,clearable=False,persistence=True),
            dcc.Dropdown(['$/€', '%', 'Pt'],'$/€',id="select_unit", className="pt-2",searchable=False,clearable=False,persistence=True),
            dcc.Dropdown(['Mean', 'Median','Standard Deviation','Sum','Count'], 'Count',id="select_statistics", className="pt-2",searchable=False,clearable=False,persistence=True),
            dcc.Dropdown(['Close - Close (-1)', 'Close - Open','High - Low','High Count','Low Count','High + Low'], 'High Count',id="select_metric", className="py-2",searchable=False,clearable=False,persistence=True),
            dcc.Checklist(
                    options={'1': 'European/Rome time'},
                    id="european_time",
                    value=[],
                    inline=True,persistence=True
                    ),
            dcc.Checklist(
                    options={'1': 'CumSum'},
                    value=[],
                    id="cum_sum",
                    inline=True,persistence=True
                    ),
            ],width=3,
            className="border-right"
                ),
        dbc.Col([
            dcc.Loading( 
                dcc.Graph(id='headach_chart',config = {'displaylogo': False,'responsive': 'auto'}),
                type="cube", 
                ),
            
            html.Div(id="table_output"),
            
            ], width=9,
                className="px-0 mr-0 pt-0 mt-0 border-top border-left",
                ),
        ]),
    ],className="pt-1 mx-0")

@app.callback(
    Output('output', 'children'),
    [Input('hour_range', 'value')]
)
def update_output(value):
    # Convert minutes to hours and minutes
    start_hour, start_minute = divmod(value[0], 60)
    end_hour, end_minute = divmod(value[1], 60)
    return f'Hour range: {start_hour:02d}:{start_minute:02d} - {end_hour:02d}:{end_minute:02d}'

@app.callback(
    Output('date_range','value'),
    Input('select_stock','value'),
    )
def change_year_range(select_stock):
    print("The function change_year_range was called at {}...".format(datetime.now()))
    retrive=HistoricalData.objects.filter(instrument__symbol=select_stock).order_by('datetime')
    left_year=retrive.first().date
    left_year=left_year.strftime("%Y-%m-%d").split('-')[0]
    righ_year=retrive.last().date
    righ_year=righ_year.strftime("%Y-%m-%d").split('-')[0]
    new_range=[left_year,righ_year]
    return new_range

@app.callback(                 
    [Output('headach_chart','figure'),
    Output('table_output', 'children')],
    
    [Input('months','value'),
    Input('week_days','value'),
    Input('days','value'),
    Input('select_chart','value'),
    Input('date_range','value'),
    Input('hour_range','value'),
    Input('select_stock','value'),
    
    Input('select_series','value'),
    Input('select_group','value'),
    Input('select_unit','value'),
    Input('select_statistics','value'),
    Input('select_metric','value'),
    
    Input('european_time','value'),
    Input('cum_sum','value')]
)
def update_chart(months,week_days,days,select_chart,date_range,hour_range,
                select_stock,select_series,select_group,select_unit,
                select_statistics,select_metric,european_time,cum_sum):
    #Define the days of the week for comparison
    wd=['mon','tue','wed','thu','fri','sun','sut']
    #Create a list to store the unselected days of the week
    week_days_to_hide=[] #This one is realy to use
    #Loop to Store the days in the list
    for d in wd:
        if not d in week_days:
            week_days_to_hide.append(d)   
    #Make sure you won't have an emptly list that could cause errors
    if len(week_days_to_hide)==0:
        week_days_to_hide=['sut','mon']  
    #Store the Unselected days in a list                
    unselected_dates=[]   #This on e is also to use
    for year in range(int(date_range[0]),int(date_range[1])+1):
        for month in range(1,13):
            for day in range(1,32):
                #This is in the case all the three are selected
                if not str(month) in months and not str(day) in days: 
                    base=f"{year}-{month:02d}-{day:02d}"
                    if not base in unselected_dates:
                        unselected_dates.append(base)
                #In the case we only have months
                elif not str(month) in months:
                    base=f"{year}-{month:02d}-{day:02d}"
                    if not base in unselected_dates:
                        unselected_dates.append(base)
                        
                elif not str(day) in days:
                    base=f"{year}-{month:02d}-{day:02d}"
                    if not base in unselected_dates:
                        unselected_dates.append(base)
                        
    #Start the filter that is going to bring you headaches  
    #Grabb the stock to use in your filters       
    #Then define the variables to be using throughout the project
            
    retrive=HistoricalData.objects.filter(instrument__symbol=select_stock).order_by('datetime')
    start_hour, start_minute = divmod(hour_range[0], 60)
    end_hour, end_minute = divmod(hour_range[1], 60)
    hour_range=[start_hour,end_hour]  #This one is also to use
    #This is for debugging only
    print("The function update_chart was called at {}...".format(datetime.now()))
    #My approch is to use the memory to go changing the values and then present it at once
    #Otherwise, i would have to do the same task more than 800 times as there could be more than 800k
    #Possibilities of combinations
    
    #What if the user select a line or a histogram or a column chart
    #What comes first? what next? Who is the most important, What defines the order of the selection in the developmente perspective?
    #The logic is going to be:
    # 1. Chart Type (Three chart types, three possibilities ahead)[3]
    # 2. Statistic (Five Statistics available, 15 possibilites ahead)[15]
    # 3. Metric (Six metrics available, 90 Possibilities ahead)[90]
    # 4. Group (Nine groups available, 891 Possibilities ahead)[891]
    
    # As we can predict, there are a lot of combinations, we need to create
    # a mechanism to evoid all these possibilities, analysing the charts, we can see
    # that some os this 'selects' only change some properties of the value to be passed to the chart
    # therefore, we are going to do it:
    # as we can not create multiple 'if's for the same attribute, we are going to use only
    # one of the 'selects' to change the value to be passed to the filter, in this case
    # it is going to be the 'metric', leaving us with only 90 possibilities which looks better to me
    
    if select_metric=="Close - Close (-1)":
        #Here i will create a new df row and add to it the diff of actual close and the previous
        fields=retrive.values('datetime','closing_price')
        df=pd.DataFrame.from_records(fields)
        df['closing_difference'] = df['closing_price'].diff(periods=1)
    elif select_metric=="Close - Open":
        #Here, i do the same thing as before with the difference on the formula being used
        fields=retrive.values('datetime','opening_price','closing_price')
        df=pd.DataFrame.from_records(fields)
        df['close_open_difference']=df['closing_price']-df['opening_price']
    elif select_metric=="High - Low":
        #fields=retrive.values('datetime','opening_price','closing_price','min_price','max_price','volume')
        #Here, i do the same thing as before with the difference on the formula being used
        fields=retrive.values('datetime','min_price','max_price')
        df=pd.DataFrame.from_records(fields)
        df['high_low_difference']=df['max_price']-df['min_price']
    elif select_metric=="Low Count":
        #fields=retrive.values('datetime','opening_price','closing_price','min_price','max_price','volume')
        #Here, i do the same thing as before with the difference on the formula being used
        fields=retrive.values('datetime','min_price')
        df=pd.DataFrame.from_records(fields)
    elif select_metric=="High + Low":
        #Here is the same as High - Low, just inverting the signal
        fields=retrive.values('datetime','min_price','max_price')
        df=pd.DataFrame.from_records(fields)
        df['high_low_sum']=df['max_price']+df['min_price']
    elif select_metric=="High Count":
        #In this case, y_values are on the standard which i choose as 'High' values from the database
        fields=retrive.values('datetime','max_price')
        df=pd.DataFrame.from_records(fields)
    #This way the values for the filter will be already defined, even if 
    # the user selects a 'statistic' or a group, it does not affect it at all        
    
    #Now we dive into the complete possibilites
    
    if select_unit=='$/€':
        unit_tip="$/€"
        #Just put all my data in the original state
        #Looks like there is no need to do anything, the data itself is already formated
        #But what if i change from '$/€' and i want it to go back to normal?
        #I will just say who is my current data now
        #I need to know who is the last column in the dataframe and grabb it from the original dataframe as it is
        #Thinking a little bit highter i can see that there is really no need to do anything here
        #If you put the data into % and would like to go back to $/€, it is going to happen automatically
        pass
    elif select_unit=='%':
        #Find the biggest value of the column and then compare every other
        #Value to it, showing it in percentage
        #First, we select who is the last column, which is the column of work
        second_column = df.columns[-1]
        #Then we create a variable to store the name of the selected Unit
        #Therefore we are going to do the same for all the other groups
        unit_tip="%"
        #Then we return the last column of the dataframe with the values in percentage
        max_value = df[second_column].max()
        df[second_column] = df[second_column] / max_value * 100
            
    elif select_unit=='Pt':
        second_column = df.columns[-1]
        unit_tip="Pt"
        #The difference between the first value and the subsequents
        # Rewrite the column with the difference between each value and the first value
        first_value = df[second_column].iloc[0]                    
        df[second_column] = df[second_column] - first_value
    
    if '1' in european_time:
        #Get all the selected data and then Add the equivalent hours to it
        #This simple line of code do the magic and solves the problem.
        df['datetime']=df['datetime']+pd.Timedelta(hours=6)
        
    if '1' in cum_sum:
        #Get all the selected data and CumSum all the fields in it
        second_column = df.columns[-1]
        opening_price=df[second_column].cumsum()
        df[second_column]=opening_price                    
        
    if select_statistics=="Count":
        #If you select an option that does not change nothing, there is nothing to change
        pass
    elif select_statistics=="Median":
        #Here there is a new approach to be applied, before, i created a new column to store 
        #The value of the Median and other but now, we only apply it to the last column, which is better
        second_column = df.columns[-1]
        #This way, we calculate the mean between all the past two rows ot the last column available for computation
        rolling_median = df[second_column].rolling(window=2, min_periods=1).median()
        df[second_column]=rolling_median
        
    elif select_statistics=="Mean":
        rolling_mean = df[second_column].rolling(window=2, min_periods=1).mean()
        df[second_column]=rolling_mean
        
    elif select_statistics=="Standard Deviation":
        rolling_std = df[second_column].rolling(window=2, min_periods=1).std()
        df[second_column]=rolling_std
        
    elif select_statistics=="Sum":
        rolling_sum = df[second_column].rolling(window=2, min_periods=1).sum()
        df[second_column]=rolling_sum
        
    #The groups bellow are very connected to the charts
    #Here i defenetely will have to nast these nine possibilities with
    #The chart types and the series option.
    #I don't see a better way for now, it will have to be anought
    
    if select_group=="Year, HH:MM":
        #It means i must group it into years and present it into minutes, which means, just group into year as it is already into minutes
        df_grouped = df.groupby(pd.Grouper(key='datetime', freq='YE'))
        second_column = df.columns[-1]
        df['year'] = df['datetime'].dt.year
        df_grouped = df.groupby('year')                   
        #Here we make the same dance as ever three x Two, Six combinations
        if select_chart=="Line":
            if select_series=="All Series":
                #Now it is time to add the table
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                #groups = dict(list(df)) #This is a holy line
                figure = go.Figure()
                for year, data in df_grouped:
                    # Creating a trace for each group
                    trace = go.Scatter(x=data['datetime'],y=data[second_column],mode='lines',name="Year {}".format(str(year)))
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=5, label="5h", step="hour", stepmode="todate"),dict(count=12, label="12h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                #Here i create many figures, each one on it's own chart
                #groups = dict(list(df)) #This is a holy line
                figure = make_subplots(rows=len(df_grouped), cols=1)
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )

                for i, (year, data) in enumerate(df_grouped):
                    figure.add_trace(go.Scatter(x=data['datetime'], y=data[second_column], mode='lines', name=f'Year {year}'), row=i+1, col=1)

                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)])
                return figure, table
            
        elif select_chart=="Bar":
            if select_series=="All Series":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                #groups = dict(list(df)) #This is a holy line
                figure = go.Figure()
                for year, group in df_grouped:
                    # Creating a trace for each group
                    trace = go.Bar(x=group['datetime'],y=group[second_column],name=str(year))
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=5, label="5h", step="hour", stepmode="todate"),dict(count=12, label="12h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            elif select_series=="One Per Chart":
                #Here i create many figures, each one on it's own chart
                #groups = dict(list(df)) #This is a holy line
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = make_subplots(rows=len(df_grouped), cols=1, shared_xaxes=True)
                for i, (year, group) in enumerate(df_grouped):
                    # Creating a trace for each group
                    trace = go.Bar(x=group['datetime'],y=group[second_column],name=str(year))
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                )
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                return figure, table
        elif select_chart=="Histogram":
            if select_series=="All Series":
                    #groups = dict(list(df)) #This is a holy line
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )   
                    
                figure = go.Figure()
                for year, group in df_grouped:
                    # Creating a trace for each group
                    trace = go.Histogram(x=group[second_column],name=str(year))
                    figure.add_trace(trace)
                figure.update_layout(
                    xaxis_title="Datetime",yaxis_title=second_column.capitalize(), showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=5, label="5h", step="hour", stepmode="todate"),dict(count=12, label="12h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            elif select_series=="One Per Chart":
                #Here i create many figures, each one on it's own chart
                #groups = dict(list(df)) #This is a holy line
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = make_subplots(rows=len(df_grouped), cols=1, shared_xaxes=True)
                for i, (year, group) in enumerate(df_grouped):
                    # Creating a trace for each group
                    trace = go.Histogram(x=group[second_column],name=str(year))
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                return figure, table
    
    elif select_group=="Month of Year, Day":
        second_column = df.columns[-1]
        df['month'] = df['datetime'].dt.month
        df['day'] = df['datetime'].dt.day
        df_grouped = df.groupby(['month', 'day'])
        # Aggregating data to daily level
        df_daily = df_grouped.agg({'{}'.format(second_column): 'mean'}).reset_index()
        
        if select_chart=="Line":
            if select_series=="All Series":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                for month in df['month'].unique():
                    df_month = df_daily[df_daily['month'] == month]
                    figure.add_trace(go.Scatter(x=df_month['day'], y=df_month[second_column], mode='lines', name=f'Month {month}'))
                
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=5, label="5d", step="day", stepmode="todate"),dict(count=15, label="15d", step="day", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            elif select_series=="One Per Chart":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                unique_months = df['month'].unique()
                num_months = len(unique_months)
                    
                figure = make_subplots(rows=num_months,cols=1)

                for i, month in enumerate(unique_months):
                    df_month = df_daily[df_daily['month'] == month]
                    trace=go.Scatter(x=df_month['day'], y=df_month[second_column], mode='lines',name=f'Month {month}')
                    figure.add_trace(trace, row=i+1, col=1)
                    
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                
                return figure, table
        elif select_chart=="Bar":
            if select_series=="All Series":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                for month in df['month'].unique():
                    df_month = df_daily[df_daily['month'] == month]
                    figure.add_trace(go.Bar(x=df_month['day'], y=df_month[second_column], name=f'Month {month}'))
                
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=5, label="5d", step="day", stepmode="todate"),dict(count=15, label="15d", step="day", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                unique_months = df['month'].unique()
                num_months = len(unique_months)
                    
                figure = make_subplots(rows=num_months,cols=1)

                for i, month in enumerate(unique_months):
                    df_month = df_daily[df_daily['month'] == month]
                    trace=go.Bar(x=df_month['day'], y=df_month[second_column], name=f'Month {month}')
                    figure.add_trace(trace, row=i+1, col=1)
                    
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                
                return figure, table
            
        elif select_chart=="Histogram":
            if select_series=="All Series":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                for month in df['month'].unique():
                    df_month = df_daily[df_daily['month'] == month]
                    figure.add_trace(go.Histogram(x=df_month['day'], name=f'Month {month}'))
                
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=5, label="5d", step="day", stepmode="todate"),dict(count=15, label="15d", step="day", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                unique_months = df['month'].unique()
                num_months = len(unique_months)
                    
                figure = make_subplots(rows=num_months,cols=1)

                for i, month in enumerate(unique_months):
                    df_month = df_daily[df_daily['month'] == month]
                    trace=go.Histogram(x=df_month['day'],name=f'Month {month}')
                    figure.add_trace(trace, row=i+1, col=1)
                    
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                
                return figure, table
        
    elif select_group=="Month of Year, HH:MM":
        second_column = df.columns[-1]
        df['month'] = df['datetime'].dt.month
        df_grouped = df.groupby(['month'])
        # Aggregating data to daily level
        
        if select_chart=="Line":
            if select_series=="All Series":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                i=1
                for month, group in df_grouped:
                    figure.add_trace(go.Scatter(x=group['datetime'], y=group[second_column], mode='lines', name=f'Month {i}'))
                    i+=1
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=5, label="5d", step="day", stepmode="todate"),dict(count=15, label="15d", step="day", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (_, group) in enumerate(df_grouped):
                    trace=go.Scatter(x=group['datetime'], y=group[second_column], mode='lines',name=f'Month {i+1}')
                    figure.add_trace(trace, row=i+1, col=1)
                    
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=800)  
                
                return figure, table
        
        elif select_chart=="Bar":
            if select_series=="All Series":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                i=1
                for month, group in df_grouped:
                    figure.add_trace(go.Bar(x=group['datetime'], y=group[second_column], name=f'Month {i}'))
                    i+=1
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=5, label="5d", step="day", stepmode="todate"),dict(count=15, label="15d", step="day", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (_, group) in enumerate(df_grouped):
                    trace=go.Bar(x=group['datetime'], y=group[second_column], name=f'Month {i+1}')
                    figure.add_trace(trace, row=i+1, col=1)
                    
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=800)  
                
                return figure, table
            
        elif select_chart=="Histogram":
            if select_series=="All Series":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                i=1
                for month, group in df_grouped:
                    figure.add_trace(go.Histogram(x=group['datetime'], name=f'Month {i}'))
                    i+=1
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=5, label="5d", step="day", stepmode="todate"),dict(count=15, label="15d", step="day", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=7, label="7d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                # Plotting
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (_, group) in enumerate(df_grouped):
                    trace=go.Histogram(x=group['datetime'],name=f'Month {i+1}')
                    figure.add_trace(trace, row=i+1, col=1)
                    
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=800)  
                
                return figure, table
        
    elif select_group=="Days of the Week, Day":
        second_column = df.columns[-1]
        df['week'] = df['datetime'].dt.isocalendar().week
        df['day'] = df['datetime'].dt.date
        df_grouped = df.groupby(['week', 'day'])
        df_weekly = df_grouped.mean().reset_index()
        if select_chart=="Line":
            if select_series=="All Series":
                # Calculating daily average within each week
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                for week, group in df_weekly.groupby('week'):
                    trace = go.Scatter(x=group['datetime'],y=group[second_column],mode='lines',name="Week Day {}".format(str(week)))
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = make_subplots(rows=len(df['week'].unique()),cols=1)

                #for i, month in enumerate(unique_months):
                for i, (week, group) in enumerate(df_weekly.groupby('week')):
                    trace = go.Scatter(x=group['datetime'],y=group[second_column],mode='lines',name="Week Day {}".format(str(week)))
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=4000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
            
        elif select_chart=="Bar":
            if select_series=="All Series":
                # Calculating daily average within each week
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                for week, group in df_weekly.groupby('week'):
                    trace = go.Bar(x=group['datetime'],y=group[second_column],name="Week Day {}".format(str(week)))
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = make_subplots(rows=len(df['week'].unique()),cols=1)

                #for i, month in enumerate(unique_months):
                for i, (week, group) in enumerate(df_weekly.groupby('week')):
                    trace = go.Bar(x=group['datetime'],y=group[second_column],name="Week Day {}".format(str(week)))
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=4000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
            
        elif select_chart=="Histogram":
            if select_series=="All Series":
                # Calculating daily average within each week
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                for week, group in df_weekly.groupby('week'):
                    trace = go.Histogram(x=group['datetime'],name="Week Day {}".format(str(week)))
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=len(df['week'].unique()),cols=1)

                #for i, month in enumerate(unique_months):
                for i, (week, group) in enumerate(df_weekly.groupby('week')):
                    trace = go.Histogram(x=group['datetime'],name="Week Day {}".format(str(week)))
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=4000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
        
        
    elif select_group=="Day of the Week, HH:MM":
        second_column = df.columns[-1]
        df['week'] = df['datetime'].dt.isocalendar().week
        df_grouped = df.groupby('week')
        if select_chart=="Line":
            if select_series=="All Series":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                # Calculating daily average within each week
                
                figure = go.Figure()
                for week, group in df_grouped:
                    trace = go.Scatter(x=group['datetime'],y=group[second_column],mode='lines',name="Week Day {}".format(str(week)))
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (_, group) in enumerate(df_grouped):
                    trace = go.Scatter(x=group['datetime'],y=group[second_column],mode='lines',name="Week Day {}".format(str(_)))
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=3000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
        
        elif select_chart=="Bar":
            if select_series=="All Series":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                # Calculating daily average within each week
                
                figure = go.Figure()
                for week, group in df_grouped:
                    trace = go.Bar(x=group['datetime'],y=group[second_column],name="Week Day {}".format(str(week)))
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (_, group) in enumerate(df_grouped):
                    trace = go.Bar(x=group['datetime'],y=group[second_column],name="Week Day {}".format(str(_)))
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=3000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
        
        elif select_chart=="Histogram":
            if select_series=="All Series":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                # Calculating daily average within each week
                
                figure = go.Figure()
                for week, group in df_grouped:
                    trace = go.Histogram(x=group['datetime'],name="Week Day {}".format(str(week)))
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (_, group) in enumerate(df_grouped):
                    trace = go.Histogram(x=group['datetime'],name="Week Day {}".format(str(_)))
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=3000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
            
    elif select_group=="Days of Month, Day":
        second_column = df.columns[-1]
        df['year'] = df['datetime'].dt.year
        df['month'] = df['datetime'].dt.month
        df['day'] = df['datetime'].dt.day

        # Grouping by year, month, and day of the month, then calculating the mean for each day
        df_mean = df.groupby(['year', 'month', 'day'])[second_column].mean().reset_index()
        
        if select_chart=="Line":
            if select_series=="All Series":
                # Calculating daily average within each week
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                
                figure = go.Figure()
                for day in range(1, 32):
                    day_data = df_mean[df_mean['day'] == day]
                    if not day_data.empty:
                        trace = go.Scatter(x=pd.to_datetime(day_data[['year', 'month', 'day']]),y=day_data[second_column],mode='lines',name=f"Day {day}")
                        figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=31, cols=1)

                for day in range(1, 32):
                    day_data = df_mean[df_mean['day'] == day]
                    if not day_data.empty:
                        trace = go.Scatter(x=pd.to_datetime(day_data[['year', 'month', 'day']]),y=day_data[second_column],mode='lines',name=f"Day {day}")
                        figure.add_trace(trace,row=day, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(), height=2000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
        
        elif select_chart=="Bar":
            if select_series=="All Series":
                # Calculating daily average within each week
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = go.Figure()
                for day in range(1, 32):
                    day_data = df_mean[df_mean['day'] == day]
                    if not day_data.empty:
                        trace = go.Bar(x=pd.to_datetime(day_data[['year', 'month', 'day']]),y=day_data[second_column],name=f"Day {day}")
                        figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=31, cols=1)

                for day in range(1, 32):
                    day_data = df_mean[df_mean['day'] == day]
                    if not day_data.empty:
                        trace = go.Bar(x=pd.to_datetime(day_data[['year', 'month', 'day']]),y=day_data[second_column],name=f"Day {day}")
                        figure.add_trace(trace,row=day, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(), height=2000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
        
        elif select_chart=="Histogram":
            if select_series=="All Series":
                # Calculating daily average within each week    
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )                        
                figure = go.Figure()
                for day in range(1, 32):
                    day_data = df_mean[df_mean['day'] == day]
                    if not day_data.empty:
                        trace = go.Histogram(x=pd.to_datetime(day_data[['year', 'month', 'day']]),name=f"Day {day}")
                        figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=31, cols=1)

                for day in range(1, 32):
                    day_data = df_mean[df_mean['day'] == day]
                    if not day_data.empty:
                        trace = go.Histogram(x=pd.to_datetime(day_data[['year', 'month', 'day']]),name=f"Day {day}")
                        figure.add_trace(trace,row=day, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(), height=2000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
            
    elif select_group=="Day of Month, HH:MM":
        second_column = df.columns[-1]
        df['day'] = df['datetime'].dt.day
        df_grouped = df.groupby('day')
        
        if select_chart=="Line":
            if select_series=="All Series":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = go.Figure()
                for day, group in df_grouped:
                    trace = go.Scatter(x=group['datetime'],y=group[second_column],mode='lines',name=f"Day {day}")
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (day, group) in enumerate(df_grouped):
                    trace = go.Scatter(x=group['datetime'],y=group[second_column],mode='lines',name=f"Day {day}")
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=3000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
        
        elif select_chart=="Bar":
            if select_series=="All Series":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = go.Figure()
                for day, group in df_grouped:
                    trace = go.Bar(x=group['datetime'],y=group[second_column],name=f"Day {day}")
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (day, group) in enumerate(df_grouped):
                    trace = go.Bar(x=group['datetime'],y=group[second_column],name=f"Day {day}")
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=3000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
        
        elif select_chart=="Histogram":
            if select_series=="All Series":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = go.Figure()
                for day, group in df_grouped:
                    trace = go.Histogram(x=group['datetime'],name=f"Day {day}")
                    figure.add_trace(trace)
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),showlegend=True,margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                figure.update_xaxes(
                    rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], 
                    rangeslider_visible=True,rangeselector=dict(buttons=list([dict(count=1, label="1h", step="hour", stepmode="todate"),
                    dict(count=1, label="1d", step="day", stepmode="todate"),dict(count=3, label="3d", step="day", stepmode="todate"),dict(step="all")
                ])))
                return figure, table
            
            elif select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                figure = make_subplots(rows=len(df_grouped),cols=1)

                for i, (day, group) in enumerate(df_grouped):
                    trace = go.Histogram(x=group['datetime'],name=f"Day {day}")
                    figure.add_trace(trace, row=i+1, col=1)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(yaxis_title=second_column.capitalize(),height=3000,margin_t=30,margin_b=0,margin_l=0,margin_r=0)
                return figure, table
    
    elif select_group=="Day, Day":
        second_column = df.columns[-1]
        df['day'] = df['datetime'].dt.date
        df_grouped = df.groupby('day')
        # Calculating daily mean
        df_daily_mean = df_grouped.mean().reset_index()
        if select_chart=="Line":
            if select_series=="All Series" or select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                # Calculating daily average within each week                         
                figure = go.Figure()
                trace = go.Scatter(x=df_daily_mean['datetime'],y=df_daily_mean[second_column],mode='lines',name="Daily Mean")
                figure.add_trace(trace)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], )
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                return figure, table
        
        elif select_chart=="Bar":
            if select_series=="All Series" or select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                # Calculating daily average within each week                         
                figure = go.Figure()
                trace = go.Bar(x=df_daily_mean['datetime'],y=df_daily_mean[second_column],name="Daily Mean")
                figure.add_trace(trace)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], )
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                return figure, table
        
        elif select_chart=="Histogram":
            if select_series=="All Series" or select_series=="One Per Chart":
                # Calculating daily average within each week
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )                         
                figure = go.Figure()
                trace = go.Histogram(x=df_daily_mean['datetime'],name="Daily Mean")
                figure.add_trace(trace)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(values=unselected_dates)], )
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                return figure, table
            
    elif select_group=="D.HH":
        second_column = df.columns[-1]
        df['day'] = df['datetime'].dt.date
        df_grouped = df.groupby('day')
        if select_chart=="Line":
            if select_series=="All Series" or select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                # Calculating daily average within each week
                figure = go.Figure()
                trace = go.Scatter(x=df['datetime'],y=df[second_column],mode='lines')
                figure.add_trace(trace)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                return figure, table
        
        elif select_chart=="Bar":
            if select_series=="All Series" or select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                # Calculating daily average within each week
                figure = go.Figure()
                trace = go.Bar(x=df['datetime'],y=df[second_column])
                figure.add_trace(trace)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                return figure, table
        
        elif select_chart=="Histogram":
            if select_series=="All Series" or select_series=="One Per Chart":
                table=dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=10
                )
                # Calculating daily average within each week
                figure = go.Figure()
                trace = go.Histogram(x=df['datetime'])
                figure.add_trace(trace)
                figure.update_xaxes(rangebreaks=[dict(bounds=week_days_to_hide),dict(bounds=hour_range, pattern="hour"),dict(values=unselected_dates)], )
                figure.update_layout(xaxis_title="Datetime",yaxis_title=second_column.capitalize(),margin_t=30,margin_b=0,margin_l=0,margin_r=0,height=400)  
                return figure, table