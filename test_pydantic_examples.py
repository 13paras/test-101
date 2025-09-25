"""
Comprehensive Test Cases for Pydantic Training Examples
======================================================

This module provides extensive test cases demonstrating various Pydantic scenarios,
validation patterns, error handling, and edge cases for AI training datasets.
"""

import json
import pytest
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID

from pydantic import ValidationError, BaseModel, Field
from pydantic_training_examples import (
    User, Product, Order, Address, APIResponse, PaginatedResponse,
    DatabaseSettings, AppSettings, FileMetadata, EmailCampaign,
    Point, Vector, InventoryItem, BusinessLogicError
)
from similar_libraries_examples import (
    Person, UserAccount, BankAccount, CerberusValidator,
    user_schema_vol, product_schema_vol, order_schema_vol
)


# =============================================================================
# 1. BASIC VALIDATION TESTS
# =============================================================================

class TestBasicValidation:
    """Test basic Pydantic validation features"""
    
    def test_user_valid_creation(self):
        """Test creating a valid user"""
        user_data = {
            "username": "john_doe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "age": 30,
            "phone": "+1-555-123-4567",
            "website": "https://johndoe.com",
            "tags": ["developer", "python", "backend"]
        }
        
        user = User(**user_data)
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert user.age == 30
        assert len(user.tags) == 3
        assert user.display_name == "John Doe (@john_doe)"
    
    def test_user_validation_errors(self):
        """Test various user validation errors"""
        # Test age validation
        with pytest.raises(ValidationError) as exc_info:
            User(
                username="test",
                email="test@example.com",
                full_name="Test User",
                age=-5  # Invalid age
            )
        assert "ensure this value is greater than or equal to 0" in str(exc_info.value)
        
        # Test email validation
        with pytest.raises(ValidationError):
            User(
                username="test",
                email="invalid-email",  # Invalid email
                full_name="Test User",
                age=25
            )
        
        # Test username validation
        with pytest.raises(ValidationError) as exc_info:
            User(
                username="admin",  # Reserved username
                email="test@example.com",
                full_name="Test User",
                age=25
            )
        assert "Username cannot be a reserved word" in str(exc_info.value)
    
    def test_product_validation(self):
        """Test product validation"""
        product_data = {
            "name": "Test Product",
            "price": Decimal("99.99"),
            "category_id": 1,
            "sku": "TP-123456",
            "stock_quantity": 10,
            "weight_kg": 1.5,
            "dimensions": {"length": 10.0, "width": 5.0, "height": 3.0}
        }
        
        product = Product(**product_data)
        assert product.name == "Test Product"
        assert product.price == Decimal("99.99")
        assert product.currency == "USD"  # Default value
    
    def test_product_cross_field_validation(self):
        """Test product cross-field validation"""
        with pytest.raises(ValidationError) as exc_info:
            Product(
                name="Test Product",
                price=Decimal("99.99"),
                category_id=1,
                sku="TP-123456",
                stock_quantity=0,  # No stock
                is_active=True  # But active - should fail
            )
        assert "Active products must have stock quantity > 0" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            Product(
                name="Test Product",
                price=Decimal("99.99"),
                category_id=1,
                sku="TP-123456",
                dimensions={"length": 10.0, "width": 5.0}  # Missing height
            )
        assert "Dimensions must include" in str(exc_info.value)


# =============================================================================
# 2. SERIALIZATION TESTS
# =============================================================================

