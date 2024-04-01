## Introduction

- This is a Social Networking REST APIs based application build with Python, Django and Django Rest Framework and Postgres as Database.

## Features

- Users can Sign-up using email and passowrd and can login into the syatem.
- Users can search other users based on keywords (sub-string).
- only Admin can see the list of all users that have signed up.
- Users can send, accept and reject friend requests.
- User can see the Pending requests which are sent by him and recieved to him.
- User can see the frined list as well.
- Note : One user can only send upto 3 requests in one minute.

## Requirements

- Python (>= 3.6)
- Django (>= 3.x)
- PostgreSQL (>= 9.x)
- Docker (optional, for development)

## Getting Started

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/madhavsh96/Accuknox_Social_networking.git
    cd your-project
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up PostgreSQL database:
   
   - Install PostgreSQL if not already installed.
   - Create a new PostgreSQL database and configure the connection settings in `settings.py`.

4. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

5. Create super user (which will act as admin):

    ```bash
    python manage.py createsuperuser
    ```
    Enter email and password

### Development

- Run the development server:

    ```bash
    python manage.py runserver
    ```

- Access the Django admin interface at `http://localhost:8000/admin/` (default credentials may apply).
