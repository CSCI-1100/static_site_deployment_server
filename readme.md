# Static Site Deployment Server

<div align="center">
  <p><em>A Django-based web server designed for students to deploy static websites on a local network.</em>This provides a simple, educational deployment experience without the complexities of production hosting.</p>

  <img src="./media/dashboard.png" alt="Static Site Deployment Server dashboard" width="700"/>
</div>

In CSCI 1100, our Web Literacy module exposes students to HTML, CSS and Web accessibility, while our Digital Content Creation module explores design considerations. Toward the end of class we explore AI, and in our CLEAR prompting lab, we practice using the [CLEAR framework](https://csci-1100.github.io/class_resources_public/ai_and_machine_learning/clear_ai_prompting_tips.html) to refine our prompts and critically assess the outputs. In wanting to push students beyond just generating text and bring together several of the literacies and skills we cover, I developed this web project (with AI!) to use in my CLEAR prompting lab. I want students to explore the power of AI-assisted web development by having them start their own portfolio sites (something we discuss in class). This project aims at giving them a way to instantly deploy and view their websites without the overhead of having to know how to use FileZilla!

## Features

- **Student-friendly interface**: Drag-and-drop file uploads matching your wireframe design
- **Organized file structure**: Automatic organization into `css/`, `js/`, `img/` folders
- **User management**: Admin panel for CRUD operations and bulk CSV user import
- **Local network access**: Accessible via `https://<hostname>:5000`
- **File export**: Students can download ZIP files of their websites
- **Live website viewing**: Each student gets their own URL: `https://<hostname>:5000/username`

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   ./setup.sh
   ```

2. **Start the server**:
   ```bash
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:5000
   ```

3. **Access the application**:
   - Admin panel: `https://<hostname>:5000/admin/`
   - Student login: `https://<hostname>:5000/`

## File Structure

The server organizes student files in this structure:
```
media/
  username/
    index.html
    about.html
    contact.html
    css/
      style.css
      forms.css
    img/
      profile-photo.png
      logo.svg
    js/
      main.js
      contact-form.js
```

## Admin Tasks

### Creating Individual Users

1. Go to the admin panel: `https://<hostname>:5000/admin/`
2. Click "Users" → "Add user"
3. Fill in username, password, email, first name, last name
4. Save - a UserProfile will be created automatically

### Bulk User Import

1. In the admin panel, go to "Users"
2. Click "Bulk Upload" button
3. Upload a CSV file with format:
   ```csv
   First Name,Last Name,Email,Password
   Ryan,Haas,haasrr@etsu.edu,E00123456
   Chelsie,Dubay,dubayc@etsu.edu,E00789101
   ```

### Managing Files

- View all uploaded files in the admin under "Uploaded files"
- Files are automatically deleted when users are deleted (CASCADE)
- File types are automatically categorized (HTML, CSS, JS, Image, Asset)

## Student Experience

### Logging In
Students use their username/password to access the dashboard.

### File Upload
- Drag and drop or click to upload files
- Files are automatically organized by type
- Real-time feedback with progress bars
- File size and count displayed

### Viewing Website
- Click "View Website" to see their deployed site
- URL format: `https://<hostname>:5000/<username>`
- If no index.html exists, shows a helpful message

### Exporting Files
- "Export ZIP" button downloads all their files
- Maintains folder structure for easy backup

## Technical Details

### Requirements
- Python 3.8+
- Django 4.2+
- Pillow for image handling
- SQLite database (default)

### File Upload Limits
- Max file size: 10MB per file
- Max total upload: 50MB per request
- Supported types: HTML, CSS, JS, images, fonts, PDFs

### Security Considerations
- Self-signed SSL certificate for HTTPS
- Basic authentication (no registration)
- File type validation
- Directory traversal protection
- Local network only (not internet-facing)

## Deployment Options

### Development
```bash
./run_server.sh
```

### Production with HTTPS
```bash
./run_server_https.sh
```

### As System Service
```bash
sudo ./install_service.sh
```

### Docker
```bash
docker-compose up -d
```

## File Reference Guide for Students

When students create their HTML files, they should reference assets like this:

```html
<!-- CSS files -->
<link rel="stylesheet" href="css/style.css">
<link rel="stylesheet" href="css/forms.css">

<!-- JavaScript files -->
<script src="js/main.js"></script>
<script src="js/contact-form.js"></script>

<!-- Images -->
<img src="img/profile-photo.png" alt="Profile">
<img src="img/logo.svg" alt="Logo">
```

## Troubleshooting

### Server won't start
- Check if port 5000 is available: `sudo netstat -tlnp | grep :5000`
- Ensure virtual environment is activated: `source venv/bin/activate`
- Check SSL certificates exist: `ls ssl/`

### Upload failures
- Check file permissions on `media/` directory
- Verify file size limits in settings.py
- Check available disk space

### SSL certificate warnings
- Normal for self-signed certificates
- In Chrome, type thisisunsafe to bypass
- For production, use proper SSL certificates

### Can't access from other machines
- Verify server binds to `0.0.0.0:5000` not `127.0.0.1:5000`
- Check firewall settings
- Ensure your hostname resolves correctly

## Directory Structure

```
static-site-deployment/
├── static_deploy/           # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── deployment/              # Main Django app
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── runserver_plus.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/               # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── registration/
│   │   └── login.html
│   ├── admin/
│   │   └── bulk_upload.html
│   └── site_not_found.html
├── media/                   # User uploaded files
├── ssl/                     # SSL certificates
├── static/                  # Static files (CSS, JS)
├── requirements.txt
├── manage.py
├── setup.sh                 # Automated setup script
├── generate_ssl.sh
├── run_https_server.py
├── run_server.sh            # Script to run with HTTP on port 5000
├── run_server_https.sh      # Script to run with HTTPS (invokes run_https_server.py)
├── install_service.sh
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Environment Variables

Create a `.env` file for configuration (or use the `setup.sh` script to help you):

```env
# Django Configuration
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,<hostname>

# Site Configuration
USE_TLS=True
PORT=5000

# Additional CSRF trusted origins (optional)
ADDITIONAL_CSRF_ORIGINS=https://<hostname>:5000,http://<hostname>:5000

# Database Configuration (optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:password@localhost:5432/static_deploy

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE=10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE=52428800  # 50MB
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Django logs for error details
3. Ensure all dependencies are installed
4. Verify file permissions are correct
