from fastapi import FastAPI
from app.utils import setup_cors
from app.routes import spotify_router, main_router


def create_app():
    app = FastAPI()

    """ Middleware Setup """
    setup_cors(app)

    """ Routes """

    """ Healthcheck Route """

    @app.get("/health")
    def healthcheck():
        return {"status": "ok"}

    app.include_router(router=spotify_router, prefix="/api/auth/spotify")
    app.include_router(router=main_router, prefix="/api/sonemica")

    return app
