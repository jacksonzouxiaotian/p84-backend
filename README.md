# 9900

A web application backend API that helps research students organize and track their research progress.

## Docker Quickstart

This app can be run completely using `Docker` and `docker compose`. **Using Docker is recommended, as it guarantees the application runs using compatible versions of Python**.

There are two main services:

- `flask-dev` — run the development version of the app  
- `flask-prod` — run the production version of the app

To run the development version:

```bash
docker compose up flask-dev
```

To run the production version:

```bash
docker compose up flask-prod
```

The list of `environment:` variables in the `docker compose.yml` file takes precedence over any variables specified in `.env`.

To run any commands using the `Flask CLI`:

```bash
docker compose run --rm manage <COMMAND>
```

For example, to initialize and migrate the database:

```bash
docker compose run --rm manage db init
docker compose run --rm manage db migrate
docker compose run --rm manage db upgrade
```

## Running Locally

If you cannot use Docker, follow these steps to set up the environment locally:

```bash
cd research_assistant
pip install -r requirements/dev.txt
```

Run the Flask server locally:

```bash
flask run
```

By default, it will be accessible at `http://localhost:5000`.

### Database Initialization (Locally)

After installing your database server, run:

```bash
flask db init
flask db migrate
flask db upgrade
```

to create database tables and apply migrations.

## Deployment

When using Docker, reasonable production defaults are set in `docker compose.yml`:

```text
FLASK_ENV=production
FLASK_DEBUG=0
```

Start the app in production mode with:

```bash
docker compose up flask-prod
```

If running without Docker, set environment variables accordingly and run:

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export DATABASE_URL="<YOUR DATABASE URL>"
flask run
```

## Shell

To open an interactive Flask shell:

```bash
docker compose run --rm manage shell
# Or if running locally without Docker:
flask shell
```

## Running Tests and Linter

Run all tests:

```bash
docker compose run --rm manage test
# Or locally:
flask test
```

Run the linter (to check and fix style issues):

```bash
docker compose run --rm manage lint
# Or locally:
flask lint
```

Add `--check` to the lint command to only check without fixing.

## Database Migrations

Whenever you need to make database schema changes, generate a migration:

```bash
docker compose run --rm manage db migrate
# Or locally:
flask db migrate
```

Apply the migration:

```bash
docker compose run --rm manage db upgrade
# Or locally:
flask db upgrade
```

If deploying remotely (e.g., on Heroku), add the migrations folder to version control after migration:

```bash
git add migrations/*
git commit -m "Add migrations"
```

Ensure `migrations/versions` is not empty before committing.
