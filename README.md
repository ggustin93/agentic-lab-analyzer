# Health Document Analyzer

A modern, AI-powered health document analysis application built with Angular 20 and FastAPI, featuring OCR text extraction and intelligent health insights generation.

## 🚀 Features

- **Multi-Modal Document Processing**: Support for PDF, PNG, JPG, and JPEG files
- **Flexible AI Backend**: Configurable cloud (Chutes.ai) or local (Ollama) AI services
- **Advanced OCR**: Support for Tesseract (local) and Mistral OCR (cloud)
- **Health Data Extraction**: Structured extraction of health markers with validation
- **AI-Powered Insights**: Contextual health recommendations and analysis
- **Real-time Processing**: Live status updates and streaming responses
- **Type-Safe Architecture**: Full TypeScript implementation with Pydantic validation
- **Monitoring & Observability**: Integrated Logfire instrumentation
- **Responsive Design**: Modern UI with Tailwind CSS

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Angular 20    │    │    FastAPI       │    │   AI Services   │
│   Frontend      │◄──►│    Backend       │◄──►│                 │
│                 │    │                  │    │ • Ollama (Local)│
│ • Upload UI     │    │ • Document API   │    │ • Chutes.ai     │
│ • Results View  │    │ • OCR Service    │    │ • Mistral OCR   │
│ • Real-time     │    │ • Health Agent   │    │ • PydanticAI    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **Tesseract OCR** (for local OCR)
- **Ollama** (for local AI) - Optional
- **API Keys** (for cloud services) - Optional

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd health-document-analyzer

# Install frontend dependencies
npm install

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### 3. Install Ollama (for Local AI)

**Linux/macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from: https://ollama.ai/download

**Pull Models:**
```bash
# Basic model for health analysis
ollama pull llama3.2

# Advanced model for insights
ollama pull qwen2.5-coder:7b
```

### 4. Configure Environment

```bash
# Backend configuration
cp backend/.env.example backend/.env
# Edit backend/.env with your preferences
```

### 5. Start Services

```bash
# Terminal 1: Start Ollama (if using local AI)
ollama serve

# Terminal 2: Start backend
cd backend
python main.py

# Terminal 3: Start frontend
npm start
```

Visit: http://localhost:4200

## ⚙️ Configuration Options

### Local AI Configuration (Privacy-First)

```env
# Full Local Setup
AI_SERVICE_TYPE=local
LOCAL_PROVIDER=ollama
OCR_SERVICE_TYPE=tesseract

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_INSIGHTS_MODEL=qwen2.5-coder:7b
```

### Cloud AI Configuration

```env
# Chutes.ai (Decentralized AI)
AI_SERVICE_TYPE=cloud
CLOUD_PROVIDER=chutes_ai
CHUTES_AI_API_KEY=your_chutes_api_key
CHUTES_AI_ENDPOINT=https://api.chutes.ai/v1

# Mistral OCR (Cloud)
OCR_SERVICE_TYPE=mistral
MISTRAL_API_KEY=your_mistral_api_key
```

### Hybrid Configuration

```env
# Local AI + Cloud OCR
AI_SERVICE_TYPE=local
LOCAL_PROVIDER=ollama
OCR_SERVICE_TYPE=mistral
MISTRAL_API_KEY=your_mistral_api_key
```

### OpenAI Configuration

```env
# OpenAI Cloud
AI_SERVICE_TYPE=cloud
CLOUD_PROVIDER=openai
OPENAI_API_KEY=your_openai_key

# Or Local OpenAI-compatible endpoint
AI_SERVICE_TYPE=local
LOCAL_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:8080/v1
```

## 🔧 Ollama Setup Guide

### 1. Install Ollama

