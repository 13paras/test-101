"""
Response formatting and validation module for the Researcher agent.

This module provides functions to validate and format research outputs
against the defined JSON schema to ensure compliance with expected structure.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError
import json

# Configure logging
logger = logging.getLogger(__name__)


class ResearchRoleRequirements(BaseModel):
    """Research role requirements model - JSON schema definition"""
    skills: List[str] = Field(
        ..., 
        description="List of recommended skills for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements."
    )
    experience: List[str] = Field(
        ..., 
        description="List of recommended experience for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements."
    )
    qualities: List[str] = Field(
        ..., 
        description="List of recommended qualities for the ideal candidate aligned with the company's culture, ongoing projects, and the specific role's requirements."
    )


def validate_schema(response_output: Dict[str, Any]) -> bool:
    """
    Validate response output against the ResearchRoleRequirements JSON schema.
    
    Args:
        response_output: The response data to validate
        
    Returns:
        bool: True if schema is valid, False otherwise
    """
    try:
        # Step 1: Attempt to parse the response into the Pydantic model
        ResearchRoleRequirements(**response_output)
        logger.info("Schema validation successful")
        return True
        
    except ValidationError as e:
        # Step 2: Log validation errors with details
        logger.error(f"Schema validation failed: {e}")
        logger.error(f"Invalid output: {json.dumps(response_output, indent=2)}")
        return False
        
    except Exception as e:
        # Step 3: Handle unexpected errors
        logger.error(f"Unexpected error during schema validation: {e}")
        logger.error(f"Output causing error: {json.dumps(response_output, indent=2)}")
        return False


def format_and_validate_response(
    raw_output: Any,
    strict_mode: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Format and validate the researcher agent's response output.
    
    This function implements the complete response formatting workflow:
    Step 1: Parse raw output
    Step 2: Clean and normalize data
    Step 3: Structure data according to schema
    Step 4: Validate against JSON schema (CRITICAL STEP - Added per requirements)
    
    Args:
        raw_output: The raw output from the researcher agent
        strict_mode: If True, raises exception on validation failure
        
    Returns:
        Optional[Dict[str, Any]]: Validated response dict or None if validation fails
        
    Raises:
        ValueError: If validation fails and strict_mode is True
    """
    logger.info("Starting response formatting and validation process")
    
    # Step 1: Parse raw output
    if isinstance(raw_output, str):
        try:
            response_output = json.loads(raw_output)
            logger.debug("Successfully parsed string input to JSON")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse raw output as JSON: {e}")
            if strict_mode:
                raise ValueError(f"Invalid JSON format: {e}")
            return None
    elif isinstance(raw_output, dict):
        response_output = raw_output
    else:
        logger.error(f"Unsupported output type: {type(raw_output)}")
        if strict_mode:
            raise ValueError(f"Unsupported output type: {type(raw_output)}")
        return None
    
    # Step 2: Clean and normalize data
    # Ensure all required fields exist with proper types
    normalized_output = {
        'skills': response_output.get('skills', []),
        'experience': response_output.get('experience', []),
        'qualities': response_output.get('qualities', [])
    }
    
    # Convert any non-list values to lists
    for field in ['skills', 'experience', 'qualities']:
        if not isinstance(normalized_output[field], list):
            logger.warning(f"Field '{field}' is not a list, converting to list")
            normalized_output[field] = [str(normalized_output[field])] if normalized_output[field] else []
    
    logger.debug(f"Normalized output: {json.dumps(normalized_output, indent=2)}")
    
    # Step 3: Structure data according to schema
    # Data is already structured in Step 2
    
    # Step 4: Validate against JSON schema (CRITICAL VALIDATION STEP)
    logger.info("Step 4: Validating output against JSON schema")
    is_schema_valid = validate_schema(normalized_output)
    
    # Enhanced logging as per requirements
    if not is_schema_valid:
        log_error("Output does not conform to schema", normalized_output)
        if strict_mode:
            raise ValueError("Output validation failed: Schema compliance check failed")
        return None
    
    logger.info("Response formatting and validation completed successfully")
    return normalized_output


def log_error(message: str, response_output: Dict[str, Any]) -> None:
    """
    Enhanced error logging for non-compliant outputs.
    
    Args:
        message: Error message
        response_output: The output that failed validation
    """
    logger.error("=" * 80)
    logger.error(f"VALIDATION ERROR: {message}")
    logger.error("-" * 80)
    logger.error(f"Non-compliant output:\n{json.dumps(response_output, indent=2)}")
    logger.error("-" * 80)
    
    # Log specific missing or incorrect fields
    try:
        ResearchRoleRequirements(**response_output)
    except ValidationError as e:
        for error in e.errors():
            field = error.get('loc', ['unknown'])[0]
            error_type = error.get('type', 'unknown')
            msg = error.get('msg', 'unknown error')
            logger.error(f"Field '{field}': {error_type} - {msg}")
    
    logger.error("=" * 80)
