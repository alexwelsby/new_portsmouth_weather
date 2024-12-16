
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
        precip_obj = generate_precipitation(data['min_precipitation'], data['max_precipitation'], temp, data['chance_snow'], data['chance_rain'] )
        if precip_obj["precipitation"] == 0.0:
            generate_dry_weather_desc()
        else:
            generate_wet_weather_desc(precip_obj['weather-main'], precip_obj["precipitation"], temp)


def generate_temp(min, max):
    realFeel = random.uniform(min, max)
    dif = (max - min)/2
    rand_dif = random.uniform(min, min+dif)
    min_temp = min+rand_dif
    rand_dif = random.uniform(max-dif, max)
    max_temp = max-rand_dif
    return realFeel, max_temp, min_temp

def generate_precipitation(min, max, temp, chance_snow, chance_rain):
    snow_roll = random.randint(0, 100)
    rain_roll = random.randint(0, 100)
    precip = random.uniform(min, max)

    #if both chance_snow and chance_rain win their rng rolls, we let temp>32 decide which wins
    if precip > 0.0:
        if snow_roll <= chance_snow and rain_roll <= chance_rain:
            if temp > 32:
                return {"weather-main": "Rain", "precipitation": precip}
            else:
                return {"weather-main": "Snow", "precipitation": precip}
        elif snow_roll <= chance_snow:
            return {"weather-main": "Snow", "precipitation": precip}
        elif rain_roll <= chance_rain:
             return {"weather-main": "Rain", "precipitation": precip}
    return {"weather-main": "Clouds", "precipitation": precip}  #in this case we need to generate_dry_weather_desc instead for our weather description

def generate_wet_weather_desc(type_precip, precip_amount, temp):
    weather_description = ""
    amt = ""
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
    elif type_precip == "Rain":
        if temp < 32:
            weather_description = "freezing "
        weather_description += f"{amt} rain"
        
    return weather_description
        
def generate_dry_weather_desc(min, max):
    rng = random.randint(min, max)
    weather_description = ""
    condition = "Clouds"
    if rng < 11:
        condition = "Clear"
        weather_description = "sky is clear"
    if rng >= 11 and rng < 25:
        weather_description = "few clouds"
    elif rng >= 25 and rng <= 50:
        weather_description = "scattered clouds"
    elif rng >= 51 and rng <= 84:
        weather_description = "broken clouds"
    else:
        weather_description = "overcast clouds"
           
    return {"weather-main": condition, "weather-description": weather_description }

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