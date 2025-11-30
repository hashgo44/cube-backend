from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, test_connection, engine
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage de l'application...")
    test_connection()
    yield
    # Shutdown
    print("👋 Arrêt de l'application...")
    engine.dispose()


app = FastAPI(
    title="Cube Backend API",
    description="API simple avec connexion PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer selon vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API Cube Backend",
        "status": "running"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Endpoint de santé avec vérification de la connexion DB"""
    try:
        # Tester la connexion à la base de données
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/db/test")
async def test_database(db: Session = Depends(get_db)):
    """Tester la connexion et récupérer des infos sur la DB"""
    try:
        # Version de PostgreSQL
        result = db.execute(text("SELECT version()"))
        version = result.scalar()
        
        # Liste des tables
        tables_result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in tables_result]
        
        return {
            "status": "success",
            "postgres_version": version,
            "tables": tables
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

