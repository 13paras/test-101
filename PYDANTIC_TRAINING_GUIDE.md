# Comprehensive Pydantic Training Guide for AI Models

This guide provides extensive examples and documentation for training AI models on Pydantic and similar Python data validation libraries.

## Table of Contents

1. [Overview](#overview)
2. [Pydantic Fundamentals](#pydantic-fundamentals)
3. [Advanced Pydantic Features](#advanced-pydantic-features)
4. [Similar Libraries Comparison](#similar-libraries-comparison)
5. [Real-World Use Cases](#real-world-use-cases)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [Performance Considerations](#performance-considerations)
9. [Migration Strategies](#migration-strategies)
10. [Testing Strategies](#testing-strategies)

## Overview

Pydantic is a Python library that provides data validation and parsing using Python type hints. It's particularly powerful for:

- **API Development**: Automatic request/response validation
- **Configuration Management**: Type-safe settings and environment variables
- **Data Processing**: ETL pipelines with guaranteed data integrity
- **Machine Learning**: Feature validation and model input/output schemas

### Key Benefits

- ✅ **Type Safety**: Leverages Python type hints for compile-time and runtime validation
- ✅ **Performance**: Built on Rust for exceptional speed
- ✅ **Developer Experience**: Excellent IDE support and error messages
- ✅ **JSON Schema**: Automatic generation for API documentation
- ✅ **Serialization**: Built-in JSON serialization with custom formatters

## Pydantic Fundamentals

### Basic Model Definition

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=150)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v.lower() in ['admin', 'root']:
            raise ValueError('Username cannot be reserved')
        return v.lower()
```

### Configuration Options

```python
from pydantic import ConfigDict

class Product(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatically strip whitespace
        validate_assignment=True,   # Validate on field assignment
        use_enum_values=True,      # Use enum values in serialization
        extra='forbid',            # Forbid extra fields
        frozen=True                # Make model immutable
    )
    
    name: str
    price: float
```

### Field Validation

#### Built-in Validators

```python
from pydantic import Field, EmailStr, HttpUrl
from pydantic_extra_types import PhoneNumber, Color
from decimal import Decimal

class ContactInfo(BaseModel):
    email: EmailStr                    # Email validation
    website: Optional[HttpUrl] = None  # URL validation
    phone: Optional[PhoneNumber] = None # Phone number validation
    preferred_color: Optional[Color] = None # Color validation
    
    # Numeric constraints
    age: int = Field(..., ge=18, le=100)
    score: float = Field(..., gt=0.0, le=100.0)
    price: Decimal = Field(..., decimal_places=2)
    
    # String constraints
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    description: Optional[str] = Field(None, max_length=1000)
    
    # Collection constraints
    tags: List[str] = Field(..., min_length=1, max_length=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### Custom Validators

```python
from pydantic import field_validator, model_validator
from typing_extensions import Self

class BankAccount(BaseModel):
    account_number: str
    balance: Decimal
    currency: str = "USD"
    is_frozen: bool = False
    
    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v):
        if len(v) != 10 or not v.isdigit():
            raise ValueError('Account number must be 10 digits')
        return v
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        allowed_currencies = ['USD', 'EUR', 'GBP', 'JPY']
        if v not in allowed_currencies:
            raise ValueError(f'Currency must be one of {allowed_currencies}')
        return v.upper()
    
    @model_validator(mode='after')
    def validate_frozen_account(self) -> Self:
        if self.is_frozen and self.balance < 0:
            raise ValueError('Frozen accounts cannot have negative balance')
        return self
```

### Cross-Field Validation

```python
from datetime import date
from typing import Optional

class Event(BaseModel):
    name: str
    start_date: date
    end_date: Optional[date] = None
    max_attendees: int
    current_attendees: int = 0
    
    @model_validator(mode='after')
    def validate_dates_and_capacity(self) -> Self:
        # Validate date order
        if self.end_date and self.end_date < self.start_date:
            raise ValueError('End date must be after start date')
        
        # Validate attendance
        if self.current_attendees > self.max_attendees:
            raise ValueError('Current attendees cannot exceed maximum')
        
        return self
```

## Advanced Pydantic Features

### Generic Models

```python
from typing import Generic, TypeVar
from uuid import UUID, uuid4

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "Operation successful"
    request_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)

# Usage
user_response = APIResponse[User](data=user, message="User retrieved")
product_list_response = APIResponse[List[Product]](data=products)
```

### Custom Serialization

```python
from pydantic import field_serializer, model_serializer

class FileInfo(BaseModel):
    path: Path
    size_bytes: int
    created_at: datetime
    
    @field_serializer('path')
    def serialize_path(self, value: Path) -> str:
        return str(value)
    
    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()
    
    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        return {
            'file_path': str(self.path),
            'size': {
                'bytes': self.size_bytes,
                'human_readable': self._format_size(self.size_bytes)
            },
            'created': self.created_at.isoformat()
        }
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
```

### Computed Fields

```python
from pydantic import computed_field

class Rectangle(BaseModel):
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    
    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @computed_field
    @property
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)
    
    @computed_field
    @property
    def is_square(self) -> bool:
        return abs(self.width - self.height) < 0.01
```

### Settings Management

```python
from pydantic_settings import BaseSettings
from pydantic import SecretStr

class DatabaseSettings(BaseSettings):
    model_config = ConfigDict(env_prefix='DB_')
    
    host: str = 'localhost'
    port: int = 5432
    username: str = 'postgres'
    password: SecretStr = SecretStr('default_password')
    name: str = 'myapp'
    
    @computed_field
    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"

class AppSettings(BaseSettings):
    model_config = ConfigDict(env_file='.env')
    
    app_name: str = 'My Application'
    debug: bool = False
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    allowed_hosts: List[str] = Field(default_factory=lambda: ['localhost'])
```

### Nested Models and Relationships

```python
class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$')
    country: str = 'US'
    
    @computed_field
    @property
    def full_address(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}"

class Customer(BaseModel):
    name: str
    email: EmailStr
    shipping_address: Address
    billing_address: Optional[Address] = None
    
    @model_validator(mode='after')
    def set_billing_address(self) -> Self:
        if self.billing_address is None:
            self.billing_address = self.shipping_address
        return self

class OrderItem(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    
    @computed_field
    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.unit_price

class Order(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    customer: Customer
    items: List[OrderItem] = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)
    
    @computed_field
    @property
    def total_amount(self) -> Decimal:
        return sum(item.total_price for item in self.items)
    
    @computed_field
    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
```

## Similar Libraries Comparison

### Python Dataclasses

**Pros:**
- Built into Python 3.7+
- Minimal boilerplate
- Good IDE support
- Fast performance

**Cons:**
- Limited validation
- No automatic serialization
- Manual type conversion

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Person:
    name: str
    age: int
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age cannot be negative")
```

### Attrs

**Pros:**
- More features than dataclasses
- Excellent performance
- Flexible attribute definition
- Good ecosystem

**Cons:**
- Third-party dependency
- Less validation than Pydantic
- Manual serialization

```python
import attrs

@attrs.define
class Product:
    name: str = attrs.field()
    price: float = attrs.field()
    
    @price.validator
    def _validate_price(self, attribute, value):
        if value <= 0:
            raise ValueError("Price must be positive")
```

### Marshmallow

**Pros:**
- Excellent serialization/deserialization
- Flexible field types
- Good for APIs
- Mature ecosystem

**Cons:**
- Schema-based (not class-based)
- More verbose
- Separate validation step
- Limited type hints support

```python
from marshmallow import Schema, fields, validates, ValidationError

class UserSchema(Schema):
    username = fields.Str(required=True, validate=Length(min=3))
    email = fields.Email(required=True)
    age = fields.Int(required=True, validate=Range(min=0))
    
    @validates('username')
    def validate_username(self, value):
        if value in ['admin', 'root']:
            raise ValidationError('Username is reserved')
```

### Cerberus

**Pros:**
- Simple schema definition
- Good for configuration validation
- Lightweight
- Flexible rules

**Cons:**
- Dict-based validation only
- No type hints support
- Limited serialization
- Basic error messages

```python
import cerberus

schema = {
    'username': {'type': 'string', 'minlength': 3, 'maxlength': 50},
    'email': {'type': 'string', 'regex': r'^[^@]+@[^@]+\.[^@]+$'},
    'age': {'type': 'integer', 'min': 0, 'max': 150}
}

validator = cerberus.Validator(schema)
```

### Feature Comparison Matrix

| Feature | Pydantic | Dataclasses | Attrs | Marshmallow | Cerberus |
|---------|----------|-------------|-------|-------------|----------|
| Type Hints | ✅ Excellent | ✅ Good | ✅ Good | ❌ Limited | ❌ None |
| Performance | ✅ Very Fast | ✅ Fast | ✅ Fast | ⚠️ Moderate | ⚠️ Moderate |
| Validation | ✅ Comprehensive | ❌ Manual | ⚠️ Basic | ✅ Good | ✅ Good |
| Serialization | ✅ Built-in | ❌ Manual | ❌ Manual | ✅ Excellent | ❌ None |
| JSON Schema | ✅ Auto-gen | ❌ No | ❌ No | ⚠️ Plugin | ❌ No |
| IDE Support | ✅ Excellent | ✅ Good | ✅ Good | ⚠️ Limited | ❌ Poor |
| Learning Curve | ⚠️ Moderate | ✅ Easy | ✅ Easy | ⚠️ Moderate | ✅ Easy |

## Real-World Use Cases

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    is_active: bool

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # Pydantic automatically validates the request body
    # and serializes the response
    return UserResponse(
        id=uuid4(),
        username=user.username,
        email=user.email,
        created_at=datetime.now(),
        is_active=True
    )
```

### Configuration Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., env='DATABASE_URL')
    database_pool_size: int = Field(10, env='DB_POOL_SIZE')
    
    # Redis
    redis_url: str = Field('redis://localhost:6379', env='REDIS_URL')
    
    # Security
    secret_key: SecretStr = Field(..., env='SECRET_KEY')
    jwt_expiration: int = Field(3600, env='JWT_EXPIRATION')
    
    # Features
    enable_debug: bool = Field(False, env='DEBUG')
    allowed_hosts: List[str] = Field(['localhost'], env='ALLOWED_HOSTS')
    
    class Config:
        env_file = '.env'
        env_prefix = 'APP_'

settings = Settings()
```

### Data Processing Pipeline

```python
class RawData(BaseModel):
    """Raw input data with minimal validation"""
    timestamp: str
    user_id: str
    event_type: str
    properties: Dict[str, Any]

class ProcessedEvent(BaseModel):
    """Processed event with strict validation"""
    timestamp: datetime
    user_id: UUID
    event_type: Literal['click', 'view', 'purchase', 'signup']
    properties: Dict[str, Union[str, int, float, bool]]
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
    
    @field_validator('user_id', mode='before')
    @classmethod
    def parse_user_id(cls, v):
        if isinstance(v, str):
            return UUID(v)
        return v

def process_events(raw_events: List[Dict[str, Any]]) -> List[ProcessedEvent]:
    """Process raw events with validation"""
    processed = []
    for raw_event in raw_events:
        try:
            # First, minimal validation
            raw_data = RawData(**raw_event)
            
            # Then, strict processing
            processed_event = ProcessedEvent(
                timestamp=raw_data.timestamp,
                user_id=raw_data.user_id,
                event_type=raw_data.event_type,
                properties=raw_data.properties
            )
            processed.append(processed_event)
            
        except ValidationError as e:
            logger.error(f"Failed to process event: {e}")
            continue
    
    return processed
```

## Best Practices

### 1. Model Design

```python
# ✅ Good: Clear, specific field names and types
class UserProfile(BaseModel):
    user_id: UUID
    display_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[HttpUrl] = None
    is_verified: bool = False
    follower_count: int = Field(0, ge=0)
    created_at: datetime = Field(default_factory=datetime.now)

# ❌ Bad: Vague names, missing validation
class User(BaseModel):
    data: Dict[str, Any]  # Too generic
    info: str             # Unclear purpose
    count: int            # No constraints
```

### 2. Validation Strategy

```python
# ✅ Good: Specific, helpful error messages
class Product(BaseModel):
    sku: str = Field(..., pattern=r'^[A-Z]{2}-\d{6}$', 
                     description="Format: XX-123456")
    
    @field_validator('sku')
    @classmethod
    def validate_sku_checksum(cls, v):
        # Custom business logic validation
        if not cls._validate_sku_checksum(v):
            raise ValueError(f"SKU {v} has invalid checksum")
        return v
    
    @staticmethod
    def _validate_sku_checksum(sku: str) -> bool:
        # Implementation of checksum validation
        return True

# ❌ Bad: Generic validation, poor error messages
class Product(BaseModel):
    sku: str
    
    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v):
        if len(v) != 9:  # Unclear requirement
            raise ValueError("Invalid SKU")
        return v
```

### 3. Error Handling

```python
from pydantic import ValidationError

def create_user_safely(user_data: Dict[str, Any]) -> Optional[User]:
    """Create user with proper error handling"""
    try:
        return User(**user_data)
    except ValidationError as e:
        # Log specific validation errors
        logger.error(f"User validation failed: {e.json()}")
        
        # Return None or raise custom exception
        return None
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error creating user: {e}")
        raise

def validate_bulk_users(users_data: List[Dict[str, Any]]) -> Tuple[List[User], List[Dict]]:
    """Validate multiple users, collecting errors"""
    valid_users = []
    errors = []
    
    for i, user_data in enumerate(users_data):
        try:
            user = User(**user_data)
            valid_users.append(user)
        except ValidationError as e:
            errors.append({
                'index': i,
                'data': user_data,
                'errors': e.errors()
            })
    
    return valid_users, errors
```

### 4. Performance Optimization

```python
# ✅ Use model_validate for better performance
users_data = [{"username": "user1", "email": "user1@example.com"}, ...]
users = [User.model_validate(data) for data in users_data]

# ✅ Use model_dump for serialization
user_dict = user.model_dump(exclude={'password'}, by_alias=True)

# ✅ Use frozen models for immutable data
class ImmutableConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    api_key: str
    timeout: int = 30

# ✅ Use __slots__ for memory efficiency when needed
class OptimizedUser(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    username: str
    email: str
    
    class Config:
        __slots__ = ('username', 'email')
```

## Common Patterns

### 1. Base Models

```python
class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def touch(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()

class BaseEntity(TimestampMixin):
    """Base class for all entities"""
    id: UUID = Field(default_factory=uuid4)
    is_active: bool = True
    
    class Config:
        validate_assignment = True

class User(BaseEntity):
    """User inherits timestamps and base fields"""
    username: str
    email: EmailStr
```

### 2. Factory Pattern

```python
class ModelFactory:
    """Factory for creating models with defaults"""
    
    @classmethod
    def create_test_user(cls, **overrides) -> User:
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'age': 25
        }
        defaults.update(overrides)
        return User(**defaults)
    
    @classmethod
    def create_admin_user(cls, **overrides) -> User:
        defaults = {
            'username': 'admin',
            'email': 'admin@example.com',
            'full_name': 'Administrator',
            'age': 30,
            'tags': ['admin', 'staff']
        }
        defaults.update(overrides)
        return User(**defaults)
```

### 3. Validation Helpers

```python
def validate_json_data(data: str, model_class: Type[BaseModel]) -> BaseModel:
    """Validate JSON data against a Pydantic model"""
    try:
        parsed_data = json.loads(data)
        return model_class(**parsed_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e}")

def safe_model_update(instance: BaseModel, updates: Dict[str, Any]) -> BaseModel:
    """Safely update a model instance"""
    return instance.model_copy(update=updates)

def model_diff(old: BaseModel, new: BaseModel) -> Dict[str, Dict[str, Any]]:
    """Compare two model instances"""
    old_dict = old.model_dump()
    new_dict = new.model_dump()
    
    diff = {}
    for key in set(old_dict.keys()) | set(new_dict.keys()):
        old_val = old_dict.get(key)
        new_val = new_dict.get(key)
        if old_val != new_val:
            diff[key] = {'old': old_val, 'new': new_val}
    
    return diff
```

## Performance Considerations

### 1. Validation Performance

```python
# ✅ Fast: Use specific types and constraints
class FastModel(BaseModel):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    score: float = Field(..., ge=0.0, le=100.0)

# ⚠️ Slower: Complex regex patterns
class SlowModel(BaseModel):
    complex_field: str = Field(..., pattern=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$')

# ✅ Better: Custom validator with caching
import functools

@functools.lru_cache(maxsize=1000)
def validate_complex_pattern(value: str) -> bool:
    # Expensive validation logic here
    return True

class OptimizedModel(BaseModel):
    complex_field: str
    
    @field_validator('complex_field')
    @classmethod
    def validate_complex(cls, v):
        if not validate_complex_pattern(v):
            raise ValueError("Invalid pattern")
        return v
```

### 2. Memory Usage

```python
# ✅ Memory efficient: Use appropriate types
class EfficientModel(BaseModel):
    model_config = ConfigDict(
        extra='forbid',  # Prevent extra fields
        str_strip_whitespace=True  # Reduce memory usage
    )
    
    # Use specific types
    count: int  # Not float if integer is sufficient
    flag: bool  # Not string for boolean values
    
# ❌ Memory inefficient
class WastefulModel(BaseModel):
    data: Dict[str, Any]  # Too generic, no constraints
    everything: List[Any]  # Unbounded list
```

### 3. Serialization Performance

```python
# ✅ Fast serialization
user_dict = user.model_dump(
    include={'id', 'username', 'email'},  # Only needed fields
    exclude_none=True,  # Skip None values
    by_alias=True  # Use field aliases
)

# ✅ Batch operations
users_data = [user.model_dump() for user in users]  # List comprehension
users_json = json.dumps([user.model_dump() for user in users])  # Single JSON call

# ❌ Inefficient
for user in users:
    json.dumps(user.model_dump())  # Multiple JSON calls
```

## Migration Strategies

### From Dataclasses to Pydantic

```python
# Before: Dataclass
@dataclass
class OldUser:
    username: str
    email: str
    age: int = 0
    
    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age cannot be negative")

# After: Pydantic
class NewUser(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    age: int = Field(0, ge=0)
    
    # Migration helper
    @classmethod
    def from_dataclass(cls, old_user: OldUser) -> 'NewUser':
        return cls(
            username=old_user.username,
            email=old_user.email,
            age=old_user.age
        )
```

### From Dictionary Validation

```python
# Before: Manual dictionary validation
def validate_user_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    if 'username' not in data:
        raise ValueError("Username required")
    if len(data['username']) < 3:
        raise ValueError("Username too short")
    # ... more validation
    return data

# After: Pydantic model
class ValidatedUser(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    age: int = Field(..., ge=0)
    
    # Migration helper
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidatedUser':
        return cls(**data)
```

## Testing Strategies

### 1. Unit Tests

```python
import pytest
from pydantic import ValidationError

class TestUserModel:
    def test_valid_user_creation(self):
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            age=25
        )
        assert user.username == "testuser"
        assert user.display_name == "Test User (@testuser)"
    
    def test_invalid_email(self):
        with pytest.raises(ValidationError) as exc_info:
            User(
                username="testuser",
                email="invalid-email",
                full_name="Test User",
                age=25
            )
        assert "email" in str(exc_info.value)
    
    def test_age_validation(self):
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                age=-1
            )
    
    @pytest.mark.parametrize("username,expected", [
        ("TESTUSER", "testuser"),
        ("TestUser", "testuser"),
        ("test_user", "test_user")
    ])
    def test_username_normalization(self, username, expected):
        user = User(
            username=username,
            email="test@example.com",
            full_name="Test User",
            age=25
        )
        assert user.username == expected
```

### 2. Property-Based Testing

```python
from hypothesis import given, strategies as st

class TestUserModelProperties:
    @given(
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd', 'Pc'))),
        age=st.integers(min_value=0, max_value=150)
    )
    def test_valid_user_properties(self, username, age):
        """Test that valid inputs always create valid users"""
        try:
            user = User(
                username=username,
                email="test@example.com",
                full_name="Test User",
                age=age
            )
            assert user.age == age
            assert len(user.username) >= 3
        except ValidationError:
            # Skip if username contains reserved words
            pass
    
    @given(age=st.integers(max_value=-1))
    def test_invalid_age_always_fails(self, age):
        """Test that negative ages always fail"""
        with pytest.raises(ValidationError):
            User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                age=age
            )
```

### 3. Integration Tests

```python
class TestModelIntegration:
    def test_order_calculation(self):
        """Test complete order workflow"""
        # Create customer
        customer = Customer(
            name="John Doe",
            email="john@example.com",
            shipping_address=Address(
                street="123 Main St",
                city="Anytown",
                state="CA",
                postal_code="12345"
            )
        )
        
        # Create order items
        items = [
            OrderItem(
                product_id=uuid4(),
                quantity=2,
                unit_price=Decimal("10.00")
            ),
            OrderItem(
                product_id=uuid4(),
                quantity=1,
                unit_price=Decimal("5.00")
            )
        ]
        
        # Create order
        order = Order(customer=customer, items=items)
        
        # Verify calculations
        assert order.total_amount == Decimal("25.00")
        assert order.item_count == 3
        assert order.customer.billing_address == order.customer.shipping_address
    
    def test_json_round_trip(self):
        """Test serialization and deserialization"""
        original_user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            age=25,
            tags=["developer", "python"]
        )
        
        # Serialize to JSON
        json_data = original_user.model_dump_json()
        
        # Deserialize from JSON
        data_dict = json.loads(json_data)
        restored_user = User(**data_dict)
        
        # Verify equality (excluding computed fields and defaults)
        assert restored_user.username == original_user.username
        assert restored_user.email == original_user.email
        assert restored_user.age == original_user.age
        assert restored_user.tags == original_user.tags
```

## Conclusion

This comprehensive guide provides extensive examples and patterns for using Pydantic and similar Python data validation libraries. The examples cover:

- **Basic to advanced Pydantic features**
- **Comparison with similar libraries**
- **Real-world use cases and patterns**
- **Performance optimization techniques**
- **Testing strategies**
- **Migration approaches**

These examples should provide sufficient training data for AI models to understand and generate accurate responses about Python data validation libraries, with a focus on Pydantic's comprehensive feature set and best practices.

## Additional Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Attrs Documentation](https://attrs.readthedocs.io/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)