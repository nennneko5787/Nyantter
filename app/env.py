from typing import Optional, Any
import os
if os.path.isfile(".env"):
    from dotenv import load_dotenv
    load_dotenv(verbose=True)

def getenv(name: str) -> Optional[str]:
    return os.getenv(name)