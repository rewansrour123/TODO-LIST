# Lab 2: Login & To-Do Application

A web-based **Login and To-Do Management System** built using Flask and MySQL. The application allows users to create accounts, log in securely, and manage their personal tasks.

---

## 👥 1. Team Members

| Rewan Mahmoud Mohamed | 2304098 | Database Design, Flask Backend, Authentication, and To-Do List |

## 🛠️ 2. Technologies & Tools

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **Database Connector:** PyMySQL
- **Password Security:** bcrypt
- **Session Management:** Flask Sessions

## 🚀 3. Installation & Setup

Follow these steps to run the project locally.

**Step 1 — Install the requirements**

Make sure Python and MySQL are installed on your computer.

```bash
pip install -r requirements.txt
```

**Step 2 — Set up the database**

Execute the SQL script located at `database/schema.sql` in MySQL to create the required database and tables.

**Step 3 — Configure environment variables**

Copy `.env.example` to a new file named `.env`.

Update the MySQL credentials and configure a secure, randomly generated secret key.

**Step 4 — Run the application**

```bash
python app.py
```

**Step 5 — Open the website**

Visit the following URL in your browser:

[http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)

You can now register a new account and start managing your tasks.

## ✨ 4. Implemented Requirements

| Requirement | Description |
|---|---|
| R1 | User registration with duplicate email handling |
| R2 | Login, password verification, and logout |
| R3 | Private user-specific to-do lists using sessions |
| R4 | Adding new tasks |
| R5 | Editing task titles |
| R6 | Marking tasks as completed or incomplete |
| R7 | Deleting tasks with confirmation |
| R8 | Client-side and server-side input validation |
| R9 | bcrypt password hashing and parameterized SQL queries |
| R10 | Responsive interface using CSS |

## 📸 5. Screenshots

Add screenshots demonstrating the main features of the application.

1. **Registration:** Registration form with validation errors.
2. **Login:** Login page.
3. **Task Management:** To-do list showing at least one completed task.
4. **Responsive Design:** Application displayed in a phone-sized browser window.

## 🗄️ 6. Database & Security Questions

### A. Why do UPDATE and DELETE queries include `AND user_id = ?`?

This condition ensures that users can only update or delete their own tasks. Without it, a user might access or modify another user's task by supplying its ID.

### B. What happens if a to-do references a nonexistent `user_id`?

MySQL rejects the operation if the referenced user does not exist and the foreign key constraint is enforced. This maintains referential integrity between the users and tasks tables.

### C. Why store a password hash instead of the original password?

Storing a password hash avoids keeping passwords in plaintext. bcrypt applies a salt and uses a computationally expensive hashing process, making password-guessing attacks more difficult.

### D. Why validate an empty name if the database column is `NOT NULL`?

The `NOT NULL` constraint prevents NULL values, but it does not prevent empty strings or strings containing only spaces. Application-level validation is therefore necessary to reject invalid names.

---

## ✅ Conclusion

This project demonstrates the implementation of a basic web application with user authentication, database integration, secure password storage, and personal task management. It also applies input validation, session handling, and database constraints to improve security and reliability.