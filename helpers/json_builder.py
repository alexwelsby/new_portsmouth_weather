
import random

def generate_json_event(data):
    time_period = data['time_period']
    count = 3 #minimum of 3 reports
    time = 0
    if time_period == "day":
        pass #we don't have to do anything
    if time_period == "week":
        count *= 7
    if time_period == "month":
        count *= 30 #average amt of days. don't really care if the current month actually has 30 or not

    while time != count:
        temp, max_temp, min_temp = generate_temp(data['min_temp'], data['max_temp'])
        weather_main, precipitation = generate_precipitation(data['min_precipitation'], data['max_precipitation'], temp, data['chance_snow'], data['chance_rain'] )
        if precipitation == 0.0:
            weather_main, weather_description, weather_icon = generate_dry_weather_desc(data['min_cloud_cover'], data['max_cloud_cover'])
        else:
            weather_description, weather_icon = generate_wet_weather_desc(weather_main, precipitation, temp)
        
        time += 1


def generate_temp(min, max):
    realFeel = round(random.uniform(min, max), 1)
    dif = (max - min)/2
    min_temp = round(random.uniform(min, min+dif), 1)
    max_temp = round(random.uniform(max-dif, max), 1)
    print(f"realFeel: {realFeel}, max_temp: {max_temp}, min_temp: {min_temp}")
    return realFeel, max_temp, min_temp

def generate_precipitation(min, max, temp, chance_snow, chance_rain):
    snow_roll = random.randint(0, 100)
    rain_roll = random.randint(0, 100)
    precip = random.uniform(min, max)

    #if both chance_snow and chance_rain win their rng rolls, we let temp>32 decide which wins
    if precip > 0.0:
        if snow_roll <= chance_snow and rain_roll <= chance_rain:
            if temp > 32:
                return "Rain", precip
            else:
                return "Snow", precip
        elif snow_roll <= chance_snow:
            return "Snow", precip
        elif rain_roll <= chance_rain:
             return "Rain", precip
    return "Clouds", precip  #in this case we need to generate_dry_weather_desc instead for our weather description

def generate_wet_weather_desc(type_precip, precip_amount, temp):
    weather_description = ""
    amt = ""
    weather_icon = ""
    if precip_amount <= 0.1:
        amt = "light"
    elif precip_amount > 0.1 and precip_amount <= 0.3:
        amt = "moderate"
    elif precip_amount > 0.3 and precip_amount <= 2.0:
        amt = "heavy"
    elif precip_amount > 2.0:
        amt = "extreme"

    if type_precip == "Snow":
        weather_description += f"{amt} snow"
        weather_icon = "13d"
    elif type_precip == "Rain":
        if temp < 32:
            weather_description = f"freezing {amt} rain"
            weather_icon = "13d"
        else:
            weather_description = f"{amt} rain"
            weather_icon = "10d"
        
    return weather_description, weather_icon
        
def generate_dry_weather_desc(min, max):
    rng = random.randint(min, max)
    weather_description = ""
    weather_main = "Clouds"
    weather_icon = "04d" #the 'd'/'n' indicator will come later
    if rng < 11:
        weather_main = "Clear"
        weather_description = "sky is clear"
        weather_icon = "01d"
    if rng >= 11 and rng < 25:
        weather_description = "few clouds"
        weather_icon = "02d"
    elif rng >= 25 and rng <= 50:
        weather_description = "scattered clouds"
        weather_icon = "03d"
    elif rng >= 51 and rng <= 84:
        weather_description = "broken clouds"
        weather_icon = "04d"
    else:
        weather_description = "overcast clouds"
        weather_icon = "04d"
           
    return weather_main, weather_description, weather_icon

def build_json_entry(data): #builds an entry for one segment
                return {
                    "dt": int(data["dt"]),
                    "dt_iso": data["dt_iso"],
                    "timezone": int(data["timezone"]),
                    "main": {
                        "temp": float(data["temp"]),
                        "temp_min": float(data["temp_min"]),
                        "temp_max": float(data["temp_max"]),
                        "feels_like": float(data["feels_like"]),
                        "pressure": int(data["pressure"]),
                        "humidity": int(data["humidity"]),
                        "dew_point": float(data["dew_point"])
                    },
                    "clouds": {
                        "all": int(data["clouds_all"])
                    },
                    "weather": [
                        {
                            "id": int(data["weather_id"]),
                            "main": data["weather_main"],
                            "description": data["weather_description"],
                            "icon": data["weather_icon"]
                        }
                    ],
                    "wind": {
                        "speed": float(data["wind_speed"]),
                        "deg": int(data["wind_deg"]),
                        "gust": float(data["wind_gust"]) if data["wind_gust"] != '' else ''
                    },
                    "precipitation": float(data["precipitation"]),
                }

generate_temp(40, 65)