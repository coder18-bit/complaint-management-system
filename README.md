# Complaint Management System

A web-based Complaint Management System built using Django that allows users to register and track complaints while enabling administrators and engineers to manage, assign, and resolve issues efficiently.

## Features

### User Features
- Register and log in securely
- Submit complaints
- View complaint status
- Track complaint progress

### Admin Features
- View all complaints
- Assign complaints to engineers
- Update complaint priority
- Monitor complaint status
- Manage engineers

### Engineer Features
- View assigned complaints
- Update complaint status
- Add progress notes
- Maintain complaint history

## Tech Stack

- Backend: Django (Python)
- Database: SQLite
- Frontend: HTML, CSS, Bootstrap 5
- Authentication: Django Authentication System

## Project Structure

```text
complaint_management/
│
├── complaint/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── login/
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── complaint_management/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
└── requirements.txt
```

## Installation

### Clone Repository

```bash
git clone https://github.com/coder18-bit/complaint-management-system.git
cd complaint-management-system
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

Linux/Mac:

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Apply Migrations

```bash
python manage.py migrate
```

### Run Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Future Improvements

- Email notifications
- Complaint analytics dashboard
- File attachment support
- Complaint categories
- REST API integration
- Mobile responsive enhancements

## Author

**Apoorva**

B.Tech CSE (Data Science)

GitHub: https://github.com/coder18-bit

## License

This project is developed for educational and learning purposes.
