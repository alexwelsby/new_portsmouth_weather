import random
import math
from helpers.category_utils import get_unix_date
from config import SharedState
from helpers.redis_utils import add_to_redis, get_current_json, get_event_json
from helpers.event import Event

def generate_json_event(param_data):
    time_period = param_data['time_period']
    #print(f"time period set as {time_period}")
    EVENT_yyyymm = "EVENT_" + param_data['start_date'][:-3] #this will be the redis key
    #print(f"EVENT_yyyymm set as {EVENT_yyyymm}")
    start_time = get_unix_date(param_data['start_date']) #going to add 8 hours to this per loop
    print(f"start_time set as {start_time}")
    num_slices = get_num_of_slices(3, time_period) #3 = minimum of 3 reports per day (matches our json)
    #print(f"num_slices set as {num_slices}")
    json_data = get_current_json(param_data['start_date'], None, param_data['time_period'])
    #print(f"json data got")
    param_data = fill_none_values(json_data, param_data) #if the user left out any parameters, this populates them from the historical data
    #print(f"param_data is {param_data}")
    fields_to_replace = generate_8hr_slices(start_time, num_slices, param_data)
    #print(f"{fields_to_replace[0]}")
    new_json = update_json(json_data, fields_to_replace)
    print(new_json)
    end_time = json_data[-1]["dt"] #unix time of the last entry
    add_to_redis(EVENT_yyyymm, new_json) #adds this event to the database
    print("add_to_redis successful")
    add_event(EVENT_yyyymm, start_time, end_time) #adds an event object to the sharedState (start_time and end_time are in unix)

def fill_none_values(json_data, param_data):
    if param_data['min_temp'] is None:
        param_data['min_temp'] = min(entry["main"]["temp_min"] for entry in json_data)
    if param_data['max_temp'] is None:
        param_data['max_temp'] = max(entry["main"]["temp_max"] for entry in json_data)
    if param_data['min_precipitation'] is None:
        param_data['min_precipitation'] = min(entry["precipitation"] for entry in json_data)
    if param_data['max_precipitation'] is None:
        param_data['max_precipitation'] = max(entry["precipitation"] for entry in json_data)
    if param_data['max_cloud_cover'] is None:
        param_data['max_cloud_cover'] = max(entry["clouds"]["all"] for entry in json_data)
    if param_data['min_cloud_cover'] is None:
        param_data['min_cloud_cover'] = min(entry["clouds"]["all"] for entry in json_data)
    if param_data["max_wind_speed"] is None:
        param_data['max_wind_speed'] = max(entry["wind"]["speed"] for entry in json_data)
    if param_data["min_wind_speed"] is None:
        param_data['min_wind_speed'] = min(entry["wind"]["speed"] for entry in json_data)
    if param_data["max_humidity"] is None:
        param_data['max_humidity'] = max(entry["main"]["humidity"] for entry in json_data)
    if param_data["min_humidity"] is None:
        param_data['min_humidity'] = min(entry["main"]["humidity"] for entry in json_data)
    if param_data['chance_rain'] is None:
        param_data['chance_rain'] = ((sum(1 for entry in json_data if entry["weather"][0]["main"] == "Rain")) / len(json_data)) * 100
    if param_data['chance_snow'] is None:
        param_data['chance_snow'] = ((sum(1 for entry in json_data if entry["weather"][0]["main"] == "Snow")) / len(json_data)) * 100
    
    return param_data

    

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


def generate_8hr_slices(start_time, count, param_data):
    all_outputs = []
    time = 0
    while time != count:
        output = {
            'dt': start_time,
            'temp': 0.0,
            'max_temp': 0.0,
            'min_temp': 0.0,
            'precipitation': 0.0,
            'humidity': 0,
            'feels_like': 0.0,
            'wind_speed': 0.0,
            'dew_point': 0.0,
            'weather_main': "",
            'weather_description': "",
            'weather_icon': "",
        }
        output['temp'], output['max_temp'], output['min_temp'] = generate_temp(param_data['min_temp'], param_data['max_temp']) 

        output['wind_speed'] = generate_windspeed(param_data['min_wind_speed'], param_data['max_wind_speed'])

        output['humidity'] = generate_humidity(param_data['min_humidity'], param_data['max_humidity'])

        output['dew_point'] = generate_dew_point(output['temp'], output['humidity'])

        output['feels_like'] = generate_realFeel(output['temp'], output['wind_speed'], output['humidity'])

        output['weather_main'], output['precipitation'] = generate_precipitation(param_data['min_precipitation'], 
                                                                                    param_data['max_precipitation'], 
                                                                                    output['temp'], 
                                                                                    param_data.get('chance_snow', 0), 
                                                                                    param_data.get('chance_rain', 33) )

        if output['precipitation'] == 0.00:
            output['weather_main'], output['weather_description'], output['weather_icon'] = generate_dry_weather_desc(param_data['min_cloud_cover'], 
                                                                                                                      param_data['max_cloud_cover'])

        else:
            output['weather_description'], output['weather_icon'] = generate_wet_weather_desc(output)

        #print(f"temp: {output['temp']}, max_temp: {output['max_temp']}, min_temp: {output['min_temp']}, weather_icon: {output['weather_icon']}, weather_main: {output['weather_main']}, weather_description: {output['weather_description']}, precipitation: {output['precipitation']}")
        all_outputs.append(output)
        start_time += 28800 #adding 8 hours to our current time (so we're ready for the next loop)
        time += 1
    return all_outputs

