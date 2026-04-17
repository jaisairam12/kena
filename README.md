# ApexCare ERP

A complete Hospital and University ERP system built with **Python Flask** and **MySQL**.

---

## Project Structure

```
apexcare/
├── app.py              ← Flask routes & logic
├── config.py           ← MySQL + Flask config
├── schema.sql          ← Database schema + seed data
├── requirements.txt    ← Python dependencies
├── static/
│   └── css/style.css   ← Dark theme stylesheet
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── hospital/
    │   ├── patients.html
    │   ├── doctors.html
    │   ├── appointments.html
    │   └── beds.html
    └── university/
        ├── students.html
        ├── faculty.html
        ├── courses.html
        ├── attendance.html
        └── fees.html
```

---

## Prerequisites

| Tool            | Version     |
|-----------------|-------------|
| Python          | 3.8+        |
| MySQL Server    | 5.7+ / 8.0+ |
| pip             | Latest      |

---

## Setup Instructions

### Step 1 — Clone / place the project

Put the project folder anywhere you like, e.g.  `D:\kena`.

---

### Step 2 — Create & activate a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Windows note:** `flask-mysqldb` requires the MySQL C connector.  
> If the install fails, run:
> ```bash
> pip install mysqlclient --find-links https://www.lfd.uci.edu/~gohlke/pythonlibs/
> ```
> Or install the **MySQL Connector/C** from https://dev.mysql.com/downloads/connector/c/ first.

---

### Step 4 — Configure database credentials

Edit **`config.py`**:

```python
MYSQL_HOST     = 'localhost'
MYSQL_USER     = 'root'
MYSQL_PASSWORD = ''          # ← put your MySQL root password here
MYSQL_DB       = 'apexcare_erp'
```

---

### Step 5 — Create the database & tables

Open your MySQL client (Workbench, XAMPP shell, or plain `mysql`) and run:

```bash
mysql -u root -p < schema.sql
```

Or paste the contents of `schema.sql` into MySQL Workbench and execute.

This will:
- Create the `apexcare_erp` database
- Create all 10 tables
- Insert the default admin user (`admin` / `admin123`)

---

### Step 6 — Run the application

```bash
python app.py
```

You should see:

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### Step 7 — Open in browser

Navigate to: **http://localhost:5000**

Login with:
- **Username:** `admin`
- **Password:** `admin123`

---

## Modules

### 🏥 Hospital
| Page         | Route                    | Description                               |
|--------------|--------------------------|-------------------------------------------|
| Patients     | `/hospital/patients`     | Register & view patients                  |
| Doctors      | `/hospital/doctors`      | Add & view doctors                        |
| Appointments | `/hospital/appointments` | Book appointments (FK to patients+doctors)|
| Beds         | `/hospital/beds`         | Track bed availability                    |

### 🎓 University
| Page       | Route                    | Description                           |
|------------|--------------------------|---------------------------------------|
| Students   | `/university/students`   | Enroll & view students                |
| Faculty    | `/university/faculty`    | Add faculty members                   |
| Courses    | `/university/courses`    | Define courses and credits            |
| Attendance | `/university/attendance` | Mark attendance (FK to students)      |
| Fees       | `/university/fees`       | Record fee payments (FK to students)  |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask_mysqldb` | Run `pip install flask-mysqldb` |
| `Access denied for user 'root'` | Update `MYSQL_PASSWORD` in `config.py` |
| `Unknown database 'apexcare_erp'` | Run `schema.sql` first |
| `Table doesn't exist` | Re-run `schema.sql` |
| Page shows no data after form submit | Check terminal for `[... ERROR]` print messages |

---

## Default Login

```
Username: admin
Password: admin123
```
