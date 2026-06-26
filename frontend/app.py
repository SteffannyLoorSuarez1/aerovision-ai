import os
from nicegui import ui, app

app.add_static_files(
    '/static',
    'static'
)
import requests
import pages.login
import pages.register
import pages.shipments

API_URL = 'http://backend:8000'



rows = []

# =====================================================
# GLOBAL STYLE
# =====================================================
ui.add_head_html("""

<script
    type="text/javascript"
    src="https://www.gstatic.com/charts/loader.js">
</script>
<link
    rel="stylesheet"
    href="/static/leaflet/leaflet.css"
/>

<script
    src="/static/leaflet/leaflet.js">
</script>

<style>

body {

    margin: 0;
    padding: 0;

    background:
        linear-gradient(
            135deg,
            #020617,
            #0f172a,
            #111827
        );

    color: white;

    overflow-x: hidden;
}

/* =========================
SIDEBAR
========================= */

.sidebar {

    background: rgba(15,23,42,0.95);

    backdrop-filter: blur(16px);

    border-radius: 28px;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.5);

    padding: 24px;

    position: fixed;

    left: 15px;
    top: 15px;

    width: 280px;

    height: 94vh;

    z-index: 999;
}

/* =========================
MAIN CONTENT
========================= */

.main-content {

    margin-left: 330px;

    width: calc(100% - 360px);

    padding: 25px;
}

/* =========================
CARDS
========================= */

.main-card {

    background: rgba(255,255,255,0.05);

    backdrop-filter: blur(12px);

    border-radius: 28px;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.35);

    padding: 24px;
}

.kpi-card {

    background: rgba(255,255,255,0.05);

    border-radius: 24px;

    padding: 24px;

    min-width: 220px;

    flex: 1;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.3);

    transition: 0.3s;
}

.kpi-card:hover {

    transform: translateY(-5px);

    box-shadow:
        0 15px 40px rgba(59,130,246,0.3);
}

/* =========================
BUTTONS
========================= */

.sidebar-btn {

    width: 100%;

    margin-top: 14px;

    border-radius: 18px;

    padding: 14px;

    background: linear-gradient(
        135deg,
        #2563eb,
        #3b82f6
    );

    color: white;

    font-weight: bold;

    transition: 0.3s;
}

.sidebar-btn:hover {

    transform: scale(1.03);
}

/* =========================
TEXTS
========================= */

.title {

    font-size: 52px;

    font-weight: bold;
}

.subtitle {

    font-size: 22px;

    color: #cbd5e1;
}

.kpi-title {

    font-size: 14px;

    color: #cbd5e1;
}

.kpi-value {

    font-size: 38px;

    font-weight: bold;
}

.section-title {

    font-size: 32px;

    font-weight: bold;
}

/* =========================
TABLES
========================= */

.q-table {

    background: rgba(15,23,42,0.95) !important;

    color: white !important;

    border-radius: 22px !important;

    overflow: hidden;
}

.q-table th {

    background: #1e293b !important;

    color: #93c5fd !important;

    font-size: 14px;
}

.q-table td {

    color: white !important;
}

.q-table__bottom {

    background: #0f172a !important;

    color: white !important;
}

/* =========================
INPUTS
========================= */

.q-field input {

    color: white !important;

    font-weight: 500;
}

.q-field__native {

    color: white !important;
}

.q-field__label {

    color: #93c5fd !important;
}

.q-field--filled .q-field__control {

    background: rgba(255,255,255,0.08) !important;

    border: 1px solid rgba(255,255,255,0.08);
}

.q-field__control {

    border-radius: 18px !important;

    background: rgba(255,255,255,0.05) !important;
}

.q-field__control:before {

    border-bottom: 1px solid #3b82f6 !important;
}

.q-field__control:hover {

    border-color: #60a5fa !important;
}

.admin-shipments-status-menu {

    z-index: 10000 !important;

    color: #0f172a !important;
}

</style>

""", shared=True)

# =====================================================
# API FUNCTIONS
# =====================================================

def get_total_flights():

    return requests.get(
        f'{API_URL}/warehouse/flights/count'
    ).json()['count']


def get_total_airlines():

    return requests.get(
        f'{API_URL}/warehouse/airlines/count'
    ).json()['count']


def get_avg_delay():

    return requests.get(
        f'{API_URL}/warehouse/delays/avg'
    ).json()['avg_delay']


def get_cancelled_count():

    return requests.get(
        f'{API_URL}/warehouse/cancelled/count'
    ).json()['count']


def get_airline_kpis():

    return requests.get(
        f'{API_URL}/warehouse/kpi/airlines'
    ).json()['data']

def get_airports():

    return requests.get(
        f'{API_URL}/airports/'
    ).json()['data']

def get_top_airports():

    response = requests.get(
        f'{API_URL}/warehouse/kpi/airports'
    )

    return response.json()['data']

def get_top_routes():

    response = requests.get(
        f'{API_URL}/warehouse/kpi/routes'
    )

    return response.json()['data']

def get_best_airlines():

    response = requests.get(
        f'{API_URL}/warehouse/kpi/punctuality'
    )

    return response.json()['data']

def get_cancelled_airlines():

    response = requests.get(
        f'{API_URL}/warehouse/kpi/cancellations'
    )

    return response.json()['data']
# =====================================================
# ROUTES API
# =====================================================

def get_routes():

    response = requests.get(
        f'{API_URL}/routes'
    )

    return response.json()['data']

def get_aircraft():

    response = requests.get(
        f'{API_URL}/aircraft'
    )

    return response.json()['data']
# =====================================================
# AIRLINES CRUD
# =====================================================

def load_airlines():

    response = requests.get(
        f'{API_URL}/airlines/'
    )

    data = response.json()['data']

    rows.clear()

    for airline in data[:30]:

        rows.append({

            'airline_key': airline[0],
            'reporting_airline': airline[1],
            'dot_id': airline[2],
            'iata_code': airline[3],

        })

    table.update()


