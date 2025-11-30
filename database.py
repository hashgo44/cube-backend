from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    database_url: str


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

# Créer l'engine SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=True  # Pour voir les requêtes SQL (désactiver en production)
)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Fonction pour tester la connexion
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Connexion à PostgreSQL réussie!")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion à PostgreSQL: {e}")
        return False

