# Quick Start Guide - Enhanced Weather Inquiry Agent

## Overview
This guide will help you quickly integrate the enhanced weather inquiry agent into your system.

---

## 🚀 Quick Setup (5 minutes)

### Prerequisites
- Python 3.7+
- PyYAML library (`pip install pyyaml`)
- Access to a weather API

### Installation

1. **Navigate to the agent directory**:
```bash
cd /workspace/agents/LLM_Call
```

2. **Verify files are present**:
```bash
ls -la
# Should show: agents.yaml, tasks.yaml, example_implementation.py, test_validation.py
```

3. **Run validation tests**:
```bash
python3 test_validation.py
```

Expected output:
```
✅ ALL VALIDATION CRITERIA MET
Success Rate: 100.0%
```

---

## 📋 Quick Test

### Option 1: Run the Example
```bash
python3 example_implementation.py
```

This will demonstrate three test cases with enhanced contextual responses.

### Option 2: Quick Python Test
```python
from example_implementation import WeatherInquiryAgent

# Initialize agent
agent = WeatherInquiryAgent("agents.yaml")

# Test query
query = "What's the weather in Paris?"
data = {
    'location': 'Paris',
    'temperature': 68,
    'unit': 'F',
    'conditions': 'partly_cloudy'
}

# Get enhanced response
response = agent.process_weather_query(query, data)
print(response)
```

---

## 🔧 Integration Examples

### Basic Integration

```python
import yaml
from typing import Dict, Any

# Load configuration
with open('agents.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Extract prompt template
weather_prompt = config['llm_call_session']['prompts']['weather_inquiry']['tools']['get_current_weather']['prompt']

# Use in your LLM system
def get_enhanced_weather_response(user_query: str, weather_data: Dict[str, Any]) -> str:
    """Generate enhanced weather response using the prompt template."""
    
    # Your LLM call here with the enhanced prompt
    llm_input = {
        'system_prompt': weather_prompt,
        'user_query': user_query,
        'weather_data': weather_data
    }
    
    response = your_llm_call(llm_input)
    return response
```

### With CrewAI Framework

```python
from crewai import Agent, Task, Crew
import yaml

# Load agent configuration
with open('agents.yaml', 'r') as f:
    agent_config = yaml.safe_load(f)

# Create agent
weather_agent = Agent(
    role=agent_config['llm_call_session']['role'],
    goal=agent_config['llm_call_session']['goal'],
    backstory=agent_config['llm_call_session']['backstory'],
    verbose=True
)

# Create task
weather_task = Task(
    description="Provide comprehensive weather information for user query",
    agent=weather_agent,
    expected_output="Contextual weather response with temperature and conditions"
)

# Run crew
crew = Crew(
    agents=[weather_agent],
    tasks=[weather_task]
)

result = crew.kickoff()
```

### With LangChain

```python
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import yaml

# Load prompt
with open('agents.yaml', 'r') as f:
    config = yaml.safe_load(f)
    
prompt_text = config['llm_call_session']['prompts']['weather_inquiry']['tools']['get_current_weather']['prompt']

# Create template
template = PromptTemplate(
    input_variables=["location", "temperature", "unit", "conditions"],
    template=prompt_text + "\n\nUser Query: {query}\nWeather Data: Location={location}, Temp={temperature}°{unit}, Conditions={conditions}"
)

# Use with LLM
llm = OpenAI(temperature=0.7)
chain = template | llm

response = chain.invoke({
    "query": "What's the weather in Paris?",
    "location": "Paris",
    "temperature": 68,
    "unit": "F",
    "conditions": "partly_cloudy"
})
```

---

## 📊 Response Quality Checklist

Every response should include:

- [ ] **Accurate Temperature**: Exact temperature in requested unit
- [ ] **Current Conditions**: Description of weather (sunny, cloudy, etc.)
- [ ] **Seasonal Context**: How it compares to typical weather
- [ ] **Comfort Guidance**: What to wear, activity recommendations
- [ ] **Calculations Explained**: If any math is involved, explain clearly
- [ ] **Natural Language**: Conversational and easy to understand

---

## 💡 Example Queries & Expected Outputs

### Query 1: Basic Weather
**Input**: "What's the weather in Tokyo?"

**Expected Output**:
```
The current temperature in Tokyo is 55°F. The skies are clear with plenty 
of sunshine. This is cool and comfortable, typical for spring or fall in 
Tokyo. A light jacket or sweater would be comfortable.
```