def generate_windspeed(min, max):
    return round(random.uniform(min, max), 2)

def generate_humidity(min, max):
    return random.randint(int(min), int(max))

def update_json(json_data, outputs):

    for output in outputs:
        dt = output['dt']
        print(dt)
        for entry in json_data:
            if entry["dt"] == dt:
                entry["main"]["temp"] = output["temp"]
                entry["main"]["temp_min"] = output["min_temp"]
                entry["main"]["temp_max"] = output["max_temp"]
                entry["main"]["humidity"] = output["humidity"]
                entry["main"]["dew_point"] = output["dew_point"]
                entry["main"]["feels_like"] = output["feels_like"]
                entry["weather"][0]["main"] = output["weather_main"]
                entry["weather"][0]["description"] = output["weather_description"]
                entry["weather"][0]["icon"] = output["weather_icon"]
                entry["precipitation"] = output["precipitation"]
                entry["wind"]["speed"] = output["wind_speed"]
                break
    return json_data


def generate_temp(min, max):
    temp = round(random.uniform(min, max), 1)
    dif = (max - min)/2
    min_temp = round(random.uniform(min, min+dif), 1)
    max_temp = round(random.uniform(max-dif, max), 1)
    return temp, max_temp, min_temp

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
        
def generate_dry_weather_desc(min=0.0, max=100.0):
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


def generate_dew_point(temp, humidity):
    celsius = (temp - 32) / 1.8 #since we're burgerbrained all our temps are in fahrenheit
    #but the formula is for C, so...
    dew_point = celsius - ((100 - humidity)/5)
    dew_point = (dew_point * 1.8) + 32
    return round(dew_point,1)

#taken from jfcarr's feelslike algorithm found here: https://gist.github.com/jfcarr/e68593c92c878257550d
#note that his algorithm assumes US units - degrees F, MPH
def generate_realFeel(vTemperature, vWindSpeed, vRelativeHumidity):
    if vTemperature <= 50 and vWindSpeed >= 3:
        vFeelsLike = 35.74 + (0.6215*vTemperature) - 35.75*(vWindSpeed**0.16) + ((0.4275*vTemperature)*(vWindSpeed**0.16))
    else:
        vFeelsLike = vTemperature
    
    # Replace it with the Heat Index, if necessary
    if vFeelsLike == vTemperature and vTemperature >= 80:
        vFeelsLike = 0.5 * (vTemperature + 61.0 + ((vTemperature-68.0)*1.2) + (vRelativeHumidity*0.094))
    
    if vFeelsLike >= 80:
        vFeelsLike = -42.379 + 2.04901523*vTemperature + 10.14333127*vRelativeHumidity - .22475541*vTemperature*vRelativeHumidity - .00683783*vTemperature*vTemperature - .05481717*vRelativeHumidity*vRelativeHumidity + .00122874*vTemperature*vTemperature*vRelativeHumidity + .00085282*vTemperature*vRelativeHumidity*vRelativeHumidity - .00000199*vTemperature*vTemperature*vRelativeHumidity*vRelativeHumidity
        if vRelativeHumidity < 13 and vTemperature >= 80 and vTemperature <= 112:
            vFeelsLike = vFeelsLike - ((13-vRelativeHumidity)/4)*math.sqrt((17-math.fabs(vTemperature-95.))/17)
        if vRelativeHumidity > 85 and vTemperature >= 80 and vTemperature <= 87:
            vFeelsLike = vFeelsLike + ((vRelativeHumidity-85)/10) * ((87-vTemperature)/5)
    
    return round(vFeelsLike, 1)
