import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
import os

# =========================
# GROQ API
# =========================

client = Groq(
    api_key="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"   
)

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Smart Data Analyst Dashboard",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>

/* Features Heading */
[data-testid="stSidebar"] p {
    font-size:22px !important;
    font-weight:500 !important;
}

    /* Sidebar*/           
[data-testid="stSidebar"]{
    width:240px !important;
}

            
.block-container{
    max-width:1200px;
    margin:auto;
}

/* Menu Text */
[data-testid="stSidebar"] span {
    font-size:12px !important;
    font-weight:500 !important;
}

/* Hover Text */
[data-testid="stSidebar"] span:hover {
    color:#63B3ED !important;
}

</style>
""", unsafe_allow_html=True)
# =========================
# TITLE
# =========================

st.title("🧠 Smart Data Analyst Dashboard")
st.write("Upload your CSV or Excel dataset and generate AI-powered insights.")

# =========================
# SIDEBAR
# =========================

menu = st.sidebar.radio(
    "🚀 FEATURES",
    [
        "📊 Dashboard",
        "📈 Visualization",
        "🧠 AI Insights",
        "🔍 Data Quality",
        "💬 AI Analysis"
    ]
)

# =========================
# FILE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    try:
        # Read dataset
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # =========================
        # DASHBOARD
        # =========================

        if menu == "📊 Dashboard":

            st.success("File Uploaded Successfully!")
            st.subheader("Dataset Preview")
            st.dataframe(df.head())

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Rows", df.shape[0])
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                st.metric("Missing Values", int(df.isnull().sum().sum()))
            with col4:
                st.metric("Duplicate Rows", int(df.duplicated().sum()))

            st.subheader("Column Names")
            st.write(list(df.columns))

            st.subheader("Statistical Summary")
            st.dataframe(df.describe())

        # =========================
        # VISUALIZATION
        # =========================

        elif menu == "📈 Visualization":

            st.subheader("📈 Data Visualization")

            selected_column = st.selectbox("Select Column", df.columns)

            chart_type = st.selectbox(
                "Select Chart Type",
                ["Histogram", "Bar Chart", "Pie Chart"]
            )

            if chart_type == "Histogram":
                fig = px.histogram(df, x=selected_column)

            elif chart_type == "Bar Chart":
                vc = df[selected_column].value_counts().head(20).reset_index()
                vc.columns = [selected_column, "Count"]
                fig = px.bar(vc, x=selected_column, y="Count")

            else:
                vc = df[selected_column].value_counts().head(10).reset_index()
                vc.columns = [selected_column, "Count"]
                fig = px.pie(vc, names=selected_column, values="Count")

            st.plotly_chart(fig, use_container_width=True)
            st.download_button(
            "📥 Download Data",
            df.to_csv(index=False),
            file_name="dataset.csv"
            )

        # =========================
        # AI INSIGHTS
        # =========================

        elif menu == "🧠 AI Insights":

            st.subheader("🧠 AI Generated Insights")

            if st.button("Generate Insights"):

                with st.spinner("Generating Insights..."):

                    prompt = f"""
Analyze this dataset:

Columns: {list(df.columns)}
Rows: {df.shape[0]}
Sample:
{df.head(50).to_string()}

Give:
1. Summary
2. Trends
3. Insights
4. Recommendations
"""

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}]
                    )

                    st.write(response.choices[0].message.content)
                    st.download_button(
                    "📥 Download Insights",
                    response.choices[0].message.content,
                    file_name="ai_insights.txt"
                    )

        # =========================
        # DATA QUALITY
        # =========================

        elif menu == "🔍 Data Quality":

            st.subheader("🔍 Data Quality Report")
            total_cells = df.shape[0] * df.shape[1]
            missing = df.isnull().sum().sum()
            score = round(
                 ((total_cells - missing) / total_cells) * 100,
                  2
                  )
            st.metric(
                "Dataset Health Score",
                f"{score}%"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Missing Values", int(df.isnull().sum().sum()))

            with col2:
                st.metric("Duplicate Rows", int(df.duplicated().sum()))

            missing_df = df.isnull().sum().reset_index()
            missing_df.columns = ["Column", "Missing Values"]
            missing_df = missing_df[missing_df["Missing Values"] > 0]

            st.subheader("Missing Values by Column")

            if len(missing_df) > 0:
                st.dataframe(missing_df)
            else:
                st.success("No Missing Values Found")

            st.subheader("Column Data Types")

            dtype_df = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str)
            })

            st.dataframe(dtype_df)

            if st.button("Fill Missing Values"):

                cleaned_df = df.fillna("N/A")

                st.success("Missing Values Filled Successfully")
                st.subheader("Cleaned Dataset Preview")
                st.dataframe(cleaned_df.head())

                st.download_button(
                    label="📥 Download Cleaned Dataset",
                    data=cleaned_df.to_csv(index=False).encode("utf-8"),
                    file_name="cleaned_dataset.csv",
                    mime="text/csv"
                )
                

        # =========================
        # AI ANALYSIS
        # =========================

        elif menu == "💬 AI Analysis":

            st.subheader("💬 AI Dataset Analysis")

            question = st.text_input("Ask a question about your dataset")

            if st.button("Analyze Data"):

                if question.strip():

                    prompt = f"""
Dataset Columns: {list(df.columns)}
Rows: {df.shape[0]}
Sample:
{df.head(50).to_string()}

Question: {question}
"""

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}]
                    )

                    st.write(response.choices[0].message.content)
                    st.download_button(
                    "📥 Download Analysis",
                    response.choices[0].message.content,
                    file_name="ai_analysis.txt"
)

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload a CSV or Excel file to begin.")