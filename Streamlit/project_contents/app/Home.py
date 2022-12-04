import streamlit as st
from PIL import Image

# Read in custom CSS
with open('project_contents/app/style.css') as f:
       st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Open images for homepage
carbon_predictor_image = Image.open('project_contents/app/carbon_predictor.png')
calculator_image = Image.open('project_contents/app/calculator.png')
land_selection_image = Image.open('project_contents/app/land_selection.png')
product_image = Image.open('project_contents/app/CALCUlator_product_image.png')

# Render product image
st.image(product_image)

# Top Section of the page
st.write("""The Carbon Absorption Loss from Continued Urbanization (CALCUlator) product provides City Planners as well as Chief Sustainability Officers the tools they need to understand how vegetated land must play into their Net Carbon zero goals for creating a more sustainable future. Through this product, users can select a specific area of land to analyze how much natural carbon absorption would be lost by developing over that land and what the cost would be to replinish that natural carbon absorption. In addition to understanding carbon absorption loss and offsetting costs, users can analyze newly established vegetation to monitor carbon absorption gain to ensure that any replinished vegetation is actually meeting the carbon offsetting objectives to reach Net Zero Carbon.""")
st.write('')
st.write('')

# Create areas for text and image rendering
area3, area4 = st.columns([2,1])
area5, area6 = st.columns([2,4])
area7, area8 = st.columns([2,1])
area9, area10 = st.columns([2,4])

# Product Feature Descriptions
st.write('')
st.write('')
area3.write('')
area3.write('')
area3.write('')
area3.markdown("**Land Selection.** Use the land selection tool to select a specific area to analyze for carbon absorption loss. No matter what you choose, we'll take those polygon coordinates to analyze the vegetation within that selected area.")
area4.image(land_selection_image)
area4.write('')

area5.image(carbon_predictor_image)
area6.write('')
area6.write('')
area6.write('')
area6.markdown("**Carbon Absorption Predictor (CAP).** We use Google Earth Engine (GEE) data and Random Forest regression techniques to predict the carbon absorption for your selected area in the continguous United States.")
area5.write('')

area7.write('')
area7.write('')
area7.write('')
area7.markdown("**Calculator.** If you are planning to develop over that vegetated land, we will calculate the costs to offset that natural carbon absorption. These costs can be used for your decision making and budgetary planning purposes.")
area8.image(calculator_image)
area8.write('')
