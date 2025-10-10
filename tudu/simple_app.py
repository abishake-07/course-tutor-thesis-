from fastapi import FastAPI

# Simple test app
app = FastAPI(title="Tudu Test", description="Testing basic FastAPI setup")

@app.get("/")
async def root():
    return {"message": "Hello, Tudu is working!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Test endpoint
@app.get("/test")
async def test():
    return {"test": "success", "message": "Basic FastAPI is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)