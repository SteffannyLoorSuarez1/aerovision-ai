import requests
from nicegui import ui, app
from auth import check_auth, get_current_user
from pages.login import AUTH_STYLES

API_URL = 'http://backend:8000'


@ui.page('/shipments')
def shipments_page():
    if not check_auth():
        ui.navigate.to('/login')
        return

    user = get_current_user()

    ui.add_head_html(AUTH_STYLES)

    with ui.column().classes('absolute-center items-center').style('gap:24px'):
        with ui.element('div').classes('auth-card'):

            ui.label('📦 Mis Solicitudes de Envío').style(
                'font-size:28px; font-weight:bold; color:white; margin-bottom:24px'
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

            ui.button('Crear solicitud', on_click=do_create).classes('auth-btn')

        list_container = ui.column()

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
