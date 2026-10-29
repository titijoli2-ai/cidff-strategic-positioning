from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="CIDFF — Strategic Positioning",
    layout="wide"
)

# Locate data relative to this application
project_folder = Path(__file__).resolve().parent
data_folder = project_folder / "data" / "processed"

department_names = {
    "38": "Isère",
    "69": "Rhône",
    "73": "Savoie",
    "74": "Haute-Savoie"
}


@st.cache_data
def load_associations():
    data = pd.read_csv(
        data_folder / "territorial_associations.csv",
        dtype="string"
    )

    # Convert the exported topic flags to booleans
    for column in ["VSS_VIF", "WOMEN_EQUALITY"]:
        data[column] = (
            data[column].str.lower().eq("true").fillna(False)
        )

    return data


st.title("CIDFF Rhône–Arc Alpin")
st.subheader("Data to support strategic positioning")

section = st.sidebar.radio(
    "Explore the project",
    [
        "Overview",
        "Territorial associations",
        "Social issues",
        "State funding",
        "Machine learning"
    ]
)

st.header(section)


if section == "Overview":
    st.write(
        "This project explores territorial associations, recorded "
        "violence indicators and state funding across four departments."
    )

    st.write(
        "**Territories:** Isère, Rhône, Savoie and Haute-Savoie."
    )

    st.info(
        "Sources cover different periods and populations. "
        "They do not measure all needs or all association resources."
    )


elif section == "Territorial associations":
    associations = load_associations()

    st.write(
        "Which associations appear in our RNA selection, "
        "and what missions do they declare?"
    )

    selected_departments = st.multiselect(
        "Departments",
        options=list(department_names),
        default=list(department_names),
        format_func=lambda code: f"{code} — {department_names[code]}"
    )

    topic = st.selectbox(
        "Topic",
        [
            "All selected associations",
            "VSS / VIF",
            "Women / equality"
        ]
    )

    filtered = associations[
        associations["department"].isin(selected_departments)
    ].copy()

    if topic == "VSS / VIF":
        filtered = filtered[filtered["VSS_VIF"]]

    elif topic == "Women / equality":
        filtered = filtered[filtered["WOMEN_EQUALITY"]]

    st.metric(
        "Associations in the current selection",
        len(filtered)
    )

    if filtered.empty:
        st.info("No associations match these filters.")

    else:
        counts = (
            filtered.groupby("department")
            .size()
            .reindex(selected_departments, fill_value=0)
            .rename(index=department_names)
            .rename("Association count")
        )

        st.subheader("Recorded location by department")
        st.bar_chart(counts)

        st.subheader("Explore the associations")

        display_data = filtered[
            ["titre", "adrs_libcommune", "objet", "siteweb"]
        ].rename(columns={
            "titre": "Association",
            "adrs_libcommune": "Municipality",
            "objet": "Declared purpose",
            "siteweb": "Website"
        })

        st.dataframe(display_data, hide_index=True)

    st.caption(
        "Source: RNA selection prepared in notebook 1. "
        "Topic flags use keywords and may overlap. "
        "Declared missions and registered locations do not measure "
        "actual activity, service capacity or all territories served."
    )


elif section == "Social issues":
    violence = pd.read_csv(
        data_folder / "department_violence.csv",
        dtype={"department_code": "string"}
    )

    st.write(
        "How have recorded violence indicators changed "
        "across the four departments?"
    )

    violence_type = st.selectbox(
        "Recorded violence category",
        sorted(violence["violence_type"].unique())
    )

    selected_departments = st.multiselect(
        "Departments",
        options=list(department_names),
        default=list(department_names),
        format_func=lambda code: f"{code} — {department_names[code]}"
    )

    measure = st.selectbox(
        "Measure",
        ["Rate per 1,000 inhabitants", "Recorded victims"]
    )

    measure_column = (
        "rate_per_1000"
        if measure == "Rate per 1,000 inhabitants"
        else "recorded_victims"
    )

    filtered = violence[
        (violence["violence_type"] == violence_type)
        & violence["department_code"].isin(selected_departments)
    ].copy()

    if filtered.empty:
        st.info("Select at least one department.")

    else:
        chart_data = filtered.pivot(
            index="year",
            columns="department_code",
            values=measure_column
        ).sort_index()

        chart_data = chart_data.rename(columns=department_names)

        # Display years as labels without thousands separators
        chart_data.index = chart_data.index.astype(str)

        st.subheader(measure)
        st.line_chart(chart_data)

        with st.expander("View the recorded data"):
            st.dataframe(
                filtered[
                    [
                        "year",
                        "department",
                        "recorded_victims",
                        "rate_per_1000"
                    ]
                ].sort_values(["year", "department"]),
                hide_index=True
            )

    st.caption(
        "Source: SSMSI departmental data prepared in notebook 2. "
        "Recorded victims do not represent all victims. "
        "Changes can reflect reporting and recording practices "
        "as well as changes in violence. "
        "Sexual violence is not restricted to intrafamily situations."
    )


