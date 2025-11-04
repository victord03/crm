# VK CRM

A lightweight desktop CRM tool built with Tkinter for managing client contacts and case tracking. Features include wildcard search, duplicate detection, and CSV-based persistence.

## Features

- **Case Management**: Track client interactions with unique case IDs
- **Contact Tracking**: Store phone numbers and emails with automatic duplicate counting
- **Wildcard Search**: Find cases using patterns (e.g., `*@gmail.com`, `69*`)
- **Duplicate Detection**: Automatically counts how many times an email/phone appears across all cases
- **Multi-Frame Navigation**: Clean UI with separate screens for viewing, adding, and searching
- **CSV Persistence**: Simple file-based storage with `cases.csv`

## Screenshots

### Main View
The application provides a clean interface for browsing and managing customer cases with automatic duplicate counting for emails and phone numbers.

## Installation

```bash
# Clone the repository
git clone https://github.com/victord03/crm.git
cd crm

# No external dependencies required (uses Python stdlib: tkinter, csv)
python3 src/main.py
```

## Usage

### Adding a Case
1. Click "Add New Case"
2. Fill in contact details (phone, email)
3. Add reactions and responses
4. System automatically generates UUID-based case ID
5. Duplicate counts updated automatically

### Searching Cases
- Use wildcards: `*pattern*`, `pattern*`, `*pattern`
- Example: `*@company.com` finds all emails from that domain
- Example: `69*` finds all mobile numbers starting with 69

### Viewing Cases
Browse all cases with email/phone occurrence counts to identify repeat contacts.

## Project Structure

```
crm/
├── src/
│   ├── main.py              # Main application (Tkinter UI + logic)
│   └── main_using_flask.py  # Alternative Flask implementation
├── cases.csv                # Database (auto-created)
└── README.md
```

## Tech Stack

- **Language**: Python 3.x
- **GUI**: Tkinter / CustomTKinter
- **Storage**: CSV (no external database required)
- **ID Generation**: UUID for unique case identifiers

## Features In Detail

### Duplicate Counter
Each case shows how many times the email and phone number appear across **all** cases. This helps identify:
- Repeat customers
- Multiple cases for the same contact
- Potential duplicate entries

### Input Validation
- Max 100 characters per field
- Prevents data overflow
- Clean error handling

### State Management
- Frame-based navigation (Main → Add → Search → back to Main)
- Proper state cleanup between screens
- UUID-based case identification

## CSV Schema

```csv
case_id, timestamp, phone_number, email, main_reaction, main_response, email_count, phone_count, comments
```

## Known Limitations

- No authentication (single-user desktop app)
- CSV can become slow with 10,000+ records
- No data encryption
- Destructive operations (delete) have no undo

## Future Enhancements

- Add confirmation dialogs for deletions
- Implement data backup/export
- Add basic authentication for multi-user scenarios
- Migrate to SQLite for better performance

## Status

**Production-Ready** - Fully functional CRM for personal/small business use. Used successfully for client interaction tracking.

## License

MIT License
