# CourseMaster

A Django-based course management system with user profiles.

## Features

- User authentication system
- User profile pages with customizable information
- Profile editing functionality
- Avatar upload support
- Admin panel for user management

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Visit http://localhost:8000/admin to access the admin panel
7. Visit http://localhost:8000/profile/ to view your profile (after logging in)

## Usage

- **View Profile**: Navigate to `/profile/` to view your own profile
- **Edit Profile**: Click "Edit Profile" button on your profile page
- **View Other Profiles**: Navigate to `/profile/<username>/` to view other users' profiles
- **Admin Panel**: Manage users and profiles at `/admin/`

## Technologies

- Django 4.2+
- Python 3.8+
- SQLite (default database)
- Pillow (for image handling)
