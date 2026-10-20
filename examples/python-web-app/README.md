# Django Docker example

This example runs the existing `devops.wsgi:application` with Gunicorn in a slim Python image as a non-root user. Django settings that vary by environment are supplied at runtime.

## Runtime configuration

Set these environment variables before starting the app:

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | Yes | none | Secret used by Django. The app fails to start if it is empty. |
| `DJANGO_DEBUG` | No | `false` | Enables Django debug mode only when set to a true value. Keep false outside local development. |
| `DJANGO_ALLOWED_HOSTS` | No | empty list | Comma-separated allowed hostnames, such as `localhost,127.0.0.1`. Configure actual hostnames for deployment; do not use `*`. |
| `DJANGO_SECURE_SSL_REDIRECT` | No | `false` | Redirects HTTP to HTTPS when set to a true value. Enable for production behind a correctly configured HTTPS endpoint. |

For a local shell session, generate an ephemeral development secret rather than putting a key in source control:

```sh
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
export DJANGO_SECURE_SSL_REDIRECT=false
```

Never use a development key in production. Supply production secrets through your deployment platform's secret manager, not a Dockerfile, image build argument, or committed `.env` file. Users with access to a local Docker daemon can inspect container environment values, so prefer the runtime secret mechanism provided by your production platform.

## Run locally with Python

From this directory:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
cd devops
python manage.py check
python manage.py runserver 0.0.0.0:8000
```

Open <http://localhost:8000/demo/>. The Django development server is only for local testing; the container uses Gunicorn.

## Build and run the container

From this directory, build and start a local-only image:

```sh
docker build -t django-example:local .
docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
  -e DJANGO_DEBUG=false \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 \
  -e DJANGO_SECURE_SSL_REDIRECT=false \
  django-example:local
```

In another terminal, verify the existing route responds:

```sh
curl -f http://localhost:8000/demo/
```

This is a local HTTP smoke test, not a production configuration. Do not publish the local image or reuse its local environment for a public deployment.

## Production considerations

- Use a strong, unique `DJANGO_SECRET_KEY` from a secret manager. Do not commit credentials or place secrets in the image.
- Set `DJANGO_DEBUG=false` and `DJANGO_ALLOWED_HOSTS` to the exact hostnames serving the application.
- Terminate TLS at a trusted ingress or reverse proxy, set `DJANGO_SECURE_SSL_REDIRECT=true`, and ensure the proxy overwrites `X-Forwarded-Proto` accurately. Django trusts that header through `SECURE_PROXY_SSL_HEADER`; do not expose the app through an untrusted proxy that allows clients to spoof it.
- Keep Django's CSRF middleware enabled. Add any required trusted origins explicitly to deployment configuration rather than weakening CSRF checks.
- Run `python manage.py check --deploy` using production environment settings before deployment. Its security warnings depend on the TLS terminator and the organization's cookie, HSTS, and proxy policies; review and configure each applicable warning rather than suppressing checks.
- The example retains SQLite for simplicity. SQLite is not suitable for multi-instance deployments because each container has its own local database file and writes are not shared. Use a separately managed, durable database before scaling out; database provisioning is intentionally outside this example.
- Gunicorn does not serve Django static files by itself. Configure static-file collection and serving at the deployment layer (for example, through a trusted web server or object storage) before relying on Django admin assets in production.

The local HTTP instructions intentionally disable HTTPS redirects. Production must explicitly enable secure redirects and provide deployment-specific hostnames and secrets.
