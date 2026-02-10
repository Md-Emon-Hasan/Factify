import os
# Disable OneDNN optimizations to avoid [Errno 22] Invalid argument on Windows
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
