#!/usr/bin/env python3
"""
Yacht Contract Generator V3 - Automated Setup Script
This script handles the complete setup and deployment of the application.
"""

import os
import sys
import subprocess
import json
import webbrowser
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(message, color=Colors.OKGREEN):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    """Print header message"""
    print_colored(f"\n{'='*60}", Colors.HEADER)
    print_colored(f"🛥️  {message}", Colors.HEADER)
    print_colored(f"{'='*60}", Colors.HEADER)

def run_command(command, description=""):
    """Run shell command with error handling"""
    try:
        print_colored(f"⚡ {description}...", Colors.OKBLUE)
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print_colored(f"✅ {description} completed successfully", Colors.OKGREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Error: {e}", Colors.FAIL)
        print_colored(f"Command output: {e.output}", Colors.WARNING)
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro} detected - Compatible!", Colors.OKGREEN)
        return True
    else:
        print_colored(f"❌ Python {version.major}.{version.minor}.{version.micro} detected - Requires Python 3.8+", Colors.FAIL)
        return False

def create_virtual_environment():
    """Create and activate virtual environment"""
    print_header("Setting Up Virtual Environment")
    
    venv_path = Path("yacht_env")
    
    if venv_path.exists():
        print_colored("⚠️  Virtual environment already exists", Colors.WARNING)
        return True
    
    # Create virtual environment
    if run_command("python -m venv yacht_env", "Creating virtual environment"):
        print_colored("📁 Virtual environment created: yacht_env/", Colors.OKGREEN)
        return True
    return False

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = "yacht_env\\Scripts\\activate"
        pip_command = "yacht_env\\Scripts\\pip"
    else:  # Unix-like
        activate_script = "source yacht_env/bin/activate"
        pip_command = "yacht_env/bin/pip"
    
    dependencies = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "plotly>=5.15.0", 
        "jinja2>=3.1.0",
        "reportlab>=4.0.0",
        "google-api-python-client>=2.100.0",
        "google-auth-httplib2>=0.1.0",
        "google-auth-oauthlib>=1.0.0",
        "python-dateutil>=2.8.0",
        "Pillow>=10.0.0"
    ]
    
    print_colored(f"📦 Installing {len(dependencies)} packages...", Colors.OKBLUE)
    
    for package in dependencies:
        package_name = package.split(">=")[0]
        if run_command(f"{pip_command} install {package}", f"Installing {package_name}"):
            print_colored(f"  ✅ {package_name} installed", Colors.OKGREEN)
        else:
            print_colored(f"  ❌ Failed to install {package_name}", Colors.FAIL)
            return False
    
    return True

