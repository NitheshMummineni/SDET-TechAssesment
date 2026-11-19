# SDET Technical Assessment — JSONPlaceholder API Automation

## Overview

This project is a maintainable REST API automation framework built for the SDET technical assessment. It validates the public [JSONPlaceholder](https://jsonplaceholder.typicode.com/) `GET /posts` endpoints using **Python**, **Pytest**, and **Requests**, with layered configuration, a reusable API client, fixtures, and HTML/JUnit reporting.

## Assessment Requirements Covered

| Requirement | Implementation |
|-------------|----------------|
| Python + Pytest + Requests | `requirements.txt`, `tests/` |
| Endpoint: `/posts` | `tests/test_posts.py` |
| Response attribute validation | TC_01–TC_07, TC_05 |
| Positive & negative scenarios | `@pytest.mark.positive` / `negative` |
| Maintainable framework | `config/`, `utils/api_client.py`, `conftest.py` |
| Reporting (terminal, JUnit, HTML) | `pytest.ini`, `reports/` |
| README documentation | This file |

## Technology Stack

- **Python** 3.10+
- **Pytest** — test runner, markers, parametrization, fixtures
- **Requests** — HTTP client
- **pytest-html** — HTML execution report

## Framework Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  test_posts │────▶│ APIClient    │────▶│ jsonplaceholder API │
│  (assertions)│     │ (utils)      │     └─────────────────────┘
└──────▲──────┘     └──────▲───────┘
       │                   │
       │            ┌──────┴───────┐
       │            │ config.py    │
       │            │ (base URL,   │
       │            │  timeouts)   │
       └────────────┤ conftest.py  │
                    │ (fixtures)   │
                    └──────────────┘
```

- **Tests** — assertions only; no raw URL strings scattered in every test.
- **APIClient** — HTTP verbs, timeouts, headers, query params, exception wrapping.
- **Config** — central base URL and thresholds (overridable via environment variables).
- **Fixtures** — shared client, settings, and cached `posts_list`.

## Folder Structure

```
SDET-TechAssessment/
├── config/
│   ├── __init__.py
│   └── config.py
├── utils/
│   ├── __init__.py
│   └── api_client.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_posts.py
├── reports/
│   ├── .gitkeep
│   ├── report.html          (generated after test run)
│   └── junit.xml            (generated after test run)
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

## Prerequisites

- Python **3.10** or newer
- `pip` (included with Python)
- Internet access to reach `https://jsonplaceholder.typicode.com`

### Verify Python Installation

```bash
python3 --version
```

Expected: `Python 3.10.x` or higher.

## Setup

### 1. Navigate to the project

```bash
cd SDET-TechAssessment
```

(Use the full path to this folder on your machine if needed.)

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

**Windows (Command Prompt):**

```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The `truststore` package is included so Python uses your **macOS system certificate store** (same as Safari/curl when corporate TLS inspection is enabled). You should not need to disable TLS verification for normal runs.

## Running Tests

### Execute all tests

```bash
pytest
```

### Execute a specific test file

```bash
pytest tests/test_posts.py
```

### Execute a single test case

```bash
pytest tests/test_posts.py::TestPostsPositive::test_tc_01_get_posts_returns_http_200
```

### Execute only positive tests

```bash
pytest -m positive
```

### Execute only negative tests

```bash
pytest -m negative
```

### Generate HTML report (default via `pytest.ini`)

```bash
pytest --html=reports/report.html --self-contained-html
```

### Generate JUnit XML report (default via `pytest.ini`)

```bash
pytest --junitxml=reports/junit.xml
```

Both reports are written under `reports/` on every default `pytest` run.

## Interpreting Results

- **Terminal**: `passed` / `failed` / `skipped` counts and assertion details.
- **HTML** (`reports/report.html`): Open in a browser for per-test status, duration, and logs.
- **JUnit XML** (`reports/junit.xml`): Use in CI tools (Jenkins, GitLab, Azure DevOps, etc.).

Exit code `0` means all tests passed; non-zero means at least one failure.

## Test Scenarios

| ID | Test name (summary) | Type | Description |
|----|---------------------|------|-------------|
| TC_01 | `test_tc_01_get_posts_returns_http_200` | Positive | `GET /posts` returns HTTP 200 |
| TC_02 | `test_tc_02_response_content_type_is_json` | Positive | `Content-Type` includes `application/json` |
| TC_03 | `test_tc_03_response_body_is_non_empty_list` | Positive | Body is a non-empty JSON array |
| TC_04 | `test_tc_04_each_post_contains_required_fields` | Positive | Each post has `userId`, `id`, `title`, `body` (parametrized) |
| TC_05 | `test_tc_05_post_field_data_types` | Positive | Field types match int/str expectations (parametrized) |
| TC_06 | `test_tc_06_post_ids_are_unique` | Positive | All `id` values in list are unique |
| TC_07 | `test_tc_07_get_single_post_by_id` | Positive | `GET /posts/1` returns expected fields and `id` |
| TC_08 | `test_tc_08_get_nonexistent_post_returns_404_empty_json` | Negative | `GET /posts/9999` → 404 and `{}` |
| TC_09 | `test_tc_09_invalid_path_returns_404` | Negative | Invalid paths → 404 and `{}` (parametrized) |
| TC_10 | `test_tc_10_response_time_within_threshold` | Positive | Response time ≤ configurable threshold (default 5000 ms) |

### Observed API behavior (negative tests)

JSONPlaceholder does **not** return real 404 HTML pages for missing posts. Verified behavior:

- `GET /posts/9999` → **404** with JSON body **`{}`**
- `GET /posts/not-a-number` → **404** with **`{}`**
- `GET /invalid/posts` → **404** with **`{}`**

Assertions match this actual behavior.

## Configuration (optional)

Environment variables override defaults in `config/config.py`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_BASE_URL` | `https://jsonplaceholder.typicode.com` | API host |
| `API_REQUEST_TIMEOUT` | `30` | Request timeout (seconds) |
| `API_RESPONSE_TIME_THRESHOLD_MS` | `5000` | TC_10 max response time (ms) |
| `API_CA_BUNDLE` | (unset) | Path to PEM file for corporate TLS inspection CAs |
| `API_SSL_VERIFY` | `true` | Set to `false` only for local debugging (not recommended) |

Example:

```bash
export API_RESPONSE_TIME_THRESHOLD_MS=8000
pytest -m positive
```

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|--------------|-----|
| `ModuleNotFoundError: config` | Wrong working directory | Run `pytest` from `SDET-TechAssessment/` root |
| `ConnectionError` / timeouts | No network or API down | Check connectivity; increase `API_REQUEST_TIMEOUT` |
| `SSLCertVerificationError` | Corporate proxy / missing CA | Re-run `pip install -r requirements.txt` (includes `truststore`). If it persists, export corporate root CA: `export API_CA_BUNDLE=/path/to/ca.pem`. Last resort only: `export API_SSL_VERIFY=false` |
| `pytest: command not found` | venv not active or deps missing | Activate venv; `pip install -r requirements.txt` |
| HTML/XML report errors | Missing `reports/` | Directory exists with `.gitkeep`; created automatically |
| Flaky TC_10 | Slow network | Raise `API_RESPONSE_TIME_THRESHOLD_MS` |

## Deactivate Virtual Environment

```bash
deactivate
```

## License

Assessment submission — internal/educational use.