from nicegui import ui, app


def check_auth() -> bool:
    return app.storage.user.get('authenticated', False)


def get_current_user() -> dict:
    return dict(app.storage.user)


def logout():
    app.storage.user.clear()
    ui.navigate.to('/login')
