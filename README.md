# CIDFF Rhône–Arc Alpin — Data for Strategic Positioning

Final project for the Ironhack Data Analytics & AI bootcamp.  
Author: Tina — October 2026

## Project overview

This project uses public data to support discussions about the strategic positioning of CIDFF Rhône–Arc Alpin.

It covers four French departments: Isère (38), Rhône (69), Savoie (73) and Haute-Savoie (74).

The analysis explores three questions:

- Which associations could be potential partners?
- What do available indicators tell us about sexism and recorded violence?
- How has recorded state funding changed between 2020 and 2024?

A separate machine learning analysis explores whether five sociodemographic characteristics can predict agreement with the statement: “Feminism threatens men's place and role in society.”

The findings are a starting point for discussion with CIDFF teams. They should be combined with field expertise before making strategic decisions.

## Main findings

- The keyword-based RNA selection identified 522 associations across the four departments. Their registered locations do not measure their service coverage or capacity.
- In 2024, 42% of recorded victims of sexual violence within the family, excluding partners, experienced violence that had started at least five years before its recording.
- Recorded state payments to CIDFF Rhône–Arc Alpin decreased from €895,359 in 2023 to €866,928 in 2024, around 3.2%. These payments do not represent all its resources.
- The classification models showed limited predictive performance. These results do not justify individual profiling or demographic targeting.

## Repository contents

The main notebooks are at the root of the project:

| File | Purpose |
| --- | --- |
| `01_territorial_associations.ipynb` | RNA selection, territorial exploration, web scraping and geographical enrichment |
| `02_emerging_social_issues.ipynb` | Exploration of HCE survey data and SSMSI recorded violence indicators |
| `03_association_funding.ipynb` | Cleaning, harmonisation and analysis of state funding from 2020 to 2024 |
| `04_database_sql.ipynb` | Data import into MySQL, checks, API configuration and API tests |
| `06_hce_classification.ipynb` | Classification, model comparison, feature comparison and model export |

Other files and folders:

- `exploration/`: preliminary notebooks, including ML feasibility and earlier experiments. These document the research process and are not the main execution pipeline.
- `data/raw/`: source files.
- `data/processed/`: cleaned datasets and exported results.
- `models/`: saved classification pipeline.
- `01_create_database.sql`: MySQL database and table creation.
- `02_sql_analysis.sql`: SQL analysis queries.
- `app.py`: Streamlit dashboard.
- `api.py`: local FastAPI application.
- `extract_bigquery.py`: optional BigQuery extraction.
- `openapi.json`: exported API specification.
- `cidff_conceptual_model.png`: conceptual database model.
- `cidff_database_schema.png`: database schema.
- `cidff_database_model.mwb`: MySQL Workbench model.
- `.env.example`: configuration template without credentials.
- `requirements.txt`: Python dependencies.

## Data sources

The project uses:

- Répertoire national des associations (RNA): declared association information.
- SSMSI: recorded violence indicators and complementary tables on intrafamily violence.
- HCE: 2025 sexism survey data.
- State funding open data for associations, covering 2020–2024.
- The official violence support directory and public address services for additional information.

Source references and processing details are documented in the notebooks.

The HCE source CSV is expected at the project root:

`base-de-donnees-toluna-harris-barometre-sexisme-vague-5-2025-dgcs-hce-.csv`

The large RNA archive is excluded from Git. To rerun notebook 01, obtain the RNA WALDEC snapshot dated 1 October 2026 from the official RNA data source and place it here:

`data/raw/rna_waldec_20261001.zip`

Notebook 01 also expects the corresponding department filenames inside that archive. Another snapshot may require changes to the filenames and may produce different results.

The dashboard uses the processed CSV files and does not require the RNA archive.

## Installation

The main project environment used Python 3.14.3.

From a terminal opened at the project root:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

The listed versions were recorded from the local project environment, except for `google-cloud-bigquery`. A fresh installation has not yet been independently validated.

## Run the dashboard

From the project root:

