import databases
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import os
from google.cloud.sql.connector import Connector, IPTypes
import os

def getconn() -> sqlalchemy.engine.base.Engine:
    connector = Connector()

    def connect() -> None:
        return connector.connect(
            os.environ["INSTANCE_CONNECTION_NAME"],
            "pg8000",
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"],
            db=os.environ["DB_NAME"],
            ip_type=IPTypes.PUBLIC,
        )

    # Create the SQLAlchemy engine using the connector
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=connect,
    )

    return pool

# Create the engine
engine = getconn()


def connect_cloud_sql() -> sqlalchemy.engine.base.Engine:
    """Initializes a TCP connection pool for a Cloud SQL instance of Postgres."""
    db_user = os.environ["DB_USER"]  # e.g. 'my-database-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-database-password'
    db_name = os.environ["DB_NAME"]  # e.g. 'my-database'
    db_host = os.environ["DB_HOST"]  # Public IP of the Cloud SQL instance

    # Create the connection pool using SQLAlchemy
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+psycopg2",  # Using psycopg2 as the database adapter
            username=db_user,
            password=db_pass,
            host=db_host,  # Use the public IP address here
            port=5432,  # Default port for PostgreSQL
            database=db_name,
        ),
        # Other engine configurations as needed
    )
    return pool

# Create the engine
#engine = connect_cloud_sql()





# #DATABASE_URL = "postgresql://postgres:Pokemon492#@localhost/Product" #for testing local
# #DATABASE_URL = "postgresql+psycopg2://yoke492:Pokemon492#@/Product?host=/cloudsql/total-method-413610:asia-south2:ondc-hackathon"

#connecting railywway postgres 
# DATABASE_URL = os.getenv("DB_URL") 
# engine = sqlalchemy.create_engine(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# # Bind the sessionmaker to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# testing conneciton
# engine = sqlalchemy.create_engine(DATABASE_URL)


# try:
#     connection = engine.connect()
#     print("Connection to the database successful!")
#     connection.close()
# except Exception as e:
#     print(f"Error connecting to the database: {e}")