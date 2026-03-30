from flask import Flask, jsonify, request

app = Flask(__name__)

PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones", "price": 79.99, "inventory": 25},
    {"id": 2, "name": "Mechanical Keyboard", "price": 119.00, "inventory": 12},
    {"id": 3, "name": "4K Monitor", "price": 299.50, "inventory": 7},
]

CARTS = {}


@app.get("/")
def health():
    return jsonify(
        {
            "service": "ecommerce-catalog-api",
            "status": "ok",
            "message": "Welcome to the e-commerce API",
        }
    )


@app.get("/products")
def list_products():
    return jsonify({"products": PRODUCTS})


@app.post("/cart/<customer_id>/items")
def add_to_cart(customer_id: str):
    payload = request.get_json(silent=True) or {}
    product_id = payload.get("product_id")
    quantity = int(payload.get("quantity", 1))

    product = next((item for item in PRODUCTS if item["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    if quantity < 1:
        return jsonify({"error": "Quantity must be at least 1"}), 400

    if quantity > product["inventory"]:
        return jsonify({"error": "Insufficient inventory"}), 400

    customer_cart = CARTS.setdefault(customer_id, [])
    customer_cart.append(
        {
            "product_id": product["id"],
            "name": product["name"],
            "quantity": quantity,
            "unit_price": product["price"],
            "line_total": round(product["price"] * quantity, 2),
        }
    )

    return jsonify({"customer_id": customer_id, "items": customer_cart}), 201


@app.get("/cart/<customer_id>")
def get_cart(customer_id: str):
    items = CARTS.get(customer_id, [])
    total = round(sum(item["line_total"] for item in items), 2)
    return jsonify({"customer_id": customer_id, "items": items, "total": total})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
