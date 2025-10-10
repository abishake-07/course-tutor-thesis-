from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Tudu - Smart Task & Budget Manager",
    description="A FastAPI application for task management and budget tracking with AI integration",
    version="1.0.0"
)

@app.get("/")
async def read_root():
    """Home page"""
    return {"message": "Welcome to Tudu!", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Tudu API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)