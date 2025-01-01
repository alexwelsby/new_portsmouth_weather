import random
from helpers.category_utils import get_unix_date
from config import SharedState
from helpers.redis_utils import add_to_redis, get_current_json
from helpers.event import Event

def generate_json_event(data):
    time_period = data['time_period']
    EVENT_yyyymm = "EVENT_" + data['start_date'][:-3] #this will be the redis key
    start_time = get_unix_date(data['start_date']) #going to add 8 hours to this per loop
    num_slices = get_num_of_slices(3, time_period) #3 = minimum of 3 reports per day (matches our json)
    json_data = get_current_json(data['start_date'], None, data['time_period'])
    fields_to_replace = generate_8hr_slices(start_time, num_slices, data)
    new_json = update_json(json_data, fields_to_replace)

    end_time = json_data[-1]["dt"] #unix time of the last entry
    add_to_redis(EVENT_yyyymm, new_json) #adds this event to the database
    add_event(EVENT_yyyymm, start_time, end_time) #adds an event object to the sharedState (start_time and end_time are in unix)
    

def add_event(EVENT_yyyymm, start_time, end_time):
    event = Event(event_redis_key=EVENT_yyyymm, start_unix=start_time, end_unix=end_time)
    SharedState.add_event(SharedState, event)
    print(SharedState.get_events(SharedState))

def get_num_of_slices(num_per_day, time_period):
    if time_period == "day":
        return num_per_day
    if time_period == "week":
        return num_per_day * 7
    if time_period == "month":
        return num_per_day * 30 #average amt of days. don't really care if the current month actually has 30 or not

    return num_per_day


def generate_8hr_slices(start_time, count, data):
    all_outputs = []
    time = 0
    while time != count:
        output = {
            'dt': start_time,
            'temp': 0.0,
            'max_temp': 0.0,
            'min_temp': 0.0,
            'precipitation': 0.0,
            'weather_main': "",
            'weather_description': "",
            'weather_icon': "",
        }
        output['temp'], output['max_temp'], output['min_temp'] = generate_temp(data['min_temp'], data['max_temp'])
        output['weather_main'], output['precipitation'] = generate_precipitation(data['min_precipitation'], data['max_precipitation'], output['temp'], data['chance_snow'], data['chance_rain'] )
        if output['precipitation'] == 0.00:
            output['weather_main'], output['weather_description'], output['weather_icon'] = generate_dry_weather_desc(data['min_cloud_cover'], data['max_cloud_cover'])
        else:
            output['weather_description'], output['weather_icon'] = generate_wet_weather_desc(output)
        #print(f"temp: {output['temp']}, max_temp: {output['max_temp']}, min_temp: {output['min_temp']}, weather_icon: {output['weather_icon']}, weather_main: {output['weather_main']}, weather_description: {output['weather_description']}, precipitation: {output['precipitation']}")
        all_outputs.append(output)
        start_time += 28800 #adding 8 hours to our current time (so we're ready for the next loop)
        time += 1
    return all_outputs



def update_json(json_data, outputs):
    for output in outputs:
        dt = output['dt']

        for entry in json_data:
            if entry["dt"] == dt:
                entry["main"]["temp"] = output["temp"]
                entry["main"]["temp_min"] = output["min_temp"]
                entry["main"]["temp_max"] = output["max_temp"]
                entry["weather"][0]["main"] = output["weather_main"]
                entry["weather"][0]["description"] = output["weather_description"]
                entry["weather"][0]["icon"] = output["weather_icon"]
                entry["precipitation"] = output["precipitation"]
                break
    return json_data


def generate_temp(min, max):
    realFeel = round(random.uniform(min, max), 1)
    dif = (max - min)/2
    min_temp = round(random.uniform(min, min+dif), 1)
    max_temp = round(random.uniform(max-dif, max), 1)
    return realFeel, max_temp, min_temp

def generate_precipitation(min_precip, max_precip, temp, chance_snow, chance_rain):
    snow_roll = random.randint(0, 100)
    rain_roll = random.randint(0, 100)
    precip = round(random.uniform(min_precip, max_precip), 2)
    #if both chance_snow and chance_rain win their rng rolls, we let temp>32 decide which wins
    if max_precip != 0 and chance_snow != 0 and chance_rain != 0:
        if snow_roll <= chance_snow and rain_roll <= chance_rain:
            if temp > 32:
                return "Rain", precip
            else:
                return "Snow", precip
        elif snow_roll <= chance_snow:
            return "Snow", precip
        elif rain_roll <= chance_rain:
            return "Rain", precip
        else:
            return "Clouds", 0.00 # we failed our rolls, we got clouds and no precip
    else: 
        return "Clouds", 0.00 #in this case we need to generate_dry_weather_desc instead for our weather description

def generate_wet_weather_desc(data):
    type_precip = data['weather_main']
    precip_amount = data['precipitation']
    temp = data['temp']
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
    rng = random.randint(int(min), int(max))
    if rng < 11:
        return "Clear", "sky is clear", "01d"
    if rng >= 11 and rng < 25:
        return "Clouds", "few clouds", "02d"
    elif rng >= 25 and rng <= 50:
        return "Clouds", "scattered clouds", "03d"
    elif rng >= 51 and rng <= 84:
        return "Clouds", "broken clouds", "04d"
    else:
        return "Clouds", "overcast clouds", "04d"

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


