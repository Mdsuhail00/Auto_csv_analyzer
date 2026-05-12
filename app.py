import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Auto CSV Analyzer",
    page_icon="📊",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ff4b4b;
    }
    .sub-title {
        font-size: 1rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# ── Title ────────────────────────────────────────────────────────
st.markdown('<p class="main-title">📊 Auto CSV Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload any CSV file and get instant analysis, charts and insights!</p>', unsafe_allow_html=True)
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4248/4248443.png", width=100)
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("Configure your analysis below")

# ── File Uploader ────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload your CSV file here",
    type=["csv"],
    help="Only CSV files are supported"
)

# ── Process uploaded file ────────────────────────────────────────
if uploaded_file is not None:

    # Load the file
    df = pd.read_csv(uploaded_file)

    st.success(f"✅ File uploaded successfully! Found {df.shape[0]} rows and {df.shape[1]} columns.")
    st.divider()

    # ── Auto Detect Column Types ─────────────────────────────────
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = [col for col in df.columns if 'date' in col.lower()]

    # ── Sidebar Options ──────────────────────────────────────────
    st.sidebar.divider()
    st.sidebar.subheader("📊 Chart Options")

    show_histograms = st.sidebar.checkbox("Show Histograms", value=True)
    show_bar_charts = st.sidebar.checkbox("Show Bar Charts", value=True)
    show_trend = st.sidebar.checkbox("Show Trend Line", value=True)
    show_correlation = st.sidebar.checkbox("Show Correlation Heatmap", value=True)

    st.sidebar.divider()
    st.sidebar.subheader("🔢 Select Columns to Analyze")

    selected_numeric = st.sidebar.multiselect(
        "Numeric Columns",
        options=numeric_cols,
        default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols
    )

    selected_text = st.sidebar.multiselect(
        "Text Columns",
        options=text_cols,
        default=text_cols[:2] if len(text_cols) >= 2 else text_cols
    )

    # ── Dataset Overview ─────────────────────────────────────────
    st.subheader("📋 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())
    with col4:
        st.metric("Duplicate Rows", df.duplicated().sum())

    st.divider()

    # ── Auto Insights ────────────────────────────────────────────
    st.subheader("💡 Auto Insights")

    st.markdown(f"""
    - 📊 This dataset has **{df.shape[1]} columns** — **{len(numeric_cols)} are numbers** and **{len(text_cols)} are text**
    - 🔢 Numeric columns: **{', '.join(numeric_cols) if numeric_cols else 'None'}**
    - 📝 Text columns: **{', '.join(text_cols) if text_cols else 'None'}**
    - 📅 Date columns detected: **{', '.join(date_cols) if date_cols else 'None'}**
    - ⚠️ Column with most missing values: **{df.isnull().sum().idxmax()}** ({df.isnull().sum().max()} missing)
    - 🔁 Duplicate rows found: **{df.duplicated().sum()}**
    """)

    st.divider()

    # ── Numeric Statistics ───────────────────────────────────────
    if selected_numeric:
        st.subheader("🔢 Numeric Column Statistics")
        stats = df[selected_numeric].describe().T
        stats['missing'] = df[selected_numeric].isnull().sum()
        stats = stats[['count', 'mean', 'min', 'max', 'std', 'missing']]
        stats.columns = ['Count', 'Mean', 'Min', 'Max', 'Std Dev', 'Missing']
        stats = stats.round(2)
        st.dataframe(stats, use_container_width=True)
        st.divider()

    # ── Text Column Statistics ───────────────────────────────────
    if selected_text:
        st.subheader("📝 Text Column Statistics")
        text_stats = pd.DataFrame({
            "Column": selected_text,
            "Unique Values": [df[col].nunique() for col in selected_text],
            "Most Common": [df[col].mode()[0] if not df[col].mode().empty else "N/A" for col in selected_text],
            "Missing": [df[col].isnull().sum() for col in selected_text]
        })
        st.dataframe(text_stats, use_container_width=True)
        st.divider()

    # ── Auto Charts ──────────────────────────────────────────────
    st.subheader("📊 Auto Generated Charts")

    # Histograms
    if show_histograms and selected_numeric:
        st.markdown("#### 🔢 Numeric Column Distributions")
        for col in selected_numeric:
            fig = px.histogram(
                df, x=col,
                title=f'Distribution of {col}',
                color_discrete_sequence=['#ff4b4b']
            )
            st.plotly_chart(fig, use_container_width=True)
        st.divider()

    # Bar Charts
    if show_bar_charts and selected_text:
        st.markdown("#### 📝 Top Values in Text Columns")
        for col in selected_text:
            top_values = df[col].value_counts().head(10).reset_index()
            top_values.columns = [col, 'Count']
            fig = px.bar(
                top_values, x=col, y='Count',
                title=f'Top 10 values in {col}',
                color='Count',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        st.divider()

    # Trend Line
    if show_trend and date_cols:
        st.markdown("#### 📅 Trend Over Time")
        for date_col in date_cols:
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                if selected_numeric:
                    trend = df.groupby(date_col)[selected_numeric[0]].sum().reset_index()
                    fig = px.line(
                        trend, x=date_col, y=selected_numeric[0],
                        title=f'{selected_numeric[0]} trend over time'
                    )
                    fig.update_traces(line_color='#ff4b4b')
                    st.plotly_chart(fig, use_container_width=True)
            except:
                pass
        st.divider()

    # Correlation Heatmap
    if show_correlation and len(selected_numeric) >= 2:
        st.markdown("#### 🔥 Correlation Heatmap")
        corr = df[selected_numeric].corr().round(2)
        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale='RdBu',
            title='Correlation between Numeric Columns'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.divider()

    # Sales Detection
    sales_keywords = ['sales', 'revenue', 'profit', 'amount', 'price', 'cost', 'total']
    sales_cols = [col for col in numeric_cols if any(
        keyword in col.lower() for keyword in sales_keywords
    )]

    if sales_cols:
        st.markdown("#### 💰 Sales Analysis")
        st.success(f"💰 Sales columns detected: {', '.join(sales_cols)}")
        for col in sales_cols:
            if selected_text:
                sales_by_cat = (
                    df.groupby(selected_text[0])[col]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
                )
                fig = px.bar(
                    sales_by_cat,
                    x=selected_text[0], y=col,
                    title=f'{col} by {selected_text[0]}',
                    color=col,
                    color_continuous_scale='Greens'
                )
                st.plotly_chart(fig, use_container_width=True)
        st.divider()

    # ── Data Preview ─────────────────────────────────────────────
    st.subheader("👀 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    st.divider()

    # ── Download Report ───────────────────────────────────────────
    st.subheader("📥 Download Report")
    report = df.describe().T
    report['missing'] = df.isnull().sum()
    report = report.round(2)
    csv = report.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Download Statistics Report as CSV",
        data=csv,
        file_name="analysis_report.csv",
        mime="text/csv"
    )

else:
    st.info("👆 Please upload a CSV file to get started!")
    st.markdown("""
    ### What this app will do:
    - 📊 **Auto generate charts** based on your data
    - 📋 **Show statistics** for every column
    - 🔍 **Detect data types** automatically
    - 💰 **Sales analysis** if your data has sales columns
    - 📥 **Download report** as CSV
    """)