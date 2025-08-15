import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from taro.cli.sub_cli import SubCli
from taro.utils import get_database_url
import taro.db.models as models


class TaroDropCli(SubCli):
    def get_name(self):
        return "drop"

    def populate_subparser(self, subparser: argparse.ArgumentParser):
        subparser.add_argument(
            "-y", "--yes",
            action="store_true",
            help="Skip confirmation prompt and proceed with drop"
        )

    def run(self, ag):
        # Get database URL
        database_url = get_database_url()

        # Confirmation prompt unless -y flag is provided
        if not ag.yes:
            print(f"WARNING: This will drop all tables from the database.")
            print(f"Database URL: {database_url}")
            confirmation = input("Are you sure you want to proceed? (yes/no): ")
            if confirmation.lower() != "yes":
                print("Operation cancelled.")
                return

        # Create engine
        engine = create_engine(database_url)

        # Drop all tables including alembic_version
        print("Dropping all tables...")
        models.Base.metadata.drop_all(engine)

        # Drop alembic_version table if it exists
        with engine.connect() as connection:
            connection.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
            connection.commit()

        print("All tables dropped successfully (including alembic_version).")
        print("Database is now empty.")