def create_project_structure():
    """Create necessary project directories and files"""
    print_header("Creating Project Structure")
    
    directories = [
        "static",
        "templates", 
        "logs",
        "exports"
    ]
    
    files = [
        "contract_audit_log.txt",
        ".env",
        ".gitignore"
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_colored(f"📁 Created directory: {directory}/", Colors.OKGREEN)
    
    # Create files
    for file in files:
        if not os.path.exists(file):
            Path(file).touch()
            print_colored(f"📄 Created file: {file}", Colors.OKGREEN)
    
    # Create .gitignore content
    gitignore_content = """
# Credentials and tokens
credentials.json
token.json
.env

# Virtual environment
yacht_env/
venv/
env/

# Logs
*.log
logs/

# Python cache
__pycache__/
*.pyc
*.pyo

# Temporary files
*.tmp
*.temp

# OS files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Streamlit
.streamlit/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content.strip())
    
    print_colored("✅ Project structure created successfully", Colors.OKGREEN)
    return True

def setup_google_drive():
    """Guide user through Google Drive setup"""
    print_header("Google Drive Integration Setup")
    
    print_colored("🔧 Google Drive setup requires manual configuration:", Colors.WARNING)
    print_colored("1. Go to Google Cloud Console: https://console.cloud.google.com/", Colors.OKBLUE)
    print_colored("2. Create a new project or select existing", Colors.OKBLUE)
    print_colored("3. Enable Google Drive API", Colors.OKBLUE)
    print_colored("4. Create OAuth 2.0 credentials (Desktop Application)", Colors.OKBLUE)
    print_colored("5. Download credentials.json file", Colors.OKBLUE)
    print_colored("6. Place credentials.json in this directory", Colors.OKBLUE)
    
    # Open browser to Google Cloud Console
    try:
        webbrowser.open("https://console.cloud.google.com/")
        print_colored("🌐 Opened Google Cloud Console in browser", Colors.OKGREEN)
    except:
        print_colored("⚠️  Could not open browser automatically", Colors.WARNING)
    
    # Check if credentials file exists
    if os.path.exists("credentials.json"):
        print_colored("✅ credentials.json found!", Colors.OKGREEN)
        return True
    else:
        print_colored("⚠️  credentials.json not found - Google Drive features will be disabled", Colors.WARNING)
        print_colored("   You can add this file later to enable Google Drive integration", Colors.OKBLUE)
        return False

def create_sample_config():
    """Create sample configuration files"""
    print_header("Creating Configuration Files")
    
    # Sample environment file
    env_content = """
# Yacht Contract Generator Configuration
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
DEBUG=False
"""
    
    with open(".env.sample", "w") as f:
        f.write(env_content.strip())
    
    print_colored("📄 Created .env.sample - Copy to .env and configure", Colors.OKGREEN)
    
    # Sample configuration JSON
    config_data = {
        "app_name": "Yacht Contract Generator V3",
        "version": "3.0.0",
        "yacht_types": {
            "Superyacht (60m+)": {
                "base_rate": 75000,
                "crew_size": 22,
                "guest_capacity": 16,
                "fuel_capacity": 45000
            },
            "Luxury Yacht (30-60m)": {
                "base_rate": 35000,
                "crew_size": 12,
                "guest_capacity": 12,
                "fuel_capacity": 20000
            }
        },
        "email_config": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587
        }
    }
    
    with open("config.json", "w") as f:
        json.dump(config_data, f, indent=2)
    
    print_colored("📄 Created config.json", Colors.OKGREEN)
    return True

def run_tests():
    """Run basic application tests"""
    print_header("Running Basic Tests")
    
    # Determine the correct Python executable path for virtual environment
    if os.name == 'nt':  # Windows
        python_exe = "yacht_env\\Scripts\\python.exe"
    else:  # Unix-like
        python_exe = "yacht_env/bin/python"
    
    test_commands = [
        (f"{python_exe} -c \"import streamlit; print(f'Streamlit {{streamlit.__version__}} imported successfully')\"", "Testing Streamlit import"),
        (f"{python_exe} -c \"import pandas; print(f'Pandas {{pandas.__version__}} imported successfully')\"", "Testing Pandas import"),
        (f"{python_exe} -c \"import jinja2; print(f'Jinja2 {{jinja2.__version__}} imported successfully')\"", "Testing Jinja2 import"),
        (f"{python_exe} -c \"import reportlab; print('ReportLab imported successfully')\"", "Testing ReportLab import")
    ]
    
    all_passed = True
    for command, description in test_commands:
        if not run_command(command, description):
            all_passed = False
    
    if all_passed:
        print_colored("✅ All tests passed!", Colors.OKGREEN)
    else:
        print_colored("❌ Some tests failed - check dependencies", Colors.FAIL)
    
    return all_passed

def create_run_script():
    """Create convenient run scripts"""
    print_header("Creating Run Scripts")
    
    # Windows batch file
    batch_content = """@echo off
echo Starting Yacht Contract Generator V3...
call yacht_env\\Scripts\\activate
streamlit run enhanced_yacht_generator_v3_fixed.py
pause
"""
    
    with open("run_app.bat", "w") as f:
        f.write(batch_content)
    
    # Unix shell script
    shell_content = """#!/bin/bash
echo "Starting Yacht Contract Generator V3..."
source yacht_env/bin/activate
streamlit run enhanced_yacht_generator_v3_fixed.py
"""
    
    with open("run_app.sh", "w") as f:
        f.write(shell_content)
    
    # Make shell script executable on Unix
    if os.name != 'nt':
        os.chmod("run_app.sh", 0o755)
    
    print_colored("📄 Created run_app.bat (Windows)", Colors.OKGREEN)
    print_colored("📄 Created run_app.sh (Unix/Mac)", Colors.OKGREEN)
    return True

def display_final_instructions():
    """Display final setup instructions"""
    print_header("Setup Complete! 🎉")
    
    print_colored("Your Yacht Contract Generator V3 is ready to use!", Colors.OKGREEN)
    print_colored("\n📋 Next Steps:", Colors.OKBLUE)
    print_colored("1. Activate virtual environment:", Colors.OKBLUE)
    if os.name == 'nt':
        print_colored("   yacht_env\\Scripts\\activate", Colors.OKCYAN)
    else:
        print_colored("   source yacht_env/bin/activate", Colors.OKCYAN)
    
    print_colored("2. Run the application:", Colors.OKBLUE)
    print_colored("   streamlit run enhanced_yacht_generator_v3_fixed.py", Colors.OKCYAN)
    print_colored("   OR double-click run_app.bat (Windows) / run_app.sh (Unix)", Colors.OKCYAN)
    
    print_colored("\n🔧 Optional Configuration:", Colors.OKBLUE)
    print_colored("• Add credentials.json for Google Drive integration", Colors.OKBLUE)
    print_colored("• Configure .env file with your settings", Colors.OKBLUE)
    print_colored("• Customize yacht types in config.json", Colors.OKBLUE)
    
    print_colored("\n📱 Application Features:", Colors.OKGREEN)
    print_colored("✅ Professional contract generation", Colors.OKGREEN)
    print_colored("✅ Multiple yacht types support", Colors.OKGREEN)
    print_colored("✅ PDF export with proper formatting", Colors.OKGREEN)
    print_colored("✅ Email integration", Colors.OKGREEN)
    print_colored("✅ Google Drive cloud storage", Colors.OKGREEN)
    print_colored("✅ Analytics and audit logging", Colors.OKGREEN)
    print_colored("✅ Searchable contract database", Colors.OKGREEN)
    
    print_colored("\n🌐 Default URL: http://localhost:8501", Colors.HEADER)
    print_colored("\n📖 For help, see README.md or Documentation.ipynb", Colors.OKBLUE)

def main():
    """Main setup function"""
    print_colored("🛥️ Welcome to Yacht Contract Generator V3 Setup!", Colors.HEADER)
    print_colored("This script will set up everything you need to run the application.\n", Colors.OKBLUE)
    
    setup_steps = [
        ("Checking Python compatibility", check_python_version),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating project structure", create_project_structure),
        ("Setting up Google Drive", setup_google_drive),
        ("Creating configuration files", create_sample_config),
        ("Running tests", run_tests),
        ("Creating run scripts", create_run_script)
    ]
    
    failed_steps = []
    
    for step_name, step_function in setup_steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print_colored(f"❌ Error in {step_name}: {e}", Colors.FAIL)
            failed_steps.append(step_name)
    
    if failed_steps:
        print_header("Setup Issues Detected")
        print_colored("⚠️  The following steps had issues:", Colors.WARNING)
        for step in failed_steps:
            print_colored(f"  • {step}", Colors.WARNING)
        print_colored("\nYou may need to resolve these manually before running the app.", Colors.WARNING)
    
    display_final_instructions()
    
    # Ask if user wants to run the app now
    print_colored("\n🚀 Would you like to run the application now? (y/n): ", Colors.OKBLUE)
    try:
        response = input().lower().strip()
        if response in ['y', 'yes']:
            print_colored("Starting application...", Colors.OKGREEN)
            if os.name == 'nt':
                os.system("yacht_env\\Scripts\\activate && streamlit run enhanced_yacht_generator_v3_fixed.py")
            else:
                os.system("source yacht_env/bin/activate && streamlit run enhanced_yacht_generator_v3_fixed.py")
    except KeyboardInterrupt:
        print_colored("\n👋 Setup complete. Run the app manually when ready!", Colors.OKGREEN)

if __name__ == "__main__":
    main()