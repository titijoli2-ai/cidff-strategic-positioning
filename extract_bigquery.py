import csv
from google.cloud import bigquery

# Connect to the Google Cloud project
client = bigquery.Client(project="cidff-data-analysis")

# Get annual record counts and payment totals
query = """
SELECT
    year,
    COUNT(*) AS record_count,
    SUM(amount) AS total_amount
FROM `cidff-data-analysis.cidff_analysis.state_funding`
GROUP BY year
ORDER BY year
"""

results = client.query(query, location="EU").result()

# Save the query results as a CSV file
with open("bigquery_annual_funding.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["year", "record_count", "total_amount"])

    for row in results:
        writer.writerow([row.year, row.record_count, row.total_amount])

print("Saved: bigquery_annual_funding.csv")
