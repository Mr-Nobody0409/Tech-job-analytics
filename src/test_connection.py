from sqlalchemy import create_engine, text

from config import DATABASE_URL


engine = create_engine(DATABASE_URL)


try:
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT DATABASE();")
        )

        print("Connected to:", result.scalar())

except Exception as error:
    print("Connection failed:")
    print(error)