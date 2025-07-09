# Canteen Management System - QR Code Integration

## Overview
This update adds automatic QR code generation for meal bookings. When employees book meals, the system now:
- Automatically sets the status to "Booked" (instead of "Pending")
- Generates a unique QR code containing employee details
- Stores the QR code data in the database
- Provides QR code viewing and downloading in the booking history

## Features Added

### 1. Automatic Booking Status
- Meals are automatically set to "Booked" status upon booking
- No pending state - immediate confirmation and QR code generation

### 2. QR Code Generation
- Unique QR codes generated for each booking
- Contains employee details: Name, Employee ID, Unit, Date, Shift
- QR codes are stored as base64 images in the database

### 3. Enhanced Booking History
- View all bookings with status indicators
- Click to view QR codes in modal popups
- Download QR codes as PNG images
- Real-time status updates

### 4. Staff QR Scanner
- Modern QR code scanner with camera support
- Manual QR code entry option
- Real-time validation and consumption tracking
- Success/error feedback with detailed information

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Database Schema
Run the update script to modify your existing database:
```bash
mysql -u root -p < update_schema.sql
```

### 3. Database Changes
The following changes are made to the database:
- Removed 'Pending' status from bookings table
- Added `qr_code_data` column to store QR code images
- Updated default status to 'Booked'
- Added performance indexes

## Usage

### For Employees
1. Login to employee portal
2. Book a meal (automatically gets "Booked" status)
3. View booking history to see QR codes
4. Click "View QR" to see/download QR code

### For Staff
1. Login to staff portal
2. Access QR Scanner
3. Use camera to scan QR codes or manually enter data
4. System validates and marks meals as consumed

## QR Code Format
The QR codes contain JSON data with:
```json
{
  "employee_name": "John Doe",
  "employee_id": "EMP001",
  "unit": "Unit 1",
  "date": "2024-06-20",
  "shift": "Lunch",
  "generated_at": "2024-06-20T10:30:00"
}
```

## Technical Details

### Files Modified
- `app/employee.py` - Updated booking logic and history
- `app/staff.py` - Added QR scanning functionality
- `app/utils.py` - New QR code generation utilities
- `app/templates/employee/history.html` - Enhanced booking history view
- `app/templates/staff/qr_scanner.html` - Modern QR scanner interface

### New Dependencies
- `qrcode[pil]==7.4.2` - QR code generation
- `Pillow==10.0.1` - Image processing

## Security Features
- QR codes contain only necessary employee information
- Staff validation required for meal consumption
- Audit trail maintained in meal_consumption_log table
- Secure QR code validation and processing

## Troubleshooting

### Common Issues
1. **QR codes not displaying**: Check if qrcode library is installed
2. **Scanner not working**: Ensure HTTPS or localhost for camera access
3. **Database errors**: Run the update_schema.sql script

### Support
For issues or questions, check the database logs and application error logs. 