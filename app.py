
from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_db_connection
import time

app = Flask(__name__)
CORS(app, expose_headers=["Idempotency-Key"])


@app.route("/")
def home():
    return jsonify({"message": "Flash Sale API is running"})


@app.route("/api/products")
def get_products():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, price, stock FROM products"
        )
        products = cursor.fetchall()

        return jsonify(products)

    except Exception:
        app.logger.exception("Failed to load products")
        return jsonify({
            "message": "Unable to load products"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.route("/api/orders")
def get_orders():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                o.id AS order_id,
                o.product_id,
                o.quantity,
                p.name AS product_name,
                p.price
            FROM orders o
            JOIN products p ON o.product_id = p.id
            ORDER BY o.id DESC
        """)

        orders = cursor.fetchall()
        return jsonify(orders)

    except Exception:
        app.logger.exception("Failed to load orders")
        return jsonify({
            "message": "Unable to load orders"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.route("/api/buy", methods=["POST"])
def buy_product():
    request_key = request.headers.get(
        "Idempotency-Key", ""
    ).strip()

    if not request_key or len(request_key) > 100:
        return jsonify({
            "success": False,
            "message": "A valid Idempotency-Key header is required."
        }), 400

    # Retry a deadlocked transaction at most three times.
    for attempt in range(3):
        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            connection.start_transaction()
            cursor = connection.cursor()

            # Always lock the product row first.
            cursor.execute(
                "SELECT stock FROM products WHERE id = %s FOR UPDATE",
                (1,)
            )
            product = cursor.fetchone()

            if product is None:
                connection.rollback()
                return jsonify({
                    "success": False,
                    "message": "Product not found."
                }), 404

            # If this request was already processed, return its order.
            cursor.execute(
                "SELECT id FROM orders WHERE request_key = %s",
                (request_key,)
            )
            existing_order = cursor.fetchone()

            if existing_order:
                connection.commit()
                return jsonify({
                    "success": True,
                    "message": "This purchase was already processed.",
                    "order_id": existing_order[0]
                }), 200

            # Never allow stock to become negative.
            if product[0] <= 0:
                connection.rollback()
                return jsonify({
                    "success": False,
                    "message": "Sorry, product is out of stock!"
                }), 409

            cursor.execute(
                """
                UPDATE products
                SET stock = stock - 1
                WHERE id = %s AND stock > 0
                """,
                (1,)
            )

            if cursor.rowcount != 1:
                connection.rollback()
                return jsonify({
                    "success": False,
                    "message": "Sorry, product is out of stock!"
                }), 409

            # Insert the order in the same transaction.
            cursor.execute(
                """
                INSERT INTO orders
                    (product_id, quantity, request_key)
                VALUES (%s, %s, %s)
                """,
                (1, 1, request_key)
            )

            order_id = cursor.lastrowid

            # Stock reduction and order insertion commit together.
            connection.commit()

            return jsonify({
                "success": True,
                "message": "Order placed successfully!",
                "order_id": order_id
            }), 201

        except Exception as error:
            if connection and connection.is_connected():
                connection.rollback()

            error_number = getattr(error, "errno", None)

            # MySQL 1213 = deadlock; retry with a short delay.
            if error_number == 1213 and attempt < 2:
                app.logger.warning(
                    "Deadlock detected; retry attempt %s",
                    attempt + 1
                )
                time.sleep(0.1 * (attempt + 1))
                continue

            # MySQL 1062 = duplicate unique key.
            if error_number == 1062:
                try:
                    if connection and connection.is_connected():
                        cursor.execute(
                            """
                            SELECT id
                            FROM orders
                            WHERE request_key = %s
                            """,
                            (request_key,)
                        )
                        existing_order = cursor.fetchone()

                        if existing_order:
                            return jsonify({
                                "success": True,
                                "message": (
                                    "This purchase was already processed."
                                ),
                                "order_id": existing_order[0]
                            }), 200
                except Exception:
                    app.logger.exception(
                        "Failed to retrieve existing order"
                    )

            app.logger.exception("Purchase failed")

            return jsonify({
                "success": False,
                "message": "Unable to place order. Please try again."
            }), 500

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    return jsonify({
        "success": False,
        "message": "Purchase could not be processed after retries."
    }), 503


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
