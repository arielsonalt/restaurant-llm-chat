
# Restaurant LLM Chat

Full-stack LLM-powered restaurant assistant with authentication, menu browsing, and a real-time chat UI. The backend exposes a FastAPI API and orchestrates LLM/RAG/agent flows (LangChain/LangGraph). The repository also includes Docker Compose and Kubernetes manifests (including Postgres, Redis, Kafka).

---

## Stack

### Backend (Python)

- **FastAPI**: REST API
- **Uvicorn**: ASGI server
- **Pydantic + pydantic-settings**: config + validation
- **Alembic + SQLAlchemy**: database migrations + ORM
- **PostgreSQL + pgvector**: system of record + vector similarity search (optional RAG)
- **LangChain / LangGraph**: LLM orchestration (tools, chains, multi-step agent graphs)
- **OpenAI SDK**: LLM provider client (can be swapped)
- **Redis**: cache, session/state, rate-limit, idempotency (optional depending on modules)
- **Kafka**: async/event-driven messaging for background tasks and decoupling services (optional)
- **OpenTelemetry**: tracing/metrics/log correlation (optional)
- **LangSmith**: LLM observability/tracing/evals (optional)

### Frontend (JavaScript)

- **React** (Vite-style structure: `src/main.jsx`)
- Pages: `Login`, `Signup`, `Menu`
- Component: `ChatWidget`
- API client: `src/api.js`
- Auth helper: `src/auth.js`

### Infrastructure & Delivery

- **Docker**: backend + frontend images
- **docker-compose**: local orchestration
- **Kubernetes manifests**: `k8s/` (backend, frontend, ingress, configmap/secret, postgres, redis, kafka)

---

## Repository structure (high level)

```
RESTAURANT-LLM-CHAT/
  backend/
    alembic/                # migrations
    app/
      auth/                 # auth endpoints & logic
      chat/                 # chat endpoints, agent orchestration
      db/                   # DB session, models, repositories
      menu/                 # menu endpoints & logic
      messaging/            # kafka/redis integration (if enabled)
      observability/        # OpenTelemetry, tracing/logging hooks
      main.py               # FastAPI app entrypoint
      settings.py           # env/config
    Dockerfile
    pyproject.toml
    alembic.ini

  frontend/
    src/
      components/ChatWidget.jsx
      pages/Login.jsx
      pages/Signup.jsx
      pages/Menu.jsx
      api.js
      auth.js
      App.jsx
      main.jsx
    Dockerfile
    package.json

  k8s/                      # Kubernetes manifests
    namespace.yaml
    backend.yaml
    frontend.yaml
    ingress.yaml
    configmap.yaml
    secret.yaml
    postgres.yaml
    redis.yaml
    kafka.yaml

  docker-compose.yml
  Makefile
  .env
```

---

## Core system flow

### 1) Authentication

- Frontend authenticates against the backend (`app/auth`) and stores a token/session (depending on your implementation in `frontend/src/auth.js`).

### 2) Menu browsing

- Frontend calls menu endpoints (`app/menu`) to list items and show details.

### 3) Chat (LLM orchestration)

- Frontend uses `ChatWidget` to send user messages to the backend (`app/chat`).
- Backend builds a context (session, user, menu info, optional retrieval) and calls the LLM.
- If using **RAG**, embeddings are generated and stored/searched in **pgvector**. Retrieval results are injected into the prompt/graph.
- If using **agents**, LangGraph coordinates tool-calling (e.g., menu lookup, order creation, FAQ retrieval).

### 4) Redis & Kafka (optional)

- **Redis**:
  - cache for repeated prompts/results
  - short-term conversation state/session
  - rate limiting / idempotency
- **Kafka**:
  - async jobs like document ingestion, reindexing, analytics, order events, audit events
  - decouples the request path from heavy processing

### 5) Observability (optional)

- **OpenTelemetry** instruments:
  - API requests
  - outbound HTTP calls (LLM provider)
  - Redis ops
- **LangSmith** captures LLM traces (prompts, tool calls, latencies, token usage) and enables evals.

---

## Run locally

### Prerequisites

- Docker + Docker Compose
- Node.js (optional if running frontend without Docker)
- Python 3.11 (recommended; some AI deps don’t support 3.12+ depending on your optional packages)

### 1) Configure environment

Create a `.env` in the repo root (or use the existing one) and set at least:

```bash
# Backend
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/restaurant
REDIS_URL=redis://redis:6379/0
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Optional: LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=restaurant-llm-chat
LANGSMITH_API_KEY=your_langsmith_key

# Optional: OTel
OTEL_SERVICE_NAME=restaurant-llm-backend
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

> Notes
>
> - If you don’t want Kafka/Redis, remove/disable their services from `docker-compose.yml` and disable related modules in `backend/app/settings.py`.

### 2) Start everything with Docker Compose

From repo root:

```bash
docker compose up --build
```

Typical endpoints:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000` (or `5173` depending on the frontend container)

### 3) Run database migrations (Alembic)

If your backend container has alembic installed and a CLI available:

```bash
docker compose exec backend alembic upgrade head
```

If you run it locally (venv):

