import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark import Session

connection_parameters = st.secrets["snowflake"]
session = Session.builder.configs(connection_parameters).create()

st.title("🍹 Smoothie Order App")

name = st.text_input("Enter your name")

df = session.table("smoothies.public.fruit_options").to_pandas()

st.dataframe(df)

fruits = df["FRUIT_NAME"].tolist()
selected = st.multiselect("Choose fruits", fruits)

for fruit in selected:
    search = df.loc[df["FRUIT_NAME"] == fruit, "SEARCH_ON"].iloc[0]
    r = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search}")
    if r.status_code == 200:
        st.write(r.json())

filled = st.checkbox("Order Filled")

if st.button("Submit"):
    if name and selected:
        ingredients = ",".join(selected)

        session.sql(f"""
        INSERT INTO smoothies.public.orders
        VALUES (
            '{name}',
            '{ingredients}',
            {str(filled).upper()},
            CURRENT_TIMESTAMP()
        )
        """).collect()

        st.success("Order placed ✅")