def create_airline():

    payload = {

        'reporting_airline': reporting_airline.value,
        'dot_id': int(dot_id.value),
        'iata_code': iata_code.value

    }

    response = requests.post(
        f'{API_URL}/airlines/',
        json=payload
    )

    ui.notify(
        response.json()['message'],
        color='positive'
    )

    reporting_airline.value = ''
    dot_id.value = ''
    iata_code.value = ''

    load_airlines()

# =====================================================
# MAIN CONTENT
# =====================================================

content = None  # set inside main_page()

# =====================================================
# DASHBOARD
# =====================================================

def show_dashboard():

    content.clear()

    total_flights = get_total_flights()
    total_airlines = get_total_airlines()
    avg_delay = get_avg_delay()
    cancelled_count = get_cancelled_count()
    kpis = get_airline_kpis()

    with content:

        ui.label(
            '✈ Enterprise Aviation Warehouse'
        ).classes('title')

        ui.label(
            'Business Intelligence and Big Data Analytics'
        ).classes('subtitle')

        ui.separator()

        with ui.row().classes('w-full').style(
            '''
            gap:20px;
            flex-wrap:nowrap;
            '''
        ):

            cards = [

                ('✈ Total Flights', f'{total_flights:,}', 'white'),
                ('⏱ Average Delay', f'{avg_delay} min', '#facc15'),
                ('❌ Cancelled Flights', f'{cancelled_count:,}', '#fb7185'),
                ('📊 Airlines', str(total_airlines), '#60a5fa')

            ]

            for title, value, color in cards:

                with ui.card().classes('kpi-card'):

                    ui.label(title).classes('kpi-title')

                    ui.label(value).classes(
                        'kpi-value'
                    ).style(
                        f'color:{color}'
                    )

        ui.separator()

        with ui.card().classes('main-card w-full'):

            ui.label(
                '📊 KPI Airlines'
            ).classes('section-title')

            columns = [

                {
                    'name': 'airline',
                    'label': 'Airline',
                    'field': 'airline'
                },

                {
                    'name': 'flights',
                    'label': 'Flights',
                    'field': 'flights'
                },

                {
                    'name': 'delay',
                    'label': 'Avg Delay',
                    'field': 'delay'
                }

            ]

            kpi_rows = []

            for item in kpis:

                kpi_rows.append({

                    'airline': item[0],
                    'flights': item[1],
                    'delay': item[2]

                })

            ui.table(
                columns=columns,
                rows=kpi_rows,
                pagination=5
            ).classes('w-full')

        # ==========================================
        # AI EXECUTIVE INSIGHTS
        # ==========================================

        insights = requests.get(
            f'{API_URL}/warehouse/insights'
        ).json()

        ui.separator()

        with ui.card().classes('main-card w-full'):

            ui.label(
                '🤖 AI Executive Insights'
            ).classes('section-title')
            for item in insights['insights']:

                with ui.card().style(
                    '''
                    background: rgba(255,255,255,0.03);
                    border-left: 4px solid #60a5fa;
                    margin-top:10px;
                    padding:10px;
                    '''
                ):

                    ui.label(item).style(
                        '''
                        font-size:18px;
                        color:white;
                        '''
                    )
        # ==========================================
        # TOP AIRPORTS
        # ==========================================

        airports = get_top_airports()

        ui.separator()
        # ==========================================
        # TOP AIRPORTS + TOP ROUTES
        # ==========================================

        airports = get_top_airports()
        routes = get_top_routes()

        ui.separator()

        with ui.row().classes('w-full').style(
            '''
            gap:20px;
            align-items:stretch;
            '''
        ):

            # ==========================
            # TOP AIRPORTS
            # ==========================

            with ui.card().classes(
                'main-card'
            ).style(
                'flex:1'
            ):

                ui.label(
                    '📊 Top Airports by Traffic'
                ).classes('section-title')
                chart_data = {

                    'tooltip': {
                        'trigger': 'axis'
                    },

                    'xAxis': {

                        'type': 'category',

                        'data': [
                            airport[0]
                            for airport in airports
                        ],

                        'axisLabel': {
                            'color': '#ffffff',
                            'fontSize': 14
                        },

                        'axisLine': {
                            'lineStyle': {
                                'color': '#ffffff'
                            }
                        }
                    },

                    'yAxis': {

                        'type': 'value',

                        'axisLabel': {
                            'color': '#ffffff',
                            'fontSize': 14
                        },

                        'axisLine': {
                            'lineStyle': {
                                'color': '#ffffff'
                            }
                        },

                        'splitLine': {
                            'lineStyle': {
                                'color': 'rgba(255,255,255,0.15)'
                            }
                        }
                    },

                    'series': [

                        {

                            'data': [
                                airport[1]
                                for airport in airports
                            ],

                            'type': 'bar',

                            'showBackground': True,

                            'itemStyle': {
                                'color': '#60a5fa'
                            },

                            'label': {
                                'show': True,
                                'position': 'top',
                                'color': '#ffffff'
                            }

                        }

                    ]

                }

                ui.echart(
                    chart_data
                ).style(
                    'height:500px'
                )

            # ==========================
            # TOP ROUTES
            # ==========================

            with ui.card().classes(
                'main-card'
            ).style(
                'flex:1'
            ):

                ui.label(
                    '📈 Top Routes'
                ).classes('section-title')

                route_labels = [

                    f'{r[0]}-{r[1]}'
                    for r in routes

                ]

                route_values = [

                    r[2]
                    for r in routes

                ]

                route_chart = {

                    'tooltip': {
                        'trigger': 'axis'
                    },

                    'xAxis': {

                        'type': 'category',

                        'data': route_labels,

                        'axisLabel': {

                            'color': '#ffffff',

                            'fontSize': 12,

                            'rotate': 45
                        },

                        'axisLine': {
                            'lineStyle': {
                                'color': '#ffffff'
                            }
                        }
                    },

                    'yAxis': {

                        'type': 'value',

                        'axisLabel': {
                            'color': '#ffffff',
                            'fontSize': 14
                        },

                        'axisLine': {
                            'lineStyle': {
                                'color': '#ffffff'
                            }
                        },

                        'splitLine': {
                            'lineStyle': {
                                'color': 'rgba(255,255,255,0.15)'
                            }
                        }
                    },

                    'series': [

                        {

                            'data': route_values,

                            'type': 'bar',

                            'showBackground': True,

                            'itemStyle': {
                                'color': '#34d399'
                            },

                            'label': {
                                'show': True,
                                'position': 'top',
                                'color': '#ffffff'
                            }

                        }

                    ]

                }

                ui.echart(
                    route_chart
                ).style(
                    'height:500px'
                )
        # ==========================================
        # BEST AIRLINES + CANCELLATIONS
        # ==========================================

        best_airlines = get_best_airlines()
        cancelled_airlines = get_cancelled_airlines()

        ui.separator()

        with ui.row().classes('w-full').style(
            '''
            gap:20px;
            align-items:stretch;
            '''
        ):

            # ==================================
            # BEST AIRLINES
            # ==================================

            with ui.card().classes(
                'main-card'
            ).style(
                'flex:1'
            ):

                ui.label(
                    '🏆 Best Airlines'
                ).classes('section-title')

                best_chart = {

                    'tooltip': {
                        'trigger': 'axis'
                    },

                    'xAxis': {

                        'type': 'category',

                        'data': [
                            row[0]
                            for row in best_airlines
                        ],

                        'axisLabel': {
                            'color': '#ffffff',
                            'fontSize': 14
                        }
                    },

                    'yAxis': {

                        'type': 'value',

                        'axisLabel': {
                            'color': '#ffffff'
                        }
                    },

                    'series': [

                        {

                            'data': [
                                row[1]
                                for row in best_airlines
                            ],

                            'type': 'bar',

                            'itemStyle': {
                                'color': '#22c55e'
                            },

                            'label': {
                                'show': True,
                                'position': 'top',
                                'color': '#ffffff'
                            }
                        }

                    ]

                }

                ui.echart(
                    best_chart
                ).style(
                    'height:500px'
                )

            # ==================================
            # CANCELLATIONS
            # ==================================

            with ui.card().classes(
                'main-card'
            ).style(
                'flex:1'
            ):

                ui.label(
                    '🚨 Airline Cancellations'
                ).classes('section-title')

                cancel_chart = {

                    'tooltip': {
                        'trigger': 'axis'
                    },

                    'xAxis': {

                        'type': 'category',

                        'data': [
                            row[0]
                            for row in cancelled_airlines
                        ],

                        'axisLabel': {
                            'color': '#ffffff',
                            'fontSize': 14
                        }
                    },

                    'yAxis': {

                        'type': 'value',

                        'axisLabel': {
                            'color': '#ffffff'
                        }
                    },

                    'series': [

                        {

                            'data': [
                                row[1]
                                for row in cancelled_airlines
                            ],

                            'type': 'bar',

                            'itemStyle': {
                                'color': '#ef4444'
                            },

                            'label': {
                                'show': True,
                                'position': 'top',
                                'color': '#ffffff'
                            }
                        }

                    ]

                }

                ui.echart(
                    cancel_chart
                ).style(
                    'height:500px'
                )
