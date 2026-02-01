# """
# Phone Repair Advisor Expert System
# Entry point for the application
# """

# from app import create_app
# from app.extensions import db
# import os

# app = create_app(os.getenv('FLASK_ENV', 'development'))

# @app.cli.command()
# def init_db():
#     """Initialize the database with tables"""
#     print("Creating database tables...")
#     db.create_all()
#     print("Database tables created successfully!")

# @app.cli.command()
# def drop_db():
#     """Drop all database tables"""
#     print("Dropping all database tables...")
#     db.drop_all()
#     print("All database tables dropped successfully!")


    
# def cli_main():
#     app.run(debug=True, host='0.0.0.0', port=5000)

# if __name__ == '__main__':
#     cli_main()





"""
Phone Repair Advisor Expert System
Entry point for the application
"""

from app import create_app
from app.extensions import db
import os

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

# CLI commands to initialize or drop DB
@app.cli.command()
def init_db():
    """Initialize the database with tables"""
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")

@app.cli.command()
def drop_db():
    """Drop all database tables"""
    print("Dropping all database tables...")
    db.drop_all()
    print("All database tables dropped successfully!")

# Only include this for local development
if __name__ == '__main__':
    app.run(debug=True)  # Remove host and port; let Flask pick default 127.0.0.1:5000
