-- Select the project database
USE cidff_project;

-- Count selected active RNA associations by department
SELECT
    d.department_code,
    d.department_name,
    COUNT(a.rna_id) AS association_count,
    SUM(a.vss_vif) AS vss_vif_count,
    SUM(a.women_equality) AS women_equality_count
FROM departments AS d
LEFT JOIN associations AS a
    ON d.department_code = a.department_code
GROUP BY d.department_code, d.department_name
ORDER BY association_count DESC;

-- Observation: Rhône accounts for 290 of the 522 selected
-- active RNA associations (55.6%).
-- These counts do not measure service capacity or all available services.
-- The two thematic categories overlap.

-- Compare program 137 payments by department and year
SELECT
    d.department_code,
    d.department_name,
    f.year,
    COUNT(*) AS record_count,
    SUM(f.amount) AS total_amount
FROM funding_payments AS f
JOIN departments AS d
    ON f.department_code = d.department_code
WHERE f.budget_program = '137'
GROUP BY d.department_code, d.department_name, f.year
ORDER BY d.department_code, f.year;

-- Observation: recorded program 137 payments in Savoie increased
-- from EUR 119,005 in 2023 to EUR 675,182.42 in 2024.
-- LA SASSON received EUR 579,338 in 2024.
-- The missing 2024 purpose limits interpretation of this increase.
-- Historical context does not confirm the purpose of the 2024 payment.

-- Compare CIDFF payments with territorial program 137 payments
SELECT
    year,
    SUM(amount) AS territorial_amount,
    SUM(
        CASE WHEN siren = '305933517' THEN amount ELSE 0 END
    ) AS cidff_amount,
    ROUND(
        100.0 * SUM(
            CASE WHEN siren = '305933517' THEN amount ELSE 0 END
        ) / NULLIF(SUM(amount), 0),
        2
    ) AS cidff_share_pct
FROM funding_payments
WHERE budget_program = '137'
GROUP BY year
ORDER BY year;

-- Observation: CIDFF program 137 payments decreased by 2.1%
-- between 2023 and 2024.
-- Its share of recorded territorial payments fell
-- from 18.61% to 14.70% (down 3.91 percentage points).
-- These data do not establish a transfer of funding
-- from CIDFF to another beneficiary.

-- Find selected associations with matching funding records
SELECT
    a.rna_id,
    a.association_name,
    a.siret,
    COUNT(f.funding_id) AS funding_record_count,
    SUM(f.amount) AS total_state_payments_2020_2024
FROM associations AS a
JOIN funding_payments AS f
    ON a.siret = f.siret
GROUP BY a.rna_id, a.association_name, a.siret
ORDER BY total_state_payments_2020_2024 DESC;

-- Observation: exact SIRET matching links part of the selected
-- RNA associations to recorded state payments.
-- Coverage is limited: only 23 of the 522 associations have a SIRET.
-- Missing matches do not prove an absence of state funding.
-- Amounts cover 2020-2024, not a single year.

-- Compare minor violence rates with selected VSS/VIF association counts
SELECT
    d.department_name,
    v.period,
    v.violence_type,
    ROUND(v.rate_per_1000_minors, 2) AS rate_per_1000_minors,
    a.vss_vif_association_count
FROM minor_intrafamily_violence AS v
JOIN departments AS d
    ON v.department_code = d.department_code
LEFT JOIN (
    SELECT
        department_code,
        COUNT(*) AS vss_vif_association_count
    FROM associations
    WHERE vss_vif = 1
    GROUP BY department_code
) AS a
    ON v.department_code = a.department_code
ORDER BY v.violence_type, d.department_code;

-- Observation: Isère has the highest recorded rates among
-- the four departments for both violence types in 2022-2024.
-- The 2026 selection includes 45 VSS/VIF associations in Isère,
-- compared with 136 in Rhône.
-- Counts do not measure capacity or specialization in minors.
-- Different periods and incomplete coverage limit interpretation.

-- Inspect how MySQL processes the program 137 query
EXPLAIN
SELECT
    year,
    SUM(amount) AS total_amount
FROM funding_payments
WHERE budget_program = '137'
GROUP BY year;

-- Optimization: MySQL uses idx_funding_program_year.
-- Estimated rows examined decreased from 29,541 to 356.
-- This confirms a more selective access plan.
-- Execution time improvement has not been measured.