# =====================================================
# AIRLINES CRUD FUNCTIONS
# =====================================================

def delete_airline(airline_key):

    response = requests.delete(
        f'{API_URL}/airlines/{airline_key}'
    )

    ui.notify(
        response.json()['message'],
        color='negative'
    )

    show_airlines()

# =====================================================
# AIRLINES PAGE
# =====================================================

def show_airlines():

    content.clear()

    with content:

        ui.label(
            '✈ Airlines Management'
        ).classes('title')

        ui.label(
            'Enterprise CRUD Module'
        ).classes('subtitle')

        ui.separator()

        global reporting_airline
        global dot_id
        global iata_code

        with ui.card().classes('main-card w-full'):

            with ui.row().style(
                'gap:15px; flex-wrap:wrap'
            ):

                reporting_airline = ui.input(
                    label='Reporting Airline'
                ).props('filled')

                dot_id = ui.input(
                    label='DOT ID'
                ).props('filled')

                iata_code = ui.input(
                    label='IATA Code'
                ).props('filled')

                ui.button(
                    'Create Airline',
                    on_click=create_airline
                ).classes('sidebar-btn').style(
                    'width:220px'
                )

            ui.separator()

            search = ui.input(
                label='Search airline...'
            ).props('filled').classes('w-full')

            ui.separator()

            response = requests.get(
                f'{API_URL}/airlines/'
            )

            data = response.json()['data']

            airline_rows = []

            for airline in data:

                airline_rows.append({

                    'airline_key': airline[0],
                    'reporting_airline': airline[1],
                    'dot_id': airline[2],
                    'iata_code': airline[3]

                })

            airline_columns = [

                {
                    'name': 'airline_key',
                    'label': 'ID',
                    'field': 'airline_key'
                },

                {
                    'name': 'reporting_airline',
                    'label': 'Airline',
                    'field': 'reporting_airline'
                },

                {
                    'name': 'dot_id',
                    'label': 'DOT ID',
                    'field': 'dot_id'
                },

                {
                    'name': 'iata_code',
                    'label': 'IATA',
                    'field': 'iata_code'
                },

                {
                    'name': 'actions',
                    'label': 'Actions',
                    'field': 'actions'
                }

            ]

            table = ui.table(
                columns=airline_columns,
                rows=airline_rows,
                pagination=10
            ).classes('w-full')

            def filter_table():

                text = search.value.lower()

                if text == '':

                    table.rows = airline_rows
                    table.update()

                    return

                filtered = []

                for row in airline_rows:

                    if (

                        text in str(
                            row['reporting_airline']
                        ).lower()

                        or

                        text in str(
                            row['iata_code']
                        ).lower()

                        or

                        text in str(
                            row['dot_id']
                        ).lower()

                    ):

                        filtered.append(row)

                table.rows = filtered
                table.update()

            search.on(
                'update:model-value',
                lambda e:
                filter_table()
            )

            table.add_slot(
                'body-cell-actions',
                '''
                <q-td :props="props">

                    <q-btn
                        color="red"
                        icon="delete"
                        size="sm"
                        @click="$parent.$emit('delete', props.row.airline_key)"
                    />

                </q-td>
                '''
            )

            table.on(
                'delete',
                lambda e:
                delete_airline(
                    e.args
                )
            )

