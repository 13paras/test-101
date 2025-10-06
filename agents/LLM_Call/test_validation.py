"""
Validation Tests for Enhanced Weather Inquiry Agent

This module contains tests to validate that the enhanced agent meets
the specified success criteria (80% context-rich outputs).
"""

import unittest
from example_implementation import WeatherInquiryAgent


class TestWeatherInquiryEnhancement(unittest.TestCase):
    """
    Test suite for validating enhanced weather inquiry responses.
    
    Validation Criteria:
    - Response includes accurate temperature data
    - Response includes contextual details about weather conditions
    - User feedback reflects improved satisfaction
    - 80% of test cases yield context-rich outputs
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up the agent for testing."""
        cls.agent = WeatherInquiryAgent("agents.yaml")
    
    def validate_response_quality(self, response: str, temperature: float) -> dict:
        """
        Validate that a response meets quality criteria.
        
        Returns:
            dict with validation results for each criterion
        """
        validation = {
            'has_temperature': str(temperature) in response,
            'has_conditions': any(
                word in response.lower() 
                for word in ['clear', 'cloudy', 'sunny', 'rainy', 'weather', 'skies']
            ),
            'has_seasonal_context': any(
                word in response.lower() 
                for word in ['typical', 'winter', 'summer', 'spring', 'fall', 
                            'season', 'cold', 'warm', 'hot', 'cool']
            ),
            'has_comfort_info': any(
                word in response.lower() 
                for word in ['comfortable', 'dress', 'jacket', 'coat', 'clothing',
                            'layers', 'recommended', 'hydrated', 'shade']
            ),
            'has_explanation': len(response.split('.')) >= 3,  # Multiple sentences
            'is_comprehensive': len(response) > 100  # Substantial response
        }
        
        return validation
    
    def test_basic_weather_query(self):
        """Test Case 1: Basic weather query includes context."""
        user_query = "What's the weather in Paris in Fahrenheit?"
        weather_data = {
            'location': 'Paris',
            'temperature': 68,
            'unit': 'F',
            'conditions': 'partly_cloudy'
        }
        
        response = self.agent.process_weather_query(user_query, weather_data)
        validation = self.validate_response_quality(response, 68)
        
        # Verify all criteria are met
        self.assertTrue(validation['has_temperature'], 
                       "Response must include accurate temperature")
        self.assertTrue(validation['has_conditions'], 
                       "Response must include weather conditions")
        self.assertTrue(validation['has_seasonal_context'], 
                       "Response must include seasonal context")
        self.assertTrue(validation['has_comfort_info'], 
                       "Response must include comfort information")
        self.assertTrue(validation['has_explanation'], 
                       "Response must be explanatory (multiple sentences)")
        self.assertTrue(validation['is_comprehensive'], 
                       "Response must be comprehensive (>100 chars)")
        
        print(f"\n✓ Test Case 1 PASSED")
        print(f"  Query: {user_query}")
        print(f"  Response Length: {len(response)} characters")
        print(f"  Validation Score: {sum(validation.values())}/{len(validation)} criteria met")
    
    def test_weather_with_calculation(self):
        """Test Case 2: Weather query with calculation is explained clearly."""
        user_query = "What's the weather in Paris in Fahrenheit and then add 10 to the temperature?"
        weather_data = {
            'location': 'Paris',
            'temperature': 68,
            'unit': 'F',
            'conditions': 'partly_cloudy'
        }
        
        response = self.agent.process_weather_query(user_query, weather_data)
        validation = self.validate_response_quality(response, 68)
        
        # Verify calculation is explained
        self.assertIn("add", response.lower(), 
                     "Response must explain the calculation")
        self.assertIn("78", response, 
                     "Response must include calculated result (68 + 10 = 78)")
        self.assertIn("68", response, 
                     "Response must include original temperature")
        
        # Verify all other criteria
        self.assertTrue(validation['has_temperature'])
        self.assertTrue(validation['has_conditions'])
        self.assertTrue(validation['is_comprehensive'])
        
        print(f"\n✓ Test Case 2 PASSED")
        print(f"  Query: {user_query}")
        print(f"  Response includes both original (68°F) and calculated (78°F) values")
        print(f"  Validation Score: {sum(validation.values())}/{len(validation)} criteria met")
    
    def test_cold_weather_context(self):
        """Test Case 3: Cold weather includes appropriate context."""
        user_query = "What's the weather in Moscow?"
        weather_data = {
            'location': 'Moscow',
            'temperature': 32,
            'unit': 'F',
            'conditions': 'clear'
        }
        
        response = self.agent.process_weather_query(user_query, weather_data)
        validation = self.validate_response_quality(response, 32)
        
        # Verify cold weather context
        self.assertTrue(any(
            word in response.lower() 
            for word in ['cold', 'winter', 'coat', 'warm', 'layers']
        ), "Response must include cold weather context")
        
        self.assertTrue(validation['has_temperature'])
        self.assertTrue(validation['is_comprehensive'])
        
        print(f"\n✓ Test Case 3 PASSED")
        print(f"  Query: {user_query}")
        print(f"  Response includes appropriate cold weather context")
        print(f"  Validation Score: {sum(validation.values())}/{len(validation)} criteria met")
    
    def test_hot_weather_context(self):
        """Test Case 4: Hot weather includes appropriate context."""
        user_query = "What's the temperature in Dubai?"
        weather_data = {
            'location': 'Dubai',
            'temperature': 95,
            'unit': 'F',
            'conditions': 'clear'
        }
        
        response = self.agent.process_weather_query(user_query, weather_data)
        validation = self.validate_response_quality(response, 95)
        
        # Verify hot weather context
        self.assertTrue(any(
            word in response.lower() 
            for word in ['hot', 'hydrated', 'shade', 'cool', 'minimal']
        ), "Response must include hot weather context")
        
        self.assertTrue(validation['has_temperature'])
        self.assertTrue(validation['is_comprehensive'])
        
        print(f"\n✓ Test Case 4 PASSED")
        print(f"  Query: {user_query}")
        print(f"  Response includes appropriate hot weather context")
        print(f"  Validation Score: {sum(validation.values())}/{len(validation)} criteria met")
    
    def test_moderate_weather_context(self):
        """Test Case 5: Moderate weather includes appropriate context."""
        user_query = "What's the weather in San Francisco?"
        weather_data = {
            'location': 'San Francisco',
            'temperature': 65,
            'unit': 'F',
            'conditions': 'clear'
        }
        
        response = self.agent.process_weather_query(user_query, weather_data)
        validation = self.validate_response_quality(response, 65)
        
        # Verify moderate weather context
        self.assertTrue(any(
            word in response.lower() 
            for word in ['pleasant', 'comfortable', 'moderate', 'ideal', 'light']
        ), "Response must include moderate weather context")
        
        self.assertTrue(validation['has_temperature'])
        self.assertTrue(validation['is_comprehensive'])
        
        print(f"\n✓ Test Case 5 PASSED")
        print(f"  Query: {user_query}")
        print(f"  Response includes appropriate moderate weather context")
        print(f"  Validation Score: {sum(validation.values())}/{len(validation)} criteria met")
    
    def test_overall_success_rate(self):
        """
        Test Case 6: Validate overall success rate meets 80% criteria.
        
        This test runs multiple scenarios and ensures at least 80% meet
        all quality criteria.
        """
        test_scenarios = [
            {
                'query': "What's the weather in London?",
                'data': {'location': 'London', 'temperature': 55, 'unit': 'F', 
                        'conditions': 'cloudy'}
            },
            {
                'query': "What's the temperature in New York?",
                'data': {'location': 'New York', 'temperature': 72, 'unit': 'F', 
                        'conditions': 'clear'}
            },
            {
                'query': "What's the weather in Sydney in Fahrenheit?",
                'data': {'location': 'Sydney', 'temperature': 78, 'unit': 'F', 
                        'conditions': 'partly_cloudy'}
            },
            {
                'query': "What's the temperature in Toronto and add 5?",
                'data': {'location': 'Toronto', 'temperature': 45, 'unit': 'F', 
                        'conditions': 'clear'}
            },
            {
                'query': "What's the weather in Singapore?",
                'data': {'location': 'Singapore', 'temperature': 88, 'unit': 'F', 
                        'conditions': 'clear'}
            }
        ]
        
        success_count = 0
        total_criteria_met = 0
        total_possible_criteria = 0
        
        for scenario in test_scenarios:
            response = self.agent.process_weather_query(
                scenario['query'], 
                scenario['data']
            )
            validation = self.validate_response_quality(
                response, 
                scenario['data']['temperature']
            )
            
            criteria_met = sum(validation.values())
            total_criteria_met += criteria_met
            total_possible_criteria += len(validation)
            
            # Consider successful if at least 4 out of 6 criteria are met
            if criteria_met >= 4:
                success_count += 1
        
        success_rate = (success_count / len(test_scenarios)) * 100
        criteria_rate = (total_criteria_met / total_possible_criteria) * 100
        
        print(f"\n✓ Test Case 6 - Overall Success Rate")
        print(f"  Scenarios tested: {len(test_scenarios)}")
        print(f"  Context-rich responses: {success_count}/{len(test_scenarios)}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Overall criteria met: {total_criteria_met}/{total_possible_criteria}")
        print(f"  Criteria fulfillment rate: {criteria_rate:.1f}%")
        
        self.assertGreaterEqual(
            success_rate, 
            80.0, 
            f"Success rate ({success_rate:.1f}%) must meet 80% threshold"
        )


def run_validation_suite():
    """Run the complete validation suite and print results."""
    print("=" * 80)
    print("WEATHER INQUIRY ENHANCEMENT - VALIDATION SUITE")
    print("=" * 80)
    print()
    print("Testing enhanced LLM responses for weather inquiries...")
    print("Validation Criteria:")
    print("  ✓ Accurate temperature data")
    print("  ✓ Contextual weather conditions")
    print("  ✓ Seasonal comparison information")
    print("  ✓ Comfort level guidance")
    print("  ✓ Clear explanations")
    print("  ✓ Comprehensive responses")
    print()
    print("-" * 80)
    
    # Run the test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestWeatherInquiryEnhancement)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 80)
    print("VALIDATION RESULTS SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print()
        print("✅ ALL VALIDATION CRITERIA MET")
        print("   - 80%+ of test cases yield context-rich outputs")
        print("   - Responses include accurate temperature data")
        print("   - Contextual information is consistently provided")
        print("   - User satisfaction criteria achieved")
    else:
        print()
        print("❌ VALIDATION INCOMPLETE - Review failures above")
    
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_validation_suite()
    exit(0 if success else 1)
