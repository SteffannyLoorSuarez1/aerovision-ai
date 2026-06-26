import requests
from nicegui import ui, app

API_URL = 'http://backend:8000'

AUTH_STYLES = """
<style>
body {
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #020617, #0f172a, #111827);
    min-height: 100vh;
}
.auth-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 28px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    padding: 40px;
    min-width: 420px;
}
.auth-btn {
    width: 100%;
    margin-top: 16px;
    border-radius: 18px;
    padding: 14px;
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
    font-weight: bold;
    font-size: 16px;
}
.q-field input { color: white !important; }
.q-field__native { color: white !important; }
.q-field__label { color: #93c5fd !important; }
.q-field--filled .q-field__control { background: rgba(255,255,255,0.08) !important; }
.q-field__control { border-radius: 18px !important; background: rgba(255,255,255,0.05) !important; }
.q-field__control:before { border-bottom: 1px solid #3b82f6 !important; }
</style>
"""


@ui.page('/register')
def register_page():
    if app.storage.user.get('authenticated', False):
        ui.navigate.to('/')
        return

    ui.add_head_html(AUTH_STYLES)

    with ui.column().classes('absolute-center items-center'):
        with ui.element('div').classes('auth-card'):

            ui.label('✈ AeroVision').style(
                'font-size:34px; font-weight:bold; color:#60a5fa; text-align:center; display:block'
            )
            ui.label('AirCargo Exchange').style(
                'font-size:14px; color:#64748b; text-align:center; display:block; margin-bottom:8px'
            )
            ui.label('Crear cuenta').style(
                'font-size:20px; color:#cbd5e1; text-align:center; display:block; margin-bottom:24px'
            )

            nombre_input = ui.input(label='Nombre completo').props('filled').classes('w-full')
            ui.space().style('height:8px')
            email_input = ui.input(label='Correo electrónico').props('filled').classes('w-full')
            ui.space().style('height:8px')
            password_input = ui.input(
                label='Contraseña (mínimo 8 caracteres)',
                password=True,
                password_toggle_button=True
            ).props('filled').classes('w-full')

            error_label = ui.label('').style(
                'color:#fb7185; font-size:13px; min-height:20px; margin-top:8px'
            )

            def do_register():
                error_label.text = ''
                if not nombre_input.value.strip():
                    error_label.text = 'El nombre no puede estar vacío'
                    return
                if len(password_input.value) < 8:
                    error_label.text = 'La contraseña debe tener al menos 8 caracteres'
                    return
                try:
                    resp = requests.post(
                        f'{API_URL}/users/register',
                        json={
                            'nombre': nombre_input.value,
                            'email': email_input.value,
                            'password': password_input.value,
                        },
                        timeout=10
                    )
                    if resp.status_code == 201:
                        ui.notify('Cuenta creada exitosamente', color='positive')
                        ui.navigate.to('/login')
                    else:
                        error_label.text = resp.json().get('detail', 'Error al registrar')
                except Exception:
                    error_label.text = 'No se pudo conectar con el servidor'

            ui.button('Registrarse', on_click=do_register).classes('auth-btn')

            with ui.row().style('margin-top:20px; justify-content:center; gap:6px'):
                ui.label('¿Ya tienes cuenta?').style('color:#94a3b8; font-size:14px')
                ui.link('Iniciar sesión', '/login').style('color:#60a5fa; font-size:14px')
