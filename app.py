
import streamlit as st

st.set_page_config(
    page_title="Faultline",
    page_icon="⌁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
    background: #101110;
    color: #eeeeea;
}
[data-testid="stSidebar"] {
    background: #171917;
    border-right: 1px solid #30342d;
}
h1, h2, h3 {
    color: #f1f2ec;
    letter-spacing: -0.04em;
}
.accent {
    color: #b7ff3c;
}
.eyebrow {
    color: #b7ff3c;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.16em;
}
.panel {
    background: #191c18;
    border: 1px solid #30342d;
    border-radius: 12px;
    padding: 20px;
}
.muted {
    color: #a5aaa0;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<p class="eyebrow">FAULTLINE / LAB</p>',
                unsafe_allow_html=True)
    page = st.radio(
        "NAVIGATION",
        ["Overview", "Experiment Lab", "Failure Explorer", "Evaluation"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("AUTOMATED COUNTEREXAMPLE DISCOVERY")
    st.caption("Version 0.1.0")

if page == "Overview":
    st.markdown('<p class="eyebrow">SOFTWARE RELIABILITY LAB</p>',
                unsafe_allow_html=True)
    st.title("Find the failure.")
    st.markdown(
        "Faultline searches for inputs that violate a program's "
        "expected behavior, then attempts to simplify those inputs "
        "into understandable counterexamples."
    )
    st.write("")
    left, right = st.columns([1.4, 1])

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("The problem")
        st.write(
            "A program can pass every example its developer thought "
            "to test and still fail on an unusual input."
        )
        st.write(
            "Faultline explores inputs systematically and checks "
            "whether specified properties remain true."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Workflow")
        st.write("01  Generate test cases")
        st.write("02  Check behavioral properties")
        st.write("03  Minimize failing inputs")
        st.write("04  Inspect and reproduce results")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("Open Experiment Lab", type="primary"):
        st.session_state["requested_page"] = "Experiment Lab"
        st.rerun()

elif page == "Experiment Lab":
    st.markdown('<p class="eyebrow">01 / EXPERIMENT</p>',
                unsafe_allow_html=True)
    st.title("Experiment Lab")
    st.info(
        "The interface is ready. The testing engine will be connected "
        "in the next build step."
    )

elif page == "Failure Explorer":
    st.markdown('<p class="eyebrow">02 / INSPECTION</p>',
                unsafe_allow_html=True)
    st.title("Failure Explorer")
    st.info(
        "Counterexample inspection will appear here once the engine "
        "is connected."
    )

elif page == "Evaluation":
    st.markdown('<p class="eyebrow">03 / EVALUATION</p>',
                unsafe_allow_html=True)
    st.title("Evaluation")
    st.info(
        "Comparative testing experiments will appear here after "
        "the testing engine is integrated."
    )
