
from db import get_db_connection

try:
    connection = get_db_connection()
    print("MySQL connected successfully!")

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    connection.close()

except Exception as error:
    print("Connection error:", error)

