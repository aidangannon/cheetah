# Intropy Back-End Take-Home Project

Welcome to my implementation of the Intropy back-end coding exercise. This project demonstrates my approach to building a robust, maintainable, and production-ready backend API for a dynamic metrics dashboard — closely aligned with Intropy’s emphasis on clarity, robustness, and practical AI integration.

---

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

This backend API is built with **FastAPI** and serves as a dynamic data retrieval engine for a metrics dashboard. It loads metric definitions and associated SQL queries, executes queries against a relational database, and exposes endpoints to fetch metric data. Additionally, it simulates a mock LLM interface for generating new SQL-backed metrics.

The system is designed to:

- Load and validate metrics from JSON and CSV datasets.
- Map metrics to SQL queries and execute them on demand.
- Provide health-check and metrics endpoints with robust error handling.
- Support token-based authentication with AWS Cognito.
- Use dependency injection and Pydantic models for clear contract definitions.
- Enable containerized deployment and automated CI/CD workflows.

This project adheres closely to Intropy’s brief, focusing on both AI-augmented productivity and code clarity — all core components are explained and fully controlled by me.

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

---

## Testing & CI/CD

- Automated regression tests written with `unittest` in BDD style, located in `tests.test_scenarios`.

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

---

## Next Steps & Further Improvements

If I had more time, I would:

- Expand the mock AI LLM endpoint to generate real SQL queries from natural language prompts using a fine-tuned LLM model.

- Add role-based access control on authenticated endpoints for more granular permissions.

- Implement a more advanced caching layer using Redis for distributed cache.

- Improve database schema with foreign keys and indexing for query optimization.

- Enhance API documentation with example requests/responses and SDK generation.

- Integrate real-time WebSocket updates for metrics data changes.

---

Thank you for reviewing my submission!  
Please feel free to reach out for any questions or clarifications.

---

*This project was built following Intropy’s guidelines to deliver a maintainable, well-structured, and AI-empowered backend service.*