elif section == "State funding":
    funding = pd.read_csv(
        data_folder / "state_funding_2020_2024.csv",
        dtype={
            "department_code": "string",
            "budget_program": "string",
            "siren": "string"
        }
    )

    st.write(
        "How have recorded state payments changed, "
        "and what share went to CIDFF Rhône–Arc Alpin?"
    )

    selected_departments = st.multiselect(
        "Beneficiary location",
        options=list(department_names),
        default=list(department_names),
        format_func=lambda code: f"{code} — {department_names[code]}"
    )

    programs = sorted(
        funding["budget_program"].dropna().unique().tolist()
    )

    program_options = ["All programs"] + programs

    selected_program = st.selectbox(
        "Budget program",
        options=program_options,
        index=program_options.index("137"),
        format_func=lambda code: (
            "137 — Gender equality"
            if code == "137" else code
        )
    )

    filtered = funding[
        funding["department_code"].isin(selected_departments)
    ].copy()

    if selected_program != "All programs":
        filtered = filtered[
            filtered["budget_program"] == selected_program
        ]

    if filtered.empty:
        st.info("No recorded payments match these filters.")

    else:
        comparison = (
            filtered.groupby("year")["amount"]
            .sum()
            .to_frame("Territorial payments")
        )

        cidff_amounts = (
            filtered[
                filtered["siren"] == "305933517"
            ].groupby("year")["amount"].sum()
        )

        comparison["CIDFF payments"] = (
            cidff_amounts.reindex(comparison.index).fillna(0)
        )

        comparison["CIDFF share (%)"] = (
            comparison["CIDFF payments"]
            / comparison["Territorial payments"].where(
                comparison["Territorial payments"] != 0
            )
            * 100
        )

        st.subheader("Recorded payments by year (€)")

        # Display years as labels rather than formatted numbers
        payment_chart = comparison[
            ["Territorial payments", "CIDFF payments"]
        ].copy()

        payment_chart.index = payment_chart.index.astype(str)

        st.line_chart(payment_chart)

        st.subheader("CIDFF share of the selected payments")
        st.dataframe(comparison.round(2))

    st.caption(
        "Source: state association funding annexes, 2020–2024. "
        "Amounts are in nominal euros. "
        "These records include different payment categories, "
        "not only subsidies, and do not cover all association resources. "
        "Location refers to the beneficiary address, not all areas served."
    )

    st.info(
        "CIDFF Rhône–Arc Alpin is identified by SIREN 305933517 "
        "and recorded in Rhône (69). Excluding Rhône from the filter "
        "also excludes its payments from this comparison."
    )


elif section == "Machine learning":
    comparison = pd.read_csv(
        data_folder / "hce_model_comparison.csv"
    )

    selected = comparison[
        comparison["model"] == "Tuned Random Forest"
    ].iloc[0]

    st.write(
        "Can five sociodemographic characteristics predict agreement "
        "with the statement: "
        "'Feminism threatens men's place and role in society'?"
    )

    st.caption(
        "Source: 2025 HCE survey. The analysis includes 2,779 respondents "
        "who expressed an opinion. The 282 non-response or "
        "'Don't know' answers were excluded."
    )

    st.subheader("Selected model: Tuned Random Forest")

    column1, column2, column3 = st.columns(3)

    column1.metric(
        "Test balanced accuracy",
        f"{selected['test_balanced_accuracy']:.1%}"
    )

    column2.metric(
        "Test ROC AUC",
        f"{selected['test_roc_auc']:.3f}"
    )

    column3.metric("Test respondents", 556)

    st.subheader("Compare the models")

    st.dataframe(
        comparison.rename(columns={
            "model": "Model",
            "test_balanced_accuracy": "Test balanced accuracy",
            "test_roc_auc": "Test ROC AUC"
        }).round(3),
        hide_index=True
    )

    fig, ax = plt.subplots(figsize=(9, 4))

    colors = [
        "#2563eb" if name == "Tuned Random Forest" else "#94a3b8"
        for name in comparison["model"]
    ]

    ax.barh(
        comparison["model"],
        comparison["test_balanced_accuracy"],
        color=colors
    )

    ax.set_xlim(0, 1)
    ax.set_xlabel("Survey-weighted test balanced accuracy")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.2)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.caption(
        "Blue: the model retained for the demonstration. "
        "Grey: the other models and baseline."
    )

    st.subheader("Method")

    st.write(
        "Predictors: declared sex, age, education, employment status "
        "and urban area size. The data were split into 80% training "
        "and 20% test respondents."
    )

    st.write(
        "The analysis compared a majority-class baseline, SGD logistic "
        "regression, Random Forest and XGBoost. Hyperparameter searches "
        "used three-fold cross-validation on the training set. "
        "Preprocessing was fitted within each training fold. "
        "Survey weights were used for training and evaluation."
    )

    st.write(
        "A separate experiment compared sex and age alone with all five "
        "predictors, using logistic regression with fixed settings. "
        "The validation scores were close: 0.585 and 0.577 respectively."
    )

    st.subheader("Why retain Random Forest?")

    st.write(
        "Random Forest achieved the highest test balanced accuracy, "
        "the project's main metric. However, its advantage was small. "
        "XGBoost achieved a higher test ROC AUC and a higher "
        "cross-validation balanced accuracy. There is no clear "
        "overall winner."
    )

    st.subheader("What did we learn?")

    st.warning(
        "Predictive performance remains modest. These results do not "
        "support individual profiling or operational targeting."
    )

    st.write(
        "Group differences can exist without allowing reliable "
        "prediction of individual opinions. These results do not "
        "establish causality or identify which awareness activities "
        "would be effective."
    )

    st.caption(
        "The same test set was used for several evaluations, including "
        "earlier experiments in the draft notebook. These comparisons "
        "are exploratory, rather than a fully independent final "
        "assessment. All displayed scores are survey-weighted."
    )

else:
    st.write("This section is under construction.")