Visit [ollama.ai](https://ollama.ai) for installation instructions.

### 2. Download Models

```bash
# Health analysis model (lightweight)
ollama pull llama3.2

# Advanced insights model
ollama pull qwen2.5-coder:7b

# Alternative models
ollama pull mistral:7b
ollama pull codellama:7b
```

### 3. Verify Installation

```bash
# Check available models
ollama list

# Test model
ollama run llama3.2 "Hello, how are you?"
```

### 4. Configure for Health Analyzer

Update your `.env` file:
```env
AI_SERVICE_TYPE=local
LOCAL_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_INSIGHTS_MODEL=qwen2.5-coder:7b
```

## 🧪 Quality Assurance & Testing

### Frontend Testing

```bash
# Unit tests
npm test

# E2E tests
npm run e2e

# Linting
npm run lint

# Type checking
npm run type-check

# Build verification
npm run build
```

### Backend Testing

```bash
cd backend

# Unit tests
pytest tests/ -v

# Integration tests
pytest tests/integration/ -v

# API tests
pytest tests/api/ -v

# Coverage report
pytest --cov=. --cov-report=html

# Type checking
mypy .

# Code quality
flake8 .
black . --check
isort . --check-only
```

### Load Testing

```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

### Security Testing

```bash
# Dependency vulnerability scanning
npm audit
pip-audit

# SAST scanning
bandit -r backend/
semgrep --config=auto backend/
```

## 🚀 DevOps & Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### CI/CD Pipeline

The project includes GitHub Actions workflows for:

- **Continuous Integration**: Automated testing, linting, and security scans
- **Continuous Deployment**: Automated deployment to staging/production
- **Dependency Updates**: Automated dependency updates with Dependabot
- **Security Monitoring**: Regular security scans and alerts

### Monitoring & Observability

#### Application Monitoring

```bash
# Enable Logfire monitoring
export LOGFIRE_TOKEN=your_token

# Health checks
curl http://localhost:8000/health

# Metrics endpoint
curl http://localhost:8000/metrics
```

#### Performance Monitoring

- **Frontend**: Web Vitals, Angular DevTools
- **Backend**: FastAPI metrics, Pydantic instrumentation
- **AI Services**: Token usage, response times, error rates
- **Ollama**: Model performance, memory usage

### Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring alerts set up
- [ ] Rate limiting configured
- [ ] CORS policies reviewed
- [ ] Security headers configured
- [ ] Log aggregation set up
- [ ] Health checks implemented
- [ ] Disaster recovery plan documented
- [ ] Ollama models downloaded and tested

## 📊 Performance Optimization

### Frontend Optimization

```bash
# Bundle analysis
npm run build -- --stats-json
npx webpack-bundle-analyzer dist/stats.json

# Performance audit
npm run lighthouse
```

### Backend Optimization

```python
# Enable async processing
ASYNC_PROCESSING=true

# Configure connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Enable caching
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

### Ollama Optimization

```bash
# Use GPU acceleration (if available)
ollama run llama3.2 --gpu

# Optimize model loading
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
```

## 🔒 Security Best Practices

### Data Protection

- **Encryption**: All data encrypted in transit and at rest
- **API Security**: Rate limiting, authentication, input validation
- **File Upload**: Type validation, size limits, virus scanning
- **Privacy**: Local processing option for sensitive documents

### Local AI Benefits

- **Data Privacy**: Documents never leave your infrastructure
- **Compliance**: Easier HIPAA/GDPR compliance
- **Cost Control**: No per-token charges
- **Offline Capability**: Works without internet connection

## 🐛 Troubleshooting

### Common Issues

#### Ollama Not Working

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Check logs
ollama logs
```

#### OCR Not Working

```bash
# Check Tesseract installation
tesseract --version

# Verify file permissions
ls -la uploads/

# Check logs
tail -f backend/logs/app.log
```

#### AI Service Errors

```bash
# Test Ollama connectivity
curl http://localhost:11434/api/generate -d '{"model":"llama3.2","prompt":"test"}'

# Check service status
curl http://localhost:8000/health
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Frontend debug mode
ng serve --configuration=development

# Backend debug mode
uvicorn main:app --reload --log-level debug
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript/Python style guides
- Write comprehensive tests
- Update documentation
- Use conventional commits
- Ensure CI/CD passes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Wiki](wiki-url)
- **Issues**: [GitHub Issues](issues-url)
- **Discussions**: [GitHub Discussions](discussions-url)
- **Email**: support@healthanalyzer.com

## 🗺️ Roadmap

- [x] **Q4 2024**: Ollama integration for local AI
- [ ] **Q1 2025**: Mistral OCR integration
- [ ] **Q2 2025**: Chutes.ai decentralized AI support
- [ ] **Q3 2025**: Multi-language support
- [ ] **Q4 2025**: Mobile application

---

**Built with ❤️ by the Health Document Analyzer Team**

*Powered by Ollama for local AI, PydanticAI for type safety, and modern web technologies.*