```bash
python -m streamlit run app.py
```

The dashboard presents territorial associations, recorded violence indicators, state funding and model results.

It reads processed CSV files. It does not connect to MySQL or generate individual predictions.

## Run the notebooks

Launch JupyterLab from the project root:

```bash
python -m jupyterlab
```

Run notebooks 01, 02 and 03 to reproduce the main data preparation and exploratory analysis.

Notebook 04 requires a running MySQL server and additional setup described below.

Notebook 06 uses the HCE source CSV and can be run separately from the territorial analyses.

Keep the folder structure and filenames unchanged, as the notebooks use relative paths.

Notebook 01 makes external web requests. Website changes or unavailable services may affect the results.

## MySQL and local API

MySQL must be installed and running separately.

1. Execute `01_create_database.sql` in MySQL Workbench.
2. Run the import and validation sections of `04_database_sql.ipynb`.
3. Configure a local `.env` file using `.env.example`, or use the notebook's configuration cells.
4. Start the API from a separate terminal at the project root:

```bash
python -m uvicorn api:app --reload
```

5. Keep the server running, then execute the API test cells in notebook 04.
6. Execute `02_sql_analysis.sql` to explore the database.

Interactive API documentation is available locally at:

`http://127.0.0.1:8000/docs`

Protected endpoints require the `X-API-Key` header.

The notebook imports data only into empty tables. Existing tables are not automatically refreshed when CSV files change.

Never publish the local `.env` file, database passwords or API keys.

## Optional BigQuery extraction

`extract_bigquery.py` demonstrates a separate cloud extraction.

It requires Google Cloud authentication and access to:

`cidff-data-analysis.cidff_analysis.state_funding`

The script exports annual funding totals to `bigquery_annual_funding.csv` in the current working directory.

This step is optional and is not needed to launch the dashboard. The BigQuery library was not installed in the notebook environment used to record the other dependency versions.

## Machine learning

The target is agreement or disagreement with the HCE statement about feminism threatening men's place and role in society.

Unknown responses were excluded, leaving 2,779 respondents.

Predictors:

- Sex
- Age
- Education
- Employment status
- Urban area size

The data were split into 80% training and 20% test sets, using `random_state=42`. The test set contains 556 respondents.

The analysis includes a baseline, logistic regression using `SGDClassifier`, Random Forest and XGBoost, with cross-validation, hyperparameter searches and a feature comparison.

Reported test metrics use survey weights.

| Model | Balanced accuracy | ROC AUC |
| --- | ---: | ---: |
| Baseline | 0.500 | 0.500 |
| Logistic regression | 0.579 | 0.570 |
| Tuned Random Forest | 0.585 | 0.575 |
| Random search XGBoost | 0.579 | 0.582 |

The tuned Random Forest was retained for the saved model because it had the highest observed test balanced accuracy, the main evaluation metric.

However, the differences are small and there is no clear overall winner. Repeated comparisons on the same test set limit confidence in model selection. These scores should not be treated as an independent final assessment of generalisation.

The saved pipeline is:

`models/hce_agreement_classifier.joblib`

Loading a saved scikit-learn model requires a compatible environment. The recorded scikit-learn version is 1.9.0.

## Limitations and ethical choices

- Sources cover different periods, populations and geographical levels.
- Registered associations do not necessarily represent active services or available capacity.
- Police-recorded violence does not capture all victims or all incidents.
- Recording dates do not necessarily correspond to first disclosure dates.
- State funding records do not represent all association resources.
- Missing descriptions and unresolved geographical values limit some funding analyses.
- The national HCE survey does not directly describe the local CIDFF service population.
- Limited model performance does not establish causal relationships or prove that demographic differences do not exist.
- No individual profiling or operational targeting is proposed.

The project provides a documented data foundation for further investigation with CIDFF teams.

## Presentation

[View the presentation (PDF)](https://drive.google.com/file/d/1MjeaWOzQ4cSV1DHChS4isbEZPHijfKUU/view?usp=sharing)