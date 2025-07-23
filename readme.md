# 🛥️ Yacht Contract Generator V3

## Overview
A professional maritime charter contract generation platform built with Streamlit. This application generates legally-compliant yacht charter contracts with PDF export, Google Drive integration, email capabilities, and comprehensive analytics.

## Features
- ✅ Multiple yacht types (Superyacht, Luxury, Motor, Sport)
- ✅ Professional PDF generation with proper formatting
- ✅ Google Drive cloud storage integration
- ✅ Email contracts with attachments
- ✅ Real-time analytics and audit logging
- ✅ Customizable annexes and contract clauses
- ✅ Searchable contract database
- ✅ Export capabilities (PDF, HTML, CSV logs)

## 🚀 Quick Start

### Prerequisites
- Windows 10/11 (as per your environment)
- Python 3.8+ installed
- VSCode (recommended)
- Google Account (for Drive integration)

### Installation Steps

1. **Download and Extract**
   ```bash
   # Extract the provided ZIP file to your desired location
   # Example: C:\YachtContracts\
   ```

2. **Open in VSCode**
   ```bash
   # Open VSCode
   # File > Open Folder > Select your extracted folder
   ```

3. **Create Virtual Environment**
   ```bash
   # Open VSCode Terminal (Terminal > New Terminal)
   python -m venv yacht_env
   yacht_env\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Google Drive Setup (Optional but Recommended)**
   
   **Step A: Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Google Drive API
   - Go to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID (Desktop Application)
   - Download credentials.json file
   
   **Step B: Place Credentials**
   - Save `credentials.json` in your app folder
   - Create a Google Drive folder for contracts
   - Get the folder ID from the URL (the long string after `/folders/`)
   - Edit line 42 in `yacht_contract_generator.py`:
     ```python
     GOOGLE_DRIVE_FOLDER_ID = "your_actual_folder_id_here"
     ```

6. **Run the Application**
   ```bash
   streamlit run yacht_contract_generator.py
   ```

## 📱 Usage Guide

### Creating Your First Contract

1. **Select Yacht Type**: Choose from 4 predefined yacht categories
2. **Fill Contract Details**: Complete all required fields
3. **Configure Parties**: Enter Lessor and Lessee information
4. **Set Financial Terms**: Define rates, deposits, and payment schedules
5. **Choose Annexes**: Select which additional clauses to include
6. **Generate**: Click "Generate Contract" to create PDF

### Google Drive Integration

- First run will prompt for Google authentication
- Contracts automatically save to specified folder
- View saved contracts in "Saved Contracts" page
- Real-time file synchronization

### Email Functionality

- Built-in SMTP support (Gmail recommended)
- Use App Passwords for Gmail accounts
- Automatic PDF attachment
- Customizable email templates

## 🔧 Configuration

### Email Setup (Gmail Example)
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: Account Settings > Security > App Passwords
3. Use App Password (not regular password) in the application

### Custom Yacht Types
Edit the `YACHT_TEMPLATES` dictionary in the main file to add new yacht categories:

```python
YACHT_TEMPLATES = {
    "Custom Yacht Type": {
        "base_rate": 50000,
        "crew_size": 15,
        "guest_capacity": 10,
        "fuel_capacity": 25000,
        "description": "Your custom description"
    }
}
```

## 📊 Analytics Features

- **Contract Generation Trends**: Daily/weekly charts
- **Activity Distribution**: Pie charts of actions
- **Audit Logging**: Complete action history
- **Export Capabilities**: CSV export of logs
- **Search Functionality**: Filter and search logs

## 🔒 Security Considerations

- OAuth 2.0 for Google Drive authentication
- Local credential storage only
- No sensitive data transmitted to external servers
- Audit trail for all actions

## 🚨 Troubleshooting

### Common Issues

1. **Google Drive Auth Error**
   ```
   Solution: Delete token.json and re-authenticate
   ```

2. **PDF Generation Error**
   ```
   Solution: Check reportlab installation: pip install --upgrade reportlab
   ```

3. **Email Sending Fails**
   ```
   Solution: Use App Password for Gmail, check SMTP settings
   ```

4. **Module Import Error**
   ```
   Solution: Ensure virtual environment is activated
   pip install -r requirements.txt
   ```

## 📁 File Structure
```
yacht_contract_generator/
├── yacht_contract_generator.py    # Main application
├── requirements.txt               # Dependencies
├── README.md                     # This file
├── credentials.json              # Google OAuth (you create)
├── token.json                    # Auto-generated auth token
└── contract_audit_log.txt        # Auto-generated audit log
```

## 🔄 Future Canvas App Integration

This application is designed for future integration into Dynamics 365 as a Canvas App:

### Integration Strategy
1. **API Wrapper**: Convert Streamlit functions to REST API endpoints
2. **Power Platform Connectors**: Use custom connectors for API integration
3. **Data Flow**: Dynamics 365 → Canvas App → Python API → Google Drive
4. **Authentication**: Integrate with Azure AD for single sign-on

### Canvas App Architecture (Future)
```
Dynamics 365 Account → Canvas App → Python Backend → Contract Generation
                   ↓
                Power Automate → Email/Storage
```

## 🤝 Portability for Other Users

### Sharing with Other Offices

**Option 1: Complete Package (Recommended)**
1. Create ZIP with all files including requirements.txt
2. Include setup instructions (this README)
3. Provide Google Cloud project sharing access
4. Each user creates their own credentials.json

**Option 2: Docker Deployment**
```dockerfile
# Future Docker implementation for consistent deployment
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "yacht_contract_generator.py"]
```

**Option 3: Cloud Deployment**
- Deploy to Streamlit Cloud (streamlit.io)
- Deploy to Azure Container Instances
- Deploy to AWS ECS/Fargate

### Environment Variables (Production)
```bash
# For production deployment
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 📞 Support

For technical support or feature requests:
1. Check troubleshooting section above
2. Verify all dependencies are installed
3. Ensure Google Drive credentials are properly configured
4. Check audit logs for error patterns

## 📄 Legal Notice

This software generates contract templates for informational purposes. Always consult with maritime law professionals before using contracts in commercial transactions. The generated contracts should be reviewed and customized according to local regulations and specific business requirements.

---

**Version**: 3.0  
**Last Updated**: December 2024  
**Compatible with**: Windows 10/11, Python 3.8+, Streamlit 1.28+