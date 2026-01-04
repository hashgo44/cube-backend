from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, test_connection, engine, Base
from models import Article
from schemas import ArticleCreate, ArticleUpdate, ArticleResponse
from contextlib import asynccontextmanager
from typing import Optional


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage de l'application...")
    test_connection()
    # Créer les tables automatiquement
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées/vérifiées")
    yield
    # Shutdown
    print("👋 Arrêt de l'application...")
    engine.dispose()


app = FastAPI(
    title="Cube Backend API",
    description="API simple avec connexion PostgreSQL - Style LeBonCoin simplifié",
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
        result = db.execute(text("SELECT version()"))
        version = result.scalar()
        
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


# ==================== ARTICLES ENDPOINTS ====================

@app.post("/articles", response_model=ArticleResponse, status_code=201)
async def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle annonce"""
    db_article = Article(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


@app.get("/articles", response_model=list[ArticleResponse])
async def get_articles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    """Récupérer la liste des annonces avec filtres optionnels"""
    query = db.query(Article)
    
    if category:
        query = query.filter(Article.category == category)
    
    if search:
        query = query.filter(Article.title.ilike(f"%{search}%"))
    
    articles = query.order_by(Article.created_at.desc()).offset(skip).limit(limit).all()
    return articles


@app.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """Récupérer une annonce par son ID"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article


@app.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int, 
    article_update: ArticleUpdate, 
    db: Session = Depends(get_db)
):
    """Mettre à jour une annonce"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    update_data = article_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(article, key, value)
    
    db.commit()
    db.refresh(article)
    return article


@app.delete("/articles/{article_id}")
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    """Supprimer une annonce"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    db.delete(article)
    db.commit()
    return {"message": "Article supprimé avec succès", "id": article_id}


@app.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Récupérer la liste des catégories existantes"""
    result = db.query(Article.category).distinct().filter(Article.category.isnot(None)).all()
    categories = [row[0] for row in result if row[0]]
    return {"categories": categories}
