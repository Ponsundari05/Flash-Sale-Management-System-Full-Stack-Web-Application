Flash Sale Management System
A simple e-commerce style website application which allows users to view products, purchase them while stock lasts, and view their order history. This showcases how to make a REST API, using relational databases, transactions and safely handle concurrent purchase requests.

1. Overview
During a flash sale there will be many users wanting to purchase the same product. We need to ensure we do not allow the stock to go below zero and have duplicate orders if they attempt to purchase again.

The project consists of:
- Front end written with React to display product information, pricing, stock levels and order history.
- API written with Flask. This can be used to view product/order information as well as purchasing items.
- MySQL database for storing stock levels and order information.
- Logic to ensure transactions are atomic and rows are locked.
- Idempotency keys to prevent multiple requests being made to purchase an item.

2. Main Features
- View the featured product, price, and available stock.
- Place a purchase using the Buy Now button.
- Display purchase success or failure messages.
- Display order history.
- Prevent stock from going below zero through a conditional stock update and transaction logic.
- Handle simultaneous purchase requests safely using a product-row lock.
- Use an idempotency key so a retry with the same key does not create a second order.
- Return an out-of-stock response when inventory is exhausted.

3. Database Design
This application contains a MySQL database called flash_sale_db.

products table
This table contains product and stock information. This application uses the product ID 1 for the featured purchase endpoint.

Columns:
id (primary key)
name
price
stock

orders table
This table contains data about completed purchases.

Columns:
id - (primary key)
product_id - (the product id of this purchase)
quantity - (how much was purchased)
request_key - (the idempotency key for this purchase)

- If there are any additional columns please use your real database table definitions.
- The following indexes have been confirmed using MySQL Workbench.
- products table has a primary key index on the id column.
- orders table has a primary key index on the id column.
- orders table has a unique index on the request_key column.
- orders table has an index on the product_id column.
- The unique index on the request_key column helps ensure that there are no duplicate request keys. The index on the product_id column can help when querying orders by product.

4. Backend API Endpoints
Method	    Endpoint	      Purpose
GET	          /	              Backend health check
GET	         /api/products	  Retrieve product information
GET	        /api/orders	      Retrieve order history
POST	    /api/buy	      Attempt to purchase the featured product


Buy endpoint

Requires Idempotency-Key header.

Example:

Idempotency-Key: a-unique-request-key

Possible responses:

201 - Order was created.

200 - Request was already made with same key. Return the already created order.

400 - No/Invalid idempotency key.

409 - Product not in stock.

500 - Unexpected server/database error.


5. Concurrency and preventing overselling

Locking rows
- When selecting the quantity of a product from the database we will lock it within a transaction by using 
SELECT stock FROM products 
WHERE id = 1
FOR UPDATE. This means any other transactions trying to purchase this row will be held up.

Conditional Update
- We perform a conditional update on the database. This is done using:

UPDATE products 
SET stock = stock - 1 
WHERE id = 1 AND stock > 0;

This will only decrease the stock if there is still stock left.

Transactions
- We carry out the updating of the stock and inserting of orders within a transaction. If it is successful we commit the transaction. If not we roll it back.

Idempotency
- When an attempt to buy is made the frontend will generate a unique Idempotency-Key. If another transaction is made with the same key the backend will return the previous order.


6. Setup and Execution

Requirements:
- Python
- Node.js and npm
- MySQL 

1. Database Setup.
- Launch MySQL.
- Create or choose the database "flash_sale_db".
- Ensure that there are tables called products - and orders within your database and that they have the required columns.
- Add a record to the product table.
- Set up your credentials to connect to the database in backend/db.py.
- Don’t include actual passwords or secrets in your repository.

2. Launching the Flask backend.
In the backend folder open a terminal. Assuming you have the virtual environment for the project in Windows PowerShell:

.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

Your backend will be running on:
http://127.0.0.1:5000

3. Launching the React frontend.

Open another terminal and navigate to the frontend folder. Then type:

- npm install

- npm run dev

A URL will be shown for you to open locally.

Currently the frontend has the backend API base URL of http://127.0.0.1:5000 but if your backend is running somewhere else then you’ll need to change this in frontend/src/App.jsx.

7. Testing and Results
A. Idempotency test
The same Idempotency-Key was sent twice.

Observed result:
- First request: HTTP 201, order ID 67.
- Second request: HTTP 200, same order ID 67.
- MySQL verification showed exactly one order for the test request key.
This demonstrates that a retry with the same key did not create a second order.

B. Concurrent purchase test
- The Python concurrency test sent 20 purchase requests using 20 worker threads. Each request used a different unique idempotency key. With stock reset to 5 for the test, the observed result was:

| Metric                  | Result| 
| Total requests          | 20 |
| Successful orders       | 5  |
| Out-of-stock responses  | 15 |
| Other errors            |  0 |

8. Conclusion
- The Flash Sale Management System has shown a simple example of a full stack e-commerce application using React, Flask and MySQL. This includes displaying products, purchasing items, storing order history, indexing the database, transactions, row level locking, conditional inventory updates and idempotency. The testing has been recorded to show how duplicate requests are handled and overselling avoided.