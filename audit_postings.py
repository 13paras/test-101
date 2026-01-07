import os
import glob

def audit_postings(directory):
    """
    Scans markdown files in the directory for a 'Salary Range' section.
    """
    anomalies = []
    # Search for markdown files
    md_files = glob.glob(os.path.join(directory, "**/*.md"), recursive=True)
    
    for file_path in md_files:
        if any(ignored in file_path for ignored in ["node_modules", ".pytest_cache", "README.md"]):
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
            if "Salary Range" not in content:
                anomalies.append(file_path)
    
    return anomalies

if __name__ == "__main__":
    search_dir = "/workspace"
    print(f"Auditing postings in {search_dir}...")
    anomalies = audit_postings(search_dir)
    
    if anomalies:
        print("\nAnomalies found (missing Salary Range):")
        for anomaly in anomalies:
            print(f"- {anomaly}")
    else:
        print("\nNo anomalies found. All postings include a Salary Range.")
