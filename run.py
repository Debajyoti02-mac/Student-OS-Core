import os
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", settings.PORT))
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=port,
        reload=False if os.getenv("RENDER") else True
    )
