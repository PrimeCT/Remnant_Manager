import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64

# Page configuration with logo
st.set_page_config(page_title="Prime Countertops Remnant Stock", layout="wide", page_icon="logo.png")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("stockremnant-test.csv")

df = load_data()

# Password protection for manager page
def check_password():
    """Check if the entered password matches."""
    password = st.text_input("Enter Password", type="password")
    if password == "Jenny@PrimeCountertops2025":
        return True
    return False

# Display logo
logo = Image.open("logo.png")
st.sidebar.image(logo, width=200)

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Customer View", "Manager View"])

# Customer View
if page == "Customer View":
    st.title("Prime Countertops Remnant Stock")
    st.write("Browse our available remnant stock below.")
    
    # Filter by material
    material = st.selectbox("Filter by Material", ["All"] + df["material"].unique().tolist())
    filtered_df = df if material == "All" else df[df["material"] == material]
    
    for index, row in filtered_df.iterrows():
        with st.expander(f"{row['name']} ({row['material']}) - {row['dimensions']}"):
            st.write(f"ID: {row['id']}")
            # Display image from Google Photos
            image_url = row["image_url"]
            st.image(image_url, caption=f"{row['name']} Remnant", use_column_width=True)

# Manager View
elif page == "Manager View":
    st.title("Remnant Stock Manager")
    if not check_password():
        st.error("Incorrect password. Please try again.")
    else:
        st.success("Access granted. Manage your remnant stock below.")
        
        # Display current stock
        st.subheader("Current Stock")
        st.dataframe(df)
        
        # Update remnant size
        st.subheader("Update Remnant Size")
        id_to_update = st.number_input("Enter ID to update", min_value=1, max_value=len(df), step=1)
        new_dimensions = st.text_input("New Dimensions (e.g., 46x97)")
        if st.button("Update Size"):
            df.loc[df['id'] == id_to_update, 'dimensions'] = new_dimensions
            df.to_csv("stockremnant-test.csv", index=False)
            st.success(f"Updated dimensions for ID {id_to_update}")
        
        # Delete remnant
        st.subheader("Delete Remnant")
        id_to_delete = st.number_input("Enter ID to delete", min_value=1, max_value=len(df), step=1)
        if st.button("Delete"):
            df.drop(df[df['id'] == id_to_delete].index, inplace=True)
            df.to_csv("stockremnant-test.csv", index=False)
            st.success(f"Deleted remnant with ID {id_to_delete}")
        
        # Add new remnant (simple form)
        st.subheader("Add New Remnant")
        new_id = st.number_input("New ID", min_value=df['id'].max() + 1, step=1)
        new_name = st.text_input("Name")
        new_material = st.selectbox("Material", df["material"].unique().tolist())
        new_dimensions = st.text_input("Dimensions (e.g., 46x97)")
        new_image_url = st.text_input("Image URL (Google Photos link)")
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

# CSS for modern and clean look
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f0f0;
        font-family: 'Arial', sans-serif;
    }
    .stSidebar {
        background-color: #333;
        color: #fff;
    }
    .stButton>button {
        background-color: #d4af37;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #b8860b;
    }
    </style>
    """,
    unsafe_allow_html=True
)