class TestSerialization:
    """Test Pydantic serialization features"""
    
    def test_user_serialization(self):
        """Test user JSON serialization"""
        user = User(
            username="jane_doe",
            email="jane@example.com",
            full_name="Jane Doe",
            age=28,
            tags=["designer", "ui/ux"]
        )
        
        # Test JSON serialization
        json_data = user.model_dump_json()
        parsed_data = json.loads(json_data)
        
        assert parsed_data["username"] == "jane_doe"
        assert parsed_data["email"] == "jane@example.com"
        assert "display_name" in parsed_data  # Computed field
        assert isinstance(parsed_data["created_at"], str)  # Serialized datetime
    
    def test_file_metadata_custom_serialization(self):
        """Test custom serialization with FileMetadata"""
        file_meta = FileMetadata(
            path=Path("/home/user/document.pdf"),
            size_bytes=1048576,  # 1MB
            created_at=datetime.now(),
            modified_at=datetime.now(),
            mime_type="application/pdf",
            checksum="d41d8cd98f00b204e9800998ecf8427e"
        )
        
        # Test custom model serialization
        serialized = file_meta.serialize_model()
        
        assert "file_path" in serialized
        assert "size" in serialized
        assert serialized["size"]["human_readable"] == "1.0 MB"
        assert "timestamps" in serialized
        assert "integrity" in serialized
    
    def test_generic_api_response(self):
        """Test generic API response serialization"""
        user = User(
            username="test_user",
            email="test@example.com",
            full_name="Test User",
            age=25
        )
        
        response = APIResponse[User](
            data=user,
            message="User retrieved successfully"
        )
        
        json_data = response.model_dump_json()
        parsed_data = json.loads(json_data)
        
        assert parsed_data["success"] is True
        assert "data" in parsed_data
        assert parsed_data["data"]["username"] == "test_user"
        assert "timestamp" in parsed_data


# =============================================================================
# 3. ADVANCED FEATURES TESTS
# =============================================================================

class TestAdvancedFeatures:
    """Test advanced Pydantic features"""
    
    def test_settings_configuration(self):
        """Test Pydantic Settings"""
        # Test with environment variables
        import os
        os.environ["DB_HOST"] = "production.db.com"
        os.environ["DB_PORT"] = "5432"
        os.environ["APP_DEBUG"] = "true"
        
        settings = AppSettings()
        
        assert settings.database.host == "production.db.com"
        assert settings.database.port == 5432
        assert settings.debug is True
        
        # Test computed field
        db_url = settings.database.url
        assert "production.db.com" in db_url
        assert "5432" in db_url
        
        # Clean up
        del os.environ["DB_HOST"]
        del os.environ["DB_PORT"]
        del os.environ["APP_DEBUG"]
    
    def test_nested_models(self):
        """Test nested model validation"""
        order_data = {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "products": [
                {
                    "name": "Product 1",
                    "price": "99.99",
                    "category_id": 1,
                    "sku": "P1-123456"
                }
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "postal_code": "12345"
            }
        }
        
        order = Order(**order_data)
        
        assert len(order.products) == 1
        assert order.products[0].name == "Product 1"
        assert order.shipping_address.city == "Anytown"
        assert order.billing_address == order.shipping_address  # Auto-set
        assert order.total_amount == Decimal("99.99")  # Auto-calculated
    
    def test_pydantic_dataclasses(self):
        """Test Pydantic dataclasses"""
        point1 = Point(x=0.0, y=0.0, z=0.0)
        point2 = Point(x=3.0, y=4.0, z=0.0)
        
        vector = Vector(start=point1, end=point2)
        
        assert vector.magnitude == 5.0  # 3-4-5 triangle
        assert point1.distance_from_origin() == 0.0
        assert point2.distance_from_origin() == 5.0
    
    def test_email_campaign_validation(self):
        """Test email campaign validation"""
        # Test future scheduled time
        future_time = datetime.now().replace(year=datetime.now().year + 1)
        
        campaign = EmailCampaign(
            name="Test Campaign",
            subject="Test Subject",
            template_id=1,
            recipient_list_ids=[1, 2, 3],
            scheduled_at=future_time,
            sender_email="sender@example.com",
            tags=["newsletter", "promotion"]
        )
        
        assert campaign.scheduled_at == future_time
        assert len(campaign.tags) == 2
        
        # Test past scheduled time
        with pytest.raises(ValidationError):
            EmailCampaign(
                name="Test Campaign",
                subject="Test Subject",
                template_id=1,
                recipient_list_ids=[1, 2, 3],
                scheduled_at=datetime(2020, 1, 1),  # Past date
                sender_email="sender@example.com"
            )


