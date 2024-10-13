import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

def connect_to_mysql():
    try:
        load_dotenv("D:\Project\movie-rec-system\.env")
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if conn.is_connected():
            print("Connected to MySQL")
            return conn
    except Error as e:
        print(f"error: {e}")
        return None
    
def create_table(connection): 
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS credits")
    create_table_query = """
    CREATE TABLE credits (
        cast TEXT, 
        crew LONGTEXT, 
        id INT PRIMARY KEY
    ) 
    """
    cursor.execute(create_table_query) 
    connection.commit()
    print("Table 'credits' created successfully") 

def insert_data(connection, data): 
    cursor = connection.cursor()
    success_count = 0  # Đếm số hàng chèn thành công
    error_count = 0    # Đếm số hàng thất bại

    for index, row in data.iterrows(): 
        # Giới hạn chiều dài của crew
        insert_query = """
            INSERT INTO credits (cast, crew, id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
            cast = VALUES(cast), crew = VALUES(crew)
        """
        try:
            cursor.execute(insert_query, (row['cast'], row['crew'], row['id']))
            success_count += 1  # Tăng số hàng chèn thành công
        except mysql.connector.Error as err:
            print(f"Error inserting row {index}: {err}")  # In lỗi nếu có
            error_count += 1  # Tăng số hàng thất bại
            
    connection.commit()
    print(f"{success_count} rows inserted successfully, {error_count} rows failed to insert.")

def main(): 
    file_path = 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/credits.csv'
    df = pd.read_csv(file_path)

    # Kết nối đến MySQL
    connection = connect_to_mysql()
    if connection:
        create_table(connection)  
        insert_data(connection, df)  
        connection.close()

if __name__ == "__main__":
    main()