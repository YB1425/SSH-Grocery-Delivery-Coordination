# SSH-Grocery-Delivery-Coordination

## Project Setup Guide

### Prerequisites

Make sure the following tools are installed on your machine:

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)  
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)  
- **Ngrok**: [Download Ngrok](https://ngrok.com/download)  

---

### Clone the Repository

```bash
git clone https://github.com/your-repository/SSH-Grocery-Delivery-Coordination.git
cd SSH-Grocery-Delivery-Coordination
```

---

### Set Up the Virtual Environment

If you're using a virtual environment, activate it:

```bash
source env/bin/activate
```

After activating the virtual environment, install the required dependencies:

```bash
pip install -r requirements.txt
```



If `env` doesn't exist, create it:

```bash
python3 -m venv env
source env/bin/activate
```

---

### Start Docker Containers

Run the following command to build and start the containers:

```bash
docker-compose up --build
```

This will set up:

- **Web Service** (Django application)  
- **Database Service** (PostgreSQL)  

---

### Apply Migrations

Ensure the database schema is up to date:

```bash
docker-compose run web python manage.py migrate
```

---

### Load Initial Data

Load the preloaded data (store items, users, shared carts, etc.):

```bash
docker-compose run web python manage.py loaddata final__data.json
```

---

### Create a Superuser (Optional)

If you need an admin user:

```bash
docker-compose run web python manage.py createsuperuser
```

---

### Run the Application

Ensure the containers are running:

```bash
docker-compose up
```

The application will be accessible at [http://localhost:8000/](http://localhost:8000/).

---

### Login Details (Optional)

Use the following login credentials for guest access:

- **Username**: `guest`  
- **Password**: `bham`  

---

### Expose the Application with Ngrok

To make the application accessible over the internet:

1. **Start Ngrok**:

   ```bash
   ngrok http 8000
   ```

2. **Copy the Forwarding URL** (e.g., `https://0391-38-242-183-195.ngrok-free.app`) and use it to access the application.

3. **Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`** in `settings.py` with the Ngrok URL:

   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', '4a83-38-242-183-195.ngrok-free.app']
   CSRF_TRUSTED_ORIGINS = ['https://4a83-38-242-183-195.ngrok-free.app']
   ```

---

### Summary of Commands

- **Start Containers**:  
  ```bash
  docker-compose up --build
  ```

- **Apply Migrations**:  
  ```bash
  docker-compose run web python manage.py migrate
  ```

- **Load Initial Data**:  
  ```bash
  docker-compose run web python manage.py loaddata final__data.json
  ```

- **Run Ngrok**:  
  ```bash
  ngrok http 8000
  ```

---

## Overview

This project aims to simplify grocery delivery coordination for students living in shared accommodations. By integrating advanced software engineering practices and supermarket APIs, the system provides a seamless way to manage shared grocery shopping, reduce costs, and enhance convenience.

---

## Features

- **Shared Cart Management**: Collaborative cart for flatmates to add, update, and track grocery items.   
- **Cost Splitting**: Automatically calculates and divides costs among users.  
- **Notification System**: Alerts for changes in shared cart status, such as item additions or purchases.  
- **Secure Data Handling**: Robust encryption and access controls to protect user data.  

---

## Planned Enhancements

1. Full integration with supermarket APIs for real-time price and stock updates.  
2. Advanced analytics for grocery spending and recommendations.  
3. Enhanced mobile and web UI for improved user experience.  

---

## Technical Details

- **Backend**: Django Framework  
- **Database**: Postgres with planned integration for scalable databases.  
- **API**: Simulated supermarket API with future live integration.  

---

## Contact

For questions or feedback, contact us at:  
- **GitHub Issues**: [Issue Tracker](https://github.com/YB1425/SSH-Grocery-Delivery-Coordination/issues)
