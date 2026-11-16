from pathlib import Path
from sqlalchemy import create_engine, event


def open_database(url="sqlite:///seed-stock.db"):
    engine = create_engine(url)
    @event.listens_for(engine, "connect")
    def configure(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")
    migrate(engine)
    return engine


def migrate(engine):
    folder = Path(__file__).resolve().parents[1] / "migrations"
    with engine.begin() as connection:
        connection.exec_driver_sql("CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY)")
        versions = {row[0] for row in connection.exec_driver_sql("SELECT version FROM schema_migrations")}
        for path in sorted(folder.glob("*.sql")):
            version = int(path.stem.split("_")[0])
            if version in versions:
                continue
            for statement in path.read_text().split(";"):
                if statement.strip(): connection.exec_driver_sql(statement)
            connection.exec_driver_sql("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
