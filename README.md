# Personal Accountability Engine (PAE) - Setup Instructions

The Personal Accountability Engine is a discipline-focused system designed to enforce accountability, track behavior, and generate performance insights.

## Prerequisites
- Python 3.10+
- Pip

## Installation

1. **Clone the repository** (if not already in the directory):
   ```bash
   cd DisciTrack
   ```

2. **Install dependencies**:
   ```bash
   pip install django django-crispy-forms crispy-bootstrap5 pillow
   ```

3. **Database Setup**:
   ```bash
   python manage.py makemigrations accounts attendance goals analytics
   python manage.py migrate
   ```

4. **Create Superuser** (to access admin):
   ```bash
   python manage.py createsuperuser
   # username: admin, pass: admin123 (used in setup)
   ```

5. **Run the server**:
   ```bash
   python manage.py runserver
   ```

## Key Features
- **Attendance Proof System**: Mark lectures with auto-timestamp and image upload. Credibility score reduces if proof is missing or marking is late.
- **Goal Execution Engine**: Daily checklist for goals (Gym, Coding, etc.). Locked after the day ends.
- **Daily Lock System**: Past logs become immutable.
- **Scoring Engine**: Evaluates discipline based on completion ratio, credibility, and streaks.
- **Heatmap Visualization**: GitHub-style grid for long-term consistency.

## Tech Stack
- **Backend**: Django (Modular apps: accounts, attendance, goals, analytics)
- **Database**: SQLite
- **Frontend**: Tailwind CSS + Custom Dark Premium CSS
- **PWA**: manifest.json and basic service worker included for mobile scalability.

## Credentials for Testing
- **Username**: `admin`
- **Password**: `admin123`