# =====================================================
# AIRPORTS PAGE
# =====================================================

def create_airport():

    payload = {

        'airport_id': airport_id.value,
        'airport_code': airport_code.value,
        'city_name': city_name.value,
        'state_name': state_name.value

    }

    response = requests.post(
        f'{API_URL}/airports/',
        json=payload
    )

    ui.notify(
        response.json()['message'],
        color='positive'
    )

    show_airports()

def delete_airport(airport_key):

    response = requests.delete(
        f'{API_URL}/airports/{airport_key}'
    )

    ui.notify(
        response.json()['message'],
        color='negative'
    )

    show_airports()

# =====================================================
# ROUTES CRUD
# =====================================================

def create_route():

    payload = {

        'origin_code': origin_code.value,
        'destination_code': destination_code.value,
        'avg_distance': float(
            avg_distance.value
        )

    }

    response = requests.post(
        f'{API_URL}/routes',
        json=payload
    )

    ui.notify(
        response.json()['message'],
        color='positive'
    )

    show_routes()


def delete_route(route_key):

    response = requests.delete(
        f'{API_URL}/routes/{route_key}'
    )

    ui.notify(
        response.json()['message'],
        color='negative'
    )

    show_routes()


def create_aircraft():

    payload = {

        'tail_number':
        tail_number.value,

        'aircraft_type':
        aircraft_type.value,

        'manufacturer':
        manufacturer.value,

        'status':
        status.value

    }

    requests.post(
        f'{API_URL}/aircraft',
        json=payload
    )

    show_aircraft()


def delete_aircraft(aircraft_key):

    requests.delete(
        f'{API_URL}/aircraft/{aircraft_key}'
    )

    show_aircraft()


# =====================================================
# AIRPORTS PAGE
# =====================================================

def show_airports():

    content.clear()

    with content:

        ui.label(
            '🛫 Airports Management'
        ).classes('title')

        ui.label(
            'Enterprise Airports Module'
        ).classes('subtitle')

        ui.separator()

        global airport_id
        global airport_code
        global city_name
        global state_name

        with ui.card().classes('main-card w-full'):

            with ui.row().style(
                '''
                gap:15px;
                flex-wrap:wrap;
                '''
            ):

                airport_id = ui.input(
                    label='Airport ID'
                ).props(
                    'filled'
                )

                airport_code = ui.input(
                    label='Airport Code'
                ).props(
                    'filled'
                )

                city_name = ui.input(
                    label='City Name'
                ).props(
                    'filled'
                )

                state_name = ui.input(
                    label='State Name'
                ).props(
                    'filled'
                )

                ui.button(
                    'Create Airport',
                    on_click=create_airport
                ).classes(
                    'sidebar-btn'
                ).style(
                    'width:220px'
                )

            ui.separator()

            search = ui.input(
                placeholder='Search airport...'
            ).props(
                'filled'
            ).classes(
                'w-full'
            )

            ui.separator()

            airports = get_airports()

            airport_rows = []

            for airport in airports:

                airport_rows.append({

                    'airport_key': airport[0],
                    'airport_id': airport[1],
                    'airport_code': airport[2],
                    'city_name': airport[3],
                    'state_name': airport[4]

                })

            airport_columns = [

                {
                    'name': 'airport_key',
                    'label': 'ID',
                    'field': 'airport_key'
                },

                {
                    'name': 'airport_id',
                    'label': 'Airport ID',
                    'field': 'airport_id'
                },

                {
                    'name': 'airport_code',
                    'label': 'Code',
                    'field': 'airport_code'
                },

                {
                    'name': 'city_name',
                    'label': 'City',
                    'field': 'city_name'
                },

                {
                    'name': 'state_name',
                    'label': 'State',
                    'field': 'state_name'
                },

                {
                    'name': 'actions',
                    'label': 'Actions',
                    'field': 'actions'
                }

            ]

            table = ui.table(
                columns=airport_columns,
                rows=airport_rows,
                pagination=10
            ).classes(
                'w-full'
            )

            search.bind_value(
                table,
                'filter'
            )

            table.add_slot(
                'body-cell-actions',
                '''
                <q-td :props="props">

                    <q-btn
                        color="red"
                        icon="delete"
                        size="sm"
                        @click="$parent.$emit('delete', props.row.airport_key)"
                    />

                </q-td>
                '''
            )

            table.on(
                'delete',
                lambda e:
                delete_airport(
                    e.args
                )
            )
# =====================================================
# ROUTES PAGE
# =====================================================

# =====================================================
# ROUTES PAGE
# =====================================================

# =====================================================
# ROUTES PAGE
# =====================================================

