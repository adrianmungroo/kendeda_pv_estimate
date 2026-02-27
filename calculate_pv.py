import pvlib
import pandas as pd
import numpy as np

df = pd.read_csv("./data/solar_data.csv")
df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
df = df.set_index('timestamp_utc')

location = pvlib.location.Location(latitude=33.776, longitude=-84.396, tz='US/Eastern')

# Solar position from your timestamps
solpos = location.get_solarposition(df.index)

# AOI for your fixed panel
aoi = pvlib.irradiance.aoi(
    surface_tilt=5,        # Kendeda canopy: 5° from horizontal
    surface_azimuth=180,   # south-facing
    solar_zenith=solpos['apparent_zenith'],
    solar_azimuth=solpos['azimuth']
)

# Source data is in BTU/ft²/hr — convert to W/m² for pvlib
BTU_TO_WM2 = 3.15459
dni = df['direct_normal_irradiance'] * BTU_TO_WM2
dhi = df['diffuse_radiation'] * BTU_TO_WM2
ghi = dni * np.cos(np.radians(solpos['apparent_zenith'])) + dhi

# POA using isotropic model
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=5,
    surface_azimuth=180,
    solar_zenith=solpos['apparent_zenith'],
    solar_azimuth=solpos['azimuth'],
    dni=dni,
    ghi=ghi,
    dhi=dhi,
    model='isotropic'
)

poa_total = poa['poa_global']  # W/m²

# https://www.metalarchitecture.com/articles/a-living-learning-laboratory/
area = 1496.6        # m²
efficiency = 0.22  # approximate
performance_ratio = 0.721 # Real-world derate. Using this as calibration variable.

panel_watts = poa_total * area * efficiency * performance_ratio
df['panel_watts'] = panel_watts
df.to_csv("./data/panel_watts.csv", index=True)

print("The average annual solar generation in kWh is...")
print(df["panel_watts"].sum()/1000 / 3)