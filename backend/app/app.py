from fastapi import FastAPI
from app.utils import setup_cors
from app.routes import router


def create_app():
    app = FastAPI()

    """ Middleware Setup """
    setup_cors(app)

    """ Routes """

    """ Healthcheck Route """

    @app.get("/health")
    def healthcheck():
        return {"status": "ok"}

    app.include_router(router=router, prefix="/api/auth/spotify")

    return app
