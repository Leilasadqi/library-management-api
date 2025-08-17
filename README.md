# 📚 Library Management System API

A backend API built with **Django + Django REST Framework (DRF)** that manages books, users, and transactions (borrowing and returning).  
This project is my **Capstone Project** for Backend Development.

---

## 🚀 Features
- **Books Management (CRUD)**  
  - Add, view, update, and delete books  
  - Track availability with `copies_available`  

- **Users Management (CRUD)**  
  - Admin can manage users  
  - Each user has unique email and membership date  

- **Borrow & Return**  
  - Users can check out a book (if available)  
  - Copies decrease/increase automatically  
  - Transaction log stores checkout/return dates  

- **Search & Filters**  
  - Search books by title, author, or ISBN  
  - Filter by availability  
  - Pagination included  

- **Authentication**  
  - Session authentication (default)  
  - Optional JWT authentication  

---

## 🛠️ Tech Stack
- **Backend:** Django 5, Django REST Framework  
- **Database:** SQLite (dev) / PostgreSQL (production)  
- **Deployment:** Heroku or PythonAnywhere  
- **Auth:** Django Auth / JWT (optional)  

---

## ⚙️ Quick Start

1. **Clone repo**
   ```bash
   git clone https://github.com/<your-username>/library-management-api.git
   cd library-management-api
