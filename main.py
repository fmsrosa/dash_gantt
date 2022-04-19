import datetime
from datetime import timedelta, date

import numpy as np
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

global df


def create_fake_df(path):
    df = pd.read_csv(path)
    _df = df.copy()

    def do_repeated_value(col: str, _min: int = 0, _max: int = 50) -> pd.DataFrame:
        values = np.random.choice(_df.loc[_min:_max, col], size=len(_df))
        _df[col] = values
        return _df

    def correct_datatypes(cols_types: dict) -> pd.DataFrame:
        for col in cols_types.keys():
            if cols_types[col] == 'date':
                _df[col] = pd.to_datetime(_df[col])#.dt.date
        return _df

    def random_ids (col: str) -> pd.DataFrame:
        indexes = _df.groupby(col).groups.values()
        for ind in indexes:
            _df.loc[ind, col] = _df.loc[ind, col] + np.random.randint(100, 200)
        return _df

    _df = do_repeated_value('id')
    _df = do_repeated_value('Type', _max=2)
    _df = do_repeated_value('Assignee', _max=9)
    _df = correct_datatypes({'Start': 'date', 'End': 'date'})
    _df = random_ids('id')

    return _df


def create_app(start_col: str, end_col: str, y_col: str, color_col: str,
               start_default: datetime.date = None, end_default: datetime.date = None) -> dash.Dash.layout:
    _df = df.copy()

    def do_cronograma(_start_col: str, _end_col: str, _y_col: str, _color_col: str) -> px.timeline:
        _fig = px.timeline(_df, x_start=_start_col, x_end=_end_col, y=_y_col, color=_color_col)
        return _fig

    def create_app_layout(_start_col: str, _end_col: str, _y_col: str, _color_col: str,
                          _start_default: datetime.date = None, _end_default: datetime.date = None) -> dash.Dash.layout:
        def do_header(_title: str, _text: str):
            html_title = html.H1(children=_title, className="header-title", )
            html_par = html.P(children=_text, className="header-description", )

            return html_title, html_par

        def do_dash_graph(_id: str) -> dcc.Graph:
            _graph = dcc.Graph(id=_id, config={"displayModeBar": False}, className='card')
            return _graph

        def do_dropdown(_col: str, _id: str) -> dcc.Dropdown:
            _options = [{"label": value, "value": value} for value in np.sort(_df[_col].unique())]
            _dropdown = dcc.Dropdown(id=_id, clearable=True, multi=True, options=_options, className="dropdown",
                                     value=_options)
            return _dropdown

        def do_daterange_picker(_start_col: str, _id: str,
                                _start_default: datetime.date, _end_default: datetime.date) -> dcc.DatePickerRange:
            _start = _df[_start_col].min()
            _end = _df[_start_col].max()

            if not _start_default:
                _start_default = _start
            if not _end_default:
                _end_default = _end

            _date_picker_range = dcc.DatePickerRange(id=_id, min_date_allowed=_start, max_date_allowed=_end,
                                                     start_date=_start_default, end_date=_end_default)
            return _date_picker_range

        main_title1 = "Timeline example"
        par_title1 = "This is an example of a cronograma." \
                     " It was created using Dash and Plotly." \
                     " Hope you like it!"
        title, title_description = do_header(main_title1, par_title1)
        # fig = do_cronograma(start_col, end_col, y_col, color_col)
        gantt = do_dash_graph('gantt')

        dropdown_id = html.Div(children=[html.Div(children='ID', className='menu-title'),
                                         do_dropdown('id', 'dropdown_id')])

        dropdown_assignee = html.Div(children=[html.Div(children='Assignee', className='menu-title'),
                                               do_dropdown('Assignee', 'dropdown_assignee')])

        daterange_start = html.Div(children=[html.Div(children='Start date', className='menu-title'),
                                             do_daterange_picker(start_col, 'daterange_start',
                                                                 start_default, end_default)])

        # menus = html.Div(children=[dropdown_id, dropdown_assignee, daterange_start], className="menu")
        menus = html.Div(children=[dropdown_id, daterange_start], className="menu")

        _layout = html.Div(children=[html.Div(children=[title, title_description], className="header"), menus, gantt])
        return _layout

    external_stylesheets = [{"href": "https://fonts.googleapis.com/css2?"
                                     "family=Lato:wght@400;700&display=swap",
                             "rel": "stylesheet", }, ]

    _app = dash.Dash(external_stylesheets=external_stylesheets)
    _app.title = "My first app"

    _app.layout = create_app_layout(start_col, end_col, y_col, color_col, start_default, end_default)

    @_app.callback(
        Output("gantt", "figure"),
        [Input("dropdown_id", "value"),
         Input("daterange_start", "start_date"),
         Input("daterange_start", "end_date"),
         ]
    )
    def update_charts(ids, start_date, end_date):
        if not ids:
            ids = df['id']
        mask = (
                (df['id'].isin(ids))
                & (df['Start'] >= start_date)
                & (df['Start'] <= end_date)
        )

        filtered_df = df.loc[mask, :]
        y = [str(i) for i in filtered_df['id']]
        trace = px.timeline(filtered_df, x_start='Start', x_end='End', y=y, color='Type', text='Name')
        trace.update_layout(transition_duration=500)
        print(start_date, end_date, len(filtered_df), ids)

        trace.update_xaxes(
        #    dtick="d7",  # display x-ticks every 24 months months
            tickformat="%Y-%m-%d"  # date format
        )
        return trace

    return _app


if __name__ == "__main__":
    df = create_fake_df('MOCK_DATA.csv')
    today = date.today()
#    app = create_app('Start', 'End', 'id', 'Assignee',
#                     start_default= datetime.date(today.year, today.month-1, 1),
#                     end_default= datetime.date(today.year, today.month+2, 1) - timedelta(1))
    app = create_app('Start', 'End', 'id', 'Assignee', start_default=datetime.date(2015,6,1), end_default=datetime.date(2015,12,31))
    app.run_server()
pass
