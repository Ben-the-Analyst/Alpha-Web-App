"""Build tables from user selections."""

import streamlit as st
from streamlit import session_state as ss


st.set_page_config(layout="wide")


# Constants
BRAND_LIST = ["ABC"]
BRICK_LIST = ["", "Kurta", "Sarees", "Chudidar Set", "Chudidar"]
PRODUCT_LIST = {
    "Chudidar Set": ["Chudidar Set", "Winter Chudidar Set"],
    "Sarees": ["Sarees"],
    "Kurta": ["Kurta", "Winter Kurta"],
    "Chudidar": ["Chudidar", "Chudi"],
}
CLASS_LIST = {
    "Chudidar Set": "Set",
    "Sarees": "Set",
    "Kurta": "Top Wear",
    "Chudidar": "Bottom Wear",
}


# Session variables
if "style_data" not in ss:
    ss.style_data = []

if "product_class" not in ss:
    ss.product_class = ""


# Functions
def new_styles_cb():
    """Append data to style_data from selection."""
    ss.style_data.append(
        {
            "brand": ss.brand,
            "brick": ss.brick,
            "product": ss.product,
            "product_class": ss.product_class,
        }
    )


def build_table():
    """Build table via user inputs"""
    # User selections
    with st.container(border=True):
        st.subheader("Select")

        brand_col, brick_col, product_col, class_col = st.columns(4)

        with brand_col:
            st.selectbox("BRAND:", BRAND_LIST, key="brand")

        with brick_col:
            st.selectbox("BRICK:", BRICK_LIST, key="brick")

        with product_col:
            st.selectbox(
                label="PRODUCT:",
                options=PRODUCT_LIST.get(ss.brick, [""]),
                key="product",
            )

        with class_col:
            st.text("CLASS:")
            ss.product_class = CLASS_LIST.get(ss.brick, "")
            st.text(ss.product_class)

        # Access the values of selectbox thru the keys.
        st.write(f"{ss.brand}, {ss.brick}, {ss.product}, {ss.product_class}")

        # Our callback new_styles_cb does not need any arguments
        # because we use the state variable values via its keys.
        st.button("Submit", on_click=new_styles_cb)

    # Show the table.
    with st.container(border=True):
        st.subheader("Style Attributes Data table")
        st.dataframe(ss.style_data, width=600)


def main():
    build_table()


if __name__ == "__main__":
    main()
