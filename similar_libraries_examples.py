"""
Similar Python Libraries Examples
=================================

This module demonstrates data validation and serialization libraries similar to Pydantic,
providing comprehensive examples for AI training datasets.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import attr
import attrs
import cerberus
import marshmallow
import voluptuous as vol
from dataclasses_json import dataclass_json
from marshmallow import Schema, fields, post_load, validates, ValidationError


# =============================================================================
# 1. PYTHON DATACLASSES (Built-in)
# =============================================================================

@dataclass
class Person:
    """Basic dataclass example"""
    first_name: str
    last_name: str
    age: int
    email: Optional[str] = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization validation"""
        if self.age < 0:
            raise ValueError("Age cannot be negative")
        if self.email and "@" not in self.email:
            raise ValueError("Invalid email format")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with datetime serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass_json
@dataclass
class Product:
    """Dataclass with JSON serialization support"""
    name: str
    price: Decimal
    category: str
    in_stock: bool = True
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("Price must be positive")


# =============================================================================
# 2. ATTRS LIBRARY
# =============================================================================

@attrs.define
class UserAccount:
    """User account using attrs library"""
    username: str = attrs.field()
    email: str = attrs.field()
    age: int = attrs.field()
    is_active: bool = attrs.field(default=True)
    created_at: datetime = attrs.field(factory=datetime.now)
    
    @username.validator
    def _validate_username(self, attribute, value):
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not value.isalnum():
            raise ValueError("Username must be alphanumeric")
    
    @email.validator
    def _validate_email(self, attribute, value):
        if "@" not in value:
            raise ValueError("Invalid email format")
    
    @age.validator
    def _validate_age(self, attribute, value):
        if not 13 <= value <= 120:
            raise ValueError("Age must be between 13 and 120")


