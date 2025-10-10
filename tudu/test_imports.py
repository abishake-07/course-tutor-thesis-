"""
Test the application imports and basic functionality
"""
try:
    print("Testing imports...")
    
    from app.main import app
    print("✅ Main app imported successfully")
    
    from app.models import User, Task, BudgetItem
    print("✅ Models imported successfully")
    
    from app.schemas import UserCreate, TaskCreate
    print("✅ Schemas imported successfully")
    
    from app.database import get_db, engine
    print("✅ Database imported successfully")
    
    print("\n🎉 All imports successful!")
    print("You can now run the application with: python main.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")