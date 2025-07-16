"""
Create initial database migration
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic.config import Config
from alembic import command

def create_initial_migration():
    """Create initial database migration"""
    # Set up Alembic config
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    
    # Create initial migration
    command.revision(
        alembic_cfg,
        message="Initial migration - create all tables",
        autogenerate=True
    )
    
    print("Initial migration created successfully!")

if __name__ == "__main__":
    create_initial_migration()