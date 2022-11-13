import streamlit as st
from PIL import Image

# Read in custom CSS
with open('project_contents/app/style.css') as f:
       st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Top Section of the page
st.markdown("# CALCUlator -> Carbon Absorption Loss from Continued Urbanization")
st.write("""Understanding Carbon Absorption Loss and the cost to replinish in order to achieve net zero carbon.""")
st.write('')
st.write('')

# Open images for homepage
city_image = Image.open('project_contents/app/city_view.png')
red_arrow = Image.open('project_contents/app/red_arrow.jpeg')
green_arrow = Image.open('project_contents/app/green_arrow.jpeg')
calculator_image = Image.open('project_contents/app/calculator.jpeg')

# Create areas for text and image rendering
area3, area4 = st.columns([2,1])
area5, area6 = st.columns([2,4])
area7, area8 = st.columns([2,1])
area9, area10 = st.columns([2,4])

# Product Feature Descriptions
st.write('')
st.write('')
area3.text_area('Land Selection', 
  '''Use the land selection tool to select a county or specific site to analyze for carbon absorption loss and gain.''', height = 60, key="area3")
area4.image(city_image)
area4.write('')
area4.write('')

area5.image(red_arrow)
area6.text_area('Carbon Loss Predictor (CLP)', 
  '''Estimate the carbon absoprtion loss for a selected county or site using the CLP.''', height = 60, key="area6")
area6.write('')
area6.write('')

area7.text_area('Cost Analysis', 
  '''Use the cost analysis capabilities to understand the cost to offset carbon absoprtion loss.''', height = 60, key="area7")
area8.image(calculator_image)
area8.write('')
area8.write('')

area9.image(green_arrow)
area10.text_area('Carbon Gain Predictor (CGP)', 
  '''Estimate the carbon absoprtion gain through carbon offsetting efforts.''', height = 60, key="area10")
