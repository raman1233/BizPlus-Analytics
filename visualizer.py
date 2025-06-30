import streamlit as st
import pandas as pd
import plotly.express as px

def show_visuals(df: pd.DataFrame):
    st.header("📊 Business Performance Dashboard")

    # --- Debugging Column Names ---
    # Convert column names to a list and print for debugging
    st.sidebar.subheader("DEBUG: DataFrame Columns")
    st.sidebar.write(df.columns.tolist())

    # --- Clean Column Names ---
    # Strip whitespace from column names and convert to a consistent case (e.g., Title Case)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.title() # Convert to Title Case for consistency

    st.sidebar.subheader("DEBUG: Cleaned DataFrame Columns")
    st.sidebar.write(df.columns.tolist())

    # Define expected column names after cleaning
    unit_price_col = "Unit Price"
    quantity_col = "Quantity"
    order_date_col = "Order Date"
    product_col = "Product"
    customer_id_col = "Customer Id" # Assuming "Customer ID" becomes "Customer Id" after .title()
    region_col = "Region"

    # --- Calculate Total Revenue ---
    # Ensure 'Unit Price' and 'Quantity' columns exist and are numeric
    if unit_price_col in df.columns and quantity_col in df.columns:
        try:
            # Clean numeric columns: remove non-numeric characters (like currency symbols)
            # and then convert to numeric.
            # This regex removes anything that is not a digit or a decimal point.
            df[unit_price_col] = df[unit_price_col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df[quantity_col] = df[quantity_col].astype(str).str.replace(r'[^\d.]', '', regex=True)

            df[unit_price_col] = pd.to_numeric(df[unit_price_col], errors='coerce')
            df[quantity_col] = pd.to_numeric(df[quantity_col], errors='coerce')

            # Drop rows where conversion to numeric failed for these columns
            initial_rows = len(df)
            df.dropna(subset=[unit_price_col, quantity_col], inplace=True)
            if len(df) < initial_rows:
                st.warning(f"Removed {initial_rows - len(df)} rows due to non-numeric 'Unit Price' or 'Quantity' values.")

            df["Total Revenue"] = df[unit_price_col] * df[quantity_col]
            st.success("✅ 'Total Revenue' calculated successfully!")
        except Exception as e:
            st.error(f"Error calculating 'Total Revenue'. Please ensure '{unit_price_col}' and '{quantity_col}' columns contain valid numbers: {e}")
            return # Stop execution if calculation fails
    else:
        st.error(f"Missing '{unit_price_col}' or '{quantity_col}' column in the uploaded CSV. Cannot calculate 'Total Revenue'.")
        return # Stop execution if essential columns are missing

    # Clean and process 'Order Date'
    if order_date_col in df.columns:
        df[order_date_col] = pd.to_datetime(df[order_date_col], errors="coerce")
        df.dropna(subset=[order_date_col], inplace=True) # Drop rows where date conversion failed
        df["Month"] = df[order_date_col].dt.to_period("M").astype(str)
    else:
        st.warning(f"'{order_date_col}' column not found. Monthly Revenue Trend might be affected.")
        # Create a dummy 'Month' if not present to avoid errors in groupby
        df["Month"] = "Unknown"


    # ==== 1. Revenue Trend ====
    st.subheader("📈 Monthly Revenue Trend")
    if "Total Revenue" in df.columns and "Month" in df.columns:
        monthly = df.groupby("Month")["Total Revenue"].sum().reset_index()
        fig_line = px.line(monthly, x="Month", y="Total Revenue",
                           markers=True, template="plotly_white",
                           labels={"Total Revenue": "Revenue (₹)"})
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Cannot generate Monthly Revenue Trend. 'Total Revenue' or 'Month' column missing.")

    # ==== 2. Top Products ====
    st.subheader("🏆 Top 5 Products by Revenue")
    if product_col in df.columns and "Total Revenue" in df.columns:
        top_products = df.groupby(product_col)["Total Revenue"].sum().sort_values(ascending=False).head(5).reset_index()
        fig_bar = px.bar(top_products, x=product_col, y="Total Revenue",
                         color="Total Revenue", text_auto=True, template="plotly_white")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info(f"Cannot generate Top Products. '{product_col}' or 'Total Revenue' column missing.")

    # ==== 3. Region-wise Revenue ====
    st.subheader("📍 Revenue by Region")
    if region_col in df.columns and "Total Revenue" in df.columns:
        region_rev = df.groupby(region_col)["Total Revenue"].sum().reset_index()
        fig_region = px.pie(region_rev, names=region_col, values="Total Revenue",
                             template="plotly_white", title="Revenue Contribution by Region")
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info(f"'{region_col}' column not found in your data or 'Total Revenue' is missing. Skipping Region-wise Revenue visualization.")


    # ==== 4. New vs Repeat Customers ====
    st.subheader("👥 Customer Type Breakdown")
    if customer_id_col in df.columns:
        customer_counts = df[customer_id_col].value_counts()
        new_customers = (customer_counts == 1).sum()
        repeat_customers = (customer_counts > 1).sum()
        fig_customers = px.pie(names=["New", "Repeat"], values=[new_customers, repeat_customers],
                                template="plotly_white", title="New vs Repeat Customers")
        st.plotly_chart(fig_customers, use_container_width=True)
    else:
        st.info(f"'{customer_id_col}' column not found in your data. Skipping Customer Type Breakdown visualization.")


    # ==== 5. KPIs ====
    st.markdown("---")
    col1, col2 = st.columns(2)

    if "Total Revenue" in df.columns:
        avg_order_value = df["Total Revenue"].mean()
        col1.metric("📦 Average Order Value", f"₹{avg_order_value:,.2f}")

        col2.metric("📈 Total Revenue", f"₹{df['Total Revenue'].sum():,.0f}")
    else:
        st.info("Cannot display KPIs. 'Total Revenue' column missing.")

