#!/usr/bin/env python3
"""
Debug script to identify import issues
"""
import sys
import traceback

def test_import(module_name, description):
    try:
        exec(f"import {module_name}")
        print(f"✅ {description}: {module_name}")
        return True
    except Exception as e:
        print(f"❌ {description}: {module_name}")
        print(f"   Error: {e}")
        traceback.print_exc()
        return False

print("🔍 Testing imports step by step...\n")

# Test basic imports
test_import("fastapi", "FastAPI framework")
test_import("sqlalchemy", "SQLAlchemy ORM")
test_import("pydantic", "Pydantic validation")

print("\n🔍 Testing app imports...\n")

# Test app components
test_import("app.database", "Database configuration")
test_import("app.models", "Database models")
test_import("app.schemas", "Pydantic schemas")

print("\n🔍 Testing router imports...\n")

# Test routers
test_import("app.routers.auth", "Auth router")
test_import("app.routers.tasks", "Tasks router")
test_import("app.routers.budget", "Budget router")
test_import("app.routers.ai_agent", "AI agent router")

print("\n🔍 Testing main app import...\n")

# Test main app
print("Attempting to import app.main...")
try:
    import app.main
    print("✅ app.main module imported")
    try:
        from app.main import app
        print("✅ FastAPI app object imported successfully")
        print(f"   App type: {type(app)}")
    except Exception as e:
        print(f"❌ Error importing app object: {e}")
        traceback.print_exc()
except Exception as e:
    print(f"❌ Error importing app.main module: {e}")
    traceback.print_exc()

print("\n🔍 Testing complete!")