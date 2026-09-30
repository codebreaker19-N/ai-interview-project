from sqlalchemy import text

from app.database.database import engine


with engine.connect() as connection:
    connection.execute(
        text("""
            ALTER TABLE attempts
            ADD COLUMN IF NOT EXISTS session_id INTEGER
            REFERENCES interview_sessions(id)
        """)
    )

    connection.commit()

print("session_id column added successfully")