# =============================================================================
# 4. ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Test error handling and business logic validation"""
    
    def test_business_logic_errors(self):
        """Test custom business logic errors"""
        # Test negative available stock
        with pytest.raises(BusinessLogicError) as exc_info:
            InventoryItem(
                sku="AB-123456",
                name="Test Item",
                current_stock=10,
                reserved_stock=15,  # More than current
                reorder_point=5,
                max_stock=100
            )
        assert "Available stock cannot be negative" in str(exc_info.value)
        
        # Test stock exceeding maximum
        with pytest.raises(BusinessLogicError):
            InventoryItem(
                sku="AB-123456",
                name="Test Item",
                current_stock=150,  # Exceeds max
                reserved_stock=0,
                reorder_point=5,
                max_stock=100
            )
        
        # Test valid item
        item = InventoryItem(
            sku="AB-123456",
            name="Test Item",
            current_stock=50,
            reserved_stock=10,
            reorder_point=20,
            max_stock=100
        )
        
        assert item.available_stock == 40
        assert item.needs_reorder is True  # 40 <= 20
    
    def test_validation_error_details(self):
        """Test detailed validation error information"""
        try:
            User(
                username="ab",  # Too short
                email="invalid-email",  # Invalid format
                full_name="",  # Empty
                age=200  # Too old
            )
        except ValidationError as e:
            errors = e.errors()
            
            # Check that multiple validation errors are captured
            assert len(errors) >= 3
            
            # Check specific error types
            error_fields = [error["loc"][0] for error in errors]
            assert "username" in error_fields
            assert "email" in error_fields
            assert "full_name" in error_fields


# =============================================================================
# 5. SIMILAR LIBRARIES TESTS
# =============================================================================

