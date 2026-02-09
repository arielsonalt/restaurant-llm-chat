
---

## `.env.example`
```env
# Backend
APP_NAME=restaurant-llm-chat
ENV=local
JWT_SECRET=change_me
JWT_ISSUER=restaurant-llm-chat
ACCESS_TOKEN_TTL_MIN=15
REFRESH_TOKEN_TTL_DAYS=14

DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/restaurant
REDIS_URL=redis://redis:6379/0

KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_CLIENT_ID=restaurant-api

# LLM / Observability
OPENAI_API_KEY=replace_me
LANGSMITH_API_KEY=replace_me
LANGSMITH_PROJECT=restaurant-llm-chat
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=restaurant-llm-chat

# Frontend
VITE_API_BASE_URL=http://localhost:8000
