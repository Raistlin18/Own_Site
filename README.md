# Developer Portfolio

A small Django portfolio application that demonstrates server-rendered pages and a product finder backed by a resilient HTML scraper.

## Features

- Responsive portfolio and project pages built with Django templates and Bootstrap 5
- Product search on eMAG
- Product parser isolated from the HTTP layer for testability
- Time-limited external requests, safe fallbacks, and visitor-friendly error messages
- Automated tests for parsing, sorting, input validation, and rendered results

## Technology

- Python
- Django
- Requests
- Beautiful Soup
- Bootstrap 5

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies with `python3 -m pip install -r requirements.txt`.
3. Set the required environment variables. On Linux or macOS:

```bash
export DJANGO_SECRET_KEY="replace-with-a-long-random-secret"
export DJANGO_DEBUG=True
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
```

4. Run migrations with `python3 manage.py migrate`.
5. Start the development server with `python3 manage.py runserver`.
6. Run the test suite with `python3 manage.py test`.

Copy `.env.example` only as a reference for the required variables. Do not commit a real `.env` file or a production secret.

For production, set `DJANGO_DEBUG=False`, configure the public host name in `DJANGO_ALLOWED_HOSTS`, and terminate HTTPS before deploying. Production mode enables HTTPS redirects, secure cookies, and HSTS, including preload settings. Enable it only when every present and future subdomain will support HTTPS.

## Project structure

- `MySite/views.py`: request handling and template rendering
- `MySite/forms.py`: product-search validation
- `MySite/scraper.py`: external request and HTML parsing logic
- `MySite/tests.py`: unit and integration-style Django tests

## Notes

eMAG is an external source and its HTML can change. The parser deliberately skips incomplete results and reports unavailable sources gracefully. For a production system, use eMAG's supported API where available and consider background jobs plus caching for long-running searches.
