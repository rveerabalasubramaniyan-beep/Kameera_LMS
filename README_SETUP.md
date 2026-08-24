# KameeraLMS — SQL Server / Windows Auth Setup

## 1. Install dependencies
```
pip install -r requirements.txt
```

## 2. Confirm your ODBC driver
Open a terminal on the machine running Django and check which driver is installed:

```
python -c "import pyodbc; print(pyodbc.drivers())"
```

- If `ODBC Driver 17 for SQL Server` appears in the list, `settings.py` is already correct as-is.
- If only `ODBC Driver 18 for SQL Server` is present, open `settings.py` and change:
  ```python
  DB_DRIVER = "ODBC Driver 17 for SQL Server"
  ```
  to:
  ```python
  DB_DRIVER = "ODBC Driver 18 for SQL Server"
  ```
  (Driver 18 defaults to encrypted connections and stricter cert checks — the
  `TrustServerCertificate: "yes"` option already in `settings.py` handles that
  for a local/dev SQL Server instance.)

## 3. Verify SQL Server is reachable
- Confirm SQL Server on `DESKTOP-L7KQ31C` has **Windows Authentication** enabled
  (not "SQL Server auth only").
- Confirm the database `KameeraLMS` already exists on that instance (Django won't
  create the database itself — only the tables inside it).
- Confirm the Windows account running the Django process (e.g. the account you're
  logged in as, or the app pool identity if deployed under IIS) has access rights
  to that SQL Server instance and database.

## 4. Create migrations and apply them
Once you have models defined in an app (see note below):
```
python manage.py makemigrations
python manage.py migrate
```

## Note on models
No models were generated yet because the LMS domain (courses, students,
instructors, assignments, enrollments, etc.) hasn't been specified. Tell me
what entities KameeraLMS needs to track and I'll generate SQL Server–compatible
Django models (with proper field types, e.g. avoiding unsupported `TextField`
default quirks, and unique constraints that work well under mssql-django) plus
the migrations.
