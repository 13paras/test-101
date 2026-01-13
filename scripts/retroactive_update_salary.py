import os
import sys
import re
from src.job_posting.compensation import get_salary_range_for_band

def update_postings(directory, band):
    salary_range = get_salary_range_for_band(band)
    if not salary_range:
        print(f"Invalid band: {band}")
        return

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                content = f.read()

            if "Salary Range:" not in content:
                print(f"Updating {filename}...")
                # Simple logic to add salary range before Location or at the end
                if "Location" in content:
                    new_content = re.sub(r"(Location)", f"Salary Range: {salary_range}\n\n\\1", content)
                else:
                    new_content = content + f"\n\nSalary Range: {salary_range}"
                
                with open(filepath, 'w') as f:
                    f.write(new_content)
            else:
                print(f"Skipping {filename}, Salary Range already present.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python retroactive_update_salary.py <directory> <band>")
        sys.exit(1)
    
    update_postings(sys.argv[1], sys.argv[2])
