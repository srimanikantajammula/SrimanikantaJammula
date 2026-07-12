# Queue Management System (QMS)

A modern, mobile-friendly Django web application designed to optimize queue management in retail stores, restaurants, banks, and other institutions where customers wait in line. The system allows customers to join a virtual queue, track their position in real-time, and receive notifications when it's their turn.

## 📌 Table of Contents
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## ðŸš€ Features

### Customer Features
- **ðŸ“± Mobile-Optimized Interface** - Fully responsive design that works perfectly on smartphones and tablets
- **ðŸ” Email Verification** - Secure OTP-based registration via email
- **ðŸŽ« Token System** - Unique token numbers for easy identification
- **â±ï¸ Live Countdown** - Real-time countdown showing estimated wait time
- **ðŸ“§ Email Notifications** - Automatic notifications for position updates and turn alerts
- **ðŸ‘¤ Availability Toggle** - Mark yourself as available/unavailable in the queue
- **ðŸ“Š Queue Status** - View current position and estimated wait time
- **ðŸ”„ Auto-Refresh** - Automatic page updates to show latest queue information

### Employee Features
- **ðŸ‘¨â€ðŸ’¼ Employee Dashboard** - Clean, intuitive interface for staff
- **ðŸŽ¯ Customer Management** - Serve, skip, or remove customers from queue
- **â° Delay Management** - Add delays to queue (5, 10, 15 minutes) or reset
- **ðŸ“¢ Notifications** - Send notifications to next customers
- **ðŸ“‹ Queue Overview** - View all customers with availability status
- **ðŸ”„ Real-time Updates** - Live updates of queue changes

### Admin Features
- **ðŸ‘‘ Django Admin Panel** - Full administrative control
- **ðŸ‘¥ User Management** - Manage customers and employees
- **ðŸ“Š Analytics** - View queue statistics and user data
- **âš™ï¸ System Configuration** - Configure queue settings

## ðŸ› ï¸ Technology Stack

### Backend
- **Django 5.2.5** - Web framework
- **SQLite** - Database (development)
- **Python 3.13** - Programming language

### Frontend
- **HTML5** - Markup
- **CSS3** - Responsive styling
- **JavaScript** - Client-side functionality
- **Mobile-First Design** - Optimized for mobile devices

### Email Service
- **Gmail SMTP** - Email delivery
- **SMTP Protocol** - Email communication

### Dependencies
- **python-dotenv** - Environment variable management
- **Django Built-ins** - Authentication, admin, email, etc.
            

## ðŸ“± Mobile Features

- **Responsive Design** - Works on all screen sizes
- **Touch-Friendly** - Optimized for touch interactions
- **Progressive Web App** - Can be installed on mobile devices
- **Offline-Ready** - Basic functionality works without internet
- **Fast Loading** - Optimized for mobile networks

## ðŸš€ Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Queue_Management_System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env file with your email credentials
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

7. **Access the application**
   - **Desktop**: http://127.0.0.1:8000
   - **Mobile**: http://YOUR_IP_ADDRESS:8000

## ðŸ“§ Email Configuration

Configure your email settings in the `.env` file:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

**Note**: For Gmail, you'll need to use an App Password instead of your regular password.

## ðŸŽ¯ Usage

### For Customers
1. **Register** - Enter name and email address
2. **Verify** - Check email for OTP and enter it
3. **Join Queue** - Get your token number and position
4. **Track Progress** - View live countdown and position updates
5. **Get Notified** - Receive email when it's your turn

### For Employees
1. **Login** - Use admin-created credentials
2. **Select Counter** - Choose your counter number
3. **Manage Queue** - Serve customers, add delays, send notifications
4. **Monitor Status** - View all customers and their availability

### For Admins
1. **Access Admin Panel** - Go to `/admin/`
2. **Manage Users** - Add/remove employees and customers
3. **Configure System** - Set up queue parameters
4. **Monitor Activity** - View system statistics

## ðŸ”§ Configuration

### Mobile Access
To access from mobile devices on the same network:
1. Find your computer's IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Add the IP to `ALLOWED_HOSTS` in `settings.py`
## 👥 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests and ensure code quality
5. Commit your changes: `git commit -m 'Add some feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use docstrings for functions and classes
- Write clear commit messages

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Django
- Inspired by real-world queue management needs
- Thanks to all contributors who have helped improve this project
- Special thanks to the Django community for their excellent documentation and support
- **Delay Management**: Add 5, 10, or 15-minute delays
- **Availability**: Users can mark themselves unavailable
- **Auto-Refresh**: Pages refresh every 30-60 seconds

## ðŸ“Š Database Models

- **QueueUser** - Customer information and queue position
- **Employee** - Staff members and counter assignments
- **QueueConfig** - Global queue settings
- **UserRequest** - Customer requests and messages

## ðŸŽ¨ UI/UX Features

- **Modern Design** - Clean, professional interface
- **Color-Coded Status** - Green (available), Red (unavailable)
- **Real-time Updates** - Live countdown timers
- **Mobile Navigation** - Touch-friendly buttons and menus
- **Responsive Tables** - Horizontal scroll on small screens
- **Loading States** - Visual feedback for actions

## ðŸ”’ Security Features

- **CSRF Protection** - Cross-site request forgery prevention
- **Email Verification** - OTP-based registration
- **Session Management** - Secure user sessions
- **Input Validation** - Form validation and sanitization
- **Admin Authentication** - Secure admin access

## ðŸ“± Mobile Optimization

- **Viewport Meta Tags** - Proper mobile rendering
- **Touch Targets** - 44px minimum button size
- **Swipe Support** - Horizontal table scrolling
- **Orientation Handling** - Smooth rotation support
- **Performance** - Optimized for mobile networks

## ðŸš€ Deployment

### Development
```bash
python manage.py runserver 0.0.0.0:8000
```

### Production
- Use a production WSGI server (Gunicorn, uWSGI)
- Set up a reverse proxy (Nginx)
- Use a production database (PostgreSQL, MySQL)
- Configure proper static file serving
- Set up SSL certificates

## ðŸ“ API Endpoints

- `/` - Home page
- `/register/` - Customer registration
- `/otp/` - OTP verification
- `/queue-details/` - View queue status
- `/employee/` - Employee dashboard
- `/admin/` - Django admin panel
- `/toggle-availability/` - Mark availability
- `/cancel-spot/` - Leave queue

## ðŸ¤ Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ðŸ“„ License

This project is open source and available under the MIT License.

## ðŸ†˜ Support

For support and questions:
- Check the Django documentation
- Review the code comments
- Test with the provided sample data
- Ensure email configuration is correct

## ðŸ”„ Recent Updates

- âœ… **Mobile Optimization** - Full responsive design
- âœ… **Live Countdown** - Real-time wait time updates
- âœ… **Availability System** - Mark users as available/unavailable
- âœ… **Delay Management** - Add delays without affecting current user
- âœ… **Email Notifications** - Automated position updates
- âœ… **Touch-Friendly UI** - Optimized for mobile devices
- âœ… **Auto-Refresh** - Automatic page updates
- âœ… **Performance Improvements** - Faster loading and better UX

---

**Built with â¤ï¸ using Django and modern web technologies**
