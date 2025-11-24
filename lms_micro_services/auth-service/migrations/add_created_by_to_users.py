"""
Migration: Add created_by column to users table
Run this script to add the created_by field for tracking which teacher created each student
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """Add created_by column to users table"""
    
    try:
        # Create engine
        engine = create_engine(settings.database_url)
        print("Connected to database successfully")
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'created_by'
            """))
            
            if result.fetchone():
                print("✅ Column 'created_by' already exists")
                return
            
            # Add created_by column
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN created_by INTEGER;
            """))
            
            # Commit the transaction
            conn.commit()
            
            print("✅ Successfully added 'created_by' column to users table")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    print("🔧 Running migration: Add created_by to users table")
    run_migration()
    print("🎉 Migration completed successfully!")
