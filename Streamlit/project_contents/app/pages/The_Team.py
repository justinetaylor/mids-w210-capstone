import streamlit as st
import pandas as pd
from PIL import Image

# Read in custom CSS
with open('project_contents/app/style.css') as f:
       st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("# UC Berkeley W210 Castone Team")
st.write("""Motivation. We are a carbon concious team, looking for ways to drive awareness around creating a more sustainable future. The motivation
for our project came from the Geo for Environment (G4E) Organization at Google. This org owns Google Earth Engine, Environmental Insights
Explorer, Earth Desktop and Web, as well as MyMaps. They work with partners around the world, including but not limited to the World Resource 
Institute (WRI), the United Nations Food and Argiculture Organization (FAO), the Global Covenant of Mayors for Climate & Energy (GCoM), 
and multiple government and native communities. With these products, data scientists and politicians are doing incredible things, including 
habitat protection and restoration, sustainable city planning, carbon accounting, and much much more.""")
st.write('')
st.write("""Problem. With the motivation from the G4E Organization at Google, we set our focus on land vegetation and the natural carbon absorption that 
happens through photosynthesis. Its the photosynthesis process that takes carbon dioxide from the atmosphere, converts it to nautral organic compounds, 
which then becomes energy for plants. This is an amazing natural process that is protecting our very well being. But...with continued land development 
due to growing urbanization, this natural carbon dioxide absorption is diminishing as vegetated land is being replaced with concrete and other structures. 
Meaning, as we continue to expand land development we are losing more and more of this natural carbon absorption. In fact, cities are responsible for 75% 
of global carbon dioxide emissions. So we must get creative about how to protect vegetated land or replinish any vegetation that was destroyed due to land development.""")
st.write('')
st.write("""Solution. Our product, CALCUlator (Carbon Absroption Loss from Continued Urbanization), providers City Planners as well as Chief Sustainability Officers 
the tools they need to understand how vegetated land must play into their Carbon Net Zero goals for creating a more sustainable future. Through our produduct, users can 
select a specific area of land to analyze how much natural carbon absorption would be lost by developing over that land and what the cost would be to replish 
that natural carbon absroption. In addition to understanding carbon absorption loss and offseting costs, users of our product can analyze newly established vegetation to 
monitor carbon absorption gain to ensure that any replinished vegetation is actually meeting the carbon offsetting objectives to reach Carbon Net Zero. We hope users enjoy this 
MVP product and if there is enough interest in the market, we look forward to providing subsequent updates to the product. """)
st.write('')
st.markdown("**The Team from University of California Berkeley - MIDS Capstone Fall 2022**")
st.write("Clayton Summit")
st.write("Jacob Wilson")
st.write("Justine Taylor")
st.write("Prathyusha Charagondla")
st.write("Stephen Chen")