def show_routes():

    content.clear()

    with content:

        ui.label(
            '🛣 Routes Management'
        ).classes('title')

        ui.label(
            'Enterprise Routes Module'
        ).classes('subtitle')

        ui.separator()

        global origin_code
        global destination_code
        global avg_distance

        with ui.card().classes('main-card w-full'):

            with ui.row().style(
                '''
                gap:15px;
                align-items:center;
                flex-wrap:wrap;
                '''
            ):

                origin_code = ui.input(
                    label='Origin Airport'
                ).props(
                    'filled'
                ).classes(
                    'w-48'
                )

                destination_code = ui.input(
                    label='Destination Airport'
                ).props(
                    'filled'
                ).classes(
                    'w-48'
                )

                avg_distance = ui.input(
                    label='Average Distance'
                ).props(
                    'filled'
                ).classes(
                    'w-48'
                )

                ui.button(
                    'CREATE ROUTE',
                    on_click=create_route
                ).classes(
                    'sidebar-btn'
                ).style(
                    'width:220px'
                )

            ui.separator()

            search_route = ui.input(
                placeholder='Search route...'
            ).props(
                'filled'
            ).classes(
                'w-full'
            )

            routes = get_routes()

            route_rows = []

            for route in routes:

                route_rows.append({

                    'route_key': route[0],
                    'origin_code': route[1],
                    'destination_code': route[2],
                    'avg_distance': route[3]

                })

            route_columns = [

                {
                    'name': 'route_key',
                    'label': 'ID',
                    'field': 'route_key'
                },

                {
                    'name': 'origin_code',
                    'label': 'Origin',
                    'field': 'origin_code'
                },

                {
                    'name': 'destination_code',
                    'label': 'Destination',
                    'field': 'destination_code'
                },

                {
                    'name': 'avg_distance',
                    'label': 'Distance',
                    'field': 'avg_distance'
                },

                {
                    'name': 'actions',
                    'label': 'Actions',
                    'field': 'actions'
                }

            ]

            table = ui.table(
                columns=route_columns,
                rows=route_rows,
                pagination=10
            ).classes(
                'w-full'
            )

            search_route.bind_value(
                table,
                'filter'
            )

            table.add_slot(
                'body-cell-actions',
                '''
                <q-td :props="props">

                    <q-btn
                        color="red"
                        icon="delete"
                        size="sm"
                        @click="$parent.$emit('delete', props.row.route_key)"
                    />

                </q-td>
                '''
            )

            table.on(
                'delete',
                lambda e:
                delete_route(
                    e.args
                )
            )

# =====================================================
# AIRCRAFT PAGE
# =====================================================

def show_aircraft():

    content.clear()

    with content:

        ui.label(
            '✈ Aircraft Management'
        ).classes('title')

        ui.label(
            'Enterprise Aircraft Module'
        ).classes('subtitle')

        ui.separator()

        global tail_number
        global aircraft_type
        global manufacturer
        global status

        with ui.card().classes('main-card w-full'):

            with ui.row().style(
                '''
                gap:15px;
                align-items:center;
                flex-wrap:wrap;
                '''
            ):

                tail_number = ui.input(
                    label='Tail Number'
                ).props(
                    'filled'
                ).classes(
                    'w-48'
                )

                aircraft_type = ui.input(
                    label='Aircraft Type'
                ).props(
                    'filled'
                ).classes(
                    'w-48'
                )

                manufacturer = ui.input(
                    label='Manufacturer'
                ).props(
                    'filled'
                ).classes(
                    'w-48'
                )

                status = ui.input(
                    label='Status'
                ).props(
                    'filled'
                ).classes(
                    'w-48'
                )

                ui.button(
                    'CREATE AIRCRAFT',
                    on_click=create_aircraft
                ).classes(
                    'sidebar-btn'
                ).style(
                    'width:220px'
                )

            ui.separator()

            search_aircraft = ui.input(
                placeholder='Search aircraft...'
            ).props(
                'filled'
            ).classes(
                'w-full'
            )

            aircrafts = get_aircraft()

            aircraft_rows = []

            for aircraft in aircrafts:

                aircraft_rows.append({

                    'aircraft_key': aircraft[0],
                    'tail_number': aircraft[1],
                    'aircraft_type': aircraft[2],
                    'manufacturer': aircraft[3],
                    'status': aircraft[4]

                })

            aircraft_columns = [

                {
                    'name': 'aircraft_key',
                    'label': 'ID',
                    'field': 'aircraft_key'
                },

                {
                    'name': 'tail_number',
                    'label': 'Tail Number',
                    'field': 'tail_number'
                },

                {
                    'name': 'aircraft_type',
                    'label': 'Aircraft Type',
                    'field': 'aircraft_type'
                },

                {
                    'name': 'manufacturer',
                    'label': 'Manufacturer',
                    'field': 'manufacturer'
                },

                {
                    'name': 'status',
                    'label': 'Status',
                    'field': 'status'
                },

                {
                    'name': 'actions',
                    'label': 'Actions',
                    'field': 'actions'
                }

            ]

            table = ui.table(
                columns=aircraft_columns,
                rows=aircraft_rows,
                pagination=10
            ).classes(
                'w-full'
            )

            search_aircraft.bind_value(
                table,
                'filter'
            )

            table.add_slot(
                'body-cell-actions',
                '''
                <q-td :props="props">

                    <q-btn
                        color="red"
                        icon="delete"
                        size="sm"
                        @click="$parent.$emit('delete', props.row.aircraft_key)"
                    />

                </q-td>
                '''
            )

            table.on(
                'delete',
                lambda e:
                delete_aircraft(
                    e.args
                )
            )

# =====================================================
# FLIGHT MAP
# =====================================================

