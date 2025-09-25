#!/usr/bin/env python3
"""
Setup script for Pydantic AI Response Verification System

This script initializes the complete verification system and demonstrates its usage.
"""

import os
import sys
import subprocess
from pathlib import Path
from pydantic_knowledge_updater import PydanticKnowledgeUpdater
from accuracy_assessment_report import generate_accuracy_assessment


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Install project dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True


def initialize_knowledge_base():
    """Initialize the Pydantic knowledge base"""
    print("🧠 Initializing Pydantic knowledge base...")
    
    try:
        updater = PydanticKnowledgeUpdater()
        updater.update_knowledge_base()
        print("✅ Knowledge base initialized successfully")
        
        # Get knowledge base stats
        knowledge = updater.get_latest_knowledge()
        kb_entries = len(knowledge.get("knowledge_base", {}))
        version = knowledge.get("version_info", {}).get("version", "Unknown")
        
        print(f"📊 Knowledge base contains {kb_entries} entries")
        print(f"📋 Current Pydantic version tracked: {version}")
        
    except Exception as e:
        print(f"❌ Failed to initialize knowledge base: {e}")
        return False
    
    return True


def run_accuracy_assessment():
    """Run initial accuracy assessment"""
    print("🔍 Running initial accuracy assessment...")
    
    try:
        report = generate_accuracy_assessment()
        print("✅ Accuracy assessment completed")
        
        # Show key metrics
        total = report["executive_summary"]["total_responses_assessed"]
        verified = report["executive_summary"]["accuracy_distribution"]["verified"]
        confidence = report["executive_summary"]["average_confidence_score"]
        
        print(f"📈 Assessment Results: {verified}/{total} verified, {confidence:.3f} avg confidence")
        
    except Exception as e:
        print(f"❌ Failed to run accuracy assessment: {e}")
        return False
    
    return True


def test_verification_system():
    """Test the verification system with a sample response"""
    print("🧪 Testing verification system...")
    
    try:
        from pydantic_verification_system import assess_pydantic_ai_response
        
        # Test with a response containing v1 syntax
        test_response = """
        Pydantic is a data validation library. Here's how to use it:
        
        ```python
        from pydantic import BaseModel
        
        class User(BaseModel):
            name: str
            age: int
            
            class Config:
                validate_assignment = True
        
        user = User.parse_obj({'name': 'John', 'age': 30})
        print(user.dict())
        ```
        """
        
        result = assess_pydantic_ai_response(test_response)
        
        accuracy = result["verification_result"]["accuracy_level"]
        issues_count = len(result["verification_result"]["issues_found"])
        improved = result["improvement_needed"]
        
        print(f"✅ Verification system test completed")
        print(f"📊 Test result: {accuracy}, {issues_count} issues found, improved: {improved}")
        
        if improved:
            print("🔧 System correctly identified and enhanced outdated syntax")
        
    except Exception as e:
        print(f"❌ Verification system test failed: {e}")
        return False
    
    return True


def create_monitoring_setup():
    """Create monitoring and update setup"""
    print("⚙️  Setting up monitoring and update system...")
    
    cache_dir = Path("/workspace/pydantic_cache")
    cache_dir.mkdir(exist_ok=True)
    
    # Create a simple monitoring script
    monitor_script = cache_dir / "monitor.py"
    monitor_script.write_text("""#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_knowledge_updater import run_update_scheduler

if __name__ == "__main__":
    print("Starting Pydantic knowledge base monitoring...")
    run_update_scheduler()
""")
    
    monitor_script.chmod(0o755)
    
    # Create a simple status check script
    status_script = cache_dir / "status.py"
    status_script.write_text("""#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_knowledge_updater import PydanticKnowledgeUpdater

def check_status():
    updater = PydanticKnowledgeUpdater()
    knowledge = updater.get_latest_knowledge()
    
    print("🔍 Pydantic Verification System Status")
    print("=" * 40)
    print(f"Knowledge Base Entries: {len(knowledge.get('knowledge_base', {}))}")
    print(f"Last Updated: {knowledge.get('last_updated', 'Unknown')}")
    print(f"Current Version: {knowledge.get('version_info', {}).get('version', 'Unknown')}")
    print(f"Cache Directory: {updater.cache_dir}")
    print(f"System Time: {datetime.now().isoformat()}")
    
    # Check if files exist
    files_exist = {
        "Knowledge Base": updater.knowledge_file.exists(),
        "Version Info": updater.version_file.exists(),
        "Update Log": updater.update_log.exists()
    }
    
    print("\\nFile Status:")
    for name, exists in files_exist.items():
        status = "✅" if exists else "❌"
        print(f"{status} {name}")

if __name__ == "__main__":
    check_status()
""")
    
    status_script.chmod(0o755)
    
    print("✅ Monitoring setup created")
    print(f"📁 Monitor script: {monitor_script}")
    print(f"📊 Status script: {status_script}")
    
    return True


def main():
    """Main setup function"""
    print("🚀 Setting up Pydantic AI Response Verification System")
    print("=" * 60)
    
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Initialize Knowledge Base", initialize_knowledge_base),
        ("Test Verification System", test_verification_system),
        ("Run Accuracy Assessment", run_accuracy_assessment),
        ("Create Monitoring Setup", create_monitoring_setup)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Pydantic AI Response Verification System Setup Complete!")
    print("=" * 60)
    
    print("\n📖 Usage Guide:")
    print("1. The verification system is now integrated into your AI response pipeline")
    print("2. All Pydantic-related responses will be automatically verified and enhanced")
    print("3. Run accuracy assessments periodically with: python accuracy_assessment_report.py")
    print("4. Monitor knowledge base status with: python pydantic_cache/status.py")
    print("5. Start automated updates with: python pydantic_cache/monitor.py")
    
    print("\n🔧 Key Features Enabled:")
    print("✅ Automatic detection of Pydantic v1 syntax in responses")
    print("✅ Real-time enhancement of outdated code examples")
    print("✅ Verification against official Pydantic documentation")
    print("✅ Comprehensive accuracy reporting and monitoring")
    print("✅ Automated knowledge base updates")
    
    print("\n📊 Next Steps:")
    print("- Monitor the accuracy reports for ongoing improvements")
    print("- Schedule regular knowledge base updates")
    print("- Review and act on verification system recommendations")
    print("- Collect user feedback on response quality")
    
    return True


if __name__ == "__main__":
    main()