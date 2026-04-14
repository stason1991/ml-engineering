from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import user_router
from routes.profile import profile_router
from routes.history import history_router
from routes.wallet import wallet_router
from routes.transaction import transaction_router
from routes.ml_model import ml_model_router
from routes.centroid import centroid_router
from routes.predict import predict_router
from routes.auth import auth_router
from database.database import init_db
from database.config import get_settings
import uvicorn
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def create_application() -> FastAPI:
    """ Create and configure FastAPI application. """
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs/",
        redoc_url="/api/redoc"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(user_router, prefix='/api/users', tags=['Users'])
    app.include_router(profile_router, prefix='/api/profiles', tags=['Profiles'])
    app.include_router(history_router, prefix='/api/history', tags=['History'])
    app.include_router(wallet_router, prefix='/api/wallets', tags=['Wallets'])
    app.include_router(transaction_router, prefix='/api/transactions', tags=['Transactions'])
    app.include_router(ml_model_router, prefix='/api/ml-models', tags=['ML Models'])
    app.include_router(centroid_router, prefix='/api/centroids', tags=['Centroids'])
    app.include_router(predict_router, prefix='/api/predict', tags=['Predict'])
    app.include_router(auth_router, prefix='/api/auth', tags=['Auth'])

    return app

app = create_application()

@app.get('/test')
def test():
    return {"message": "test_message"}

@app.on_event("startup")
async def on_startup():
    try:
        logger.info("Initializing database...")
        await init_db()
        logger.info("Application completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise e

@app.on_event("shutdown")
async def on_shutdown():
    """Cleanup on application shutdown."""
    logger.info("Application shutting down...")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run(
        'api:app',
        host='0.0.0.0',
        port=8080,
        reload=True,
        log_level="info"
    )
