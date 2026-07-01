COMPLIANCE_FRAMEWORKS = {
    "None": {
        "name": "No Compliance Framework",
        "controls": {}
    },
    "PCI-DSS": {
        "name": "Payment Card Industry Data Security Standard",
        "controls": {
            "authentication": {
                "id": "PCI-DSS 8.2",
                "title": "Strong Authentication",
                "description": "Verify user identity before granting access"
            },
            "session": {
                "id": "PCI-DSS 8.1.8",
                "title": "Session Timeout",
                "description": "Sessions idle 15+ minutes require re-authentication"
            },
            "lockout": {
                "id": "PCI-DSS 8.1.6",
                "title": "Account Lockout",
                "description": "Lock account after 6 failed login attempts"
            },
            "invalid_login": {
                "id": "PCI-DSS 8.2.1",
                "title": "Credential Protection",
                "description": "Invalid credentials must not reveal which field was incorrect"
            }
        }
    },
    "HIPAA": {
        "name": "Health Insurance Portability and Accountability Act",
        "controls": {
            "authentication": {
                "id": "HIPAA 164.312(d)",
                "title": "Person or Entity Authentication",
                "description": "Verify person seeking access to ePHI is who they claim"
            },
            "session": {
                "id": "HIPAA 164.312(a)(2)(iii)",
                "title": "Automatic Logoff",
                "description": "Terminate session after predetermined inactivity period"
            },
            "access_control": {
                "id": "HIPAA 164.312(a)(1)",
                "title": "Access Control",
                "description": "Allow access only to persons granted access rights"
            },
            "audit": {
                "id": "HIPAA 164.312(b)",
                "title": "Audit Controls",
                "description": "Record and examine activity in systems containing ePHI"
            }
        }
    },
    "SR 11-7": {
        "name": "Federal Reserve Model Risk Management Guidance",
        "controls": {
            "authentication": {
                "id": "SR 11-7 IV",
                "title": "Model Access Controls",
                "description": "Controls to ensure only authorized users access the model"
            },
            "input_validation": {
                "id": "SR 11-7 V",
                "title": "Input Data Validation",
                "description": "Verify data quality and integrity of model inputs"
            },
            "invalid_login": {
                "id": "SR 11-7 VI",
                "title": "Boundary Testing",
                "description": "Test model behavior at and beyond input boundaries"
            },
            "audit": {
                "id": "SR 11-7 VII",
                "title": "Audit Trail",
                "description": "Maintain records of model access and changes"
            }
        }
    },
    "SOX": {
        "name": "Sarbanes-Oxley Act",
        "controls": {
            "authentication": {
                "id": "SOX 404",
                "title": "Access Controls",
                "description": "Internal controls over financial system access"
            },
            "audit": {
                "id": "SOX 302",
                "title": "Audit Trail",
                "description": "Track all changes to financial data with attribution"
            },
            "access_control": {
                "id": "SOX 404.2",
                "title": "Segregation of Duties",
                "description": "No single user has conflicting access rights"
            }
        }
    }
}


def get_framework(framework_name: str) -> dict:
    return COMPLIANCE_FRAMEWORKS.get(
        framework_name,
        COMPLIANCE_FRAMEWORKS["None"]
    )


def get_control_for_test(
    framework_name: str,
    test_category: str
) -> dict:
    framework = get_framework(framework_name)
    return framework.get("controls", {}).get(test_category)


def list_frameworks() -> list:
    return list(COMPLIANCE_FRAMEWORKS.keys())
