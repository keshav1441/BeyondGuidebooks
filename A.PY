import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
def test_snowflake_connection():
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA')
    )
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM SITES"
        cursor.execute(query)

        # Fetch all data
        data = cursor.fetchall()

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Convert to DataFrame for easy viewing
        df = pd.DataFrame(data, columns=columns)

        print("Data from Snowflake SITES table:")
        print(df)
        
        return df

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    df = test_snowflake_connection()
    print(df)

