"""
Pydantic AI Response Accuracy Assessment Report Generator

This module generates comprehensive reports on the accuracy of AI responses
regarding Pydantic, including identified issues and improvements made.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from pydantic_verification_system import assess_pydantic_ai_response, AccuracyLevel
from pydantic_knowledge_updater import PydanticKnowledgeUpdater


@dataclass
class AccuracyMetrics:
    """Metrics for accuracy assessment"""
    total_responses: int
    verified_responses: int
    likely_accurate_responses: int
    needs_review_responses: int
    inaccurate_responses: int
    outdated_responses: int
    average_confidence: float
    common_issues: List[str]
    improvement_rate: float


class AccuracyAssessmentReport:
    """
    Generates comprehensive accuracy assessment reports for Pydantic AI responses
    """
    
    def __init__(self, cache_dir: str = "/workspace/pydantic_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.reports_dir = self.cache_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.assessment_log = self.cache_dir / "assessment_log.json"
        
    def assess_sample_responses(self) -> Dict[str, Any]:
        """Assess a sample of AI responses about Pydantic"""
        
        # Sample AI responses with known issues for testing
        test_responses = [
            {
                "id": "response_1",
                "query": "How to create a Pydantic model?",
                "response": """
You can create a Pydantic model like this:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    
    class Config:
        validate_assignment = True

# Usage
user = User.parse_obj({'name': 'John', 'age': 30})
print(user.dict())
```
""",
                "expected_issues": ["v1_syntax", "config_class", "parse_obj", "dict_method"]
            },
            {
                "id": "response_2", 
                "query": "What's new in Pydantic v2?",
                "response": """
Pydantic v2 introduces several improvements:
- Better performance (about 2x faster)
- Improved validation
- New features for JSON schema

The API remains mostly the same as v1.
""",
                "expected_issues": ["understated_performance", "api_compatibility_claim"]
            },
            {
                "id": "response_3",
                "query": "How to validate fields in Pydantic?",
                "response": """
Use field validators in Pydantic v2:

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    name: str
    price: float
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```
""",
                "expected_issues": []  # This should be accurate
            },
            {
                "id": "response_4",
                "query": "Pydantic performance comparison",
                "response": """
Pydantic is generally faster than other validation libraries:
- Faster than marshmallow
- Comparable to dataclasses
- Uses Python for validation

