# Messenger

This is a real-time messaging web application built with Django Channels. It features real-time chat functionality with support for message forwarding, reply, seen status, online/offline indicators, and more.

## Features

- **Real-Time Chat:**  
  Utilizes Django Channels and WebSockets for instant message delivery.
  
- **User Authentication:**  
  Integrated with Django Allauth for secure signup and login.

- **Message Forwarding & Replies:**  
  Allows users to forward messages and reply to specific messages with context.

- **Online/Offline Status:**  
  Tracks and displays user online status in real-time.

- **Rich Text Support:**  
  Uses CKEditor for composing messages with formatting.

## Technologies Used

- **Backend:**  
  - Django  
  - Django Channels (for WebSocket support)  
  - Django Allauth (for authentication)  
  - PostgreSQL

- **Frontend:**  
  - HTMX (for AJAX-like interactions)  
  - Alpine.js (for interactive UI components)  
  - Tailwind CSS (for styling)  
  - CKEditor (for rich text editing)
  
## Installation

### Prerequisites

[Docker](https://www.docker.com/) for containerized development

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ArianN8610/messenger.git
   cd messenger
   ```

2. **Configure Environment Variables:**  
   Create `.env.dev` and `.env.dev.db` files in the project root (or set the environment variables manually).\
   `.env.dev`:
   ```env
   DEBUG=True
   SECRET_KEY=your_secret_key
   SQL_ENGINE=django.db.backends.postgresql
   SQL_DATABASE=postdb
   SQL_HOST=db
   SQL_PORT=5432
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   EMAIL_HOST='smtp.gmail.com'
   EMAIL_HOST_USER=your_email
   EMAIL_HOST_PASSWORD=your_email_host_password
   DEFAULT_FROM_EMAIL=your_default_email
   CKEDITOR_LICENSE_KEY=your_ckeditor_license_key
   ```
   `.env.dev.db`:
   ```env
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   POSTGRES_DB=postdb
   ```

3. **Build and start containers:**

   ```bash
   docker compose up -d --build
   ```

4. **Apply migrations in the Docker container:**

   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Create styles with tailwind:**

   ```bash
   docker compose exec backend python manage.py tailwind start
   ```

6. **Create a Superuser (optional):**

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

7. **Access the application via the exposed port (e.g., `http://localhost:8000`).**
