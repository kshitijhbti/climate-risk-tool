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