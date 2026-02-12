#!/usr/bin/env python3
"""
GitHub Readiness Checker
Verifies that the project is ready to be pushed to GitHub
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report result"""
    if Path(filepath).exists():
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[MISSING] {description}: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).exists() and Path(dirpath).is_dir():
        print(f"[OK] {description}: {dirpath}")
        return True
    else:
        print(f"[MISSING] {description}: {dirpath}")
        return False

def check_gitignore():
    """Check if .gitignore has essential entries"""
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("[MISSING] .gitignore file")
        return False
    
    content = gitignore_path.read_text()
    essential_patterns = ["venv/", "__pycache__/", "*.pyc", ".env", "*.log"]
    missing = [p for p in essential_patterns if p not in content]
    
    if missing:
        print(f"[WARN] .gitignore missing patterns: {', '.join(missing)}")
        return False
    else:
        print("[OK] .gitignore has essential patterns")
        return True

def check_sensitive_files():
    """Check for sensitive files that shouldn't be in repo"""
    sensitive_patterns = [".env", "*.key", "*.pem", "credentials.json"]
    found = []
    
    for pattern in sensitive_patterns:
        if "*" in pattern:
            # Simple glob check
            files = list(Path(".").rglob(pattern))
            found.extend(files)
        else:
            if Path(pattern).exists():
                found.append(pattern)
    
    if found:
        print(f"[WARN] Potentially sensitive files found:")
        for f in found:
            print(f"    - {f}")
        return False
    else:
        print("[OK] No sensitive files detected")
        return True

def main():
    print("\n" + "="*80)
    print("GITHUB READINESS CHECK")
    print("="*80 + "\n")
    
    checks_passed = 0
    total_checks = 0
    
    # Essential files
    print("Essential Files:")
    total_checks += 5
    checks_passed += check_file_exists("README.md", "README")
    checks_passed += check_file_exists("LICENSE", "License")
    checks_passed += check_file_exists(".gitignore", "Git ignore")
    checks_passed += check_file_exists("requirements.txt", "Requirements")
    checks_passed += check_file_exists("CONTRIBUTING.md", "Contributing guide")
    print()
    
    # Optional but recommended
    print("Recommended Files:")
    total_checks += 3
    checks_passed += check_file_exists("SETUP.md", "Setup guide")
    checks_passed += check_file_exists(".env.example", "Environment template")
    checks_passed += check_file_exists(".github/workflows/python-ci.yml", "CI/CD workflow")
    print()
    
    # Main application
    print("Application Files:")
    total_checks += 2
    checks_passed += check_file_exists("app.py", "Main launcher")
    checks_passed += check_file_exists("satellite-detection-project/src/api/main.py", "API main")
    print()
    
    # Key directories
    print("Key Directories:")
    total_checks += 4
    checks_passed += check_directory_exists("satellite-detection-project/src", "Source code")
    checks_passed += check_directory_exists("satellite-detection-project/data", "Data directory")
    checks_passed += check_directory_exists("satellite-detection-project/static", "Static files")
    checks_passed += check_directory_exists("satellite-detection-project/logs", "Logs directory")
    print()
    
    # Additional checks
    print("Security Checks:")
    total_checks += 2
    checks_passed += check_gitignore()
    checks_passed += check_sensitive_files()
    print()
    
    # Summary
    print("="*80)
    print(f"Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("PROJECT IS READY FOR GITHUB!")
        print("\nNext steps:")
        print("1. Review all files to ensure no sensitive data")
        print("2. git init (if not already initialized)")
        print("3. git add .")
        print("4. git commit -m 'Initial commit'")
        print("5. git remote add origin <your-repo-url>")
        print("6. git push -u origin main")
    elif checks_passed >= total_checks * 0.8:
        print("[WARN] PROJECT IS MOSTLY READY")
        print("Fix the issues above before pushing to GitHub")
        return 1
    else:
        print("[FAILED] PROJECT NEEDS MORE WORK")
        print("Please address the missing items above")
        return 1
    
    print("="*80 + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
