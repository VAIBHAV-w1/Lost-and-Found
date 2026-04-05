# Lost and Found Platform

A professional, generalized Lost and Found platform built with Django. This system allows users to report lost or found items, track them on a map localized to India, and securely communicate with other users to coordinate recoveries.

## Core Features
- **Map-Based Tracking**: Integrated Leaflet.js mapping with geofencing restricted to India's boundaries.
- **Automated Matching**: Intelligent categorical matching system that notifies users when a potential match is reported within a 10km radius.
- **Secure Messaging**: Internal peer-to-peer messaging system for safe coordination without exposing private contact details.
- **Categorical Reporting**: Dedicated categories for Electronics, Wallets, Pets, Documents, and more.
- **Responsive UI**: A solid, professional dark-mode design built for clarity and precision.

## Technology Stack
- **Backend**: Python 3.x, Django 5.2.x
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Mapping**: Leaflet.js (OpenStreetMap)
- **Database**: SQLite (default), compatible with PostgreSQL

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VAIBHAV-w1/Lost-and-Found.git
   cd Lost-and-Found
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start the server:**
   ```bash
   python manage.py runserver
   ```

5. **Access the platform:**
   Navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Project Structure
- `tracker/`: The core Django app containing models, views, and business logic.
- `tracker/utils.py`: Modular utilities for geographical distance and matching algorithms.
- `tracker/templates/`: Highly polished HTML templates with a consistent design system.

---
Managed by VAIBHAV-w1. Licensed under MIT.
