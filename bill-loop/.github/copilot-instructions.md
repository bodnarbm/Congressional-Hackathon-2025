# Congressional Hackathon 2025: AI Coding Agent Instructions

## Project Overview

This project is a FastAPI service for converting legislative PDFs to Markdown using the `markitdown` library. The main entry point is `app.py`, which exposes two endpoints:
- `GET /` — Root endpoint, returns file upload form
- `GET /health` — Health check, returns `{"status": "ok"}`
- `POST /convert` — Accepts a PDF upload, converts it to Markdown, and returns the result

## Key Files & Structure
- `app.py`: Main FastAPI app, PDF upload and conversion logic
- `README.md`: Project context (legislation authors work with PDFs and think in text)
- `pyproject.toml`, `uv.lock`: Python dependencies and environment
- `run.sh`: Likely used for launching the service (inspect for details if present)

## Developer Workflows

- **Run the API locally:**
  - If `run.sh` exists, use it to start the service: `./run.sh`
  - Otherwise, run with: `uvicorn app:app --reload`
- **Dependencies:**
  - Managed via `pyproject.toml` and `uv.lock`. Use `uv sync` to install.
- **Testing:**
  - No explicit test files found. If adding tests, follow FastAPI and pytest conventions.

## Patterns & Conventions

- **PDF Handling:** Uploaded PDFs are saved to a temporary file before conversion.
- **Error Handling:** Conversion errors return a 500 JSON response with the error message.
- **External Integration:** Uses `markitdown.convert()` for PDF-to-Markdown conversion. Ensure this package is installed and compatible.
- **Minimal API:** Only two endpoints, focused on conversion. Extend by adding new routes in `app.py`.

## Examples

- To add a new endpoint, follow the FastAPI decorator pattern in `app.py`:
  ```python
  @app.get("/new-endpoint")
  async def new_func():
      ...
  ```
- To handle file uploads, use `UploadFile = File(...)` and save with `tempfile.NamedTemporaryFile`.

## Integration Points
- **markitdown**: Central to conversion logic. If updating, test thoroughly.
- **FastAPI**: All API logic is in `app.py`.

## Conventions

- Return JSON responses for all endpoints except the root form.
- Use temporary files for intermediate PDF storage.
- Keep endpoints simple and focused.

---
For questions or unclear patterns, review `app.py` and `README.md` for current conventions. Extend functionality by following FastAPI and Python best practices as exemplified in this codebase.