### Query 2: With Calculation
**Input**: "What's the weather in Paris in Fahrenheit and then add 10 to the temperature?"

**Expected Output**:
```
The current temperature in Paris is 68°F. With 10 degrees added, that would 
be 78°F. However, the actual current temperature is 68°F. The weather is 
partly cloudy with a light breeze. This is pleasant and moderate, typical 
spring or fall weather for Paris. Light clothing should be comfortable for 
outdoor activities.
```

### Query 3: Cold Weather
**Input**: "What's the temperature in Moscow?"

**Expected Output** (for 32°F):
```
The current temperature in Moscow is 32°F. The skies are clear with plenty 
of sunshine. This is quite cold for Moscow, typical of winter conditions. 
Dress warmly with layers, and consider a heavy coat.
```

---

## 🔍 Validation & Testing

### Quick Validation Test
```bash
# Run full validation suite
python3 test_validation.py

# Expected: All 6 tests pass with 100% success rate
```

### Manual Testing
```python
# Test different temperature ranges
test_cases = [
    {'temp': 32, 'expected_context': 'cold'},     # Cold weather
    {'temp': 55, 'expected_context': 'cool'},     # Cool weather
    {'temp': 68, 'expected_context': 'pleasant'}, # Moderate weather
    {'temp': 78, 'expected_context': 'warm'},     # Warm weather
    {'temp': 95, 'expected_context': 'hot'}       # Hot weather
]

for case in test_cases:
    data = {'location': 'Test City', 'temperature': case['temp'], 
            'unit': 'F', 'conditions': 'clear'}
    response = agent.process_weather_query("What's the weather?", data)
    assert case['expected_context'] in response.lower()
    print(f"✓ {case['temp']}°F test passed")
```

---

## 🛠️ Troubleshooting

### Issue: Tests Failing
**Solution**: Ensure you're in the correct directory
```bash
cd /workspace/agents/LLM_Call
python3 test_validation.py
```

### Issue: Import Errors
**Solution**: Install required dependencies
```bash
pip install pyyaml
```

### Issue: No Contextual Information
**Solution**: Verify you're using the correct prompt template from agents.yaml

### Issue: Calculations Not Explained
**Solution**: Check that the query contains keywords like "add", "plus", "subtract"

---

## 📈 Performance Metrics

After integration, monitor these metrics:

1. **Response Length**: Should average >150 characters
2. **Context Inclusion Rate**: Should be 100% (all responses have context)
3. **User Satisfaction**: Track feedback scores
4. **Calculation Accuracy**: Verify math is correct when applicable

---

## 🎯 Success Indicators

You'll know the integration is successful when:

✅ All validation tests pass  
✅ Responses are consistently >100 characters  
✅ Every response includes weather conditions  
✅ Seasonal context is always present  
✅ Comfort guidance is provided  
✅ Users report improved satisfaction  

---

## 📞 Support

If you encounter issues:

1. **Check Configuration**: Verify agents.yaml is properly loaded
2. **Review Examples**: See example_implementation.py for reference
3. **Run Tests**: Use test_validation.py to identify problems
4. **Check Documentation**: Refer to README.md for detailed info

---

## 🚦 Next Steps

After successful integration:

1. ✅ Monitor response quality in production
2. ✅ Collect user feedback
3. ✅ Track satisfaction metrics
4. ✅ Consider additional enhancements (multi-day forecasts, etc.)
5. ✅ Regularly update seasonal context based on feedback

---

## 📝 Quick Reference

### File Structure
```
agents/LLM_Call/
├── agents.yaml              # Main configuration
├── tasks.yaml               # Task definitions
├── example_implementation.py # Python implementation
├── test_validation.py       # Test suite
├── README.md                # Full documentation
├── IMPLEMENTATION_SUMMARY.md # Implementation details
└── QUICK_START.md           # This file
```

### Key Commands
```bash
# Run example
python3 example_implementation.py

# Run tests
python3 test_validation.py

# Verify config
python3 -c "import yaml; print(yaml.safe_load(open('agents.yaml')))"
```

### Configuration Path
Main prompt template location in agents.yaml:
```
llm_call_session → prompts → weather_inquiry → tools → get_current_weather → prompt
```

---

**Version**: 1.0  
**Last Updated**: October 6, 2025  
**Status**: Production Ready ✅