class TestSimilarLibraries:
    """Test similar libraries examples"""
    
    def test_dataclasses_example(self):
        """Test Python dataclasses example"""
        person = Person(
            first_name="Alice",
            last_name="Johnson",
            age=30,
            email="alice@example.com"
        )
        
        assert person.full_name == "Alice Johnson"
        
        # Test validation in __post_init__
        with pytest.raises(ValueError):
            Person(
                first_name="Bob",
                last_name="Smith",
                age=-5,  # Invalid age
                email="bob@example.com"
            )
    
    def test_attrs_example(self):
        """Test attrs library example"""
        user = UserAccount(
            username="testuser",
            email="test@example.com",
            age=25
        )
        
        assert user.username == "testuser"
        assert user.is_active is True
        
        # Test bank account operations
        account = BankAccount(
            account_number="1234567890",
            balance="1000.00"
        )
        
        account.deposit(Decimal("500.00"))
        assert account.balance == Decimal("1500.00")
        
        account.withdraw(Decimal("200.00"))
        assert account.balance == Decimal("1300.00")
        
        # Test validation
        with pytest.raises(ValueError):
            account.withdraw(Decimal("2000.00"))  # Insufficient funds
    
    def test_cerberus_validation(self):
        """Test Cerberus validation"""
        valid_user_data = {
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
        
        validated_user = CerberusValidator.validate_user(valid_user_data)
        assert validated_user['username'] == 'diana_prince'
        assert validated_user['preferences']['theme'] == 'dark'
        
        # Test validation error
        invalid_user_data = {
            'username': 'ab',  # Too short
            'email': 'invalid-email',
            'age': 30
        }
        
        with pytest.raises(ValueError):
            CerberusValidator.validate_user(invalid_user_data)
    
    def test_voluptuous_validation(self):
        """Test Voluptuous validation"""
        valid_user_data = {
            'username': 'eve_adams',
            'email': 'eve@example.com',
            'full_name': 'Eve Adams',
            'age': 28,
            'tags': ['designer', 'ui/ux']
        }
        
        validated_user = user_schema_vol(valid_user_data)
        assert validated_user['username'] == 'eve_adams'
        assert validated_user['is_active'] is True  # Default value
        
        # Test product validation with coercion
        product_data = {
            'name': 'Wireless Headphones',
            'price': '149.99',  # String that should be coerced to float
            'sku': 'EL-001234',
            'category': 'electronics',
            'dimensions': {
                'length': '20.5',  # String that should be coerced
                'width': '18.0',
                'height': '8.5'
            }
        }
        
        validated_product = product_schema_vol(product_data)
        assert isinstance(validated_product['price'], float)
        assert validated_product['price'] == 149.99


# =============================================================================
# 6. PERFORMANCE AND EDGE CASES
# =============================================================================

class TestPerformanceAndEdgeCases:
    """Test performance scenarios and edge cases"""
    
    def test_large_dataset_validation(self):
        """Test validation with large datasets"""
        # Create a large list of users
        users_data = []
        for i in range(100):
            users_data.append({
                "username": f"user_{i}",
                "email": f"user_{i}@example.com",
                "full_name": f"User {i}",
                "age": 20 + (i % 50),
                "tags": [f"tag_{i % 5}", f"category_{i % 3}"]
            })
        
        # Validate all users
        users = [User(**user_data) for user_data in users_data]
        
        assert len(users) == 100
        assert all(user.age >= 20 for user in users)
        
        # Test paginated response
        paginated = PaginatedResponse[User](
            items=users[:10],
            total=100,
            page=1,
            size=10,
            pages=10
        )
        
        assert len(paginated.items) == 10
        assert paginated.pages == 10
    
    def test_json_schema_generation(self):
        """Test JSON schema generation"""
        user_schema = User.model_json_schema()
        
        assert "properties" in user_schema
        assert "username" in user_schema["properties"]
        assert "email" in user_schema["properties"]
        assert user_schema["properties"]["age"]["minimum"] == 0
        assert user_schema["properties"]["age"]["maximum"] == 150
    
    def test_model_copy_and_update(self):
        """Test model copying and updating"""
        original_user = User(
            username="original",
            email="original@example.com",
            full_name="Original User",
            age=30
        )
        
        # Test model copy with updates
        updated_user = original_user.model_copy(update={
            "age": 31,
            "tags": ["updated"]
        })
        
        assert updated_user.username == "original"  # Unchanged
        assert updated_user.age == 31  # Updated
        assert updated_user.tags == ["updated"]  # Updated
        assert original_user.age == 30  # Original unchanged
    
    def test_model_validation_on_assignment(self):
        """Test validation when assigning to model fields"""
        user = User(
            username="test",
            email="test@example.com",
            full_name="Test User",
            age=30
        )
        
        # Valid assignment
        user.age = 35
        assert user.age == 35
        
        # Invalid assignment (should raise validation error)
        with pytest.raises(ValidationError):
            user.age = -5


# =============================================================================
# 7. INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Test integration scenarios"""
    
    def test_complete_workflow(self):
        """Test a complete workflow with multiple models"""
        # Create user
        user = User(
            username="workflow_user",
            email="workflow@example.com",
            full_name="Workflow User",
            age=35,
            tags=["customer", "premium"]
        )
        
        # Create products
        products = [
            Product(
                name="Premium Product",
                price=Decimal("199.99"),
                category_id=1,
                sku="PP-123456",
                stock_quantity=50
            ),
            Product(
                name="Standard Product",
                price=Decimal("99.99"),
                category_id=2,
                sku="SP-789012",
                stock_quantity=100
            )
        ]
        
        # Create address
        address = Address(
            street="123 Workflow St",
            city="Test City",
            state="CA",
            postal_code="12345"
        )
        
        # Create order
        order = Order(
            user_id=user.id,
            products=products,
            shipping_address=address
        )
        
        # Verify relationships and calculations
        assert order.total_amount == Decimal("299.98")
        assert order.billing_address == order.shipping_address
        assert len(order.products) == 2
        
        # Create API response
        response = APIResponse[Order](
            data=order,
            message="Order created successfully"
        )
        
        # Verify the complete workflow
        assert response.success is True
        assert response.data.user_id == user.id
        assert len(response.data.products) == 2


if __name__ == "__main__":
    # Run basic demonstrations
    print("Running Pydantic Training Examples Tests...")
    
    # Basic validation
    try:
        user = User(
            username="demo_user",
            email="demo@example.com",
            full_name="Demo User",
            age=30
        )
        print(f"✅ Created user: {user.display_name}")
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    
    # Serialization
    try:
        product = Product(
            name="Demo Product",
            price=Decimal("49.99"),
            category_id=1,
            sku="DP-123456"
        )
        print(f"✅ Created product: {product.model_dump_json()}")
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    
    print("Tests completed successfully!")