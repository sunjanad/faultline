import json

import pandas as pd
import streamlit as st

from faultline_engine import (
    VERSION,
    SUBJECTS,
    run_experiment,
    result_to_dict,
)


st.set_page_config(
    page_title="Faultline",
    page_icon="faultline_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# REPORT HELPERS
# --------------------------------------------------

def get_violation_count(report):
    """Count individual property violations."""
    if "property_violation_records" in report:
        return report["property_violation_records"]

    return sum(report.get("property_counts", {}).values())


def get_failing_case_count(report):
    """Count unique inputs that triggered at least one violation."""
    if "failing_cases" in report:
        return report["failing_cases"]

    failures = report.get("failures", [])
    fingerprints = set()

    for failure in failures:
        original_case = failure.get("original_case")

        if original_case is not None:
            fingerprints.add(
                json.dumps(
                    original_case,
                    sort_keys=True,
                    default=str,
                )
            )

    if fingerprints:
        return len(fingerprints)

    # Older reports may not contain enough information to
    # distinguish failing inputs from individual violations.
    return None


def get_failure_record_count(report):
    """Count recorded property-specific failure explanations."""
    return len(report.get("failures", []))


# --------------------------------------------------
# VISUAL DESIGN
# --------------------------------------------------

st.markdown(
    """
    <style>
    /* Main application backgrounds */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    section[data-testid="stMain"] {
        background-color: #101110 !important;
        color: #eeeeea !important;
    }

    .stApp {
        color: #eeeeea;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #171917 !important;
        border-right: 1px solid #30342d;
    }

    [data-testid="stSidebar"] > div {
        background-color: #171917 !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #eeeeea;
    }

    /* Headings and normal text */
    .stApp h1,
    .stApp h2,
    .stApp h3 {
        color: #f5f5f0 !important;
        letter-spacing: -0.035em;
    }

    .stApp p,
    .stApp li,
    .stApp label,
    .stApp [data-testid="stMarkdownContainer"] {
        color: #eeeeea;
    }

    /* Brand accent */
    .eyebrow {
        color: #b7ff3c !important;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.16em;
    }

    /* Secondary text */
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stCaptionContainer"] p,
    .stApp .stCaption {
        color: #b9beb3 !important;
    }

    /* Content panels */
    .panel {
        background-color: #191c18;
        border: 1px solid #383d34;
        border-radius: 12px;
        padding: 18px;
    }

    /* Dividers */
    .stApp hr {
        border-color: #383d34;
    }

    /* Metrics */
    .stApp [data-testid="stMetric"],
    .stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stMetricValue"],
    .stApp [data-testid="stMetricDelta"] {
        color: #eeeeea !important;
    }

    .stApp [data-testid="stMetricLabel"] *,
    .stApp [data-testid="stMetricValue"] * {
        color: #eeeeea !important;
    }

    /* Text inputs, number inputs, and text areas */
    .stApp input,
    .stApp textarea {
        background-color: #20231f !important;
        color: #f5f5f0 !important;
        -webkit-text-fill-color: #f5f5f0 !important;
        border-color: #596052 !important;
    }

    /* Select boxes */
    .stApp [data-baseweb="select"] > div {
        background-color: #20231f !important;
        border-color: #596052 !important;
        color: #f5f5f0 !important;
    }

    .stApp [data-baseweb="select"] input,
    .stApp [data-baseweb="select"] span,
    .stApp [data-baseweb="select"] div {
        color: #f5f5f0;
    }

    /* Dropdown menu */
    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"],
    [role="option"] {
        background-color: #20231f !important;
        color: #f5f5f0 !important;
    }

    /* Buttons */
    .stApp div.stButton > button[kind="primary"],
    .stApp div.stButton > button[kind="primary"] p,
    .stApp div.stButton > button[kind="primary"] span {
        background-color: #b7ff3c !important;
        color: #101110 !important;
        -webkit-text-fill-color: #101110 !important;
        border: 1px solid #b7ff3c !important;
        font-weight: 700;
    }

    .stApp div.stButton > button[kind="secondary"],
    .stApp div.stDownloadButton > button {
        background-color: #252923 !important;
        color: #f5f5f0 !important;
        border: 1px solid #596052 !important;
    }

    .stApp div.stButton > button:hover,
    .stApp div.stDownloadButton > button:hover {
        border-color: #b7ff3c !important;
    }

    /* Alerts and informational messages */
    .stApp [data-testid="stAlert"] {
        background-color: #20231f !important;
        border: 1px solid #41483a;
    }

    .stApp [data-testid="stAlert"] p,
    .stApp [data-testid="stAlert"] span {
        color: #eeeeea !important;
    }

    /* Tables and charts */
    .stApp [data-testid="stDataFrame"],
    .stApp [data-testid="stTable"] {
        background-color: #191c18 !important;
        color: #eeeeea !important;
    }

    /* Expanders */
    .stApp [data-testid="stExpander"] {
        background-color: #191c18 !important;
        border: 1px solid #383d34;
    }

    .stApp [data-testid="stExpander"] summary,
    .stApp [data-testid="stExpander"] summary p {
        color: #eeeeea !important;
    }

    /* JSON and code blocks */
    .stApp pre,
    .stApp code {
        background-color: #191c18 !important;
        color: #d9f7a2 !important;
    }

    /* Checkbox labels */
    .stApp [data-testid="stCheckbox"] label {
        color: #eeeeea !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "experiment_history" not in st.session_state:
    st.session_state.experiment_history = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        '<p class="eyebrow">FAULTLINE / LAB</p>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Experiment Lab",
            "Failure Explorer",
            "Evaluation",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(f"ENGINE VERSION {VERSION}")
    st.caption("Automated counterexample discovery")


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if page == "Overview":
    st.image("faultline_logo.png", width=200)
    st.markdown(
        '<p class="eyebrow">SOFTWARE RELIABILITY LAB</p>',
        unsafe_allow_html=True,
    )

    st.title("Find the issue.")

    st.write(
        "Faultline searches for inputs that violate a program's "
        "expected behavior, then attempts to simplify those inputs "
        "into understandable counterexamples."
    )

    left, right = st.columns([1.3, 1])

    with left:
        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True,
        )
        st.subheader("The problem")
        st.write(
            "A program can pass ordinary examples and still fail "
            "on an unusual input. Faultline tests stated behavioral "
            "properties across generated cases."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True,
        )
        st.subheader("How it works")
        st.write("01  Generate test cases")
        st.write("02  Check behavioral properties")
        st.write("03  Minimize failing inputs")
        st.write("04  Inspect reproducible results")
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Available test subjects")

    for name, subject in SUBJECTS.items():
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.write(subject["description"])

    st.caption(
        "The current subjects are controlled examples containing "
        "deliberate defects. Faultline is not yet a general-purpose "
        "scanner for arbitrary code."
    )


# --------------------------------------------------
# EXPERIMENT LAB
# --------------------------------------------------

elif page == "Experiment Lab":
    st.markdown(
        '<p class="eyebrow">01 / EXPERIMENT</p>',
        unsafe_allow_html=True,
    )

    st.title("Experiment Lab")
    st.write(
        "Configure and run a reproducible testing experiment."
    )

    subject_name = st.selectbox(
        "System under test",
        list(SUBJECTS.keys()),
    )

    st.info(SUBJECTS[subject_name]["description"])

    col1, col2 = st.columns(2)

    with col1:
        test_count = st.slider(
            "Random test budget",
            min_value=50,
            max_value=2000,
            value=300,
            step=50,
        )

    with col2:
        seed = st.number_input(
            "Random seed",
            min_value=0,
            max_value=2147483647,
            value=42,
            step=1,
        )

    if st.button("Run experiment", type="primary"):
        with st.spinner(
            "Generating cases and checking properties..."
        ):
            try:
                result = run_experiment(
                    subject_name=subject_name,
                    number_of_tests=test_count,
                    seed=int(seed),
                )

                report = result_to_dict(result)
                st.session_state.latest_result = report
                st.session_state.experiment_history.append(report)

                st.success("Experiment completed.")

            except Exception as exc:
                st.error(
                    f"Experiment failed: {type(exc).__name__}: {exc}"
                )

    report = st.session_state.latest_result

    if report and report["subject"] == subject_name:
        st.divider()
        st.subheader("Latest experiment")

        failing_cases = get_failing_case_count(report)
        violation_count = get_violation_count(report)
        failure_records = get_failure_record_count(report)

        m1, m2, m3, m4, m5 = st.columns(5)

        m1.metric(
            "Unique cases",
            report["unique_cases_checked"],
        )

        m2.metric(
            "Passing cases",
            report["passing_cases"],
        )

        m3.metric(
            "Failing cases",
            failing_cases if failing_cases is not None else "N/A",
        )

        m4.metric(
            "Property violations",
            violation_count,
        )

        m5.metric(
            "Runtime",
            f'{report["elapsed_seconds"]:.3f}s',
        )

        st.caption(
            f'Seed: {report["seed"]} · '
            f'Requested random tests: {report["requested_tests"]} · '
            f'Failure explanation records: {failure_records}'
        )

        if report["property_counts"]:
            st.subheader("Violations by property")

            counts = pd.DataFrame(
                [
                    {"Property": key, "Violations": value}
                    for key, value in report["property_counts"].items()
                ]
            )

            st.bar_chart(counts.set_index("Property"))

        st.download_button(
            "Download JSON report",
            data=json.dumps(report, indent=2),
            file_name=(
                f'faultline_'
                f'{subject_name.lower().replace(" ", "_")}.json'
            ),
            mime="application/json",
        )


# --------------------------------------------------
# FAILURE EXPLORER
# --------------------------------------------------

elif page == "Failure Explorer":
    st.markdown(
        '<p class="eyebrow">02 / INSPECTION</p>',
        unsafe_allow_html=True,
    )

    st.title("Failure Explorer")

    report = st.session_state.latest_result

    if not report:
        st.info("Run an experiment first.")

    elif not report["failures"]:
        st.success(
            "No property violations were found in this experiment."
        )

    else:
        failures = report["failures"]

        labels = [
            f'{i + 1}. {failure["property"]}'
            for i, failure in enumerate(failures)
        ]

        selected_index = st.selectbox(
            "Select a failure record",
            range(len(failures)),
            format_func=lambda i: labels[i],
        )

        failure = failures[selected_index]

        st.error(failure["explanation"])
        st.caption(f'Property: {failure["property"]}')

        left, right = st.columns(2)

        with left:
            st.subheader("Original input")
            st.json(failure["original_case"])
            st.caption(
                f'Complexity score: '
                f'{failure["original_complexity"]}'
            )

        with right:
            st.subheader("Minimized input")
            st.json(failure["minimized_case"])
            st.caption(
                f'Complexity score: '
                f'{failure["minimized_complexity"]}'
            )

        reduction = (
            failure["original_complexity"]
            - failure["minimized_complexity"]
        )

        st.metric(
            "Complexity reduction",
            f"{reduction:.2f}",
        )

        st.caption(
            f'Shrinker attempts: {failure["shrink_attempts"]}. '
            "The complexity score is a heuristic, not a measure "
            "of human comprehension."
        )

        with st.expander("Full experiment report"):
            st.json(report)


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

elif page == "Evaluation":
    st.markdown(
        '<p class="eyebrow">03 / EVALUATION</p>',
        unsafe_allow_html=True,
    )

    st.title("Evaluation")

    st.write(
        "Review experiments run during this browser session. "
        "Use consistent budgets and multiple seeds when comparing "
        "testing strategies."
    )

    history = st.session_state.experiment_history

    if not history:
        st.info("No experiments recorded in this session yet.")

    else:
        rows = []

        for report in history:
            failing_cases = get_failing_case_count(report)

            rows.append(
                {
                    "Subject": report["subject"],
                    "Seed": report["seed"],
                    "Requested tests": report["requested_tests"],
                    "Unique cases": report["unique_cases_checked"],
                    "Passing cases": report["passing_cases"],
                    "Failing cases": (
                        failing_cases
                        if failing_cases is not None
                        else "N/A"
                    ),
                    "Property violations": get_violation_count(report),
                    "Runtime (s)": report["elapsed_seconds"],
                }
            )

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download session history",
            data=json.dumps(history, indent=2),
            file_name="faultline_experiment_history.json",
            mime="application/json",
        )

    st.warning(
        "This page currently records experiment summaries. "
        "A controlled comparison of random-only versus "
        "boundary-aware testing is a future evaluation feature."
    )
