# Transaction Risk Service

A **FastAPI** microservice for scoring financial transaction risk using OpenAI, notifying admins, and exposing Prometheus metrics.

---

## 🚀 Features

- **Risk Analysis** via Gemini 2.0 Flash chat models (configurable in `.env`)  
- **Admin Notifications**: Sends JSON payloads to your webhook on each transaction  
- **OpenAPI Docs**: Interactive Swagger UI (`/docs`) and ReDoc (`/redoc`)  
- **Prometheus Metrics**: Built-in instrumentation at `/metrics`  
- **Structured Logging** with contextual request data  
- **Dockerized** for easy containerization and local development  
- **AWS Container Deployment**: Push to ECR, run on ECS Fargate behind an ALB for scalable production hosting  
- **Alerting & Visualization**: Grafana dashboards and Alertmanager rules trigger on error rates and P95 latency  
- **CI/CD**: GitHub Actions workflow (`.github/workflows/ci.yml`) runs linting, tests, and Docker image builds on every push  


---




