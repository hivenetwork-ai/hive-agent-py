from typing import List, Optional
from pydantic import BaseModel


class ToolInstallRequest(BaseModel):
    url: str
    functions: List[str]
    install_path: Optional[str]
