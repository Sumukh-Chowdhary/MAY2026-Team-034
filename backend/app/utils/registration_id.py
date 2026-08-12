import re

# Branch Code Mapping Table
BRANCH_CODE_MAP = {
    'COMPUTER SCIENCE': 'CS',
    'COMPUTER SCIENCE & ENGINEERING': 'CS',
    'CSE': 'CS',
    'CS': 'CS',
    'ELECTRONICS & COMMUNICATION ENGINEERING': 'EC',
    'ELECTRONICS': 'EC',
    'ECE': 'EC',
    'EC': 'EC',
    'MECHANICAL ENGINEERING': 'ME',
    'MECHANICAL': 'ME',
    'MECH': 'ME',
    'ME': 'ME',
    'ELECTRICAL & ELECTRONICS ENGINEERING': 'EE',
    'ELECTRICAL': 'EE',
    'EEE': 'EE',
    'EE': 'EE',
    'CIVIL ENGINEERING': 'CE',
    'CIVIL': 'CE',
    'CIV': 'CE',
    'CE': 'CE',
    'INFORMATION TECHNOLOGY': 'IT',
    'IT': 'IT',
    'ARTIFICIAL INTELLIGENCE & MACHINE LEARNING': 'AI',
    'ARTIFICIAL INTELLIGENCE': 'AI',
    'AIML': 'AI',
    'AI': 'AI',
    'DATA SCIENCE': 'DS',
    'DS': 'DS',
    'BUSINESS & MANAGEMENT': 'BS',
    'BUSINESS ADMINISTRATION': 'BS',
    'BUSINESS': 'BS',
    'MBA': 'BS',
    'BS': 'BS',
    'BIOTECHNOLOGY': 'BT',
    'BT': 'BT',
    'MATHEMATICS': 'MA',
    'MA': 'MA',
    'PHYSICS': 'PH',
    'PH': 'PH',
    'CHEMISTRY': 'CH',
    'CH': 'CH'
}

def get_branch_code(department_name_or_code):
    """Normalize department name/code into an exactly 2-letter uppercase branch code."""
    if not department_name_or_code:
        return 'CS'
    
    clean_str = str(department_name_or_code).strip().upper()
    if clean_str in BRANCH_CODE_MAP:
        return BRANCH_CODE_MAP[clean_str]
    
    # Extract uppercase alpha characters
    alpha_only = re.sub(r'[^A-Z]', '', clean_str)
    if len(alpha_only) >= 2:
        return alpha_only[:2]
    elif len(alpha_only) == 1:
        return (alpha_only + 'X')[:2]
    
    return 'CS'

def format_batch_year(batch_year):
    """Format batch year into 2-digit string (e.g., 2026 -> '26', 26 -> '26')."""
    try:
        yr = int(batch_year)
        if yr > 100:
            yr = yr % 100
        return f"{yr:02d}"
    except (ValueError, TypeError):
        return '26'

def format_roll_number(roll_number):
    """Format roll number integer or string into 3-digit padded string (e.g. 1 -> '001')."""
    try:
        # If roll_number string already contains letters (like Y26CS001), extract trailing digits
        num_str = str(roll_number)
        digits = re.findall(r'\d+', num_str)
        if digits:
            val = int(digits[-1])
            return f"{val:03d}"
        return '001'
    except (ValueError, TypeError):
        return '001'

def generate_registration_id(batch_year, branch_code_or_dept, roll_number):
    """
    Generates a standardized Student Registration ID string.
    Format: Y + 2-digit batch year + 2-letter branch code + 3-digit padded roll number
    Example: Y26CS001, Y26EC014, Y25ME007
    """
    yr_2d = format_batch_year(batch_year)
    br_2l = get_branch_code(branch_code_or_dept)
    roll_3d = format_roll_number(roll_number)
    return f"Y{yr_2d}{br_2l}{roll_3d}"

REGISTRATION_ID_PATTERN = re.compile(r'^Y\d{2}[A-Z]{2}\d{3,}$')

def validate_registration_id(reg_id):
    """Validate if registration ID conforms to Y + 2-digit year + 2-letter branch + digits."""
    if not reg_id or not isinstance(reg_id, str):
        return False
    return bool(REGISTRATION_ID_PATTERN.match(reg_id.strip().upper()))

def parse_registration_id(reg_id):
    """
    Parses a valid registration ID into components:
    Returns dict: {'prefix': 'Y', 'batchYear': '26', 'branchCode': 'CS', 'rollNumber': '001'} or None.
    """
    if not reg_id or not isinstance(reg_id, str):
        return None
    
    clean_id = reg_id.strip().upper()
    match = re.match(r'^Y(\d{2})([A-Z]{2})(\d{3,})$', clean_id)
    if not match:
        return None
    
    return {
        'prefix': 'Y',
        'batchYear': match.group(1),
        'branchCode': match.group(2),
        'rollNumber': match.group(3)
    }
