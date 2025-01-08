###TattooText Generator API
A powerful REST API service that transforms text into customized tattoo-style images with support for multiple fonts, colors, and sizes. Built with Django REST Framework and Celery for efficient asynchronous processing.
🚀##Features

Custom Text Generation: Convert any text into tattoo-style images
Multiple Font Support: Choose from a variety of tattoo-friendly fonts
Color Customization: Full HEX color support for personalized designs
Flexible Sizing: Adjustable font sizes from 12px to 200px
Asynchronous Processing: Efficient image generation using Celery
Secure Authentication: JWT-based user authentication system
Real-time Status Updates: Track generation progress through API endpoints
RESTful Architecture: Clean, well-documented API endpoints

🛠️ ##Technical Stack

Backend: Django/Django REST Framework
Authentication: JWT (JSON Web Tokens)
Task Queue: Celery
Documentation: Swagger/OpenAPI
Image Processing: Pillow/PIL
Database: PostgreSQL
API Security: CORS support, Token Authentication

📝 ##API Endpoints

POST /api/generate/: Generate new tattoo text image
GET /api/tasks/<task_id>/: Check generation status
POST /api/auth/register/: User registration
POST /api/auth/login/: User authentication
POST /api/auth/logout/: User logout

💡 ##Use Cases

Tattoo artists previewing text designs
Custom typography generation
Text-based logo creation
Typography exploration
Social media content creation

🚀 Getting Started

📚##Documentation
Complete API documentation is available through Swagger UI at /swagger/ and ReDoc at /redoc/ after running the server.

