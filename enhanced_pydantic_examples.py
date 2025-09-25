"""
Enhanced Pydantic Examples and Context for AI Responses
========================================================

This file contains comprehensive Pydantic examples that should be used to provide
rich context in AI responses about Pydantic questions.
"""

PYDANTIC_COMPREHENSIVE_GUIDE = """
# Complete Pydantic Guide for Python Development

## Overview
Pydantic is a Python library that provides data validation and settings management using Python type annotations. It's particularly powerful for API development, configuration management, and data processing pipelines.

## 1. Basic Usage and Core Concepts

### Simple Model Definition
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    created_at: datetime = datetime.now()

# Usage
user_data = {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
}

user = User(**user_data)
print(user.name)  # John Doe
print(user.model_dump())  # Convert to dict
print(user.model_dump_json())  # Convert to JSON
```

## 2. Advanced Validation with Field()

```python
from pydantic import BaseModel, Field, validator
from typing import List

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Price must be positive")
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.title()
    
    @validator('tags')
    def validate_tags(cls, v):
        return [tag.lower().strip() for tag in v if tag.strip()]

# Usage
product = Product(
    name="laptop computer",
    price=999.99,
    tags=["Electronics", "Computers", " TECH "]
)
print(product.name)  # "Laptop Computer"
print(product.tags)  # ["electronics", "computers", "tech"]
```

## 3. Error Handling Best Practices

```python
from pydantic import ValidationError

def create_user_safely(user_data: dict):
    try:
        user = User(**user_data)
        return {"success": True, "user": user}
    except ValidationError as e:
        return {
            "success": False,
            "errors": e.errors(),
            "message": "Validation failed"
        }

# Example usage
invalid_data = {"id": "not-a-number", "name": "", "email": "invalid-email"}
result = create_user_safely(invalid_data)

if not result["success"]:
    for error in result["errors"]:
        print(f"Field: {error['loc']}, Error: {error['msg']}")
```

## 4. FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    
    class Config:
        from_attributes = True  # For Pydantic v2

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # Pydantic automatically validates the request body
    # Your business logic here
    new_user = UserResponse(
        id=1,
        name=user.name,
        email=user.email,
        age=user.age
    )
    return new_user

@app.get("/users/", response_model=List[UserResponse])
async def get_users():
    # Return a list of users
    return [
        UserResponse(id=1, name="John", email="john@example.com", age=30)
    ]
```

## 5. Configuration Management

```python
from pydantic import BaseSettings, Field
from typing import Optional

class AppSettings(BaseSettings):
    app_name: str = "My Application"
    debug: bool = False
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field(..., env="SECRET_KEY")
    api_key: Optional[str] = Field(None, env="API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Usage
settings = AppSettings()
print(settings.database_url)  # Loaded from environment
```

## 6. Complex Data Structures

```python
from pydantic import BaseModel
from typing import Dict, List, Union
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class OrderItem(BaseModel):
    product_id: int
    name: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class Order(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus = OrderStatus.pending
    items: List[OrderItem]
    shipping_address: Address
    metadata: Dict[str, Union[str, int, float]] = {}
    
    @property
    def total_amount(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

# Usage
order_data = {
    "id": 1,
    "customer_id": 123,
    "status": "processing",
    "items": [
        {"product_id": 1, "name": "Laptop", "quantity": 1, "price": 999.99},
        {"product_id": 2, "name": "Mouse", "quantity": 2, "price": 25.00}
    ],
    "shipping_address": {
        "street": "123 Main St",
        "city": "New York",
        "country": "USA",
        "postal_code": "10001"
    },
    "metadata": {"priority": "high", "gift_wrap": True}
}

order = Order(**order_data)
print(f"Total: ${order.total_amount:.2f}")
```

## 7. Custom Validators and Serializers

```python
from pydantic import BaseModel, validator, root_validator
import re

class UserProfile(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    phone: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            # Remove all non-digit characters
            cleaned = re.sub(r'\D', '', v)
            if len(cleaned) != 10:
                raise ValueError('Phone number must be 10 digits')
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        return v
    
    @root_validator
    def validate_passwords_match(cls, values):
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        if password != confirm_password:
            raise ValueError('Passwords do not match')
        return values

# Usage
profile_data = {
    "username": "john_doe",
    "email": "JOHN@EXAMPLE.COM",
    "password": "securepass123",
    "confirm_password": "securepass123",
    "phone": "555-123-4567"
}

profile = UserProfile(**profile_data)
print(profile.email)  # "john@example.com"
print(profile.phone)  # "(555) 123-4567"
```

## 8. Pydantic v1 vs v2 Key Differences

### Migration Guide
```python
# Pydantic v1 (legacy)
class UserV1(BaseModel):
    name: str
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# Pydantic v2 (current)
from pydantic import ConfigDict

class UserV2(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # replaces orm_mode
        populate_by_name=True   # replaces allow_population_by_field_name
    )
    name: str

# Method name changes
# v1: dict(), json()
# v2: model_dump(), model_dump_json()

user = UserV2(name="John")
print(user.model_dump())      # v2 way
print(user.model_dump_json()) # v2 way
```

## 9. Testing with Pydantic

```python
import pytest
from pydantic import ValidationError

def test_user_creation():
    user_data = {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }
    user = User(**user_data)
    assert user.name == "Test User"
    assert user.email == "test@example.com"

def test_user_validation_errors():
    with pytest.raises(ValidationError) as exc_info:
        User(id="invalid", name="", email="not-an-email")
    
    errors = exc_info.value.errors()
    assert len(errors) == 3  # id, name, email errors
    
    # Check specific error types
    error_fields = [error['loc'][0] for error in errors]
    assert 'id' in error_fields
    assert 'email' in error_fields
```

## 10. Performance Tips

```python
# Use __slots__ for better memory usage
class OptimizedModel(BaseModel):
    __slots__ = ('__dict__', '__pydantic_fields_set__', '__pydantic_extra__')
    
    name: str
    value: int

# Disable validation for trusted data
trusted_data = {"name": "John", "value": 42}
user = User.model_validate(trusted_data, strict=False)

# Use model_construct for even faster creation (skips validation)
fast_user = User.model_construct(name="John", value=42)
```

## Common Pitfalls and Solutions

1. **Mutable Default Arguments**
```python
# Wrong
class BadModel(BaseModel):
    items: List[str] = []  # Dangerous!

# Correct
class GoodModel(BaseModel):
    items: List[str] = Field(default_factory=list)
```

2. **Circular Imports**
```python
# Use string annotations for forward references
class Node(BaseModel):
    value: int
    children: List['Node'] = []

# Update forward references
Node.model_rebuild()
```

3. **Validation Order**
```python
# Validators run in definition order
class MyModel(BaseModel):
    value: str
    
    @validator('value', pre=True)
    def convert_to_string(cls, v):
        return str(v)
    
    @validator('value')
    def validate_string(cls, v):
        if len(v) < 3:
            raise ValueError('Too short')
        return v
```

## Resources and Next Steps

- **Official Documentation**: https://docs.pydantic.dev/
- **FastAPI Integration**: https://fastapi.tiangolo.com/
- **Type Hints Guide**: https://docs.python.org/3/library/typing.html
- **JSON Schema**: https://json-schema.org/

## Best Practices Summary

1. Use descriptive field names and docstrings
2. Implement proper error handling with try/catch blocks
3. Use validators for complex business logic
4. Leverage Field() for constraints and metadata
5. Test your models thoroughly
6. Use appropriate types and Optional where needed
7. Handle version migrations carefully
8. Consider performance implications for large datasets
9. Use configuration classes for application settings
10. Document your models and their expected behavior
"""

def get_context_specific_examples(query_type: str) -> str:
    """Get specific examples based on the type of Pydantic question"""
    
    examples = {
        "validation": """
# Data Validation Examples
from pydantic import BaseModel, ValidationError, validator

class DataModel(BaseModel):
    value: int
    
    @validator('value')
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('must be positive')
        return v

try:
    model = DataModel(value=-1)
except ValidationError as e:
    print(e.errors())
""",
        
        "fastapi": """
# FastAPI + Pydantic Integration
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return {"message": f"Created {item.name} for ${item.price}"}
""",
        
        "v1_v2": """
# Pydantic v1 vs v2 Migration
# v1
class ModelV1(BaseModel):
    name: str
    
    class Config:
        orm_mode = True

# v2
from pydantic import ConfigDict

class ModelV2(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
""",
        
        "errors": """
# Error Handling Best Practices
from pydantic import ValidationError

def safe_parse(data: dict):
    try:
        return User(**data)
    except ValidationError as e:
        for error in e.errors():
            print(f"Field: {error['loc']}, Error: {error['msg']}")
        return None
"""
    }
    
    return examples.get(query_type, PYDANTIC_COMPREHENSIVE_GUIDE)