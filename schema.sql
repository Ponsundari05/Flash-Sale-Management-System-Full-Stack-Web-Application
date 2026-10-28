CREATE DATABASE flash_sale_db;

USE flash_sale_db;

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    CHECK (stock >= 0)
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    status VARCHAR(30) NOT NULL DEFAULT 'CONFIRMED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(id),

    CHECK (quantity > 0)
);

INSERT INTO products (name, price, stock)
VALUES ('Smartphone', 15000.00, 500);

SELECT * FROM products;

SELECT * FROM orders;

DESCRIBE orders;

USE flash_sale_db;

UPDATE products
SET stock = 50
WHERE id = 1;

SELECT id, name, stock
FROM products;

ALTER TABLE orders
ADD COLUMN request_key VARCHAR(100) NULL;

CREATE UNIQUE INDEX idx_orders_request_key
ON orders(request_key);

SHOW INDEX FROM products;
SHOW INDEX FROM orders;

SELECT * FROM orders
ORDER BY id DESC
LIMIT 10;


SELECT id, name, stock
FROM products
WHERE id = 1;

SELECT id, product_id, quantity, status, request_key
FROM orders
WHERE id >= 62
ORDER BY id DESC;

SELECT COUNT(*) AS order_count
FROM orders
WHERE request_key = 'duplicate-test-001';