@attrs.define
class BankAccount:
    """Bank account with attrs converters and validators"""
    account_number: str = attrs.field()
    balance: Decimal = attrs.field(converter=Decimal)
    currency: str = attrs.field(default="USD")
    is_frozen: bool = attrs.field(default=False)
    
    @account_number.validator
    def _validate_account_number(self, attribute, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Account number must be 10 digits")
    
    @balance.validator
    def _validate_balance(self, attribute, value):
        if value < 0:
            raise ValueError("Balance cannot be negative")
    
    def deposit(self, amount: Decimal) -> None:
        """Deposit money into account"""
        if self.is_frozen:
            raise ValueError("Cannot deposit to frozen account")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
    
    def withdraw(self, amount: Decimal) -> None:
        """Withdraw money from account"""
        if self.is_frozen:
            raise ValueError("Cannot withdraw from frozen account")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount


# =============================================================================
# 3. MARSHMALLOW LIBRARY
# =============================================================================

class UserSchema(Schema):
    """User schema using Marshmallow"""
    id = fields.Integer(required=True, validate=vol.Range(min=1))
    username = fields.String(required=True, validate=vol.Length(min=3, max=50))
    email = fields.Email(required=True)
    full_name = fields.String(required=True, validate=vol.Length(min=1, max=100))
    age = fields.Integer(required=True, validate=vol.Range(min=0, max=150))
    is_active = fields.Boolean(default=True)
    created_at = fields.DateTime(default=datetime.now)
    tags = fields.List(fields.String(), default=list)
    
    @validates('username')
    def validate_username(self, value):
        """Custom username validation"""
        if value.lower() in ['admin', 'root', 'system']:
            raise ValidationError('Username cannot be a reserved word')
    
    @post_load
    def make_user(self, data, **kwargs):
        """Convert validated data to User object"""
        return User(**data)


class User:
    """User class for Marshmallow example"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"User(username='{self.username}', email='{self.email}')"


class OrderSchema(Schema):
    """Order schema with nested relationships"""
    id = fields.UUID(required=True)
    user_id = fields.UUID(required=True)
    items = fields.List(fields.Nested('OrderItemSchema'), required=True, validate=vol.Length(min=1))
    total_amount = fields.Decimal(required=True, validate=vol.Range(min=0))
    status = fields.String(validate=vol.In(['pending', 'confirmed', 'shipped', 'delivered']))
    created_at = fields.DateTime(default=datetime.now)
    
    @validates('total_amount')
    def validate_total_amount(self, value):
        if value <= 0:
            raise ValidationError('Total amount must be positive')


class OrderItemSchema(Schema):
    """Order item schema"""
    product_id = fields.UUID(required=True)
    quantity = fields.Integer(required=True, validate=vol.Range(min=1))
    unit_price = fields.Decimal(required=True, validate=vol.Range(min=0))
    
    @post_load
    def calculate_line_total(self, data, **kwargs):
        """Calculate line total"""
        data['line_total'] = data['quantity'] * data['unit_price']
        return data


# =============================================================================
# 4. CERBERUS LIBRARY
# =============================================================================

class CerberusValidator:
    """Data validation using Cerberus library"""
    
    # User validation schema
    user_schema = {
        'username': {
            'type': 'string',
            'required': True,
            'minlength': 3,
            'maxlength': 50,
            'regex': r'^[a-zA-Z0-9_]+$'
        },
        'email': {
            'type': 'string',
            'required': True,
            'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        },
        'age': {
            'type': 'integer',
            'required': True,
            'min': 0,
            'max': 150
        },
        'phone': {
            'type': 'string',
            'nullable': True,
            'regex': r'^\+?1?\d{9,15}$'
        },
        'preferences': {
            'type': 'dict',
            'schema': {
                'notifications': {'type': 'boolean', 'default': True},
                'language': {'type': 'string', 'allowed': ['en', 'es', 'fr', 'de'], 'default': 'en'},
                'theme': {'type': 'string', 'allowed': ['light', 'dark'], 'default': 'light'}
            }
        },
        'tags': {
            'type': 'list',
            'schema': {'type': 'string'},
            'maxlength': 10
        }
    }
    
    # Product validation schema
    product_schema = {
        'name': {
            'type': 'string',
            'required': True,
            'minlength': 1,
            'maxlength': 200
        },
        'price': {
            'type': 'float',
            'required': True,
            'min': 0.01
        },
        'category': {
            'type': 'string',
            'required': True,
            'allowed': ['electronics', 'clothing', 'books', 'home', 'sports']
        },
        'sku': {
            'type': 'string',
            'required': True,
            'regex': r'^[A-Z]{2}-\d{4,6}$'
        },
        'in_stock': {
            'type': 'boolean',
            'default': True
        },
        'dimensions': {
            'type': 'dict',
            'nullable': True,
            'schema': {
                'length': {'type': 'float', 'min': 0},
                'width': {'type': 'float', 'min': 0},
                'height': {'type': 'float', 'min': 0}
            }
        }
    }
    
    @classmethod
    def validate_user(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user data using Cerberus"""
        validator = cerberus.Validator(cls.user_schema)
        if validator.validate(data):
            return validator.normalized(data)
        else:
            raise ValueError(f"Validation errors: {validator.errors}")
    
    @classmethod
    def validate_product(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product data using Cerberus"""
        validator = cerberus.Validator(cls.product_schema)
        if validator.validate(data):
            return validator.normalized(data)
        else:
            raise ValueError(f"Validation errors: {validator.errors}")


# =============================================================================
# 5. VOLUPTUOUS LIBRARY
# =============================================================================

# User schema with Voluptuous
user_schema_vol = vol.Schema({
    vol.Required('username'): vol.All(str, vol.Length(min=3, max=50), vol.Match(r'^[a-zA-Z0-9_]+$')),
    vol.Required('email'): vol.Email(),
    vol.Required('full_name'): vol.All(str, vol.Length(min=1, max=100)),
    vol.Required('age'): vol.All(int, vol.Range(min=0, max=150)),
    vol.Optional('phone', default=None): vol.Any(None, vol.Match(r'^\+?1?\d{9,15}$')),
    vol.Optional('is_active', default=True): bool,
    vol.Optional('created_at', default=datetime.now): datetime,
    vol.Optional('tags', default=list): [str],
    vol.Optional('metadata', default=dict): {str: vol.Any(str, int, float, bool, None)}
})

# Product schema with Voluptuous
product_schema_vol = vol.Schema({
    vol.Required('name'): vol.All(str, vol.Length(min=1, max=200)),
    vol.Required('price'): vol.All(vol.Coerce(float), vol.Range(min=0.01)),
    vol.Required('sku'): vol.Match(r'^[A-Z]{2}-\d{4,6}$'),
    vol.Optional('category'): vol.In(['electronics', 'clothing', 'books', 'home', 'sports']),
    vol.Optional('in_stock', default=True): bool,
    vol.Optional('stock_quantity', default=0): vol.All(int, vol.Range(min=0)),
    vol.Optional('weight_kg'): vol.All(vol.Coerce(float), vol.Range(min=0)),
    vol.Optional('dimensions'): {
        vol.Required('length'): vol.All(vol.Coerce(float), vol.Range(min=0)),
        vol.Required('width'): vol.All(vol.Coerce(float), vol.Range(min=0)),
        vol.Required('height'): vol.All(vol.Coerce(float), vol.Range(min=0))
    }
})

# Order schema with complex validation
order_schema_vol = vol.Schema({
    vol.Required('user_id'): str,
    vol.Required('items'): vol.All([{
        vol.Required('product_id'): str,
        vol.Required('quantity'): vol.All(int, vol.Range(min=1)),
        vol.Required('unit_price'): vol.All(vol.Coerce(float), vol.Range(min=0))
    }], vol.Length(min=1)),
    vol.Optional('shipping_address'): {
        vol.Required('street'): str,
        vol.Required('city'): str,
        vol.Required('state'): str,
        vol.Required('postal_code'): vol.Match(r'^\d{5}(-\d{4})?$'),
        vol.Optional('country', default='US'): str
    },
    vol.Optional('status', default='pending'): vol.In(['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']),
    vol.Optional('created_at', default=datetime.now): datetime
})


# =============================================================================
# 6. COMPARISON AND DEMONSTRATION FUNCTIONS
# =============================================================================

def demonstrate_dataclasses():
    """Demonstrate Python dataclasses"""
    print("=== Python Dataclasses ===")
    
    try:
        person = Person(
            first_name="Alice",
            last_name="Johnson",
            age=30,
            email="alice@example.com"
        )
        print(f"Person: {person.full_name}")
        print(f"Person dict: {person.to_dict()}")
        
        # JSON serialization with dataclasses-json
        product = Product(
            name="Laptop",
            price=Decimal("999.99"),
            category="Electronics",
            tags=["computer", "portable"]
        )
        print(f"Product JSON: {product.to_json()}")
        
    except ValueError as e:
        print(f"Validation error: {e}")


def demonstrate_attrs():
    """Demonstrate attrs library"""
    print("\n=== Attrs Library ===")
    
    try:
        user = UserAccount(
            username="bob123",
            email="bob@example.com",
            age=25
        )
        print(f"User: {user}")
        
        account = BankAccount(
            account_number="1234567890",
            balance="1000.00"
        )
        print(f"Account balance: {account.balance}")
        
        account.deposit(Decimal("500.00"))
        print(f"After deposit: {account.balance}")
        
    except ValueError as e:
        print(f"Validation error: {e}")


def demonstrate_marshmallow():
    """Demonstrate Marshmallow library"""
    print("\n=== Marshmallow Library ===")
    
    schema = UserSchema()
    
    # Valid data
    user_data = {
        'id': 1,
        'username': 'charlie',
        'email': 'charlie@example.com',
        'full_name': 'Charlie Brown',
        'age': 35,
        'tags': ['developer', 'python']
    }
    
    try:
        # Deserialize and validate
        user = schema.load(user_data)
        print(f"Loaded user: {user}")
        
        # Serialize back to dict
        serialized = schema.dump(user_data)
        print(f"Serialized: {serialized}")
        
    except ValidationError as e:
        print(f"Validation errors: {e.messages}")


def demonstrate_cerberus():
    """Demonstrate Cerberus library"""
    print("\n=== Cerberus Library ===")
    
    user_data = {
        'username': 'diana_prince',
        'email': 'diana@themyscira.com',
        'age': 30,
        'phone': '+1-555-0123',
        'preferences': {
            'notifications': True,
            'language': 'en',
            'theme': 'dark'
        },
        'tags': ['hero', 'amazon', 'warrior']
    }
    
    try:
        validated_user = CerberusValidator.validate_user(user_data)
        print(f"Validated user: {validated_user}")
        
    except ValueError as e:
        print(f"Validation error: {e}")


def demonstrate_voluptuous():
    """Demonstrate Voluptuous library"""
    print("\n=== Voluptuous Library ===")
    
    user_data = {
        'username': 'eve_adams',
        'email': 'eve@example.com',
        'full_name': 'Eve Adams',
        'age': 28,
        'tags': ['designer', 'ui/ux']
    }
    
    try:
        validated_user = user_schema_vol(user_data)
        print(f"Validated user: {validated_user}")
        
        product_data = {
            'name': 'Wireless Headphones',
            'price': '149.99',
            'sku': 'EL-001234',
            'category': 'electronics',
            'dimensions': {
                'length': '20.5',
                'width': '18.0',
                'height': '8.5'
            }
        }
        
        validated_product = product_schema_vol(product_data)
        print(f"Validated product: {validated_product}")
        
    except vol.Invalid as e:
        print(f"Validation error: {e}")


def compare_libraries():
    """Compare features of different validation libraries"""
    print("\n=== Library Comparison ===")
    
    comparison = {
        "Pydantic": {
            "Type Hints": "✓ Native support",
            "Performance": "✓ Very fast (Rust core)",
            "JSON Schema": "✓ Auto-generation",
            "Serialization": "✓ Built-in",
            "IDE Support": "✓ Excellent",
            "Learning Curve": "Easy"
        },
        "Dataclasses": {
            "Type Hints": "✓ Native support",
            "Performance": "✓ Fast (built-in)",
            "JSON Schema": "✗ Manual",
            "Serialization": "✗ Manual/Third-party",
            "IDE Support": "✓ Good",
            "Learning Curve": "Very Easy"
        },
        "Attrs": {
            "Type Hints": "✓ Good support",
            "Performance": "✓ Fast",
            "JSON Schema": "✗ Manual",
            "Serialization": "✗ Manual",
            "IDE Support": "✓ Good",
            "Learning Curve": "Easy"
        },
        "Marshmallow": {
            "Type Hints": "~ Limited support",
            "Performance": "~ Moderate",
            "JSON Schema": "✓ With extensions",
            "Serialization": "✓ Excellent",
            "IDE Support": "~ Limited",
            "Learning Curve": "Moderate"
        },
        "Cerberus": {
            "Type Hints": "✗ No support",
            "Performance": "~ Moderate",
            "JSON Schema": "✗ No",
            "Serialization": "✗ No",
            "IDE Support": "~ Limited",
            "Learning Curve": "Easy"
        },
        "Voluptuous": {
            "Type Hints": "✗ No support",
            "Performance": "~ Moderate",
            "JSON Schema": "✗ No",
            "Serialization": "✗ No",
            "IDE Support": "~ Limited",
            "Learning Curve": "Easy"
        }
    }
    
    for library, features in comparison.items():
        print(f"\n{library}:")
        for feature, support in features.items():
            print(f"  {feature}: {support}")


if __name__ == "__main__":
    demonstrate_dataclasses()
    demonstrate_attrs()
    demonstrate_marshmallow()
    demonstrate_cerberus()
    demonstrate_voluptuous()
    compare_libraries()