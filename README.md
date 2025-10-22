# FastAPI Project Skeleton

This project follows best practices for scalable, robust FastAPI backend applications.

## Quickstart

1.  **Set up the Environment**:
    *   Copy `.env.example` to `.env`.
    *   Adjust the environment variables in `.env` to match your local setup (e.g., database credentials).

2.  **Install Dependencies**:
    *   It is recommended to use a virtual environment.
    *   Run `pip install -r requirements-dev.txt`.

3.  **Apply Migrations**:
    *   Make sure your database server is running.
    *   Run `alembic upgrade head`.

4.  **Start the Server**:
    *   Run `uvicorn app.main:app --reload`.
    *   The API will be available at `http://127.0.0.1:8000`.

## Patterns and Structure

-   **Architecture**: Follows a clean architecture with a clear separation of layers (API, Service, Repository).
-   **Testing**: All modules are designed to be testable in isolation. Use `pytest` to run tests.
-   **Middlewares**: Place custom middlewares in `app/middlewares`.
-   **Configuration & Logging**: Centralized and environment-aware configuration management in `app/core`.
-   **Data Access**: The Repository pattern is used for all database interactions, abstracting the data source from the business logic.

## Contributing

-   Write clear, type-annotated, and tested code.
-   Add or update tests for every new feature or bug fix.
-   Document public APIs and significant architectural decisions in the `docs/` directory.
-   Follow the patterns and structure as described in `docs/architecture.md`.