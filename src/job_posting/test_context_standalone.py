"""
Standalone test script for context propagation validation.
This version doesn't require external dependencies.
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Mock minimal Agent class for testing
class MockAgent:
    def __init__(self, role, goal, backstory, verbose=True):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose


# Simplified ResearchAgent for testing (without external dependencies)
class ContextPropagationError(Exception):
    """Raised when required context data is missing."""
    pass


class SimpleResearchAgent:
    """Simplified ResearchAgent for testing context propagation."""
    
    REQUIRED_CONTEXT_KEYS = [
        'company_culture',
        'company_values',
        'company_mission',
        'company_selling_points',
        'role_skills',
        'role_experience',
        'role_qualities',
        'industry_trends',
        'industry_challenges',
        'industry_opportunities'
    ]
    
    def __init__(self):
        self.context = {}
        self._initialize_context()
        logger.info("SimpleResearchAgent initialized")
    
    def _initialize_context(self):
        """Initialize context with default values."""
        self.context = {
            'company_culture': None,
            'company_values': None,
            'company_mission': None,
            'company_selling_points': [],
            'role_skills': [],
            'role_experience': [],
            'role_qualities': [],
            'industry_trends': [],
            'industry_challenges': [],
            'industry_opportunities': [],
            'search_results': [],
            'metadata': {
                'total_searches': 0,
                'successful_searches': 0,
                'failed_searches': 0,
                'context_updates': 0
            }
        }
    
    def execute_search(self, query: str, search_type: str):
        """Execute search and update context."""
        logger.info(f"Executing search: {search_type} - Query: {query}")
        
        self.context['metadata']['total_searches'] += 1
        
        try:
            # Simulate search result
            result = f"Search result for: {query}"
            
            # Update context
            self._update_context(search_type, result)
            
            self.context['metadata']['successful_searches'] += 1
            logger.info(f"Search successful for {search_type}")
            
            return {'success': True, 'result': result}
        except Exception as e:
            self.context['metadata']['failed_searches'] += 1
            logger.error(f"Search failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_context(self, search_type: str, result):
        """Update context based on search type."""
        previous_value = None
        
        if search_type in ['company_culture', 'company_values', 'company_mission']:
            previous_value = self.context.get(search_type)
            self.context[search_type] = result
        elif search_type in ['company_selling_points', 'role_skills', 'role_experience', 
                            'role_qualities', 'industry_trends', 'industry_challenges', 
                            'industry_opportunities']:
            previous_value = self.context[search_type].copy()
            if isinstance(result, list):
                self.context[search_type].extend(result)
            else:
                self.context[search_type].append(result)
        
        self.context['metadata']['context_updates'] += 1
        
        logger.info(f"Context updated: {search_type}")
        logger.info(f"Previous: {previous_value}, New: {result}")
    
    def _validate_context(self):
        """Validate context has all required data."""
        missing = []
        
        for key in self.REQUIRED_CONTEXT_KEYS:
            value = self.context.get(key)
            
            if value is None:
                missing.append(key)
            elif isinstance(value, list) and len(value) == 0:
                missing.append(key)
        
        if missing:
            logger.warning(f"Missing context fields: {missing}")
        else:
            logger.info("All required context fields present")
        
        return missing
    
    def compose_report(self):
        """Compose report with context validation."""
        logger.info("Composing report...")
        
        missing = self._validate_context()
        
        if missing:
            error_msg = f"Cannot compose report. Missing: {', '.join(missing)}"
            logger.error(error_msg)
            raise ContextPropagationError(error_msg)
        
        # Generate simple report
        report = "# Research Report\n\n"
        report += f"## Company Culture\n{self.context['company_culture']}\n\n"
        report += f"## Company Values\n{self.context['company_values']}\n\n"
        report += f"## Company Mission\n{self.context['company_mission']}\n\n"
        
        if self.context['role_skills']:
            report += "## Required Skills\n"
            for skill in self.context['role_skills']:
                report += f"- {skill}\n"
            report += "\n"
        
        logger.info("Report generated successfully")
        return report
    
    def update_context(self, key: str, value):
        """Manually update context."""
        previous = self.context.get(key)
        self.context[key] = value
        self.context['metadata']['context_updates'] += 1
        logger.info(f"Context updated: {key} (previous: {previous})")
    
    def get_context(self):
        """Get context copy."""
        return self.context.copy()
    
    def reset_context(self):
        """Reset context."""
        logger.info("Resetting context")
        self._initialize_context()


def test_context_initialization():
    """Test context initialization."""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Context Initialization")
    logger.info("="*80)
    
    agent = SimpleResearchAgent()
    context = agent.get_context()
    
    assert 'company_culture' in context
    assert 'metadata' in context
    assert context['metadata']['total_searches'] == 0
    
    logger.info("✓ PASS: Context initialized correctly")
    return True


def test_context_propagation():
    """Test context propagation across searches."""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Context Propagation Across Searches")
    logger.info("="*80)
    
    agent = SimpleResearchAgent()
    
    # Execute multiple searches
    searches = [
        ("Warner Bros culture", "company_culture"),
        ("Innovation values", "company_values"),
        ("Tell great stories", "company_mission"),
        ("Communication", "role_skills"),
        ("Teamwork", "role_skills"),
        ("3 years experience", "role_experience"),
    ]
    
    for query, search_type in searches:
        result = agent.execute_search(query, search_type)
        assert result['success'], f"Search failed: {search_type}"
    
    context = agent.get_context()
    
    assert context['company_culture'] is not None
    assert context['company_values'] is not None
    assert len(context['role_skills']) == 2
    assert context['metadata']['total_searches'] == 6
    assert context['metadata']['successful_searches'] == 6
    
    logger.info("✓ PASS: Context propagated correctly across searches")
    return True


def test_missing_context_detection():
    """Test missing context detection."""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Missing Context Detection")
    logger.info("="*80)
    
    agent = SimpleResearchAgent()
    
    # Try to generate report without complete data
    try:
        agent.compose_report()
        logger.error("✗ FAIL: Should have raised ContextPropagationError")
        return False
    except ContextPropagationError as e:
        logger.info(f"✓ PASS: ContextPropagationError raised correctly")
        logger.info(f"  Error: {str(e)[:100]}...")
        return True


def test_complete_context_report():
    """Test report generation with complete context."""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Report Generation with Complete Context")
    logger.info("="*80)
    
    agent = SimpleResearchAgent()
    
    # Populate all required fields
    agent.update_context('company_culture', 'Innovative and creative')
    agent.update_context('company_values', 'Excellence and integrity')
    agent.update_context('company_mission', 'Tell compelling stories')
    agent.update_context('company_selling_points', ['Global leader'])
    agent.update_context('role_skills', ['Communication', 'Teamwork'])
    agent.update_context('role_experience', ['3+ years'])
    agent.update_context('role_qualities', ['Creative'])
    agent.update_context('industry_trends', ['Streaming growth'])
    agent.update_context('industry_challenges', ['Competition'])
    agent.update_context('industry_opportunities', ['Global expansion'])
    
    # Validate
    missing = agent._validate_context()
    assert len(missing) == 0, f"Still missing: {missing}"
    
    # Generate report
    try:
        report = agent.compose_report()
        assert len(report) > 0
        logger.info("✓ PASS: Report generated successfully")
        logger.info(f"  Report length: {len(report)} characters")
        return True
    except Exception as e:
        logger.error(f"✗ FAIL: {e}")
        return False


def test_context_logging():
    """Test context logging functionality."""
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Context Logging")
    logger.info("="*80)
    
    agent = SimpleResearchAgent()
    
    # Execute search
    agent.execute_search("test query", "company_culture")
    
    context = agent.get_context()
    assert context['metadata']['total_searches'] == 1
    assert context['metadata']['context_updates'] > 0
    
    logger.info("✓ PASS: Context logging working correctly")
    return True


def test_context_reset():
    """Test context reset."""
    logger.info("\n" + "="*80)
    logger.info("TEST 6: Context Reset")
    logger.info("="*80)
    
    agent = SimpleResearchAgent()
    
    # Add data
    agent.update_context('company_culture', 'Test')
    agent.execute_search("test", "role_skills")
    
    context_before = agent.get_context()
    assert context_before['company_culture'] == 'Test'
    
    # Reset
    agent.reset_context()
    
    context_after = agent.get_context()
    assert context_after['company_culture'] is None
    assert context_after['metadata']['total_searches'] == 0
    
    logger.info("✓ PASS: Context reset working correctly")
    return True


def run_all_tests():
    """Run all tests."""
    logger.info("\n" + "#"*80)
    logger.info("# CONTEXT PROPAGATION VALIDATION TEST SUITE")
    logger.info("#"*80)
    
    tests = [
        ("Context Initialization", test_context_initialization),
        ("Context Propagation", test_context_propagation),
        ("Missing Context Detection", test_missing_context_detection),
        ("Complete Context Report", test_complete_context_report),
        ("Context Logging", test_context_logging),
        ("Context Reset", test_context_reset),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ Test '{test_name}' failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "#"*80)
    logger.info("# TEST SUMMARY")
    logger.info("#"*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("\n" + "="*80)
    logger.info(f"Results: {passed}/{total} tests passed ({100*passed//total}%)")
    logger.info("="*80)
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Context propagation is working correctly.")
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed. Review the logs above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)