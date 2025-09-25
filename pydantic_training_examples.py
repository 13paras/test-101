"""
Comprehensive Pydantic Training Examples
========================================

This module provides extensive examples of Pydantic features and best practices
for AI training datasets. It covers validation, serialization, advanced features,
and real-world use cases.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal, Annotated, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import (
    BaseModel, 
    Field, 
    validator, 
    root_validator,
    field_validator,
    model_validator,
    ConfigDict,
    EmailStr,
    HttpUrl,
    SecretStr,
    computed_field,
    field_serializer,
    model_serializer,
    BeforeValidator,
    AfterValidator,
    PlainValidator,
    WrapValidator,
    ValidationError,
    BaseSettings,
)
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic_extra_types import PhoneNumber, Color
from typing_extensions import Self


# =============================================================================
# 1. BASIC MODELS AND VALIDATION
# =============================================================================

class StatusEnum(str, Enum):
    """Example enum for status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"


class User(BaseModel):
    """Basic user model with comprehensive validation"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        extra='forbid'
    )
    
    id: UUID = Field(default_factory=uuid4, description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr = Field(..., description="Valid email address")
    full_name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150, description="Age in years")
    phone: Optional[PhoneNumber] = None
    website: Optional[HttpUrl] = None
    status: StatusEnum = Field(default=StatusEnum.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list, max_length=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if v.lower() in ['admin', 'root', 'system']:
            raise ValueError('Username cannot be a reserved word')
        return v.lower()
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        return [tag.strip().lower() for tag in v if tag.strip()]
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Computed field for display name"""
        return f"{self.full_name} (@{self.username})"
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()


# =============================================================================
# 2. ADVANCED VALIDATION EXAMPLES
# =============================================================================

def validate_positive(value: float) -> float:
    """Custom validator for positive numbers"""
    if value <= 0:
        raise ValueError('Value must be positive')
    return value


def validate_currency_code(value: str) -> str:
    """Custom validator for currency codes"""
    if len(value) != 3 or not value.isalpha():
        raise ValueError('Currency code must be 3 letter alphabetic code')
    return value.upper()


class Product(BaseModel):
    """Product model with advanced validation"""
    model_config = ConfigDict(validate_assignment=True)
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Annotated[Decimal, BeforeValidator(validate_positive)] = Field(
        ..., 
        decimal_places=2, 
        description="Price in the specified currency"
    )
    currency: Annotated[str, BeforeValidator(validate_currency_code)] = Field(
        default="USD",
        description="ISO 4217 currency code"
    )
    category_id: int = Field(..., gt=0)
    sku: str = Field(..., pattern=r'^[A-Z]{2}-\d{4,6}$')
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    weight_kg: Optional[float] = Field(None, gt=0)
    dimensions: Optional[Dict[str, float]] = None
    color: Optional[Color] = None
    
    @model_validator(mode='after')
    def validate_product_logic(self) -> Self:
        """Cross-field validation"""
        if self.stock_quantity == 0 and self.is_active:
            raise ValueError('Active products must have stock quantity > 0')
        
        if self.dimensions:
            required_dims = {'length', 'width', 'height'}
            if not required_dims.issubset(self.dimensions.keys()):
                raise ValueError(f'Dimensions must include: {required_dims}')
        
        return self


# =============================================================================
# 3. NESTED MODELS AND RELATIONSHIPS
# =============================================================================

