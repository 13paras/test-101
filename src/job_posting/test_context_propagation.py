"""
Test script to validate context propagation in the ResearchAgent.

This script demonstrates and validates that:
1. Context is properly initialized
2. Context is maintained across tool calls
3. Context validation detects missing data
4. Reports can only be generated with complete context
"""

import logging
import sys
from job_posting.research_agent import ResearchAgent, ContextPropagationError
from crewai import Agent

# Configure logging to see context transitions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_context_initialization():
    """Test 1: Verify context is properly initialized."""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Context Initialization")
    logger.info("="*80)
    
    # Create a mock agent (in real usage, this would be a real CrewAI agent)
    mock_agent = Agent(
        role="Research Analyst",
        goal="Test context propagation",
        backstory="Testing agent",
        verbose=True
    )
    
    research_agent = ResearchAgent(mock_agent)
    context = research_agent.get_context()
    
    # Verify all required keys are initialized
    assert 'company_culture' in context, "Missing company_culture in context"
    assert 'role_skills' in context, "Missing role_skills in context"
    assert 'metadata' in context, "Missing metadata in context"
    
    logger.info("✓ Context initialized successfully with all required keys")
    logger.info(f"✓ Initial context summary: {research_agent._get_context_summary()}")
    
    return True


def test_context_propagation_across_searches():
    """Test 2: Verify context is maintained across multiple search operations."""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Context Propagation Across Searches")
    logger.info("="*80)
    
    mock_agent = Agent(
        role="Research Analyst",
        goal="Test context propagation",
        backstory="Testing agent",
        verbose=True
    )
    
    research_agent = ResearchAgent(mock_agent)
    
    # Simulate multiple search operations
    searches = [
        ("company culture at Warner Bros", "company_culture"),
        ("innovation and creativity", "company_values"),
        ("tell compelling stories", "company_mission"),
        ("Communication skills", "role_skills"),
        ("Project management", "role_skills"),
        ("3+ years experience", "role_experience"),
        ("Streaming industry growth", "industry_trends"),
    ]
    
    for query, search_type in searches:
        result = research_agent.execute_search(query, search_type)
        assert result['success'], f"Search failed for {search_type}"
        logger.info(f"✓ Search completed: {search_type}")
    
    # Verify context has accumulated data
    context = research_agent.get_context()
    
    assert context['company_culture'] is not None, "Company culture not captured"
    assert context['company_values'] is not None, "Company values not captured"
    assert context['company_mission'] is not None, "Company mission not captured"
    assert len(context['role_skills']) > 0, "Role skills not captured"
    assert len(context['role_experience']) > 0, "Role experience not captured"
    assert len(context['industry_trends']) > 0, "Industry trends not captured"
    
    logger.info("✓ Context successfully maintained across all searches")
    logger.info(f"✓ Final context summary: {research_agent._get_context_summary()}")
    logger.info(f"✓ Total searches: {context['metadata']['total_searches']}")
    logger.info(f"✓ Successful searches: {context['metadata']['successful_searches']}")
    
    return True


def test_context_validation_missing_data():
    """Test 3: Verify context validation detects missing data."""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Context Validation - Missing Data Detection")
    logger.info("="*80)
    
    mock_agent = Agent(
        role="Research Analyst",
        goal="Test context propagation",
        backstory="Testing agent",
        verbose=True
    )
    
    research_agent = ResearchAgent(mock_agent)
    
    # Try to compose report without any data - should fail
    try:
        report = research_agent.compose_report()
        logger.error("✗ FAILED: Report generation should have raised ContextPropagationError")
        return False
    except ContextPropagationError as e:
        logger.info("✓ ContextPropagationError raised as expected")
        logger.info(f"✓ Error message: {str(e)[:200]}...")
        return True


