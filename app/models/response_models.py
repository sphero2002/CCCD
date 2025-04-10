from typing import TypeVar, Generic, List, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Standard API response model that matches the C# model:
    
    public bool Success { get; set; }
    public string? Message { get; set; }
    public T? Data { get; set; }
    public List<string>? Errors { get; set; }
    """
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    errors: Optional[List[str]] = None