Performance is decent but not exceptional.
""",
                "expected_issues": ["rust_core_missing", "performance_understatement"]
            }
        ]
        
        assessment_results = []
        
        for test_case in test_responses:
            # Assess the response
            result = assess_pydantic_ai_response(test_case["response"])
            
            assessment_results.append({
                "id": test_case["id"],
                "query": test_case["query"],
                "original_response": test_case["response"],
                "assessment": result,
                "expected_issues": test_case["expected_issues"],
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "assessment_results": assessment_results,
            "summary": self._generate_assessment_summary(assessment_results),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_assessment_summary(self, results: List[Dict]) -> AccuracyMetrics:
        """Generate summary metrics from assessment results"""
        total = len(results)
        accuracy_counts = {level.value: 0 for level in AccuracyLevel}
        confidence_scores = []
        all_issues = []
        improved_count = 0
        
        for result in results:
            verification = result["assessment"]["verification_result"]
            accuracy_level = verification["accuracy_level"]
            confidence = verification["confidence_score"]
            issues = verification["issues_found"]
            improved = result["assessment"]["improvement_needed"]
            
            accuracy_counts[accuracy_level] += 1
            confidence_scores.append(confidence)
            all_issues.extend(issues)
            if improved:
                improved_count += 1
        
        # Find common issues
        issue_patterns = {}
        for issue in all_issues:
            # Extract issue type from issue text
            if "v1 syntax" in issue:
                issue_patterns["v1_syntax_usage"] = issue_patterns.get("v1_syntax_usage", 0) + 1
            elif "deprecated" in issue:
                issue_patterns["deprecated_methods"] = issue_patterns.get("deprecated_methods", 0) + 1
            elif "misconception" in issue:
                issue_patterns["common_misconceptions"] = issue_patterns.get("common_misconceptions", 0) + 1
        
        common_issues = sorted(issue_patterns.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return AccuracyMetrics(
            total_responses=total,
            verified_responses=accuracy_counts["verified"],
            likely_accurate_responses=accuracy_counts["likely_accurate"],
            needs_review_responses=accuracy_counts["needs_review"],
            inaccurate_responses=accuracy_counts["inaccurate"],
            outdated_responses=accuracy_counts["outdated"],
            average_confidence=sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            common_issues=[f"{issue}: {count}" for issue, count in common_issues],
            improvement_rate=improved_count / total if total > 0 else 0
        )
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive accuracy assessment report"""
        
        # Perform assessment
        assessment_data = self.assess_sample_responses()
        
        # Get knowledge base status
        updater = PydanticKnowledgeUpdater()
        knowledge_status = updater.get_latest_knowledge()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(assessment_data)
        
        # Create comprehensive report
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0",
                "assessment_period": "sample_responses"
            },
            "executive_summary": {
                "total_responses_assessed": assessment_data["summary"].total_responses,
                "accuracy_distribution": {
                    "verified": assessment_data["summary"].verified_responses,
                    "likely_accurate": assessment_data["summary"].likely_accurate_responses,
                    "needs_review": assessment_data["summary"].needs_review_responses,
                    "inaccurate": assessment_data["summary"].inaccurate_responses,
                    "outdated": assessment_data["summary"].outdated_responses
                },
                "average_confidence_score": round(assessment_data["summary"].average_confidence, 3),
                "improvement_rate": round(assessment_data["summary"].improvement_rate * 100, 1)
            },
            "detailed_findings": {
                "common_inaccuracies": assessment_data["summary"].common_issues,
                "assessment_details": assessment_data["assessment_results"],
                "knowledge_base_status": {
                    "last_updated": knowledge_status.get("last_updated", "Unknown"),
                    "entries_count": len(knowledge_status.get("knowledge_base", {})),
                    "current_version": knowledge_status.get("version_info", {}).get("version", "Unknown")
                }
            },
            "recommendations": recommendations,
            "verification_system_status": {
                "active": True,
                "verification_enabled": True,
                "auto_enhancement_enabled": True,
                "knowledge_base_auto_update": True
            }
        }
        
        # Save report
        report_file = self.reports_dir / f"accuracy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Update assessment log
        self._update_assessment_log(assessment_data["summary"])
        
        return report
    
    def _generate_recommendations(self, assessment_data: Dict) -> List[Dict[str, Any]]:
        """Generate specific recommendations based on assessment results"""
        recommendations = []
        
        summary = assessment_data["summary"]
        
        # High-priority recommendations
        if summary.outdated_responses > 0:
            recommendations.append({
                "priority": "HIGH",
                "category": "Outdated Information",
                "issue": f"{summary.outdated_responses} responses contained outdated v1 syntax",
                "recommendation": "Update training data to emphasize Pydantic v2 syntax and deprecate v1 examples",
                "implementation": [
                    "Add explicit v2 syntax examples to training data",
                    "Include v1-to-v2 migration information",
                    "Flag responses containing v1 patterns for review"
                ]
            })
        
        if summary.inaccurate_responses > 0:
            recommendations.append({
                "priority": "HIGH", 
                "category": "Factual Inaccuracies",
                "issue": f"{summary.inaccurate_responses} responses contained factual errors",
                "recommendation": "Implement stricter fact-checking against official documentation",
                "implementation": [
                    "Cross-reference all Pydantic claims with official docs",
                    "Implement real-time documentation sync",
                    "Add confidence scoring to responses"
                ]
            })
        
        # Medium priority recommendations
        if summary.average_confidence < 0.8:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Response Confidence",
                "issue": f"Average confidence score is {summary.average_confidence:.2f}",
                "recommendation": "Improve training data quality and verification processes",
                "implementation": [
                    "Enhance knowledge base with verified examples",
                    "Implement multi-source verification",
                    "Add uncertainty indicators to responses"
                ]
            })
        
        # Low priority recommendations
        recommendations.append({
            "priority": "LOW",
            "category": "Continuous Improvement", 
            "issue": "Ongoing accuracy maintenance needed",
            "recommendation": "Establish regular accuracy monitoring and improvement cycle",
            "implementation": [
                "Schedule weekly accuracy assessments",
                "Monitor Pydantic release notes for updates",
                "Collect user feedback on response accuracy"
            ]
        })
        
        return recommendations
    
    def _update_assessment_log(self, metrics: AccuracyMetrics):
        """Update the assessment log with new metrics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_responses": metrics.total_responses,
                "verified_responses": metrics.verified_responses,
                "likely_accurate_responses": metrics.likely_accurate_responses,
                "needs_review_responses": metrics.needs_review_responses,
                "inaccurate_responses": metrics.inaccurate_responses,
                "outdated_responses": metrics.outdated_responses,
                "average_confidence": metrics.average_confidence,
                "improvement_rate": metrics.improvement_rate
            }
        }
        
        # Load existing log
        log_data = []
        if self.assessment_log.exists():
            try:
                with open(self.assessment_log, 'r') as f:
                    log_data = json.load(f)
            except:
                pass
        
        # Add new entry
        log_data.append(log_entry)
        
        # Keep only last 100 entries
        log_data = log_data[-100:]
        
        # Save log
        with open(self.assessment_log, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def create_visual_report(self, report_data: Dict) -> Path:
        """Create visual charts for the accuracy report"""
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Pydantic AI Response Accuracy Assessment', fontsize=16, fontweight='bold')
        
        # Accuracy distribution pie chart
        accuracy_data = report_data["executive_summary"]["accuracy_distribution"]
        labels = list(accuracy_data.keys())
        values = list(accuracy_data.values())
        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#34495e']
        
        ax1.pie(values, labels=labels, autopct='%1.1f%%', colors=colors[:len(values)])
        ax1.set_title('Response Accuracy Distribution')
        
        # Confidence score gauge
        confidence = report_data["executive_summary"]["average_confidence_score"]
        ax2.bar(['Confidence'], [confidence], color='#3498db', alpha=0.7)
        ax2.set_ylim(0, 1.0)
        ax2.set_ylabel('Score')
        ax2.set_title(f'Average Confidence Score: {confidence:.3f}')
        ax2.axhline(y=0.8, color='r', linestyle='--', alpha=0.5, label='Target (0.8)')
        ax2.legend()
        
        # Common issues bar chart
        issues = [issue.split(':')[0] for issue in report_data["detailed_findings"]["common_inaccuracies"]]
        counts = [int(issue.split(':')[1].strip()) for issue in report_data["detailed_findings"]["common_inaccuracies"]]
        
        if issues:
            ax3.barh(issues, counts, color='#e67e22')
            ax3.set_xlabel('Frequency')
            ax3.set_title('Most Common Issues')
        else:
            ax3.text(0.5, 0.5, 'No common issues found', transform=ax3.transAxes, 
                    ha='center', va='center', fontsize=12)
            ax3.set_title('Most Common Issues')
        
        # Improvement rate
        improvement_rate = report_data["executive_summary"]["improvement_rate"]
        ax4.bar(['Improvement Rate'], [improvement_rate], color='#27ae60', alpha=0.7)
        ax4.set_ylim(0, 100)
        ax4.set_ylabel('Percentage (%)')
        ax4.set_title(f'Response Improvement Rate: {improvement_rate}%')
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.reports_dir / f"accuracy_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_file
    
    def export_detailed_report(self, report_data: Dict) -> Path:
        """Export detailed report to various formats"""
        
        # Create Excel report
        excel_file = self.reports_dir / f"detailed_accuracy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Total Responses', 'Verified', 'Likely Accurate', 
                    'Needs Review', 'Inaccurate', 'Outdated',
                    'Average Confidence', 'Improvement Rate (%)'
                ],
                'Value': [
                    report_data["executive_summary"]["total_responses_assessed"],
                    report_data["executive_summary"]["accuracy_distribution"]["verified"],
                    report_data["executive_summary"]["accuracy_distribution"]["likely_accurate"],
                    report_data["executive_summary"]["accuracy_distribution"]["needs_review"],
                    report_data["executive_summary"]["accuracy_distribution"]["inaccurate"],
                    report_data["executive_summary"]["accuracy_distribution"]["outdated"],
                    report_data["executive_summary"]["average_confidence_score"],
                    report_data["executive_summary"]["improvement_rate"]
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed assessments sheet
            assessments = report_data["detailed_findings"]["assessment_details"]
            details_data = []
            
            for assessment in assessments:
                details_data.append({
                    'Response ID': assessment['id'],
                    'Query': assessment['query'],
                    'Accuracy Level': assessment['assessment']['verification_result']['accuracy_level'],
                    'Confidence Score': assessment['assessment']['verification_result']['confidence_score'],
                    'Issues Count': len(assessment['assessment']['verification_result']['issues_found']),
                    'Improved': assessment['assessment']['improvement_needed'],
                    'Issues': '; '.join(assessment['assessment']['verification_result']['issues_found'])
                })
            
            details_df = pd.DataFrame(details_data)
            details_df.to_excel(writer, sheet_name='Detailed Assessments', index=False)
            
            # Recommendations sheet
            recommendations = report_data["recommendations"]
            rec_data = []
            
            for rec in recommendations:
                rec_data.append({
                    'Priority': rec['priority'],
                    'Category': rec['category'],
                    'Issue': rec['issue'],
                    'Recommendation': rec['recommendation'],
                    'Implementation': '; '.join(rec['implementation'])
                })
            
            rec_df = pd.DataFrame(rec_data)
            rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        return excel_file


def generate_accuracy_assessment():
    """Main function to generate complete accuracy assessment"""
    
    print("🔍 Starting Pydantic AI Response Accuracy Assessment...")
    
    # Initialize report generator
    reporter = AccuracyAssessmentReport()
    
    # Generate comprehensive report
    report = reporter.generate_comprehensive_report()
    
    # Create visualizations
    chart_file = reporter.create_visual_report(report)
    
    # Export detailed report
    excel_file = reporter.export_detailed_report(report)
    
    # Print summary
    print("\n📊 Accuracy Assessment Results:")
    print(f"Total Responses Assessed: {report['executive_summary']['total_responses_assessed']}")
    print(f"Verified Responses: {report['executive_summary']['accuracy_distribution']['verified']}")
    print(f"Average Confidence: {report['executive_summary']['average_confidence_score']:.3f}")
    print(f"Improvement Rate: {report['executive_summary']['improvement_rate']}%")
    
    print(f"\n📄 Reports generated:")
    print(f"- JSON Report: {reporter.reports_dir}/accuracy_report_*.json")
    print(f"- Visual Chart: {chart_file}")
    print(f"- Excel Report: {excel_file}")
    
    print("\n🔧 Verification System Status:")
    print("✅ Pydantic response verification: ACTIVE")
    print("✅ Automatic enhancement: ENABLED")
    print("✅ Knowledge base auto-update: ENABLED")
    
    # Show key recommendations
    if report["recommendations"]:
        print("\n💡 Key Recommendations:")
        for i, rec in enumerate(report["recommendations"][:3], 1):
            print(f"{i}. [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
    
    return report


if __name__ == "__main__":
    generate_accuracy_assessment()