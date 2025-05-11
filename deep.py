import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Load data
@st.cache_data
def load_data():
    #df = pd.read_excel("Merged_Dept_Data.xlsx", sheet_name="Sheet1")
    #df = pd.read_excel("C:\\Users\\abc\\Desktop\\Acadia BI Intern Assessment/Merged_Dept_Data.xlsx")
    df = pd.read_excel("https://github.com/GayasuddinMohd/BI-Intern-/blob/main/Merged_Dept_Data.xlsx")
    #https://github.com/GayasuddinMohd/BI-Intern-/blob/main/Merged_Dept_Data.xlsx
    return df


df = load_data()

# Data preprocessing
df['SalesPerCustomer'] = df['Sales'] / df['Customers']
df['Segment_Profile'] = df['Segment Description'] + " - " + df['Profile Description'].fillna('All Profiles')

# Dashboard layout
st.set_page_config(layout="wide", page_title="Department Sales Dashboard")

# Title
st.title("🚀 Sales Performance Dashboard")
st.markdown("Analyzing sales by department, customer segments, and profiles")

# Sidebar filters
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Year", options=sorted(df['Year'].unique()), index=1)
selected_depts = st.sidebar.multiselect(
    "Departments",
    options=sorted(df['Department Description'].unique()),
    default=sorted(df['Department Description'].unique())
)
selected_segments = st.sidebar.multiselect(
    "Segments",
    options=sorted(df['Segment Description'].unique()),
    default=sorted(df['Segment Description'].unique())
)

# Filter data
filtered_df = df[
    (df['Year'] == selected_year) &
    (df['Department Description'].isin(selected_depts)) &
    (df['Segment Description'].isin(selected_segments))
    ]

# KPI cards
col1, col2, col3, col4 = st.columns(4)
total_sales = filtered_df['Sales'].sum() / 1e6
total_customers = filtered_df['Customers'].sum() / 1000
avg_spend = filtered_df['Sales'].sum() / filtered_df['Customers'].sum()
top_dept = filtered_df.groupby('Department Description')['Sales'].sum().idxmax()

col1.metric("Total Sales", f"${total_sales:.2f}M")
col2.metric("Total Customers", f"{total_customers:.1f}K")
col3.metric("Avg Spend per Customer", f"${avg_spend:.1f}")
col4.metric("Top Department", top_dept)

# Main tabs
tab1, tab2, tab3 = st.tabs(["Department Analysis", "Customer Segments", "Profile Insights"])

with tab1:
    st.header("Department Performance")

    # Sales by department
    fig1 = px.bar(
        filtered_df.groupby(['Department Description', 'Year'])['Sales'].sum().reset_index(),
        x='Department Description',
        y='Sales',
        color='Year',
        barmode='group',
        title="Total Sales by Department"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Growth comparison
    sales_compare = df.pivot_table(
        index='Department Description',
        columns='Year',
        values='Sales',
        aggfunc='sum'
    ).reset_index()
    sales_compare['Growth'] = (sales_compare[2023] - sales_compare[2022]) / sales_compare[2022] * 100

    fig2 = px.bar(
        sales_compare,
        x='Department Description',
        y='Growth',
        title="YoY Sales Growth (%)",
        color='Growth',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Customer Segment Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Segment sales breakdown
        fig3 = px.pie(
            filtered_df.groupby('Segment Description')['Sales'].sum().reset_index(),
            names='Segment Description',
            values='Sales',
            title="Sales by Segment"
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        # Segment performance by department
        fig4 = px.bar(
            filtered_df.groupby(['Department Description', 'Segment Description'])['Sales'].sum().reset_index(),
            x='Department Description',
            y='Sales',
            color='Segment Description',
            title="Segment Performance Across Departments"
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Segment health matrix
    segment_health = filtered_df.groupby('Segment Description').agg({
        'Sales': 'sum',
        'Customers': 'sum',
        'SalesPerCustomer': 'mean'
    }).reset_index()

    fig5 = px.scatter(
        segment_health,
        x='Customers',
        y='SalesPerCustomer',
        size='Sales',
        color='Segment Description',
        hover_name='Segment Description',
        title="Segment Health Matrix (Size = Total Sales)"
    )
    st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.header("Customer Profile Insights")

    # Profile performance
    fig6 = px.treemap(
        filtered_df[filtered_df['Profile Description'].notna()],
        path=['Department Description', 'Profile Description'],
        values='Sales',
        color='SalesPerCustomer',
        title="Sales Distribution by Department and Profile"
    )
    st.plotly_chart(fig6, use_container_width=True)

    # Profile heatmap
    profile_heatmap = filtered_df.pivot_table(
        index='Profile Description',
        columns='Department Description',
        values='SalesPerCustomer',
        aggfunc='mean'
    ).reset_index()

    fig7 = px.imshow(
        profile_heatmap.set_index('Profile Description'),
        labels=dict(x="Department", y="Profile", color="Avg Spend"),
        title="Average Spend by Profile and Department"
    )
    st.plotly_chart(fig7, use_container_width=True)

# Insights section
st.header("🔍 Key Insights")
insights_col1, insights_col2 = st.columns(2)

with insights_col1:
    st.subheader("Top Opportunities")
    st.markdown("""
    - **Upsell to Elite Customers** in Cowboy Hats (High spend potential)
    - **Reactivate Infrequent Customers** in Women's Jeans
    - **Bundle Boots + Boot Accessories** (Frequently bought together)
    """)

with insights_col2:
    st.subheader("Warning Signs")
    st.markdown("""
    - **Declining Core Customers** in Formalwear
    - **Low penetration** of Blue Collar Royalty in Beachwear
    - **New customer retention** needs improvement in Knick Knacks
    """)
