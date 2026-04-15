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
            
# --- MODULE 1: EXTREME HEAT BASELINE (NEW) ---
            st.markdown("---")
            st.subheader("Module 1: Extreme Heat Baseline (Days > 40°C)")
            
            with st.spinner("Fetching historical daily temperature data..."):
                # Open-Meteo Historical API (Baseline Year: 2023)
                heat_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2023-01-01&end_date=2023-12-31&daily=temperature_2m_max"
                
                try:
                    heat_response = requests.get(heat_url)
                    heat_data = heat_response.json()
                    
                    if "error" in heat_data:
                        st.error("Error fetching historical heat data.")
                    else:
                        daily_max_temps = heat_data['daily']['temperature_2m_max']
                        valid_temps = [t for t in daily_max_temps if t is not None]
                        
                        # Calculate days exceeding 40 Celsius
                        extreme_heat_days = sum(1 for t in valid_temps if t > 40)
                        
                        st.metric(label="Days Exceeding 40°C (Recent Baseline)", value=f"{extreme_heat_days} days")
                        
                        if extreme_heat_days > 30:
                            st.error("**High Heat Risk:** Sustained periods of extreme heat threatening labor productivity and cooling infrastructure.")
                        elif extreme_heat_days > 10:
                            st.warning("**Moderate Heat Risk:** Notable exposure to extreme heat events.")
                        else:
                            st.success("**Low Heat Risk:** Limited exposure to temperatures exceeding 40°C.")
                            
                        st.info("Data Source: Open-Meteo Historical Archive. 40°C is a standard threshold for assessing severe occupational heat stress.")
                        
                except Exception as e:
                    st.warning("Could not connect to historical temperature database.")

# --- MODULE 2: FUTURE CLIMATE PROJECTIONS (2050) ---
            st.markdown("---")
            st.subheader("Module 2: Future Heat Projections (Year 2050)")
            
            with st.spinner("Fetching CMIP6 climate models..."):
                # Open-Meteo Climate API (100% Free, No Keys Required)
                climate_url = f"https://climate-api.open-meteo.com/v1/climate?latitude={lat}&longitude={lon}&start_date=2050-01-01&end_date=2050-12-31&models=MRI_AGCM3_2_S&daily=temperature_2m_max"
                
                try:
                    climate_response = requests.get(climate_url)
                    climate_data = climate_response.json()
                    
                    if "error" in climate_data:
                        st.error("Error fetching climate projections.")
                    else:
                        # Extract the daily max temperatures for the 365 days in 2050
                        temps_2050 = climate_data['daily']['temperature_2m_max']
                        
                        # Calculate the projected average max temperature
                        valid_temps = [t for t in temps_2050 if t is not None]
                        avg_temp_2050 = sum(valid_temps) / len(valid_temps)
                        
                        st.metric(label="Projected Annual Avg. Max Temperature (2050)", value=f"{avg_temp_2050:.2f}°C")
                        st.info("Data Source: Open-Meteo Climate API. Projections derived from CMIP6 Models (MRI-AGCM3-2-S) forecasting long-term shifts.")
                        
                except Exception as e:
                    st.warning("Could not connect to Open-Meteo Climate database at this time.")

# --- MODULE 3: ACUTE RISK - EXTREME PRECIPITATION ---
            st.markdown("---")
            st.subheader("Module 3: Acute Flood Risk (Extreme Rainfall)")
            
            with st.spinner("Fetching historical precipitation data..."):
                # Open-Meteo Historical API (Last full calendar year: 2023)
                precip_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date=2023-01-01&end_date=2023-12-31&daily=precipitation_sum"
                
                try:
                    precip_response = requests.get(precip_url)
                    precip_data = precip_response.json()
                    
                    if "error" in precip_data:
                        st.error("Error fetching precipitation data.")
                    else:
                        # Extract the daily rainfall totals for the whole year
                        daily_rain = precip_data['daily']['precipitation_sum']
                        valid_rain = [r for r in daily_rain if r is not None]
                        
                        # Calculate key flood risk metrics
                        max_single_day_rain = max(valid_rain)
                        heavy_rain_days = sum(1 for r in valid_rain if r > 50) # Days over 50mm
                        
                        # Display metrics side-by-side
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(label="Max Single-Day Rainfall (2023)", value=f"{max_single_day_rain:.1f} mm")
                        with col2:
                            st.metric(label="Days with Heavy Rain (>50mm)", value=f"{heavy_rain_days} days")
                            
                        # Add automated risk assessment logic
                        if max_single_day_rain > 100:
                            st.error("**High Flood Risk:** Location experiences extreme single-day rainfall events capable of severe inundation.")
                        elif max_single_day_rain > 50:
                            st.warning("**Moderate Flood Risk:** Location experiences heavy rainfall capable of overwhelming urban drainage.")
                        else:
                            st.success("**Low Flood Risk:** No extreme single-day rainfall events recorded in the baseline year.")
                            
                        st.info("Data Source: Open-Meteo Historical Archive. Note: In Indian metros, >50mm of rain in a single day typically overwhelms municipal drainage infrastructure.")
                        
                except Exception as e:
                    st.warning("Could not connect to precipitation database at this time.")