def show_flight_map():

    content.clear()

    with content:

        ui.label(
            '🗺️ Flight Operations Map'
        ).classes('title')

        ui.label(
            'Real-time operational visualization'
        ).classes('subtitle')

        ui.separator()


        airports = requests.get(
            f'{API_URL}/warehouse/geo/airports'
        ).json()['data']

        rows_js = ""

        for airport in airports:

            lat = airport.get('lat')
            lon = airport.get('lon')
            city = airport.get('city')
            code = airport.get('code')

            if lat is None or lon is None:
                continue

            rows_js += f"""
                [
                    {lat},
                    {lon},
                    '{code} - {city}'
                ],
            """

        ui.html("""

        <div
            id="geo_map"
            style="
                width:100%;
                height:700px;
                border-radius:24px;
                overflow:hidden;
                background:#020617;
            ">
        </div>

        """)

        ui.timer(
            1.5,
            lambda:
            ui.run_javascript(f"""

                if (typeof google !== 'undefined') {{

                    google.charts.load(
                        'current',
                        {{
                            packages:['geochart']
                        }}
                    );

                    google.charts.setOnLoadCallback(drawMap);

                    function drawMap() {{

                        var data =
                            google.visualization.arrayToDataTable([
                                ['Lat', 'Lon', 'Airport'],
                                {rows_js}
                            ]);

                        var options = {{

                            region: 'US',

                            displayMode: 'markers',

                            backgroundColor: '#020617',

                            datalessRegionColor: '#111827',

                            defaultColor: '#60a5fa',

                            legend: 'none'
                        }};

                        var chart =
                            new google.visualization.GeoChart(
                                document.getElementById(
                                    'geo_map'
                                )
                            );

                        chart.draw(data, options);
                    }}

                }}

            """),
            once=True
        )


# =====================================================
# OPERATIONS CENTER
# =====================================================
# =====================================================
# OPERATIONS CENTER
# =====================================================
def show_operations_center():

    content.clear()

    with content:

        ui.label(
            '🛫 Operations Center'
        ).classes('title')

        ui.label(
            'Flight Routes Analytics'
        ).classes('subtitle')

        ui.separator()

        routes = requests.get(
            f'{API_URL}/operations/routes'
        ).json()['data']

        routes_js = ""

        for route in routes[:50]:

            if (
                route.get('origin_lat') is None or
                route.get('origin_lon') is None or
                route.get('dest_lat') is None or
                route.get('dest_lon') is None
            ):
                continue

            routes_js += f"""
            [
                [{route['origin_lat']}, {route['origin_lon']}],
                [{route['dest_lat']}, {route['dest_lon']}],
                '{route['Origin']} → {route['Dest']}',
                {route['flights']}
            ],
            """

        ui.label(
            f'Rutas analizadas: {len(routes)}'
        ).style(
            'font-size:20px;color:#60a5fa'
        )

        with ui.row().classes('w-full'):

            with ui.card().classes('kpi-card'):

                ui.label('🛫 Total rutas')

                ui.label(
                    str(len(routes))
                ).classes('kpi-value')

            with ui.card().classes('kpi-card'):

                ui.label('✈ Ruta principal')

                ui.label(
                    f"{routes[0]['Origin']} → {routes[0]['Dest']}"
                )

            with ui.card().classes('kpi-card'):

                ui.label('📊 Máximo tráfico')

                ui.label(
                    str(routes[0]['flights'])
                ).classes('kpi-value')

        ui.separator()

        with ui.card().classes('w-full').style(
            'width:100%; min-width:1200px;'
        ):

            ui.html("""

            <div
                id="routes_map"
                style="
                    width:1200px;
                    min-width:1200px;
                    height:600px;
                    border-radius:24px;
                    overflow:hidden;
                    background:#111827;
                ">
            </div>

            """)

        ui.timer(
            2,
            lambda: ui.run_javascript(f"""

                if (typeof L !== 'undefined') {{

                    const div =
                        document.getElementById(
                            'routes_map'
                        );

                    console.log(
                        'WIDTH:',
                        div.offsetWidth
                    );

                    console.log(
                        'HEIGHT:',
                        div.offsetHeight
                    );

                    const map = L.map(
                        'routes_map'
                    ).setView(
                        [39.5, -98.35],
                        4
                    );

                    setTimeout(() => {{
                        map.invalidateSize();
                    }}, 1000);

                    L.tileLayer(
                        'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
                        {{
                            maxZoom: 19,
                            attribution: '© OpenStreetMap',
                            subdomains: ['a', 'b', 'c']
                        }}
                    ).addTo(map);

                    console.log(
                        'TileLayer loaded'
                    );

                    const routes = [
                        {routes_js}
                    ];

                    console.log(routes);

                    routes.forEach(route => {{

                        L.marker(
                            route[0]
                        ).addTo(map);

                        L.marker(
                            route[1]
                        ).addTo(map);

                        L.polyline(
                            [
                                route[0],
                                route[1]
                            ],
                            {{
                                color: '#00e5ff',
                                weight: 1,
                                opacity: 0.4
                            }}
                        )
                        .bindPopup(
                            route[2] +
                            '<br>Flights: ' +
                            route[3]
                        )
                        .addTo(map);

                    }});

                    const bounds = [];

                    routes.forEach(route => {{

                        bounds.push(
                            route[0]
                        );

                        bounds.push(
                            route[1]
                        );

                    }});

                    map.fitBounds(
                        bounds
                    );

                }}

            """),
            once=True
        )

        route_rows = []

        for route in routes:

            route_rows.append({

                'origin': route['Origin'],
                'dest': route['Dest'],
                'flights': route['flights'],
                'avg_delay': round(
                    route['avg_delay'],
                    2
                )

            })

        columns = [

            {
                'name': 'origin',
                'label': 'Origen',
                'field': 'origin'
            },

            {
                'name': 'dest',
                'label': 'Destino',
                'field': 'dest'
            },

            {
                'name': 'flights',
                'label': 'Vuelos',
                'field': 'flights'
            },

            {
                'name': 'avg_delay',
                'label': 'Retraso Prom.',
                'field': 'avg_delay'
            }

        ]

        ui.table(
            columns=columns,
            rows=route_rows,
            pagination=20
        ).classes('w-full')
# =====================================================
# WAREHOUSE PAGE
# =====================================================