class Address(BaseModel):
    """Address model for nested relationships"""
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., pattern=r'^\d{5}(-\d{4})?$')
    country: str = Field(default="US", min_length=2, max_length=3)
    
    @computed_field
    @property
    def full_address(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"


class Order(BaseModel):
    """Order model demonstrating nested relationships"""
    model_config = ConfigDict(validate_assignment=True)
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    products: List[Product] = Field(..., min_length=1)
    shipping_address: Address
    billing_address: Optional[Address] = None
    order_date: datetime = Field(default_factory=datetime.now)
    total_amount: Optional[Decimal] = None
    status: Literal["pending", "confirmed", "shipped", "delivered", "cancelled"] = "pending"
    notes: Optional[str] = Field(None, max_length=500)
    
    @model_validator(mode='after')
    def calculate_total(self) -> Self:
        """Calculate total amount from products"""
        if self.total_amount is None:
            self.total_amount = sum(product.price for product in self.products)
        return self
    
    @model_validator(mode='after')
    def set_billing_address(self) -> Self:
        """Set billing address to shipping if not provided"""
        if self.billing_address is None:
            self.billing_address = self.shipping_address
        return self


# =============================================================================
# 4. GENERIC MODELS
# =============================================================================

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Generic API response model"""
    success: bool = True
    data: Optional[T] = None
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: UUID = Field(default_factory=uuid4)
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        return value.isoformat()


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model"""
    items: List[T]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    size: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=1)
    
    @model_validator(mode='after')
    def validate_pagination(self) -> Self:
        expected_pages = (self.total + self.size - 1) // self.size
        if self.pages != expected_pages:
            self.pages = expected_pages
        return self


# =============================================================================
# 5. SETTINGS AND CONFIGURATION
# =============================================================================

