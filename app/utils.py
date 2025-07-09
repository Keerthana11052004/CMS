import qrcode
import json
import base64
from io import BytesIO
from datetime import datetime

def generate_meal_qr_code(employee_name, employee_id, unit_name, date, shift):
    """
    Generate a QR code with meal booking details (values only, comma-separated)
    Args:
        employee_name (str): Name of the employee
        employee_id (str): Employee ID
        unit_name (str): Unit/Location name
        date (str): Booking date
        shift (str): Meal shift (Breakfast/Lunch/Dinner)
    Returns:
        tuple: (qr_code_image_base64, qr_code_data_string)
    """
    # Create value-only string for QR code
    qr_data_string = f"{employee_name},{employee_id},{unit_name},{date},{shift}"
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data_string)
    qr.make(fit=True)
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    # Convert to base64 for storage/display
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    return qr_image_base64, qr_data_string

def decode_qr_code(qr_data_json):
    """
    Decode QR code data back to dictionary
    
    Args:
        qr_data_json (str): JSON string from QR code
    
    Returns:
        dict: Decoded QR code data
    """
    try:
        return json.loads(qr_data_json)
    except json.JSONDecodeError:
        return None 