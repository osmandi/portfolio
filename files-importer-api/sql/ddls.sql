-- hired_employees
CREATE TABLE IF NOT EXISTS hired_employees (
  id INTEGER PRIMARY KEY,
  name VARCHAR(200),
  datetime TIMESTAMP,
  department_id INTEGER,
  job_id INTEGER
)
SORTKEY (id);

-- Departments
CREATE TABLE IF NOT EXISTS departments (
  id INTEGER PRIMARY KEY,
  department VARCHAR(100)
)
SORTKEY (id);

-- Jobs
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY,
  job VARCHAR(200)
)
SORTKEY (id);
