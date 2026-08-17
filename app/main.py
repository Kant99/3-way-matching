from fastapi import FastAPI


app = FastAPI(
    title="Agentic 3-Way Matching POC",
    description="Agentic automation for Contract, Purchase Order, and Invoice 3-way matching.",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "agentic-3way-matching",
        "version": "0.1.0",
    }