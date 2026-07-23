# AllClub Frontend

This directory contains the frontend application for **AllClub**, a centralized multi-club management platform for student organizations, developed as part of the Software Engineering Project (May 2026).

## Tech Stack

- **Framework:** Vue 3
- **Build Tool:** Vite
- **Language:** JavaScript
- **Routing:** Vue Router
- **Styling:** Bootstrap 5
- **Icons:** Bootstrap Icons
- **Charts:** Chart.js and Vue Chart.js

## Project Setup

### Prerequisites

Ensure that Node.js and npm are installed on your system.

The project requires:

- Node.js (`^22.18.0` or `>=24.12.0`)
- npm

Verify the installed versions:

```bash
node -v
npm -v
```

### Installation

Open a terminal in the frontend project directory and install the required dependencies:

```bash
npm install
```

### Development

Start the local development server:

```bash
npm run dev
```

After the server starts, open the URL displayed in the terminal. By default, it is typically:

```text
http://localhost:5173
```

### Production Build

Generate a production build:

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

## Available Frontend Routes

The frontend prototype includes public and role-based interfaces for Admin, Faculty Coordinator, and Student users.

### Public Routes

- `/` — Landing Page
- `/login` — Login Page
- `/register` — Registration Page
- `/clubs` — Club Discovery Page

### Admin Routes

- `/admin` — Admin Dashboard
- `/admin/users` — User Management
- `/admin/clubs` — Club Management
- `/admin/events` — Event Management
- `/admin/requests` — Request Management

### Faculty Coordinator Routes

- `/faculty` — Faculty Dashboard
- `/faculty/roles` — Faculty Role Management
- `/faculty/clubs` — Faculty Club Interface
- `/faculty/events` — Faculty Event Interface
- `/faculty/requests` — Faculty Request Interface

### Student Routes

- `/student` — Student Dashboard
- `/student/roles` — Student Role Management
- `/student/clubs` — Student Club Interface
- `/student/events` — Student Event Discovery Interface
- `/student/requests` — Student Request and Ticket Management Interface

## Accessing Role-Based Interfaces

The current frontend prototype provides separate interfaces for Admin, Faculty Coordinator, and Student roles.

After starting the development server, the main role-specific interfaces can be accessed directly through:

```text
http://localhost:5173/admin
http://localhost:5173/faculty
http://localhost:5173/student
```

The sidebar navigation within each role-specific interface can then be used to access the available pages for that role.

## Project Structure

```text
frontend/
├── public/                 # Public static assets
├── src/
│   ├── assets/             # CSS and other frontend assets
│   ├── components/         # Reusable and role-specific UI components
│   ├── data/               # Frontend prototype data
│   ├── layouts/            # Role-specific page layouts
│   ├── router/             # Vue Router configuration
│   ├── views/              # Public, Admin, Faculty, and Student views
│   ├── App.vue             # Root Vue component
│   └── main.js             # Application entry point
├── package.json            # Project dependencies and scripts
├── package-lock.json       # Locked dependency versions
└── vite.config.js          # Vite configuration
```

## Recommended IDE Setup

- VS Code
- Vue - Official extension (Volar)

For development and debugging, Vue.js DevTools can also be used with a supported browser.