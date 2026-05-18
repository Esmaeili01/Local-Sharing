```markdown
# Local File & Text Sharing

A simple web application for sharing files and text snippets across devices on your local network. No internet required - just a local network.

## Features

- 📝 Share text snippets with automatic expiration
- 📎 Share files (up to 500MB)
- ⏰ Configurable expiration times (5 minutes to 7 days)
- 👁️ View text content in an inline drawer (no page reload)
- 📋 One-click copy to clipboard
- 🌐 Auto-detects and displays network IP for easy access
- 📱 Mobile responsive design
- 🔄 Real-time countdown timers
- 🗑️ Automatic cleanup of expired items

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Esmaeili01/Local-Sharing.git
cd Local-Sharing
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

For other devices on the same network, use the network IP shown in the header.

## Usage

### Sharing Text
1. Click the "Share Text" tab
2. Enter a title (optional) and your content
3. Choose expiration time
4. Click "Share Text"

### Sharing Files
1. Click the "Share File" tab
2. Select a file
3. Choose expiration time
4. Click "Upload & Share"

### Accessing Shared Content
- **Text:** Click the 👁️ View button to open a drawer with the content
- **Files:** Click the ⬇️ Download button to download the file
- **Copy:** Use the 📋 Copy button to copy text to clipboard

## Configuration

Edit `config.py` to modify:
- Upload folder location
- Maximum file size (default: 500MB)
- Expiration time options
- Cleanup interval

## Project Structure

```
local-file-sharing/
├── app.py              # Main application
├── models.py           # Database models
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── static/            # CSS and JavaScript files
│   ├── css/
│   └── js/
├── templates/         # HTML templates
├── uploads/           # Uploaded files (auto-created)
└── database/          # SQLite database (auto-created)
```

## Running on Different Ports

Default port is 5000. To use port 80 (no port number in URL):

```bash
# Windows (Run as Administrator)
python app.py --port=80

# Linux/Mac (with sudo)
sudo python app.py --port=80
```

## Technologies Used

- **Backend:** Flask, SQLAlchemy
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite