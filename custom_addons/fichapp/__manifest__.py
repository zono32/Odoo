{
    "name": "Fichapp Integration",
    "version": "1.0",
    "summary": "Acceso directo a mi App de Fichajes",
    "category": "Human Resources",
    "author": "Kinso",
    "depends": ["base", "hr"],
    "data": [
        "views/fichapp_views.xml",
        "views/res_users_sync_view.xml",
    ],
    "installable": True,
    "application": True,
    "icon": "/fichapp/static/description/icon.png",
    "assets": {
        "web.assets_backend": [
            "fichapp/static/src/js/fichapp_clock.js",
            "fichapp/static/src/css/fichapp_style.css",
        ],
    },
    # Opcional si añades un icono luego
}
