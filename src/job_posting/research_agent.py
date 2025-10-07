import logging
from typing import Dict, Any, List, Optional
from crewai import Agent
from crewai_tools import SerperDevTool, WebsiteSearchTool

# Configure logging for context tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextPropagationError(Exception):
    """Raised when required context data is missing during workflow execution."""
    pass


class ResearchAgent:
    """
    Custom Research Agent with enhanced context propagation capabilities.
    
    This agent maintains a context dictionary throughout the execution workflow
    to ensure all necessary data is captured and passed between tool calls.
    """
    
    # Define required context keys for validation
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
    
    def __init__(self, agent: Agent):
        """
        Initialize the ResearchAgent with context management.
        
        Args:
            agent: The underlying CrewAI Agent instance
        """
        self.agent = agent
        self.context: Dict[str, Any] = {}
        self._initialize_context()
        logger.info("ResearchAgent initialized with empty context")
    
    def _initialize_context(self):
        """Initialize the context dictionary with default values."""
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
        logger.info("Context initialized with default values")
    
    def execute_search(self, query: str, search_type: str, tool_name: str = 'web_search') -> Dict[str, Any]:
        """
        Execute a search operation while maintaining context.
        
        This method initializes and maintains a context dictionary that preserves
        information across tool executions.
        
        Args:
            query: The search query to execute
            search_type: Type of search (e.g., 'company_culture', 'role_requirements', 'industry_analysis')
            tool_name: Name of the tool to use ('web_search' or 'serper')
        
        Returns:
            Dict containing search results and updated context
        """
        logger.info(f"Executing {search_type} search with query: {query}")
        logger.info(f"Context state before search: {self._get_context_summary()}")
        
        try:
            # Track search attempt
            self.context['metadata']['total_searches'] += 1
            
            # Execute search based on tool type
            result = self._perform_search(query, tool_name)
            
            # Update context with search results
            self._update_context(search_type, result)
            
            # Track successful search
            self.context['metadata']['successful_searches'] += 1
            
            logger.info(f"Search completed successfully. Context state after search: {self._get_context_summary()}")
            
            return {
                'success': True,
                'search_type': search_type,
                'result': result,
                'context': self.context.copy()
            }
            
        except Exception as e:
            # Track failed search
            self.context['metadata']['failed_searches'] += 1
            logger.error(f"Search failed for {search_type}: {str(e)}")
            logger.error(f"Context state at failure: {self._get_context_summary()}")
            
            return {
                'success': False,
                'search_type': search_type,
                'error': str(e),
                'context': self.context.copy()
            }
    
    def _perform_search(self, query: str, tool_name: str) -> str:
        """
        Perform the actual search operation using the specified tool.
        
        Args:
            query: The search query
            tool_name: Name of the tool to use
        
        Returns:
            Search results as string
        """
        # This is a placeholder for actual tool execution
        # In a real implementation, this would call the actual CrewAI tools
        logger.info(f"Performing search with {tool_name}: {query}")
        return f"Search results for: {query}"
    
    def _update_context(self, search_type: str, result: Any):
        """
        Update the context dictionary based on search type and results.
        
        Args:
            search_type: Type of search performed
            result: Search results to incorporate into context
        """
        previous_value = None
        
        # Map search types to context keys and update accordingly
        if search_type == 'company_culture':
            previous_value = self.context.get('company_culture')
            self.context['company_culture'] = result
            
        elif search_type == 'company_values':
            previous_value = self.context.get('company_values')
            self.context['company_values'] = result
            
        elif search_type == 'company_mission':
            previous_value = self.context.get('company_mission')
            self.context['company_mission'] = result
            
        elif search_type == 'company_selling_points':
            previous_value = self.context['company_selling_points'].copy()
            if isinstance(result, list):
                self.context['company_selling_points'].extend(result)
            else:
                self.context['company_selling_points'].append(result)
                
        elif search_type == 'role_skills':
            previous_value = self.context['role_skills'].copy()
            if isinstance(result, list):
                self.context['role_skills'].extend(result)
            else:
                self.context['role_skills'].append(result)
                
        elif search_type == 'role_experience':
            previous_value = self.context['role_experience'].copy()
            if isinstance(result, list):
                self.context['role_experience'].extend(result)
            else:
                self.context['role_experience'].append(result)
                
        elif search_type == 'role_qualities':
            previous_value = self.context['role_qualities'].copy()
            if isinstance(result, list):
                self.context['role_qualities'].extend(result)
            else:
                self.context['role_qualities'].append(result)
                
        elif search_type == 'industry_trends':
            previous_value = self.context['industry_trends'].copy()
            if isinstance(result, list):
                self.context['industry_trends'].extend(result)
            else:
                self.context['industry_trends'].append(result)
                
        elif search_type == 'industry_challenges':
            previous_value = self.context['industry_challenges'].copy()
            if isinstance(result, list):
                self.context['industry_challenges'].extend(result)
            else:
                self.context['industry_challenges'].append(result)
                
        elif search_type == 'industry_opportunities':
            previous_value = self.context['industry_opportunities'].copy()
            if isinstance(result, list):
                self.context['industry_opportunities'].extend(result)
            else:
                self.context['industry_opportunities'].append(result)
        
        # Store search result in history
        self.context['search_results'].append({
            'search_type': search_type,
            'result': result,
            'timestamp': self._get_timestamp()
        })
        
        # Track context update
        self.context['metadata']['context_updates'] += 1
        
        # Log the context change
        logger.info(f"Context updated for {search_type}")
        logger.info(f"Previous value: {previous_value}")
        logger.info(f"New value: {result}")
        logger.info(f"Total context updates: {self.context['metadata']['context_updates']}")
    
    def compose_report(self, report_type: str = 'comprehensive') -> str:
        """
        Compose a report from the collected context data.
        
        This method validates that all required context data is present before
        generating the report. If any required data is missing, it raises an error.
        
        Args:
            report_type: Type of report to generate ('comprehensive', 'summary', etc.)
        
        Returns:
            Generated report as string
        
        Raises:
            ContextPropagationError: If required context data is missing
        """
        logger.info(f"Composing {report_type} report")
        logger.info(f"Current context state: {self._get_context_summary()}")
        
        # Validate context before composing report
        missing_data = self._validate_context()
        
        if missing_data:
            error_msg = (
                f"Cannot compose report: Required context data is missing.\n"
                f"Missing fields: {', '.join(missing_data)}\n"
                f"Context state: {self._get_detailed_context_status()}"
            )
            logger.error(error_msg)
            raise ContextPropagationError(error_msg)
        
        logger.info("All required context data is present. Generating report...")
        
        # Generate report based on type
        if report_type == 'comprehensive':
            report = self._generate_comprehensive_report()
        elif report_type == 'summary':
            report = self._generate_summary_report()
        else:
            report = self._generate_comprehensive_report()
        
        logger.info("Report generated successfully")
        logger.info(f"Report length: {len(report)} characters")
        
        return report
    
    def _validate_context(self) -> List[str]:
        """
        Validate that all required context keys have non-empty values.
        
        Returns:
            List of missing or empty context keys
        """
        missing_data = []
        
        for key in self.REQUIRED_CONTEXT_KEYS:
            value = self.context.get(key)
            
            # Check if value is None or empty (for lists)
            if value is None:
                missing_data.append(key)
                logger.warning(f"Context validation: {key} is None")
            elif isinstance(value, list) and len(value) == 0:
                missing_data.append(key)
                logger.warning(f"Context validation: {key} is empty list")
        
        if missing_data:
            logger.warning(f"Context validation failed. Missing: {missing_data}")
        else:
            logger.info("Context validation passed. All required data present.")
        
        return missing_data
    
    def _generate_comprehensive_report(self) -> str:
        """Generate a comprehensive report from all context data."""
        report_sections = []
        
        # Company Culture Section
        report_sections.append("## Company Culture and Values\n")
        if self.context['company_culture']:
            report_sections.append(f"**Culture:** {self.context['company_culture']}\n")
        if self.context['company_values']:
            report_sections.append(f"**Values:** {self.context['company_values']}\n")
        if self.context['company_mission']:
            report_sections.append(f"**Mission:** {self.context['company_mission']}\n")
        
        # Company Selling Points
        if self.context['company_selling_points']:
            report_sections.append("\n## Company Selling Points\n")
            for point in self.context['company_selling_points']:
                report_sections.append(f"- {point}\n")
        
        # Role Requirements Section
        report_sections.append("\n## Role Requirements\n")
        
        if self.context['role_skills']:
            report_sections.append("\n### Required Skills\n")
            for skill in self.context['role_skills']:
                report_sections.append(f"- {skill}\n")
        
        if self.context['role_experience']:
            report_sections.append("\n### Required Experience\n")
            for exp in self.context['role_experience']:
                report_sections.append(f"- {exp}\n")
        
        if self.context['role_qualities']:
            report_sections.append("\n### Desired Qualities\n")
            for quality in self.context['role_qualities']:
                report_sections.append(f"- {quality}\n")
        
        # Industry Analysis Section
        report_sections.append("\n## Industry Analysis\n")
        
        if self.context['industry_trends']:
            report_sections.append("\n### Current Trends\n")
            for trend in self.context['industry_trends']:
                report_sections.append(f"- {trend}\n")
        
        if self.context['industry_challenges']:
            report_sections.append("\n### Industry Challenges\n")
            for challenge in self.context['industry_challenges']:
                report_sections.append(f"- {challenge}\n")
        
        if self.context['industry_opportunities']:
            report_sections.append("\n### Opportunities\n")
            for opportunity in self.context['industry_opportunities']:
                report_sections.append(f"- {opportunity}\n")
        
        # Metadata
        report_sections.append("\n## Research Metadata\n")
        report_sections.append(f"- Total Searches: {self.context['metadata']['total_searches']}\n")
        report_sections.append(f"- Successful Searches: {self.context['metadata']['successful_searches']}\n")
        report_sections.append(f"- Context Updates: {self.context['metadata']['context_updates']}\n")
        
        return ''.join(report_sections)
    
    def _generate_summary_report(self) -> str:
        """Generate a summary report with key highlights."""
        summary = []
        
        summary.append("## Research Summary\n\n")
        
        if self.context['company_culture']:
            summary.append(f"**Culture:** {self.context['company_culture']}\n\n")
        
        if self.context['role_skills']:
            summary.append(f"**Key Skills:** {', '.join(self.context['role_skills'][:5])}\n\n")
        
        if self.context['industry_trends']:
            summary.append(f"**Industry Trends:** {', '.join(self.context['industry_trends'][:3])}\n\n")
        
        return ''.join(summary)
    
    def _get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context state."""
        return {
            'has_company_culture': self.context['company_culture'] is not None,
            'has_company_values': self.context['company_values'] is not None,
            'has_company_mission': self.context['company_mission'] is not None,
            'num_selling_points': len(self.context['company_selling_points']),
            'num_skills': len(self.context['role_skills']),
            'num_experience': len(self.context['role_experience']),
            'num_qualities': len(self.context['role_qualities']),
            'num_trends': len(self.context['industry_trends']),
            'num_challenges': len(self.context['industry_challenges']),
            'num_opportunities': len(self.context['industry_opportunities']),
            'total_searches': self.context['metadata']['total_searches'],
            'successful_searches': self.context['metadata']['successful_searches']
        }
    
    def _get_detailed_context_status(self) -> str:
        """Get a detailed status of all context fields."""
        status_lines = []
        
        for key in self.REQUIRED_CONTEXT_KEYS:
            value = self.context.get(key)
            
            if value is None:
                status = "MISSING (None)"
            elif isinstance(value, list):
                status = f"OK ({len(value)} items)" if len(value) > 0 else "EMPTY (0 items)"
            else:
                status = "OK"
            
            status_lines.append(f"{key}: {status}")
        
        return "\n".join(status_lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for logging."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get a copy of the current context.
        
        Returns:
            Copy of the context dictionary
        """
        return self.context.copy()
    
    def update_context(self, key: str, value: Any):
        """
        Manually update a specific context key.
        
        Args:
            key: Context key to update
            value: New value for the key
        """
        previous_value = self.context.get(key)
        self.context[key] = value
        self.context['metadata']['context_updates'] += 1
        
        logger.info(f"Context manually updated for {key}")
        logger.info(f"Previous value: {previous_value}")
        logger.info(f"New value: {value}")
    
    def reset_context(self):
        """Reset the context to initial state."""
        logger.info("Resetting context to initial state")
        self._initialize_context()
        logger.info("Context reset complete")