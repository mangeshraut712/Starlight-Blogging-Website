# 🌟 Starlight - Share Your Stories with the Universe

A modern, beautiful blogging platform where writers can connect, share their stories, and build communities under the stars. ⭐✨

![Starlight Logo](starlight-ng/src/assets/img/starlight-logo.svg)

## ✨ Features

- **📝 Modern Blog Interface**: Clean, cosmic-themed design with glassmorphism effects
- **👥 User Authentication**: Register, login, and update profiles
- **📖 Post Creation**: Rich text editor with TinyMCE for crafting beautiful content
- **💬 Interactive Comments**: Engage with other writers through threaded comments
- **❤️ Like System**: Show appreciation for great stories
- **🏷️ Communities**: Organize content by topics and connect with like-minded writers
- **📱 Responsive Design**: Beautiful experience across all devices
- **🎨 Modern UI/UX**: Gradient backgrounds, smooth animations, and professional styling

## 🚀 Quick Start

### Prerequisites
- Node.js (v14+ recommended, v19.3.0 for older setups)
- Python 3.x
- Angular CLI

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mangeshraut712/Starlight-Blogging-Website.git
   cd Starlight-Blogging-Website
   ```

2. **Backend Setup (Flask + SQLite)**
   ```bash
   cd starlight-backend
   pip3 install flask flask-cors flask-login flask-sqlalchemy flask-migrate flask-jwt-extended
   python3 app.py
   ```
   Backend will run on http://localhost:8080

3. **Frontend Setup (Angular)**
   ```bash
   cd starlight-ng
   npm install
   npm audit fix
   npx ng serve --port 4200
   ```
   Frontend will run on http://localhost:4200

4. **Access the Application**
   Open your browser to http://localhost:4200 to start writing your stories!

## 🏗️ Project Structure

```
Starlight-Blogging-Website/
├── starlight-backend/          # Flask API backend
│   ├── app.py                 # Main Flask application
│   ├── models.py             # SQLAlchemy database models
│   ├── instance/             # Database files
│   └── migrations/           # Database migrations
├── starlight-ng/             # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/   # Reusable UI components
│   │   │   │   ├── navbar/   # Navigation component
│   │   │   │   └── post-cart/# Post display component
│   │   │   ├── pages/        # Application pages
│   │   │   │   ├── homepage/ # Landing page
│   │   │   │   ├── login/    # Authentication
│   │   │   │   └── ...       # Other pages
│   │   │   └── services/     # Angular services
│   │   └── styles.css        # Global styles
│   ├── angular.json          # Angular configuration
│   └── package.json          # Dependencies
└── README.md
```

## 🔧 Technical Stack

### Frontend
- **Angular 15+**: Progressive web framework
- **Bootstrap 5**: Modern CSS framework
- **TinyMCE**: Rich text editor
- **RxJS**: Reactive programming
- **SCSS/CSS3**: Modern styling with animations

### Backend
- **Flask**: Python microframework
- **SQLAlchemy**: ORM for database operations
- **Flask-JWT-Extended**: Token-based authentication
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)
- **Flask-Migrate**: Database migration management

### Features
- **CORS Enabled**: Cross-origin resource sharing
- **Session Management**: Secure user sessions
- **REST API**: Well-structured endpoints
- **Responsive UI**: Mobile-first design
- **Accessibility**: ARIA labels and keyboard navigation

## 📱 Usage Guide

### Getting Started
1. **Register**: Create your account and join the writing community
2. **Explore**: Browse existing posts and discover new writers
3. **Create**: Use the rich text editor to craft your stories
4. **Engage**: Like and comment on posts that inspire you
5. **Connect**: Join community discussions and topics

### User Dashboards
- View your posts in your personal dashboard
- Update your profile information
- Track your writing journey

## 🎨 Design Philosophy

Starlight embodies the essence of storytelling under the stars:

- **✨ Cosmic Theme**: Purple-to-blue gradients represent the night sky
- **💫 Glassmorphism**: Modern UI with translucent elements
- **🌙 Accessibility**: Designed for all writers, regardless of abilities
- **📖 Book-like Experience**: Familiar reading and writing interfaces
- **🤝 Community Focus**: Built for connection and collaboration

## 🤝 Contributing

We welcome contributions from all writers and developers!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing new feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Future Enhancements

- [ ] Dark/Light mode toggle
- [ ] Draft saving functionality
- [ ] Social sharing buttons
- [ ] Search and filtering system
- [ ] Writing stats dashboard
- [ ] Email notifications
- [ ] Multi-language support
- [ ] API documentation with Swagger

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Change default ports in `angular.json` and `app.py`
2. **CORS errors**: Check proxy configuration in `proxy.conf.json`
3. **Database issues**: Ensure migrations are run correctly
4. **Dependency problems**: Clear node_modules and reinstall

### Getting Help

- Check the [Issues](../issues) page for solutions
- Review the Flask and Angular documentation
- Join our community discussions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Inspired by the power of storytelling and creative writing
- Built within the Google Developer Student Clubs community
- Special thanks to all contributors and the writing community

---

**Ready to share your stories?** Visit [Starlight](http://localhost:4200) and start writing! ✍️✨