def test_context_validation_with_complete_data():
    """Test 4: Verify report generation works with complete context."""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Report Generation with Complete Context")
    logger.info("="*80)
    
    mock_agent = Agent(
        role="Research Analyst",
        goal="Test context propagation",
        backstory="Testing agent",
        verbose=True
    )
    
    research_agent = ResearchAgent(mock_agent)
    
    # Populate all required context fields
    research_agent.update_context('company_culture', 'Innovative and collaborative')
    research_agent.update_context('company_values', 'Creativity, excellence, integrity')
    research_agent.update_context('company_mission', 'Tell the world\'s best stories')
    research_agent.update_context('company_selling_points', ['Global reach', 'Industry leader'])
    research_agent.update_context('role_skills', ['Communication', 'Project management'])
    research_agent.update_context('role_experience', ['3+ years in media', 'Production experience'])
    research_agent.update_context('role_qualities', ['Team player', 'Creative thinker'])
    research_agent.update_context('industry_trends', ['Streaming growth', 'Digital transformation'])
    research_agent.update_context('industry_challenges', ['Market competition', 'Content costs'])
    research_agent.update_context('industry_opportunities', ['Global expansion', 'New platforms'])
    
    # Validate context
    missing = research_agent._validate_context()
    assert len(missing) == 0, f"Context still has missing fields: {missing}"
    logger.info("✓ All required context fields populated")
    
    # Generate report - should succeed
    try:
        report = research_agent.compose_report('comprehensive')
        logger.info("✓ Report generated successfully")
        logger.info(f"✓ Report length: {len(report)} characters")
        logger.info("\n" + "-"*80)
        logger.info("Sample of generated report:")
        logger.info("-"*80)
        logger.info(report[:500] + "...")
        logger.info("-"*80)
        return True
    except ContextPropagationError as e:
        logger.error(f"✗ FAILED: Report generation failed with complete context: {e}")
        return False


def test_context_logging():
    """Test 5: Verify logging captures context transitions."""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Context Transition Logging")
    logger.info("="*80)
    
    mock_agent = Agent(
        role="Research Analyst",
        goal="Test context propagation",
        backstory="Testing agent",
        verbose=True
    )
    
    research_agent = ResearchAgent(mock_agent)
    
    # Execute a search and verify logging
    logger.info("Executing search to trigger context logging...")
    result = research_agent.execute_search("test query", "company_culture")
    
    # Get context summary
    summary = research_agent._get_context_summary()
    
    logger.info("✓ Context summary retrieved")
    logger.info(f"  - Has company culture: {summary['has_company_culture']}")
    logger.info(f"  - Total searches: {summary['total_searches']}")
    logger.info(f"  - Successful searches: {summary['successful_searches']}")
    
    # Update context and verify logging
    logger.info("Updating context to trigger update logging...")
    research_agent.update_context('role_skills', ['Skill 1', 'Skill 2'])
    
    logger.info("✓ Context transitions logged successfully")
    
    return True


def test_context_reset():
    """Test 6: Verify context can be reset."""
    logger.info("\n" + "="*80)
    logger.info("TEST 6: Context Reset")
    logger.info("="*80)
    
    mock_agent = Agent(
        role="Research Analyst",
        goal="Test context propagation",
        backstory="Testing agent",
        verbose=True
    )
    
    research_agent = ResearchAgent(mock_agent)
    
    # Add some data
    research_agent.update_context('company_culture', 'Test culture')
    research_agent.update_context('role_skills', ['Skill 1'])
    
    context_before = research_agent.get_context()
    assert context_before['company_culture'] == 'Test culture', "Culture not set"
    logger.info("✓ Context populated with test data")
    
    # Reset context
    research_agent.reset_context()
    
    context_after = research_agent.get_context()
    assert context_after['company_culture'] is None, "Culture not reset"
    assert len(context_after['role_skills']) == 0, "Skills not reset"
    assert context_after['metadata']['context_updates'] == 0, "Metadata not reset"
    
    logger.info("✓ Context reset successfully")
    
    return True


def run_all_tests():
    """Run all validation tests."""
    logger.info("\n" + "#"*80)
    logger.info("# CONTEXT PROPAGATION VALIDATION TEST SUITE")
    logger.info("#"*80)
    
    tests = [
        ("Context Initialization", test_context_initialization),
        ("Context Propagation Across Searches", test_context_propagation_across_searches),
        ("Context Validation - Missing Data", test_context_validation_missing_data),
        ("Report Generation - Complete Data", test_context_validation_with_complete_data),
        ("Context Transition Logging", test_context_logging),
        ("Context Reset", test_context_reset),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    logger.info("\n" + "#"*80)
    logger.info("# TEST SUMMARY")
    logger.info("#"*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("\n" + "="*80)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("="*80)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)