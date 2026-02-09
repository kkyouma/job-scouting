# Job Scouting

A minimalist job scouting tool orchestrated with Prefect, using JSearch, Adzuna, and GetOnBoard APIs.

## Setup

1.  **Install Dependencies**:
    The project is managed with `uv`.
    ```bash
    uv sync
    ```

2.  **Configuration**:
    Create a `.env` file based on `.env.example` and fill in your API keys:
    ```ini
    JSEARCH_API_KEY=...
    ADZUNA_APP_ID=...
    ADZUNA_API_KEY=...
    TELEGRAM_BOT_TOKEN=...
    TELEGRAM_CHAT_ID=...
    ```

3.  **Running the Scout**:
    You can run the Prefect flow directly:
    ```bash
    uv run python src/flows/job_flow.py
    ```

## Development

-   **Linting**: `uv run ruff check .`
-   **Formatting**: `uv run ruff format .`
-   **Type Checking**: `uv run ty check`

## Structure

-   `src/flows/job_flow.py`: Main entry point / orchestration.
-   `src/clients/`: API integrations.
-   `src/services/`: Business logic (filtering, notifying).
