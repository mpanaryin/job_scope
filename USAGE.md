# 📦 Usage Guide

This project offers two primary modes of operation: **development** and **testing**, each managed via its own `docker-compose` configuration.

---

## ✅ Prerequisites

Before running the project, make sure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- Python 3.11+ (for optional utility scripts)
- Telegram account (for error notifications)
- HeadHunter account for API integration

---

## 🛠 Development Setup

Follow these steps to run the project in development mode:

### 1. Clone the Repository

```bash
git clone https://github.com/mpanaryin/job_scope.git
cd job_scope
```

### 2. Create a Telegram Bot and Get Your Chat ID

This is required to receive error-level logs via Telegram:

- Create a bot using [@BotFather](https://t.me/botfather)
- Get your chat ID using [@getmyid_bot](https://t.me/getmyid_bot)

### 3. Register Your App with HeadHunter

To access the HeadHunter job API:

- Visit [HeadHunter API Docs](https://api.hh.ru/openapi/redoc#tag/Avtorizaciya-prilozheniya)
- Register an app and obtain the following credentials:
  - `HEADHUNTER_CLIENT_ID`
  - `HEADHUNTER_CLIENT_SECRET`
  - `HEADHUNTER_TOKEN`

### 4. Set Up Environment Files

Copy the example and create `.env.dev` and `.env.test`:

```bash
cp .env.example .env.dev
cp .env.example .env.test
```

Fill in the required fields:

- **`.env.dev`**:
  - ENVIRONMENT=development
  - Database configuration
  - Redis, Elasticsearch, Logstash
  - Telegram and HeadHunter integration

- **`.env.test`**:
  - ENVIRONMENT=testing
  - Only needs Redis and PostgreSQL configuration
  - You can skip sections for Elastic, Logstash, Email, HeadHunter, Telegram

### 5. Generate EC Keys for JWT Authentication

Place them in `/backend/secrets`:

```bash
openssl ecparam -genkey -name prime256v1 -noout -out backend/secrets/ec_private.pem
openssl ec -in backend/secrets/ec_private.pem -pubout -out backend/secrets/ec_public.pem
```

### 6. Start the Development Environment

```bash
docker-compose -f docker-compose.dev.yml -p job_scope --env-file=.env.dev up --build -d
```

### 7. Run Unit and Functional Tests

```bash
docker-compose -f docker-compose.dev.yml -p job_scope --env-file=.env.dev exec app bash -c "pytest -s tests/functional tests/unit"
```

---

## 🧪 Testing Setup

Use this mode to run integration tests with real dependencies.

### 1. Launch the Testing Environment

```bash
docker-compose -f docker-compose.test.yml -p job_scope_test --env-file=.env.test up --build -d
```

### 2. Run All Tests

```bash
docker-compose -f docker-compose.test.yml -p job_scope_test --env-file=.env.test exec app bash -c "pytest -s"
```

### 3. Tear Down the Testing Environment

```bash
docker-compose -f docker-compose.test.yml -p job_scope_test --env-file=.env.test down -v
```

---