```bash
cd backend
python -m venv .venv
# activate venv
pip install -U pip
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) Frontend (optional, without Docker)

```bash
cd frontend
npm install
npm run dev
```

---

## Deploy next steps (AWS production)

You already have Kubernetes manifests (`k8s/`). The cleanest production path on AWS is **EKS** + managed data services.

### Recommended AWS services

- **Amazon EKS**: managed Kubernetes
- **Amazon ECR**: container registry for backend/frontend images
- **Amazon RDS for PostgreSQL**: managed Postgres (enable pgvector)
- **Amazon ElastiCache for Redis**: managed Redis
- **Amazon MSK (Managed Streaming for Apache Kafka)**: managed Kafka
- **AWS Load Balancer Controller** + **ALB Ingress**: Kubernetes ingress to an AWS ALB
- **AWS ACM**: TLS certificates
- **Route 53**: DNS
- **AWS Secrets Manager** or **SSM Parameter Store**: secrets/config
- **CloudWatch Logs** + **ADOT (AWS Distro for OpenTelemetry)**: logs/traces/metrics
- **VPC**: private subnets for data services, public subnets for ALB
- **IAM + IRSA**: least-privilege service accounts for pods

---

## AWS deployment: EKS blueprint (practical)

### 1) Build & push images to ECR

1. Create two ECR repos:
   - `restaurant-llm-backend`
   - `restaurant-llm-frontend`
2. Build and push:

```bash
# backend
docker build -t restaurant-llm-backend:latest backend
# frontend
docker build -t restaurant-llm-frontend:latest frontend

# tag to ECR
docker tag restaurant-llm-backend:latest <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/restaurant-llm-backend:latest
docker tag restaurant-llm-frontend:latest <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/restaurant-llm-frontend:latest

# push
docker push <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/restaurant-llm-backend:latest
docker push <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/restaurant-llm-frontend:latest
```

### 2) Provision networking (VPC)

- Public subnets: ALB
- Private subnets: EKS nodes + RDS/ElastiCache/MSK
- Security Groups:
  - ALB → backend service port (e.g., 8000)
  - backend → RDS (5432), Redis (6379), MSK (9092/9094 depending)
- NAT Gateway for private subnets to pull images / call external APIs.

### 3) Provision managed data services

#### RDS (Postgres)

- Multi-AZ (prod)
- Parameter group enabling `pgvector` extension (you’ll still run `CREATE EXTENSION vector;` in DB)
- Backups + automated snapshots
- Private subnets only

#### ElastiCache (Redis)

- Cluster mode depending on scale
- Private subnets only

#### MSK (Kafka)

- Private subnets only
- TLS/auth as required (SCRAM/IAM)
- Use dedicated security groups and restrict inbound to EKS nodes/pods

### 4) Create EKS cluster

- Managed node group (or Fargate profiles if suitable)
- Enable **OIDC provider** for IRSA
- Install:
  - **AWS Load Balancer Controller**
  - (Optional) **ExternalDNS** (Route53 automation)
  - (Optional) **cert-manager** (ACM is often enough with ALB)

### 5) Configure Secrets and Config

Store secrets in:

- **AWS Secrets Manager** or **SSM Parameter Store**

Then inject into Kubernetes using:

- External Secrets Operator (recommended), or
- CI/CD to render `k8s/secret.yaml` with values at deploy time.

Minimum secrets:

- `OPENAI_API_KEY`
- DB credentials (or IAM auth if used)
- Redis auth (if enabled)
- Kafka auth (if enabled)
- `LANGSMITH_API_KEY` (optional)

### 6) Apply Kubernetes manifests

Update image references in `k8s/backend.yaml` and `k8s/frontend.yaml` to ECR image URIs, then:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

### 7) Ingress + TLS + DNS

- Use **ALB Ingress** with:
  - HTTPS listener (443)
  - ACM certificate ARN annotation
- Point Route53 record to ALB.

### 8) Observability in AWS

Recommended:

- Deploy **ADOT Collector** in EKS
- Export traces to **AWS X-Ray** or an OTLP backend
- Logs to **CloudWatch Logs**
- Instrument backend with OpenTelemetry env vars and libraries.

Example env pattern (conceptual):

- `OTEL_EXPORTER_OTLP_ENDPOINT` → ADOT Collector service
- `OTEL_RESOURCE_ATTRIBUTES` → service metadata

---

## Alternative AWS deployment (no Kubernetes)

If you want simpler ops:

- **ECS Fargate** for backend + frontend
- **ALB** for routing
- **RDS** + **ElastiCache** + **MSK**
- **CloudWatch** for logs, **X-Ray** for tracing

This reduces Kubernetes complexity but you lose K8s-native manifests and some portability.

---

## Production hardening checklist

- Use **private subnets** for RDS/Redis/MSK
- Use **Secrets Manager / SSM** (no secrets in git)
- Enable **WAF** on ALB if internet-exposed
- Set request limits + rate limiting (Redis)
- Add timeouts/retries around LLM calls
- Implement idempotency keys for side-effect tools (orders/payments)
- Add structured logging with correlation IDs
- Add health checks (`/healthz`, `/readyz`)
- Add CI/CD (GitHub Actions → ECR push → kubectl/helm deploy)

---

## License

See `LICENSE`.
