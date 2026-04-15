import streamlit as st
import pgeocode
import requests
import pandas as pd

# 1. Setup the Web Page
st.set_page_config(page_title="India Climate Risk", page_icon="🌍", layout="centered")

st.title("🌍 Climate Risk Assessment Tool")
st.subheader("Module 1: Extreme Heat Baseline")
st.write("Enter an Indian Pin Code to assess long-term historical heat risk.")

# 2. User Input (Defaults to a Gurugram pin code)
pincode = st.text_input("Enter 6-digit Indian Pin Code:", "122018")

# 3. The Action Button
if st.button("Analyze Risk"):
    with st.spinner("Locating Pin Code and fetching NASA data..."):
        
        # Translate Pin Code to Latitude/Longitude
        nom = pgeocode.Nominatim('in')
        location = nom.query_postal_code(pincode)

        if pd.isna(location.latitude):
            st.error("Invalid Pin Code. Please ensure it is a valid 6-digit Indian code.")
        else:
            lat = location.latitude
            lon = location.longitude
            st.success(f"Location Identified: {location.place_name}, {location.state_name}")
            
            # 4. Fetch Data from NASA POWER API (Long-term averages)
            # T2M_MAX stands for Maximum Temperature at 2 Meters
            url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=T2M_MAX&community=RE&longitude={lon}&latitude={lat}&format=JSON"
            
            try:
                response = requests.get(url)
                data = response.json()
                
                # Extract the Annual Average Maximum Temperature
                annual_max_temp = data['properties']['parameter']['T2M_MAX']['ANN']
                
                # 5. Display the Results beautifully
                st.metric(label="Historical Annual Avg. Max Temperature", value=f"{annual_max_temp}°C")
                
                st.info("Data Source: NASA Prediction of Worldwide Energy Resources (POWER). This represents the 30-year historical baseline.")
                
            except Exception as e:
                st.error("Could not connect to NASA databases at this time.")

# --- MODULE 2: WRI AQUEDUCT WATER STRESS ---
            st.markdown("---")
            st.subheader("Module 2: Baseline Water Stress")
            
            with st.spinner("Fetching spatial data from World Resources Institute..."):
                # WRI Aqueduct ArcGIS REST API endpoint
                wri_url = "https://gis.wri.org/server/rest/services/Aqueduct30/aqueduct_results_v01/MapServer/0/query"
                bbox = f"{lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}"
                wri_params = {
                    "geometry": f"{lon},{lat}",
                    "geometryType": "esriGeometryPoint",
                    "spatialRel": "esriSpatialRelIntersects",
                    "inSR": "4326",
                    "outFields": "bws_cat", # Pulls the text category (e.g., "Extremely High")
                    "returnGeometry": "false",
                    "f": "pjson"
                }
                
                try:
                    wri_response = requests.get(wri_url, params=wri_params)
                    wri_data = wri_response.json()
                    
                    # Extract the water stress category from the JSON response
                    if 'features' in wri_data and len(wri_data['features']) > 0:
                        water_stress = wri_data['features'][0]['attributes']['bws_cat']
                        
                        # Add a visual color cue based on the severity
                        if "Extremely High" in water_stress:
                            st.error(f"**Baseline Water Stress:** {water_stress}")
                        elif "High" in water_stress:
                            st.warning(f"**Baseline Water Stress:** {water_stress}")
                        else:
                            st.success(f"**Baseline Water Stress:** {water_stress}")
                            
                        st.info("Data Source: WRI Aqueduct 3.0. Assesses the ratio of total water withdrawals to available renewable surface and groundwater supplies.")
                    else:
                        st.warning("Data not found. Here is the exact response from the WRI server:")
                        st.json(wri_data)
                except Exception as e:
                    st.warning("Could not connect to WRI Aqueduct database at this time.")