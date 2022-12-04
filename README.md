# UC Berkeley - MIDS Capstone Fall 2022 (CALCUlator)
This GitHub repository includes our CALCUlator code files for the Fall 2022 Masters of Information and Data Science (MIDS) Capstone. Details about the project, the team, and the code below. A BIG thanks to Microsoft for our Azure grant, a BIG thanks to the Google Earth Engine team for the continued guidance and support throughout our project, and of course a BIG thanks to the prior research in this area from MOD17 and Robinson et al.
- [CALCUlator product website](https://codebeard.wixsite.com/ucb-calculator)
- [CALCUlator Streamlit application in Azure](https://carbon-web-app-ucb.azurewebsites.net/)
- [Related work with carbon absorption - GPP](https://zslpublications.onlinelibrary.wiley.com/doi/10.1002/rse2.74)
- [Related work in the area of urbanization](https://cbmjournal.biomedcentral.com/articles/10.1186/s13021-019-0128-6)
- [MOD17 prior research](http://www.ntsg.umt.edu/project/modis/mod17.php)
- [Robinson et al improvements from MOD17](https://zslpublications.onlinelibrary.wiley.com/doi/10.1002/rse2.74)

## Our Mission
To create a more sustainable future by helping City Planners and Chief Sustainability Officers understand the amount of natural carbon absorption lost from developing over vegetated land, and the cost to replenish that natural carbon absorption to achieve Net Zero Carbon.

### Motivation
The motivation for our project came from the Geo for Environment (G4E) Organization at Google. This org owns Google Earth Engine, Environmental Insights Explorer, Earth Desktop and Web, as well as MyMaps. They work with partners around the world, including but not limited to the World Resource Institute (WRI), the United Nations Food and Agriculture Organization (FAO), the Global Covenant of Mayors for Climate & Energy (GCoM), and multiple government and native communities. With these products, data scientists and politicians are doing incredible things, including habitat protection and restoration, sustainable city planning, carbon accounting, and much more.

### Problem
Photosynthesis is a natural process that takes carbon dioxide out of the atmosphere, converts it to natural organic compounds, protecting us from unwanted planet warming and climate change. Unfortunately, continued land development due to growing urbanization, destroys natural vegetation and replaces it with concrete and other structures. Carbon dioxide is the main driver of climate change and cities are responsible for 75% of global carbon dioxide emissions that affect climate change today. So what are we going to do about it?

### Solution
Our CALCUlator product uses Google Earth Engine (GEE) data and Random Forest regression techniques to help City Planners as well as Chief Sustainability Officers understand the amount of natural carbon absorption lost from developing over vegetated land, and the cost to replenish that natural carbon absorption to achieve Net Zero Carbon.

## The Team from University of California Berkeley - MIDS Capstone Fall 2022
- Justine Taylor, Product Manager
- Jacob Wilson, Architect
- Stephen Chen, Engineer
- Clayton Summit, Data Scientist
- Prathyusha Charagondla, Data Scientist

## The Code
Our application was built using Streamlit (app foundation), Bokeh (visualizations), Azure App Services (container hosting), Azure Container Registry Services, Azure Data Lake Storage Gen2, and obviously a host of Python libraries to enable our data and ML pipelines. Listed below are the primary folders that represent our codebase. 
- **Streamlit folder:** Contains all of the application code files to build a docker container image and deploy to Azure App Services via Azure Container Registry Service. However, the private json key for calls to GEE apis is not included in this folder. You would have to set up your own GEE subscription and then use your own private key which would need to be replaced in the area_change.py file and the Carbon_Analysis.py file. In the DOCKER file you will also notice a VOLUME mount path of /w210containermount. This is where the Streamlit application loads the GEE private key and model binary from Azure Data Lake Storage Gen2. 
- **Data folder:** Contains all of the raw and cleansed data for model training and evaluation. We used several sources for our data including, [Dynamic World](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1), [USGS 3DEP 10m](https://developers.google.com/earth-engine/datasets/catalog/USGS_3DEP_10m), [MOD15 Terra Leaf Area Index](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD15A2H), [GRIDMET](https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_GRIDMET), and [AmeriFlux](https://doi.org/10.17190/AMF/1671890).

