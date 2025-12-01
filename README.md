# Cube-Backend API

API simple avec FastAPI et connexion PostgreSQL.

## 🚀 Démarrage rapide

### Avec Docker Compose (Recommandé)

```bash
# Démarrer l'API et PostgreSQL
docker-compose up --build

# L'API sera accessible sur http://localhost:8000
# Documentation interactive: http://localhost:8000/docs
```

### Installation locale

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Mac/Linux
# ou sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos credentials PostgreSQL

# Lancer l'application
uvicorn main:app --reload
```

## 📝 Endpoints disponibles

- `GET /` - Message de bienvenue
- `GET /health` - Vérification de santé avec connexion DB
- `GET /db/test` - Test de connexion et informations sur la base de données
- `GET /docs` - Documentation interactive Swagger

## 🔧 Configuration

Les variables d'environnement sont définies dans le fichier `.env`:

```
DATABASE_URL=postgresql://cube_user:cube_password@localhost:5432/cube_db
```

## 📦 Stack technique

- **FastAPI** - Framework web moderne et rapide
- **SQLAlchemy** - ORM pour PostgreSQL
- **Uvicorn** - Serveur ASGI
- **PostgreSQL** - Base de données relationnelle
