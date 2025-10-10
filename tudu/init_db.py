"""
Initialize database with default data
"""
from app.database import SessionLocal, engine
from app.models import Base, BudgetCategory

def init_db():
    """Initialize database with default data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if categories already exist
        existing_categories = db.query(BudgetCategory).count()
        
        if existing_categories == 0:
            # Create default budget categories
            default_categories = [
                {"name": "Food & Dining", "description": "Restaurants, groceries, food delivery", "color": "#e74c3c"},
                {"name": "Transportation", "description": "Gas, public transport, car maintenance", "color": "#3498db"},
                {"name": "Entertainment", "description": "Movies, games, hobbies, subscriptions", "color": "#9b59b6"},
                {"name": "Shopping", "description": "Clothing, electronics, general shopping", "color": "#f39c12"},
                {"name": "Bills & Utilities", "description": "Rent, electricity, internet, phone", "color": "#34495e"},
                {"name": "Healthcare", "description": "Medical expenses, insurance, pharmacy", "color": "#2ecc71"},
                {"name": "Education", "description": "Books, courses, tuition, training", "color": "#16a085"},
                {"name": "Travel", "description": "Flights, hotels, vacation expenses", "color": "#8e44ad"},
                {"name": "Other", "description": "Miscellaneous expenses", "color": "#95a5a6"}
            ]
            
            for cat_data in default_categories:
                category = BudgetCategory(**cat_data)
                db.add(category)
            
            db.commit()
            print("✅ Default budget categories created successfully!")
        else:
            print("ℹ️  Database already initialized with categories")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()