def show_warehouse():

    content.clear()

    with content:

        ui.label(
            '🗄 Enterprise Warehouse'
        ).classes('title')

        ui.label(
            'DuckDB Analytical Engine'
        ).classes('subtitle')

        ui.separator()

        warehouse_rows = [

            {
                'table': 'raw_flights',
                'type': 'RAW',
                'records': '1,970,147'
            },

            {
                'table': 'dim_airline',
                'type': 'DIMENSION',
                'records': '33'
            },

            {
                'table': 'dim_airport',
                'type': 'DIMENSION',
                'records': '500'
            },

            {
                'table': 'dim_airport_geo',
                'type': 'GEO DIMENSION',
                'records': '500'
            },

            {
                'table': 'dim_date',
                'type': 'DIMENSION',
                'records': '365'
            },

            {
                'table': 'fact_flights',
                'type': 'FACT',
                'records': '1,970,147'
            }

        ]

        warehouse_columns = [

            {
                'name': 'table',
                'label': 'Table',
                'field': 'table'
            },

            {
                'name': 'type',
                'label': 'Type',
                'field': 'type'
            },

            {
                'name': 'records',
                'label': 'Records',
                'field': 'records'
            }

        ]

        with ui.card().classes('main-card w-full'):

            ui.table(
                columns=warehouse_columns,
                rows=warehouse_rows,
                pagination=10
            ).classes('w-full')

# =====================================================
# IMPORT PAGE
# =====================================================

def show_import():

    content.clear()

    with content:

        ui.label(
            '📦 Import Dataset'
        ).classes('title')

        ui.label(
            'Airline On-Time Performance Dataset'
        ).classes('subtitle')

        ui.separator()

        with ui.card().classes('main-card'):

            ui.upload(
                label='Select CSV Dataset'
            )

            ui.separator()

            ui.button(
                'Import Dataset',
                on_click=lambda:
                ui.notify(
                    'Dataset imported successfully',
                    color='positive'
                )
            ).classes('sidebar-btn')

