# Makefile

# --- CONFIG ---
DC_TEST = docker-compose -f docker-compose.test.yml -p job_scope_test --env-file=.env.test
DC_DEV  = docker-compose -f docker-compose.dev.yml -p job_scope --env-file=.env.dev

# --- TEST ENV ---
.PHONY: test-up test-down test-restart test-pytest test-integration test-psql test-redis test-py dev-create-superuser

test-up:
	$(DC_TEST) up --build -d

test-down:
	$(DC_TEST) down -v

test-restart:
	$(DC_TEST) restart

test-pytest:
	$(DC_TEST) exec app bash -c "pytest -s"

test-integration:
	$(DC_TEST) exec app bash -c "pytest -s tests/integration"

test-psql:
	$(DC_TEST) exec app bash -c "psql -U postgres"

test-redis:
	$(DC_TEST) exec redis redis-cli

test-py:
	$(DC_TEST) exec app sh -c "python -m asyncio"

# --- DEV ENV ---
.PHONY: dev-up dev-down dev-restart dev-pytest dev-psql dev-migrate dev-redis dev-py dev-superuser dev-elastic-indices

dev-up:
	$(DC_DEV) up --build -d

dev-down:
	$(DC_DEV) down

dev-restart:
	$(DC_DEV) restart

dev-pytest:
	$(DC_DEV) exec app bash -c "pytest -s tests/functional tests/unit"

dev-psql:
	$(DC_DEV) exec app bash -c "psql -U postgres"

dev-migrate:
	$(DC_DEV) exec app alembic upgrade head

dev-redis:
	$(DC_DEV) exec redis redis-cli

dev-py:
	$(DC_DEV) exec app sh -c "python -m asyncio"

dev-superuser:
	$(DC_DEV) exec app python scripts/create_superuser.py $(email) $(password)

dev-elastic-indices:
	$(DC_DEV) exec app python scripts/create_elastic_indices.py

# --- COMMON ---
.PHONY: structure secrets

structure:
	python tools/print_structure.py
secrets:
	python backend/scripts/generate_es256.py

