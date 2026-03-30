# multi-stage-test-python-codex

Deployable Python web app for an e-commerce company using Flask and a multi-stage Docker build.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

## Build and run container

```bash
docker build -t ecommerce-python-app .
docker run --rm -p 8000:8000 ecommerce-python-app
```

## Example API calls

```bash
curl http://localhost:8000/products
curl -X POST http://localhost:8000/cart/customer-1/items \
  -H 'Content-Type: application/json' \
  -d '{"product_id": 1, "quantity": 2}'
curl http://localhost:8000/cart/customer-1
```
