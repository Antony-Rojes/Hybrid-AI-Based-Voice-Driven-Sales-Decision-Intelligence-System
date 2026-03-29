def send_report_to_manager(report: dict) -> bool:
    """Placeholder: Send AI report to manager via email/WhatsApp."""
    print(f"[AutomationService] Report escalated: {report.get('risk_level', 'Unknown')} risk")
    return True

def log_meeting_to_crm(meeting_data: dict) -> bool:
    """Placeholder: Log meeting data to CRM system."""
    print(f"[AutomationService] Meeting logged to CRM.")
    return True