def show_shipments():
    from auth import get_current_user
    user = get_current_user()

    content.clear()

    with content:
        ui.label('📦 Mis Solicitudes de Envío').classes('title')
        ui.separator()

        with ui.card().classes('main-card'):
            ui.label('Nueva Solicitud').style(
                'font-size:18px; font-weight:bold; color:white; margin-bottom:16px'
            )

            origin_input      = ui.input(label='Origen').props('filled').classes('w-full')
            ui.space().style('height:8px')
            destination_input = ui.input(label='Destino').props('filled').classes('w-full')
            ui.space().style('height:8px')
            cargo_type_input  = ui.input(label='Tipo de carga').props('filled').classes('w-full')
            ui.space().style('height:8px')
            weight_input      = ui.number(
                label='Peso (kg)', min=0.01, format='%.2f'
            ).props('filled').classes('w-full')
            ui.space().style('height:8px')
            date_input        = ui.input(
                label='Fecha', placeholder='AAAA-MM-DD'
            ).props('type=date filled').classes('w-full')

            def do_create():
                try:
                    resp = requests.post(
                        f'{API_URL}/shipments/',
                        json={
                            'client_id':    user['user_id'],
                            'origin':       origin_input.value,
                            'destination':  destination_input.value,
                            'cargo_type':   cargo_type_input.value,
                            'weight_kg':    weight_input.value,
                            'request_date': date_input.value,
                        },
                        timeout=10
                    )
                    if resp.status_code == 201:
                        ui.notify('Solicitud de envío creada exitosamente', color='positive')
                        load_shipments()
                    else:
                        detail = resp.json().get('detail', 'Error al crear la solicitud')
                        ui.notify(detail, color='negative')
                except Exception:
                    ui.notify('No se pudo conectar con el servidor', color='negative')

            ui.button('Crear solicitud', on_click=do_create).classes('sidebar-btn')

        list_container = ui.column().style('margin-top:16px')

    def do_cancel(request_id: int):
        try:
            resp = requests.put(
                f'{API_URL}/shipments/{request_id}/cancel',
                json={'client_id': user['user_id']},
                timeout=10,
            )
            if resp.status_code == 200:
                ui.notify('Solicitud cancelada exitosamente', color='positive')
                load_shipments()
            else:
                detail = resp.json().get('detail', 'Error al cancelar la solicitud')
                ui.notify(detail, color='negative')
        except Exception:
            ui.notify('No se pudo conectar con el servidor', color='negative')

    def load_shipments():
        list_container.clear()
        with list_container:
            try:
                resp = requests.get(
                    f'{API_URL}/shipments/my',
                    params={'client_id': user['user_id']},
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()['data']
                    if not data:
                        ui.label('No tienes solicitudes de envío registradas.').style(
                            'color:#94a3b8; font-size:14px'
                        )
                    else:
                        columns = [
                            {'name': 'request_id',  'label': 'ID',        'field': 'request_id'},
                            {'name': 'origin',       'label': 'Origen',    'field': 'origin'},
                            {'name': 'destination',  'label': 'Destino',   'field': 'destination'},
                            {'name': 'cargo_type',   'label': 'Tipo',      'field': 'cargo_type'},
                            {'name': 'weight_kg',    'label': 'Peso (kg)', 'field': 'weight_kg'},
                            {'name': 'request_date', 'label': 'Fecha',     'field': 'request_date'},
                            {'name': 'status',       'label': 'Estado',    'field': 'status'},
                            {'name': 'actions',      'label': 'Acciones',  'field': 'actions'},
                        ]
                        table = ui.table(columns=columns, rows=data).classes('w-full')
                        table.add_slot('body-cell-actions', r'''
                            <q-td :props="props">
                                <q-btn
                                    v-if="props.row.status === 'Pendiente'"
                                    label="Cancelar"
                                    color="negative"
                                    size="sm"
                                    flat
                                    @click="$parent.$emit('cancel', props.row)"
                                />
                            </q-td>
                        ''')
                        table.on('cancel', lambda e: do_cancel(e.args['request_id']))
                else:
                    ui.notify('Error al cargar solicitudes', color='negative')
            except Exception:
                ui.notify('No se pudo conectar con el servidor', color='negative')

    load_shipments()

def show_admin_shipments():
    content.clear()

    with content:
        ui.label('📋 Gestión de Envíos').classes('title')
        ui.separator()

        try:
            resp = requests.get(
                f'{API_URL}/shipments/all',
                timeout=10,
            )
            if resp.status_code != 200:
                ui.notify('Error al cargar solicitudes', color='negative')
                return

            all_data = resp.json()['data']
        except Exception:
            ui.notify('No se pudo conectar con el servidor', color='negative')
            return

        if not all_data:
            ui.label('No hay solicitudes de envío registradas.').style(
                'color:#94a3b8; font-size:14px'
            )
            return

        with ui.card().classes('main-card w-full'):
            filter_select = ui.select(
                ['Todas', 'Pendiente', 'Cancelado'],
                value='Todas',
                label='Estado',
            ).props('filled popup-content-class=admin-shipments-status-menu').style('min-width:220px')

            empty_label = ui.label('').style(
                'color:#94a3b8; font-size:14px; margin-top:12px'
            )

            columns = [
                {'name': 'request_id',   'label': 'ID',            'field': 'request_id'},
                {'name': 'client_name',  'label': 'Cliente',       'field': 'client_name'},
                {'name': 'client_email', 'label': 'Email',         'field': 'client_email'},
                {'name': 'origin',       'label': 'Origen',        'field': 'origin'},
                {'name': 'destination',  'label': 'Destino',       'field': 'destination'},
                {'name': 'cargo_type',   'label': 'Tipo de carga', 'field': 'cargo_type'},
                {'name': 'weight_kg',    'label': 'Peso (kg)',     'field': 'weight_kg'},
                {'name': 'request_date', 'label': 'Fecha',         'field': 'request_date'},
                {'name': 'status',       'label': 'Estado',        'field': 'status'},
            ]

            table = ui.table(
                columns=columns,
                rows=[],
                pagination=10,
            ).classes('w-full')

            def apply_filter():
                selected = filter_select.value
                if selected == 'Todas':
                    filtered = all_data
                else:
                    filtered = [
                        row
                        for row in all_data
                        if row['status'] == selected
                    ]

                table.rows = filtered
                table.update()

                if not filtered:
                    empty_label.text = 'No hay solicitudes de envío registradas.'
                else:
                    empty_label.text = ''

            filter_select.on('update:model-value', lambda e: apply_filter())
            apply_filter()

# =====================================================
# MAIN PAGE
# =====================================================

@ui.page('/')
def main_page():
    global content
    from auth import check_auth, get_current_user, logout
    if not check_auth():
        ui.navigate.to('/login')
        return
    user = get_current_user()
    rol = user.get('rol', '')

    content = ui.column().classes('main-content')
    print("ROL:", rol)
    with ui.column().classes('sidebar'):

        ui.label(
            '✈ AeroVision AI'
        ).style(
            '''
            font-size:42px;
            font-weight:bold;
            color:#60a5fa;
            '''
        )

        ui.label(
            'Enterprise Big Data Platform'
        ).style(
            'color:#cbd5e1'
        )

        ui.separator()

        _b_dash = ui.button(
            '📊 Dashboard',
            on_click=show_dashboard
        ).classes('sidebar-btn')

        _b_wh = ui.button(
            '🗄 Warehouse',
            on_click=show_warehouse
        ).classes('sidebar-btn')

        _b_airl = ui.button(
            '✈ CRUD Aerolíneas',
            on_click=show_airlines
        ).classes('sidebar-btn')

        _b_airp = ui.button(
            '🛫 CRUD Airports',
            on_click=show_airports
        ).classes('sidebar-btn')

        _b_rout = ui.button(
            '🛣 CRUD Routes',
            on_click=show_routes
        ).classes('sidebar-btn')

        _b_airc = ui.button(
            '✈ CRUD AIRCRAFT',
            on_click=show_aircraft
        ).classes('sidebar-btn')

        _b_fmap = ui.button(
            '🗺️ Flight Map',
            on_click=show_flight_map
        ).classes('sidebar-btn')

        _b_ops = ui.button(
            '🛫 Operations Center',
            on_click=show_operations_center
        ).classes('sidebar-btn')

        _b_imp = ui.button(
            '📦 Import Dataset',
            on_click=show_import
        ).classes('sidebar-btn')

        _b_ship = ui.button(
            '📦 Mis Envíos',
            on_click=show_shipments
        ).classes('sidebar-btn')

        _b_admin_ship = ui.button(
            '📋 Gestión de Envíos',
            on_click=show_admin_shipments
        ).classes('sidebar-btn')

        ui.space()

        _b_dash.visible = rol in ('administrador', 'analista')
        _b_wh.visible   = rol == 'administrador'
        _b_airl.visible = rol == 'administrador'
        _b_airp.visible = rol == 'administrador'
        _b_rout.visible = rol == 'administrador'
        _b_airc.visible = rol == 'administrador'
        _b_fmap.visible = rol == 'administrador'
        _b_ops.visible  = rol == 'administrador'
        _b_imp.visible  = rol == 'administrador'
        _b_ship.visible = rol == 'cliente'
        _b_admin_ship.visible = rol in ('administrador', 'analista')

        ui.button(
            '🚪 Cerrar sesión',
            on_click=lambda: logout()
        ).classes('sidebar-btn').style(
            'background: linear-gradient(135deg, #dc2626, #ef4444)'
        )

        with ui.card().style(
            '''
            background:rgba(255,255,255,0.08);
            border-radius:24px;
            '''
        ):

            ui.label(
                '🤖 AI Analytics'
            ).style(
                'font-size:22px;font-weight:bold'
            )

            ui.label(
                'Advanced aviation operational analytics.'
            )

    show_dashboard()

ui.run(
    host='0.0.0.0',
    port=8080,
    storage_secret=os.environ.get('NICEGUI_STORAGE_SECRET', 'aerovision-dev-secret-2026')
)
