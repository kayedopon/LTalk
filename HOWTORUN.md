# How to Run LTalk - Language Learning Application

This guide provides step-by-step instructions to set up and run the LTalk application on your local machine.

## Prerequisites

- Python 3.x
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation

1. **Clone or download the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd LTalk
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - MacOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

2. **Access the application** in your web browser at:
   ```
   http://127.0.0.1:8000/
   ```

3. **Access the admin interface** (if you created a superuser) at:
   ```
   http://127.0.0.1:8000/admin/
   ```

## Key Features

- User authentication: Register and login to manage your word sets
- Word set creation and management
- Multiple exercise types (flashcards, multiple-choice, fill-in-the-gap)
- Progress tracking
- Public word set exploration

## Troubleshooting

- If you encounter dependency issues, ensure you're using the correct Python version and that all packages in requirements.txt are installed
- For database issues, try resetting the database:
  ```bash
  rm db.sqlite3
  python manage.py migrate
  ```

## Additional Commands

- **Collect static files**:
  ```bash
  python manage.py collectstatic
  ```

- **Run tests**:
  ```bash
  python manage.py test
  ``` 