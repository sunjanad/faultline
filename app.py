
import json
import streamlit as st
import pandas as pd

from faultline_engine import (
    VERSION,
    SUBJECTS,
    run_experiment,
    result_to_dict,
)

st.set_page_config(
    page_title="Faultline",
    page_icon="⌁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>

<style>
.stApp {
    background-color: #101110;
    color: #f5f5f0;
}

[data-testid="stSidebar"] {
    background-color: #191c18;
    border-right: 1px solid #41463d;
}

.stApp, .stApp p, .stApp li,
.stApp label, .stApp .stMarkdown,
.stApp [data-testid="stCaptionContainer"] {
    color: #f0f1eb;
}

.stApp h1, .stApp h2, .stApp h3 {
    color: #ffffff;
    letter-spacing: -0.03em;
}

.stApp .eyebrow {
    color: #c8ff63;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.16em;
}

.stApp .muted {
    color: #c2c7bd;
}

.stApp [data-testid="stCaptionContainer"] p,
.stApp .stCaption {
    color: #c2c7bd;
}

.stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stMetricDelta"] {
    color: #f5f5f0;
}

.stApp [data-testid="stAlert"] {
    background-color: #20251d;
    border: 1px solid #59634b;
}

.stApp [data-testid="stAlert"] p {
    color: #f5f5f0;
}

.stApp input, .stApp textarea {
    background-color: #20231f;
    color: #ffffff;
    border-color: #697061;
}

.stApp [data-baseweb="select"] > div {
    background-color: #20231f;
    color: #ffffff;
    border-color: #697061;
}

.stApp [data-baseweb="select"] * {
    color: #ffffff;
}

.stApp div.stButton > button[kind="primary"] {
    background-color: #c8ff63;
    color: #101110;
    border: 1px solid #c8ff63;
    font-weight: 700;
}

.stApp div.stButton > button[kind="secondary"],
.stApp div.stDownloadButton > button {
    background-color: #252923;
    color: #ffffff;
    border: 1px solid #737b6a;
}

.stApp div.stButton > button:hover,
.stApp div.stDownloadButton > button:hover {
    border-color: #c8ff63;
    color: #c8ff63;
}

.stApp [data-testid="stDataFrame"] {
    border: 1px solid #41463d;
}
</style>

</style>
""", unsafe_allow_html=True)

if "experiment_history" not in st.session_state:
    st.session_state.experiment_history = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

with st.sidebar:
    st.markdown('<p class="eyebrow">FAULTLINE / LAB</p>',
                unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Overview", "Experiment Lab", "Failure Explorer", "Evaluation"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(f"ENGINE VERSION {VERSION}")
    st.caption("Automated counterexample discovery")

if page == "Overview":
    st.markdown('<p class="eyebrow">SOFTWARE RELIABILITY LAB</p>',
                unsafe_allow_html=True)
    st.title("Find the failure.")
    st.write(
        "Faultline searches for inputs that violate a program's "
        "expected behavior, then attempts to simplify those inputs "
        "into understandable counterexamples."
    )

    left, right = st.columns([1.3, 1])

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("The problem")
        st.write(
            "A program can pass ordinary examples and still fail "
            "on an unusual input. Faultline tests stated behavioral "
            "properties across generated cases."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
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

elif page == "Experiment Lab":
    st.markdown('<p class="eyebrow">01 / EXPERIMENT</p>',
                unsafe_allow_html=True)
    st.title("Experiment Lab")
    st.write("Configure and run a reproducible testing experiment.")

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
        with st.spinner("Generating cases and checking properties..."):
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
                st.error(f"Experiment failed: {type(exc).__name__}: {exc}")

    report = st.session_state.latest_result

    if report and report["subject"] == subject_name:
        st.divider()
        st.subheader("Latest experiment")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Unique cases checked", report["unique_cases_checked"])
        m2.metric("Passing cases", report["passing_cases"])
        m3.metric("Failure records", len(report["failures"]))
        m4.metric("Runtime", f'{report["elapsed_seconds"]:.3f}s')

        st.caption(
            f'Seed: {report["seed"]} · '
            f'Requested random tests: {report["requested_tests"]}'
        )

        if report["property_counts"]:
            st.subheader("Violations by property")
            counts = pd.DataFrame([
                {"Property": key, "Violations": value}
                for key, value in report["property_counts"].items()
            ])
            st.bar_chart(counts.set_index("Property"))

        st.download_button(
            "Download JSON report",
            data=json.dumps(report, indent=2),
            file_name=f'faultline_{subject_name.lower().replace(" ", "_")}.json',
            mime="application/json",
        )

elif page == "Failure Explorer":
    st.markdown('<p class="eyebrow">02 / INSPECTION</p>',
                unsafe_allow_html=True)
    st.title("Failure Explorer")

    report = st.session_state.latest_result

    if not report:
        st.info("Run an experiment first.")
    elif not report["failures"]:
        st.success("No property violations were found in this experiment.")
    else:
        failures = report["failures"]
        labels = [
            f'{i + 1}. {f["property"]} · {i + 1}'
            for i, f in enumerate(failures)
        ]

        selected_index = st.selectbox(
            "Select a failure",
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
                f'Complexity score: {failure["original_complexity"]}'
            )

        with right:
            st.subheader("Minimized input")
            st.json(failure["minimized_case"])
            st.caption(
                f'Complexity score: {failure["minimized_complexity"]}'
            )

        reduction = (
            failure["original_complexity"]
            - failure["minimized_complexity"]
        )
        st.metric("Complexity reduction", f"{reduction:.2f}")
        st.caption(
            f'Shrinker attempts: {failure["shrink_attempts"]}. '
            "The complexity score is a heuristic, not a measure "
            "of human comprehension."
        )

        with st.expander("Full experiment report"):
            st.json(report)

elif page == "Evaluation":
    st.markdown('<p class="eyebrow">03 / EVALUATION</p>',
                unsafe_allow_html=True)
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
            rows.append({
                "Subject": report["subject"],
                "Seed": report["seed"],
                "Requested tests": report["requested_tests"],
                "Unique cases": report["unique_cases_checked"],
                "Passing cases": report["passing_cases"],
                "Failure records": len(report["failures"]),
                "Runtime (s)": report["elapsed_seconds"],
            })

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
