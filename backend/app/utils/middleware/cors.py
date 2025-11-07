from fastapi.middleware.cors import CORSMiddleware

""" Configuración del middleware CORS  """


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
