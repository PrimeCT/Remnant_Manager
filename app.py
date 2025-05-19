import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO

# Page configuration with logo
st.set_page_config(page_title="Prime Countertops Remnant Stock", layout="wide", page_icon="logo.png")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("stockremnant-test.csv")
    return df.sort_values("name")  # Sort alphabetically by name

df = load_data()

# Password protection for manager page
def check_password():
    """Check if the entered password matches."""
    password = st.text_input("Enter Password", type="password")
    if password == "Jenny@PrimeCountertops2025":
        return True
    return False

# Display logo with error handling
try:
    logo = Image.open("logo.png")
    st.sidebar.image(logo, width=200)
except FileNotFoundError:
    st.sidebar.warning("Logo file not found. Please ensure 'logo.png' is in the directory.")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Customer View", "Manager View"], label_visibility="collapsed")

# Customer View
if page == "Customer View":
    st.title("Prime Countertops Remnant Stock")
    st.write("Browse our available remnant stock below.")
    
    # Text search
    search_query = st.text_input("Search by Name, Material, or Dimensions")
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_query, case=False, na=False) |
            filtered_df["material"].str.contains(search_query, case=False, na=False) |
            filtered_df["dimensions"].str.contains(search_query, case=False, na=False)
        ]
    
    # Filter by material
    material = st.selectbox("Filter by Material", ["All"] + sorted(df["material"].unique().tolist()))
    
    if material != "All":
        filtered_df = filtered_df[filtered_df["material"] == material]
    
    for index, row in filtered_df.iterrows():
        with st.expander(f"{row['name']}"):
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.write(f"**Color/Style:** {row['name']}")
            with col2:
                st.write(f"**Material:** {row['material']}")
            with col3:
                st.write(f"**Size:** {row['dimensions']}")
            # Try to display image
            image_url = row["image_url"]
            try:
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'image' in content_type:
                        image = Image.open(BytesIO(response.content))
                        st.image(image, caption=f"{row['name']} Remnant", use_column_width=True)
                    else:
                        st.error(f"URL {image_url} returned non-image content (type: {content_type}). Use a direct image link.")
                else:
                    st.error(f"Failed to load image for {row['name']}. Status code: {response.status_code}. URL: {image_url}")
            except Exception as e:
                st.error(f"Error loading image for {row['name']}: {str(e)}. URL: {image_url}")

# Manager View
elif page == "Manager View":
    st.title("Remnant Stock Manager")
    if not check_password():
        st.error("Incorrect password. Please try again.")
    else:
        st.success("Access granted. Manage your remnant stock below.")
        
        # Display current stock with better contrast
        st.subheader("Current Stock")
        st.dataframe(df.style.set_properties(**{
            'background-color': '#2c2f33', 
            'color': '#ffffff', 
            'border-color': '#40444b'
        }).set_table_styles([{
            'selector': 'th',
            'props': [('background-color', '#23272a'), ('color', '#ffffff')]
        }]))
        
        # Edit the entire CSV table
        st.subheader("Edit Stock Table")
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "name": st.column_config.TextColumn("Name"),
                "material": st.column_config.TextColumn("Material"),
                "dimensions": st.column_config.TextColumn("Dimensions"),
                "image_url": st.column_config.TextColumn("Image URL")
            },
            use_container_width=True
        )
        if st.button("Save Changes to Table"):
            edited_df.to_csv("stockremnant-test.csv", index=False)
            st.success("Table updated successfully!")
            st.cache_data.clear()
        
        # Update remnant size
        st.subheader("Update Remnant Size")
        id_to_update = st.number_input("Enter ID to update", min_value=1, max_value=len(df), step=1)
        new_dimensions = st.text_input("New Dimensions (e.g., 46x97)")
        if st.button("Update Size"):
            df.loc[df['id'] == id_to_update, 'dimensions'] = new_dimensions
            df.to_csv("stockremnant-test.csv", index=False)
            st.success(f"Updated dimensions for ID {id_to_update}")
            st.cache_data.clear()
        
        # Delete remnant
        st.subheader("Delete Remnant")
        id_to_delete = st.number_input("Enter ID to delete", min_value=1, max_value=len(df), step=1)
        if st.button("Delete"):
            df.drop(df[df['id'] == id_to_delete].index, inplace=True)
            df.to_csv("stockremnant-test.csv", index=False)
            st.success(f"Deleted remnant with ID {id_to_delete}")
            st.cache_data.clear()
        
        # Add new remnant
        st.subheader("Add New Remnant")
        new_id = st.number_input("New ID", min_value=df['id'].max() + 1, step=1)
        new_name = st.text_input("Name")
        new_material = st.selectbox("Material", df["material"].unique().tolist())
        new_dimensions = st.text_input("Dimensions (e.g., 46x97)")
        new_image_url = st.text_input("Image URL (Google Photos or GitHub raw link)")
        if st.button("Add Remnant"):
            new_row = pd.DataFrame({
                "id": [new_id],
                "name": [new_name],
                "material": [new_material],
                "dimensions": [new_dimensions],
                "image_url": [new_image_url]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv("stockremnant-test.csv", index=False)
            st.success(f"Added new remnant with ID {new_id}")
            st.cache_data.clear()

# CSS for modern and clean look with better contrast
st.markdown(
    """
    <style>
    .stApp {
        background-color: #2c2f33;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    .stSidebar {
        background-color: #23272a;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #d4af37;
        color: white;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #b8860b;
    }
    .stExpander {
        background-color: #2c2f33;
        color: #ffffff;
        border: 1px solid #40444b;
        border-radius: 5px;
    }
    .stDataFrame, .stDataEditor {
        background-color: #2c2f33;
        color: #ffffff;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        background-color: #40444b;
        color: #ffffff;
        border-radius: 5px;
    }
    .stSelectbox > div > div, .stTextInput > div > input, .stNumberInput > div > input {
        color: #ffffff !important;
    }
    [data-testid="stDataFrame"] table, [data-testid="stDataEditor"] table {
        background-color: #2c2f33 !important;
        color: #ffffff !important;
    }
    [data-testid="stDataFrame"] th, [data-testid="stDataEditor"] th {
        background-color: #23272a !important;
        color: #ffffff !important;
    }
    [data-testid="stDataFrame"] td, [data-testid="stDataEditor"] td {
        background-color: #2c2f33 !important;
        color: #ffffff !important;
    }
    .stExpander > div > div {
        padding: 10px;
        background-color: #2c2f33;
    }
    </style>
    """,
    unsafe_allow_html=True
)
