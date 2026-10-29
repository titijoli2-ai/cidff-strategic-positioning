-- Select the project database
USE cidff_project;

-- Create the department reference table
CREATE TABLE IF NOT EXISTS departments (
    department_code CHAR(2) PRIMARY KEY,
    department_name VARCHAR(50) NOT NULL
);
-- Add the four departments
INSERT INTO departments (department_code, department_name)
VALUES
    ('38', 'Isère'),
    ('69', 'Rhône'),
    ('73', 'Savoie'),
    ('74', 'Haute-Savoie')
ON DUPLICATE KEY UPDATE
    department_name = VALUES(department_name);

-- Check the saved records
SELECT *
FROM departments;

-- Create the RNA association table
CREATE TABLE IF NOT EXISTS associations (
    rna_id VARCHAR(20) PRIMARY KEY,
    siret CHAR(14),
    association_name TEXT NOT NULL,
    association_purpose TEXT,
    creation_date DATE,
    creation_year SMALLINT,
    municipality_code CHAR(5),
    municipality_name VARCHAR(255),
    postal_code CHAR(5),
    department_code CHAR(2) NOT NULL,
    website TEXT,
    administrative_status CHAR(1),
    vss_vif BOOLEAN,
    women_equality BOOLEAN,

    FOREIGN KEY (department_code)
        REFERENCES departments(department_code)
);
-- Check the association table structure
DESCRIBE associations;
-- Check the number of imported associations
SELECT COUNT(*) AS association_count
FROM cidff_project.associations;
-- Create the annual department violence table
CREATE TABLE IF NOT EXISTS department_violence (
    department_code CHAR(2) NOT NULL,
    region_code SMALLINT,
    year SMALLINT NOT NULL,
    violence_type VARCHAR(100) NOT NULL,
    count_unit VARCHAR(100),
    recorded_victims INT,
    rate_per_1000 DOUBLE,
    population INT,
    population_reference_year SMALLINT,
    housing_units INT,
    housing_reference_year SMALLINT,

    PRIMARY KEY (department_code, year, violence_type),

    FOREIGN KEY (department_code)
        REFERENCES departments(department_code)
);
-- Check imported records by department
SELECT
    d.department_name,
    COUNT(*) AS record_count
FROM department_violence AS v
JOIN departments AS d
    ON v.department_code = d.department_code
GROUP BY d.department_code, d.department_name
ORDER BY d.department_code;
-- Create the table for average rates over a period
CREATE TABLE IF NOT EXISTS minor_intrafamily_violence (
    department_code CHAR(2) NOT NULL,
    period VARCHAR(9) NOT NULL,
    violence_type VARCHAR(100) NOT NULL,
    rate_per_1000_minors DOUBLE,

    PRIMARY KEY (department_code, period, violence_type),

    FOREIGN KEY (department_code)
        REFERENCES departments(department_code)
);

-- Check the imported rates and department names
SELECT
    d.department_name,
    v.period,
    v.violence_type,
    v.rate_per_1000_minors
FROM minor_intrafamily_violence AS v
JOIN departments AS d
    ON v.department_code = d.department_code
ORDER BY v.department_code, v.violence_type;

-- Create the state funding records table
CREATE TABLE IF NOT EXISTS funding_payments (
    funding_id INT AUTO_INCREMENT PRIMARY KEY,
    year SMALLINT NOT NULL,
    department_code CHAR(2) NOT NULL,
    municipality_code CHAR(5),
    municipality_name VARCHAR(255),
    siren CHAR(9),
    nic CHAR(5),
    association_name TEXT,
    budget_program VARCHAR(10),
    amount DECIMAL(18, 2) NOT NULL,
    funding_purpose TEXT,
    agreement TEXT,
    siren_original TEXT,
    siren_corrected BOOLEAN,
    siren_format_valid BOOLEAN,
    geography_corrected BOOLEAN,
    identical_record_flag BOOLEAN,
    siret CHAR(14),
    historical_purpose_context TEXT,

    FOREIGN KEY (department_code)
        REFERENCES departments(department_code)
);


-- Check funding records and totals by year
SELECT
    year,
    COUNT(*) AS record_count,
    SUM(amount) AS total_amount
FROM funding_payments
GROUP BY year
ORDER BY year;

-- Create the directory organization table
CREATE TABLE IF NOT EXISTS directory_organizations (
    directory_id INT AUTO_INCREMENT PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    data_source VARCHAR(255) NOT NULL,
    rna_id VARCHAR(20),
    head_office_verified BOOLEAN
);

-- Link directory organizations to their covered departments

-- Create the healthcare service table
CREATE TABLE IF NOT EXISTS healthcare_services (
    directory_service_id VARCHAR(50) PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    department_code CHAR(2) NOT NULL,
    postal_code CHAR(5),

    FOREIGN KEY (department_code)
        REFERENCES departments(department_code)
);
-- Check healthcare services and department names
SELECT
    h.service_name,
    d.department_name,
    h.postal_code
FROM healthcare_services AS h
JOIN departments AS d
    ON h.department_code = d.department_code
ORDER BY d.department_code;