class DatabaseSettings(BaseSettings):
    """Database configuration using Pydantic Settings"""
    model_config = ConfigDict(env_prefix='DB_')
    
    host: str = Field(default="localhost")
    port: int = Field(default=5432, ge=1, le=65535)
    name: str = Field(default="myapp")
    username: str = Field(default="postgres")
    password: SecretStr = Field(default="password")
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=100)
    echo: bool = Field(default=False)
    
    @computed_field
    @property
    def url(self) -> str:
        """Computed database URL"""
        return (
            f"postgresql://{self.username}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class AppSettings(BaseSettings):
    """Application settings"""
    model_config = ConfigDict(
        env_prefix='APP_',
        env_file='.env',
        env_file_encoding='utf-8'
    )
    
    name: str = Field(default="MyApp")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    secret_key: SecretStr = Field(default="dev-secret-key")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis_url: str = Field(default="redis://localhost:6379/0")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


# =============================================================================
# 6. CUSTOM SERIALIZATION AND DESERIALIZATION
# =============================================================================

class FileMetadata(BaseModel):
    """File metadata with custom serialization"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    path: Path
    size_bytes: int = Field(..., ge=0)
    created_at: datetime
    modified_at: datetime
    mime_type: str
    checksum: str = Field(..., pattern=r'^[a-f0-9]{32}$')  # MD5 checksum
    
    @field_serializer('path')
    def serialize_path(self, value: Path) -> str:
        return str(value)
    
    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Custom model serialization"""
        return {
            'file_path': str(self.path),
            'size': {
                'bytes': self.size_bytes,
                'human_readable': self._format_size(self.size_bytes)
            },
            'timestamps': {
                'created': self.created_at.isoformat(),
                'modified': self.modified_at.isoformat()
            },
            'type': self.mime_type,
            'integrity': self.checksum
        }
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


# =============================================================================
# 7. VALIDATION WITH EXTERNAL DATA
# =============================================================================

class EmailCampaign(BaseModel):
    """Email campaign model with external validation"""
    name: str = Field(..., min_length=1, max_length=200)
    subject: str = Field(..., min_length=1, max_length=300)
    template_id: int = Field(..., gt=0)
    recipient_list_ids: List[int] = Field(..., min_length=1)
    scheduled_at: Optional[datetime] = None
    sender_email: EmailStr
    reply_to: Optional[EmailStr] = None
    tags: List[str] = Field(default_factory=list)
    
    @field_validator('scheduled_at')
    @classmethod
    def validate_scheduled_time(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v <= datetime.now():
            raise ValueError('Scheduled time must be in the future')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_campaign_tags(cls, v: List[str]) -> List[str]:
        allowed_tags = ['newsletter', 'promotion', 'announcement', 'follow-up', 'welcome']
        invalid_tags = [tag for tag in v if tag not in allowed_tags]
        if invalid_tags:
            raise ValueError(f'Invalid tags: {invalid_tags}. Allowed: {allowed_tags}')
        return v


# =============================================================================
# 8. PYDANTIC DATACLASSES
# =============================================================================

@pydantic_dataclass
class Point:
    """3D Point using Pydantic dataclass"""
    x: float
    y: float
    z: float = 0.0
    
    def distance_from_origin(self) -> float:
        """Calculate distance from origin"""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5


@pydantic_dataclass
class Vector:
    """3D Vector with validation"""
    start: Point
    end: Point
    
    @computed_field
    @property
    def magnitude(self) -> float:
        """Calculate vector magnitude"""
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        dz = self.end.z - self.start.z
        return (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5


# =============================================================================
# 9. ERROR HANDLING AND CUSTOM EXCEPTIONS
# =============================================================================

class BusinessLogicError(Exception):
    """Custom business logic error"""
    pass


class InventoryItem(BaseModel):
    """Inventory item with business logic validation"""
    sku: str = Field(..., pattern=r'^[A-Z]{2}-\d{6}$')
    name: str = Field(..., min_length=1, max_length=200)
    current_stock: int = Field(..., ge=0)
    reserved_stock: int = Field(default=0, ge=0)
    reorder_point: int = Field(..., ge=0)
    max_stock: int = Field(..., gt=0)
    
    @model_validator(mode='after')
    def validate_stock_levels(self) -> Self:
        """Validate stock level business rules"""
        available_stock = self.current_stock - self.reserved_stock
        
        if available_stock < 0:
            raise BusinessLogicError(
                f"Available stock cannot be negative. "
                f"Current: {self.current_stock}, Reserved: {self.reserved_stock}"
            )
        
        if self.current_stock > self.max_stock:
            raise BusinessLogicError(
                f"Current stock ({self.current_stock}) exceeds maximum ({self.max_stock})"
            )
        
        if self.reorder_point >= self.max_stock:
            raise BusinessLogicError(
                f"Reorder point ({self.reorder_point}) must be less than max stock ({self.max_stock})"
            )
        
        return self
    
    @property
    def available_stock(self) -> int:
        """Calculate available stock"""
        return self.current_stock - self.reserved_stock
    
    @property
    def needs_reorder(self) -> bool:
        """Check if item needs reordering"""
        return self.available_stock <= self.reorder_point


# =============================================================================
# 10. DEMONSTRATION FUNCTIONS
# =============================================================================

def demonstrate_basic_usage():
    """Demonstrate basic Pydantic model usage"""
    print("=== Basic Pydantic Usage ===")
    
    # Create a user
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "age": 30,
        "phone": "+1-555-123-4567",
        "website": "https://johndoe.com",
        "tags": ["developer", "python", "backend"]
    }
    
    try:
        user = User(**user_data)
        print(f"Created user: {user.display_name}")
        print(f"User JSON: {user.model_dump_json(indent=2)}")
        
        # Validation error example
        invalid_user_data = {**user_data, "age": -5}
        User(**invalid_user_data)
    except ValidationError as e:
        print(f"Validation error: {e}")


def demonstrate_advanced_features():
    """Demonstrate advanced Pydantic features"""
    print("\n=== Advanced Features ===")
    
    # Generic models
    user_response = APIResponse[User](
        data=User(
            username="jane_doe",
            email="jane@example.com",
            full_name="Jane Doe",
            age=28
        )
    )
    print(f"API Response: {user_response.model_dump_json(indent=2)}")
    
    # Settings
    settings = AppSettings()
    print(f"App settings: {settings.model_dump(exclude={'secret_key', 'database'})}")


def demonstrate_error_handling():
    """Demonstrate error handling patterns"""
    print("\n=== Error Handling ===")
    
    try:
        # Business logic error
        item = InventoryItem(
            sku="AB-123456",
            name="Test Item",
            current_stock=10,
            reserved_stock=15,  # This will cause an error
            reorder_point=5,
            max_stock=100
        )
    except BusinessLogicError as e:
        print(f"Business logic error: {e}")
    except ValidationError as e:
        print(f"Validation error: {e}")


if __name__ == "__main__":
    demonstrate_basic_usage()
    demonstrate_advanced_features()
    demonstrate_error_handling()