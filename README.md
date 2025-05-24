## Table of Contents

- [Project Overview](#project-overview)  
- [Running the App Locally](#running-the-app-locally)  
- [Deployment](#deployment)  
- [API Access & Authentication](#api-access--authentication)  
- [Architecture & Code Structure](#architecture--code-structure)  
- [Database Design & Migrations](#database-design--migrations)  
- [Testing & CI/CD](#testing--cicd)  
- [Caching Strategy](#caching-strategy)  
- [Logging & Observability](#logging--observability)  
- [Next Steps & Further Improvements](#next-steps--further-improvements)  

---

## Project Overview

This backend service:

- Loads and validates metric definitions and associated SQL queries from JSON and CSV data sources.  
- Maps metrics to SQL and executes queries against a PostgreSQL database using a **code-first** SQLAlchemy ORM approach.  
- Manages database sessions explicitly using a **unit of work pattern** for clear transaction boundaries.  
- Caches complex aggregate query results with a **TTL-based memory cache** to optimize performance while avoiding memory bloat.  
- Applies **dependency injection** via the `punq` container to keep modules decoupled and testable.  
- Enforces strict API contracts with **Pydantic models** validating input/output schemas.  
- Drives API behavior with **BDD-style acceptance tests** for maintainability and regression safety.  
- Secures endpoints with **AWS Cognito JWT authentication**, validating tokens against well-known keys.  
- Supports containerized deployment with Docker and automated CI/CD pipelines via GitHub Actions.  
- Integrates a mock AI endpoint simulating LLM-generated SQL to dynamically add new metrics.  

The architecture prioritizes code clarity, modularity, and ease of explanation, aligning strongly with Intropy’s values of blending AI with robust backend engineering.

---

## Running the App Locally

To run the application locally with Docker and Poetry:

1. Install dependencies:

    ```bash
    poetry install
    ```

2. Prepare the application directory:

    ```bash
    cd ~/app || (mkdir ~/app && cd ~/app)
    ```

3. Build the Docker image:

    ```bash
    docker build -t myfastapiapp .
    ```

4. Run a PostgreSQL container (for database):

    ```bash
    docker run --rm -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=testdb postgres
    ```

5. Run the FastAPI app container:

    ```bash
    docker run -d --restart unless-stopped --name myfastapiapp --env-file ../.env -p 8000:8000 myfastapiapp
    ```

You can then access the API locally at `http://localhost:8000`.

---

## Deployment

The entire infrastructure is deployed using **CloudFormation** IAC templates located at `/deploy-template.yml`. Key deployment details:

- **EC2 instance** running Docker with the FastAPI application.
- PostgreSQL database hosted on **AWS RDS**.
- All components reside within a secure **VPC** with properly configured inbound and outbound rules.
- Secure SSH access configured for CI/CD pipeline integration.
- Uvicorn runs the FastAPI app locally on EC2, fronted by **NGINX** reverse proxy handling HTTPS termination.
- **AWS Cognito** manages authentication via a user pool, supporting OAuth2 flows.
- Logs are streamed to **AWS CloudWatch** and accessible directly via SSH on the EC2 instance.

---

## API Access & Authentication

- Live Swagger docs available at:  
  [https://aphextwinning.com/](https://aphextwinning.com/)

- Token generation endpoint (AWS Cognito OAuth2):  
  `https://3eef4c69-d944-4d39-837f-97f3f72f5f93.auth.eu-west-2.amazoncognito.com/oauth2/token`

- Client credentials for token generation:  
  - Client ID: `7gkl7in37d96ijhi1901gln0nv`  
  - Required scope: `api/backend_access`  
  - Auth: Basic Auth with Base64 encoding of `client_id:client_secret`

- Authenticated endpoints validate JWT tokens using Cognito’s `.well-known` keys.

---

## Architecture & Code Structure

- **Modular codebase** split into logical domains:  
  - `src.core` — pure domain models (dataclasses) and protocol interfaces  
  - `src.application` — services orchestrating business logic and LLM prompt generation  
  - `src.infrastructure` — ORM, DB session, caching, and repository implementations  
  - `src.web` — FastAPI routing, middleware, and request/response models  
  - `src.crosscutting` — shared concerns like logging and error handling

- Uses **Pydantic** for input validation and response models.

- Dependency injection is managed via the **punq** container in `src.bootstrap`.

- The code favors **explicit unit of work patterns** for database transactions to reduce boilerplate and improve clarity.

- Runtime polymorphism and duck typing improve flexibility without sacrificing static type hints or readability.

---

## Database Design & Migrations

- Schema designed to mirror the provided JSON and CSV data.

- Uses **Alembic** for managing database migrations and version control.

- Imperative mapping with SQLAlchemy separates domain models from ORM models.

- No database-level constraints or triggers; lifecycle and business logic handled fully in code.

- Unit of work pattern (`SqlAlchemyUnitOfWork`) controls session lifecycle with explicit commits and implicit rollbacks.

```python
class SqlAlchemyUnitOfWork:
    __slots__ = "session_factory", "logger", "session"

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        engine = sqlalchemy.ext.asyncio.create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
        )
        self.session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def __aenter__(self):
        self.session = self.session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.session.rollback()
        finally:
            await self.session.close()
```

---

## Testing & CI/CD

- Automated regression tests written with `unittest` in BDD style, located in `tests.test_scenarios`.

```python
def test_create_metrics(self):
    scenario = CreateMetricConfigurationScenario(self.context)
    scenario \
        .given_i_have_an_app_running() \
        .when_the_create_metric_configuration_endpoint_is_called_with_metric_configuration() \
        .and_data_is_created_for_the_metric() \
        .then_the_status_code_should_be(201) \
        .then_the_metrics_should_have_been_created() \
        .then_an_info_log_indicates_endpoint_called()
```

- Tests spin up an in-memory, isolated application lifecycle for parallel execution without cross-test contamination.

- Shared state managed via concurrent-safe in-memory structures.

- **GitHub Actions** CI/CD pipeline (`.github/workflows/cicd.yml`) automates:

  - Running regression tests on every PR.
  - Deploying code and CloudFormation changes automatically.
  - Securely injecting environment variables and CloudFormation outputs into EC2.
  - Remote Docker container restarts via SSH and SCP file transfers.

---

## Caching Strategy

- Implemented basic in-memory caching with TTL for metric configurations and query aggregates.

- This reduces repeated expensive computations for data unlikely to change during runtime.

- TTL is critical to prevent out-of-memory issues within the container, balancing performance and scalability.

---

## Logging & Observability

- Custom middleware captures detailed audit logs, error tracing, and request-scoped variables.

- Logs are sent to AWS CloudWatch with enhanced filtering and live observability.

- EC2 instances also allow direct log access over SSH via standard output streaming.

- Endpoint-level logs include scoped context propagation to facilitate root-cause analysis.

```python
with logging_scope(
    operation=get_metrics.__name__,
    id=id_str,
    start_date=start_date,
    end_date=end_date,
    day_range=day_range,
):
    logger.info("Endpoint called")

    metrics = await get_metrics_service(
        _id=id_str,
        start_date=start_date,
        end_date=end_date,
        day_range=day_range
    )
```

---

## Next Steps & Further Improvements

If given more time, I would:

- Enhance the automated testing framework by introducing reusable common steps for log assertions and token header injection, potentially developing a dedicated BDD framework library.

- Implement role-based access control on authenticated endpoints to enable finer-grained permission management.

- Optimize the database schema with b-tree indexes to improve query performance.

- Add real-time metric updates using WebSocket integration for live data streaming.

---

Thank you for reviewing my submission!  
Please feel free to reach out for any questions or clarifications.

---

