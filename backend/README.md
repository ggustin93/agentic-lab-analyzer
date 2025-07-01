# Health Document Analyzer - Backend v2.0

Backend API pour l'analyse de documents de santé utilisant **PydanticAI**, FastAPI, OCR et LLM.

## 🚀 Nouveautés v2.0

- **PydanticAI** : Framework moderne pour les applications LLM avec type safety
- **Agents spécialisés** : Agents dédiés pour l'extraction de données et la génération d'insights
- **Monitoring Logfire** : Instrumentation avancée pour le debugging et la performance
- **Modèles structurés** : Validation Pydantic pour toutes les données de santé
- **Gestion d'erreurs améliorée** : Fallbacks robustes et logging détaillé

## Installation

1. Créer un environnement virtuel Python :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Installer Tesseract OCR :

**Ubuntu/Debian :**
```bash
sudo apt-get install tesseract-ocr
```

**macOS :**
```bash
brew install tesseract
```

**Windows :**
Télécharger depuis : https://github.com/UB-Mannheim/tesseract/wiki

4. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec votre clé API OpenAI et optionnellement Logfire
```

## Lancement

```bash
python main.py
```

L'API sera disponible sur : http://localhost:8000

## Documentation API

Une fois l'API lancée, la documentation interactive est disponible sur :
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## Endpoints principaux

- `POST /api/upload` - Upload et traitement d'un document avec PydanticAI
- `GET /api/document/{document_id}` - Récupérer l'analyse d'un document
- `DELETE /api/document/{document_id}` - Supprimer un document
- `GET /api/documents` - Lister tous les documents
- `POST /api/test-analysis` - Tester l'analyse PydanticAI directement
- `GET /health` - Vérifier l'état des services

## Architecture PydanticAI

### Agents Spécialisés

1. **Health Extraction Agent** (`health_extraction_agent`)
   - Modèle : `gpt-4o-mini` (optimisé coût/performance)
   - Tâche : Extraction de données structurées
   - Output : `HealthDataExtraction` avec validation Pydantic

2. **Health Insights Agent** (`health_insights_agent`)
   - Modèle : `gpt-4o` (plus puissant pour l'analyse)
   - Tâche : Génération d'insights médicaux
   - Output : `HealthInsights` avec recommandations

### Modèles de Données

```python
class HealthMarker(BaseModel):
    marker: str = Field(description="Name of the health marker")
    value: str = Field(description="Measured value")
    unit: Optional[str] = Field(description="Unit of measurement")
    reference_range: Optional[str] = Field(description="Normal range")

class HealthDataExtraction(BaseModel):
    markers: List[HealthMarker]
    document_type: str
    test_date: Optional[str]
    patient_info: Optional[str]

class HealthInsights(BaseModel):
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    risk_factors: List[str]
    follow_up_needed: bool
    disclaimer: str
```

## Monitoring avec Logfire

Pour activer le monitoring avancé :

1. Installer Logfire :
```bash
pip install logfire
```

2. Configurer votre token dans `.env` :
```bash
LOGFIRE_TOKEN=your_logfire_token_here
```

3. Les agents PydanticAI sont automatiquement instrumentés avec `instrument=True`

## Services

### OCR Service
- Extraction de texte depuis images (PNG, JPG, JPEG)
- Extraction de texte depuis PDF
- Utilise Tesseract OCR

### Health Analysis Service (PydanticAI)
- Extraction de données structurées avec validation
- Génération d'insights médicaux contextuels
- Type safety complet avec Pydantic
- Gestion d'erreurs robuste avec fallbacks

### Document Processor
- Orchestration complète du pipeline
- Traitement asynchrone
- Stockage des données structurées et legacy

## Avantages PydanticAI

- **Type Safety** : Validation automatique des outputs LLM
- **Agents Spécialisés** : Chaque agent a une tâche spécifique
- **Dependency Injection** : Contexte propre pour chaque agent
- **Instrumentation** : Monitoring intégré avec Logfire
- **Robustesse** : Gestion d'erreurs et fallbacks automatiques
- **Maintenabilité** : Code plus propre et testable

## Structure des données

Les documents analysés contiennent maintenant :
- Données structurées validées par Pydantic
- Insights générés avec contexte médical
- Métadonnées enrichies (type de document, date, etc.)
- Compatibilité avec l'ancien format pour le frontend

## Sécurité

- Validation des types de fichiers
- Limite de taille des fichiers (10MB)
- Traitement local des données
- Pas de stockage permanent des fichiers uploadés
- Validation Pydantic pour tous les inputs/outputs

## Tests

Testez l'analyse PydanticAI directement :

```bash
curl -X POST "http://localhost:8000/api/test-analysis" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hemoglobin: 14.5 g/dL (Reference: 13.5-17.5)"}'
```