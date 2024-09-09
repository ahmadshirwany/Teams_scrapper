import pandas as pd
from sqlalchemy import create_engine, text


class DataFrameToMySQL:
    def __init__(self, host, database, user, password, table_name):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.table_name = table_name
        self.engine = None

    def create_connection(self):
        connection_string = f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.database}"
        self.engine = create_engine(connection_string)
        print("Connection to the MySQL database was successful.")

    def create_table_if_not_exists(self, df, unique_key):
        if self.engine is None:
            raise Exception("Connection to the MySQL database has not been established.")
        columns = ', '.join([f"`{col}` VARCHAR(255)" for col in df.columns])
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            {columns},
            PRIMARY KEY (`{unique_key}`)
        );
        """
        with self.engine.connect() as conn:
            conn.execute(text(create_table_sql))
        print(f"Table {self.table_name} checked/created successfully.")

    def upsert_table(self, df, unique_key):
        if self.engine is None:
            raise Exception("Connection to the MySQL database has not been established.")
        for _, row in df.iterrows():
            columns = ', '.join([f"`{col}`" for col in df.columns])
            values = ', '.join([f"'{str(val)}'" for val in row.values])
            update_clause = ', '.join([f"`{col}` = VALUES(`{col}`)" for col in df.columns if col != unique_key])
            sql_query = text(f"""
                INSERT INTO {self.table_name} ({columns})
                VALUES ({values})
                ON DUPLICATE KEY UPDATE {update_clause};
            """)
            with self.engine.connect() as conn:
                conn.execute(sql_query)

        print(f"DataFrame has been successfully upserted into the {self.table_name} table.")

    def save_dataframe(self, df, unique_key):
        self.create_table_if_not_exists(df, unique_key)
        self.upsert_table(df, unique_key)

if __name__ == "__main__":
    data = {'id': [1, 2, 3], 'name': ['John', 'Doe', 'Alice'], 'age': [26, 31, 23],
            'city': ['New York', 'Los Angeles', 'San Francisco']}
    df = pd.DataFrame(data)
    mysql_uploader = DataFrameToMySQL(
        host='localhost',
        database='your_database_name',
        user='your_mysql_username',
        password='your_mysql_password',
        table_name='your_table_name'
    )

    # Create a connection
    mysql_uploader.create_connection()

    # Save DataFrame to MySQL: create the table if not exists, and perform upsert
    mysql_uploader.save_dataframe(df, unique_key='id')
