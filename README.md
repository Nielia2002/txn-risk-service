# Transaction Risk Service

A **FastAPI** microservice for scoring financial transaction risk using OpenAI, notifying admins, and exposing Prometheus metrics.

---

## 🚀 Features

- **Risk Analysis** via OpenAI chat models (configurable in `.env`)  
- **Admin Notifications**: Sends JSON payloads to your webhook on each transaction  
- **OpenAPI Docs**: Interactive Swagger UI (`/docs`) and ReDoc (`/redoc`)  
- **Prometheus Metrics**: Built-in instrumentation at `/metrics`  
- **Structured Logging** with contextual request data  
- **Dockerized** for easy deployment  

---

## 📦 Quick Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/nielia2002/txn-risk-service.git
   cd txn-risk-service
