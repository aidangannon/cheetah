**Intropy Back-end Take-Home Task**

Welcome to the Intropy back-end take-home exercise! This project is designed to assess your strengths, coding style, and priorities as a back-end developer. You'll encounter challenges similar to those you’d face day-to-day at Intropy.

We're an AI company. We encourage the use of AI to take our productivity to the next level and we're always using the latest LLMs models. But equally as important, we encourage building robust and easy to work with software that we as developers can understand. So feel free to use AI and the internet to help you, but don't let AI take the driving seat. You should be able to explain all of the architecture and code implemented. 

---

## 📦 Project Overview

We provide:

* **Python API** scaffold (we use fastapi).
* **Data Folder** containing two sample data sets:

  * **metrics.json**: Definitions of metrics displayed on our dashboard.
  * **queries.csv**: Stored SQL queries referenced by metrics.

### Task Context
You are building a backend API and database for a metrics dashboard. Each metric references a stored SQL query, allowing dynamic data retrieval. Additionally, users can generate new metrics using a mock LLM interface: for example, given input “Metrics needing approval from March 2025 to April 2025”, the system returns a SQL query, which is then stored and used to fetch results.

### Data Relationships

Each metric in `metrics.json` references a `query_id` in `queries.csv`. Your API should:

1. Load metrics definitions.
2. Look up the corresponding SQL query string in `queries`.
3. Execute the SQL against a relational database to fetch results.

---

## 🎯 Core Tasks

1. **Set up the database**
   • Design and create schemas/tables reflecting the sample data structure.
   • Load the sample CSVs/JSON into the database.

2. **Health-check Endpoint**
   • Implement an HTTP endpoint (e.g., `GET /health`) that returns a simple JSON status.

3. **Metric-Query Endpoint**
   • Implement `GET /metrics/{metric_id}`:

   * Validate `metric_id` exists.
   * Fetch the associated SQL from `queries` table.
   * Execute the SQL and return the results in JSON format.

4. **Data Quality**
   • Handle potential errors, missing values, or duplicate entries in the CSV data.

---

## 🚀 Optional Enhancements / Areas to explore

The following are different areas / ideas you could choose from to showcase additional skills, feel free to do as many as you'd like or to create your own.  

- **API Documentation**
   • Add Swagger/OpenAPI docs or markdown API reference.

- **Error Handling**
   • Implement a robust error-handling middleware (custom exceptions, error codes).

- **Authentication**
   • Secure endpoints using JWT, OAuth2, or cookie-based auth.

- **Mock AI Endpoint**
    • POST /metrics to accept user input, simulate LLM-generated SQL, store new metric & query.

- **Containerization & CI/CD**
   • Dockerize the app and/or set up a CI/CD pipeline (GitHub Actions, GitLab CI).

- **Testing & Caching**
   • Add unit/integration tests (pytest, unittest) and implement query result caching.

- **Date Filtering**
   • Enable optional `start_date`/`end_date` parameters on metric endpoints.

- **Migration Scripts**
   • Provide SQL or ORM-based migration scripts (we use alembic).

- **Validation Middleware**
   • Add request/response validators (JSON schema, pydantic models).

- **Code Organization & Style**
   • Refactor the file structure for clarity and modularity.
   • Adhere to Python best practices (PEP8, type hints, docstrings).

---

## 📌 Submission Guidelines

* Share a Git repository link (GitHub, GitLab, etc.) with:

  * Clear README explaining setup & run instructions.
  * Dockerfile and/or migration scripts (if implemented).
  * Tests and documentation (if added).

We look forward to seeing your implementation and creativity. Good luck!
