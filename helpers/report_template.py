class report_template:
    location = ""
    time_period = ""
    weather_description = ""
    temp_min = 0.0
    temp_max = 0.0
    temp = 0.0
    precipitation = 0.0

    allData = [location, time_period, weather_description, temp, temp_min, temp_max, precipitation]

    @staticmethod
    def load_template():
        return {
                "spring": {
                    "arctic": {
                        "Clear": "It's going to be freezing coming up, so wear your mittens. We expect the {weather_description} for the next {time_period}, with temperatures around lows of {temp_min}°F to highs of {temp_max}°F, with an average RealFeel of {temp}°F.",
                        "Clouds": "We're expecting {weather_description} this {time_period} with temperatures ranging from lows of {temp_min}°F to highs of {temp_max}°F, with an average RealFeel of {temp}°F.",
                        "Rain": "It seems winter's not done with us yet, as we're getting some freezing rain and low, low temperatures this {time_period} with {weather_description}. We're expecting {precipitation} inches of rain by the end of the {time_period}; our temperatures will hover around lows of {temp_min}°F to highs of {temp_max}°F, with an average RealFeel of {temp}°F.",
                        "Snow":"It seems winter's not done with us yet, as we're getting a surprise Arctic blast this {time_period} with some {weather_description}. We're expecting {precipitation} inches of snow by the end of the {time_period}. Meanwhile, our temperatures will drop to lows of {temp_min}°F to highs of {temp_max}°F, with an average RealFeel of {temp}°F.",
                    },
                    "cold": {
                        "Clear": "We're going to have a chilly yet beautiful spring {time_period} ahead of us; the {weather_description} with temperatures ranging from lows of {temp_min}°F to highs of {temp_max}°F, and an average RealFeel of {temp}°F.",
                        "Clouds": "We've got a cold {time_period} ahead of us, with {weather_description} and temperatures ranging from lows of {temp_min}°F to highs of {temp_max}°F, with an average RealFeel of {temp}°F.",
                        "Rain": "We're heading into some cold {weather_description} this {time_period}. We're expect around {precipitation} inches of rain and for temperatures to range from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow": "Winter is making a brave return, as we're expecting some {weather_description} to hit {location} before the {time_period} is out. We expect around {precipitation} inches of snow to fall, and for temperatures to range from lows of {temp_min}°F to highs of {temp_max}°F with a RealFeel of {temp}°F.",
                    },
                    "mild": {
                        "Clear": "{location} has some beautiful mild Spring weather ahead this {time_period}; the {weather_description}, and temperatures will range from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Clouds": "It's going to be mild this {time_period} in {location}, with {weather_description} and temperatures ranging from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain": "'Spring rains bring summer flowers', or whatever the saying was, as {location} is getting some {weather_description} to the tune of {precipitation} inches this {time_period}, with temperatures ranging from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow": "We're getting some surprise winter weather as {weather_description} comes to {location} this {time_period}, with about {precipitation} inches of snow expected to drop by the time {time_period} is out. Despite that, our temperatures will range from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                    },
                    "hot": {
                        "Clear": "Summer has come early as {location} has some beautiful but HOT weather to look forward to this {time_period}; the {weather_description}, and temperatures are high, with lows of {temp_min}°F to highs of {temp_max}°F, and a RealFeel of {temp}°F.",
                        "Clouds": "The forecast is 'hot and muggy' as we head into this {time_period}, with {weather_description} and lows of {temp_min}°F to highs of {temp_max}°F. Our average RealFeel is {temp}°F.",
                        "Rain": "Tropical rains are headed our way this {time_period}; we're expecting {precipitation} inches of rain to fall by the time the {time_period} is out. We're going to have lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow":"It's HOT and SNOWING?! The end of days has come to {location}, clearly. This {time_period} we can expect {weather_description} with lows of {temp_min}°F and highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                    },
                },
                "summer": {
                    "arctic": {
                        "Clear": "We're having a surprise wintry blast in summer this {time_period}, as the {weather_description} while temperatures drop to lows of {temp_min}°F with highs of {temp_max}°F, and a RealFeel of {temp}°F.",
                        "Clouds": "'Freezing, grey, and dreary' is how I'd describe the upcoming {time_period} - you'd think it was the middle of December! We have {weather_description} and our temperatures are going to remain around lows of {temp_min}°F with highs of {temp_max}°F, and a RealFeel of {temp}°F.",
                        "Rain": "For those of you who wanted relief from warmer weather, we have some good news, as freezing {weather_description} is coming to {location} this {time_period}. We expect {precipitation} inches of rain to fall with temperatures dropping to lows of {temp_min}°F with highs of {temp_max}°F, and a RealFeel of {temp}°F.",
                        "Snow":"'Below freezing temperatures' and 'snowy wonderland' are phrases you typically associate with winter, not summer, and yet {weather_description} is coming to {location} this {time_period}, with {precipitation} inches of snow expected to drop and temperatures forecasted around lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                    },
                    "cold": {
                        "Clear": "A cool yet clear summer {time_period} is expected, with temperatures around {temp_min}°F for our lows to {temp_max}°F for our highs, and a RealFeel of {temp}°F.",
                        "Clouds": "Cloudy and chilly for a summer {time_period}, with {weather_description} and temperatures ranging from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain": "Cold rain is forecast for {location} this {time_period}, with {weather_description}; meanwhile our temperatures will be hovering around lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow": "Snow in summer?! It's more likely than you think. This {time_period} brings {weather_description} to {location}. We expect {precipitation} inches of snow as our temperatures drop to lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                    },
                    "mild": {
                        "Clear": "Fire up that grill as some beautiful mild summer weather is ahead this {time_period}. The {weather_description}, and temperatures will range from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Clouds": "Mild cloudy weather is ahead this {time_period}, with {weather_description} and temperatures ranging from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain": "Some mild summer {weather_description} is coming to {location} this {time_period}. We expect {precipitation} inches of rain to drop, and temperatures to range from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow":"It might be summer, but {weather_description} is still coming to our little town of {location} this {time_period}, with {precipitation} inches expected to drop by the time {time_period} is out. Our ground temperatures will still range from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                    },
                    "hot": {
                        "Clear": "{location} has some classic beautiful summer weather coming up. The {weather_description}, and our temperatures will range from {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                        "Clouds": "For this {time_period} we expect the weather to be 'hot, humid, and grey', with {weather_description} and temperatures ranging from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain": "We're getting hit with warm {weather_description} this {time_period}, with {precipitation} inches expected to drop while temperatures range from lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow":"It's HOT and SNOWING?! The end of days has come to {location}, clearly. This {time_period} we can expect {weather_description} and our temperatures to rise to lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                    },
                },
                "autumn": {
                    "arctic": {
                        "Clear": "It will be freezing, but we'll have clear skies for this {time_period}. Temperatures have dropped to {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                        "Clouds": "Arctic winds bring a cold and cloudy {time_period}, with {weather_description}. Temperatures have dropped to {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                        "Rain": "Freezing rain is forecast for this autumn {time_period}, with {weather_description}. Temperatures have dropped to {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                        "Snow": "Arctic conditions bring autumn snow to {location} this {time_period}, with {weather_description}. Temperatures have dropped to {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                    },
                    "cold": {
                        "Clear": "A crisp and clear autumn {time_period} is on the way, with {weather_description}. Temperatures are hovering around {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                        "Clouds": "It's looking to be a typical autumn {time_period} coming up - chilly with {weather_description}. Temperatures are hovering around {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                        "Rain": "Cool rain showers are expected this {time_period}, with {weather_description}. We expect {precipitation} inches of rain to drop. Temperatures are hovering around {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                        "Snow": "Winter is on its way to {location}, with a {weather_description} flurry expected to drop {precipitation} inches of snow. Temperatures are hovering around {temp_min}°F for our lows and {temp_max}°F for our highs, with a RealFeel of {temp}°F.",
                    },
                    "mild": {
                        "Clear": "Mild and sunny autumn days are forecast this {time_period}, with {weather_description}. Temperatures are hovering right around {temp_min}°F for our lows and highs at {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Clouds": "Mild but overcast for this {time_period}, with {weather_description}.  Temperatures are hovering right around lows of {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain": "Light autumn rain is expected this {time_period}, with {weather_description}. Our lows will be around {temp_min}°F, with highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow": "Something weird this way comes to {location}, with mild weather on the ground and snow clouds above may occur this {time_period}, with {weather_description}. Despite the freezing temperatures up above our ground temperatures are going to hold at lows of {temp_min}°F and with highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                    },
                    "hot":{
                        "Clear":"Summer's decided she wasn't done with us yet. It's looking hot and gorgeous out for {time_period}; the {weather_description}, and our lows to remain around {temp_min}°F, with our highs at {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Clouds":"We're having an August spell for much of this {time_period}, with {weather_description}. We can expect lows to remain around {temp_min}°F, with our highs at {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain":"It's turning hot and muggy out for much of this {time_period}, with {weather_description}. We can expect lows at {temp_min}°F, and highs around {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow":"It's HOT and SNOWING?! The end of days has come to {location}, clearly. This {time_period} we can expect {weather_description} and our temperatures to rise to lows of {temp_min}°F and highs of {temp_max}°F, with a RealFeel of {temp}°F.",

                    },
                },
                "winter": {
                    "arctic": 
                    {
                        "Clear":"It's going to be below freezing out this {time_period}, but gorgeous and sunny. The {weather_description}, and our lows are at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Clouds":"It's going to be freezing and grey this {time_period} in {location}, with temperatures between {temp_min}°F to {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain":"Watch out for black ice. A freezing {weather_description} is coming to {location} to drop {precipitation} inches of rain. Our temperatures for this {time_period} are going to range between lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow":"Check your snow-tires, as we're about to experience some {weather_description} and freezing conditions. We're expecting {precipitation} inches of snow. Our temperatures are going to range around lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",

                    },
                    "cold": {
                        "Clear":"Chilly but beautiful is how I'd describe the weather coming up this {time_period}. The {weather_description}, with lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Clouds":"Another cloudy winter {time_period} in {location}; grey, grey, and more grey, with temperatures ranging between lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain":"Cold {weather_description} is coming to {location} this {time_period}, with an advisory that it may turn to hail. {precipitation} inches are expected to drop, with temperatures ranging from lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow":"Mother Nature is cooking us up a winter wonderland this {time_period}, as we're headed into {weather_description} that's forecast to drop {precipitation} inches on beloved {location}. Our temperatures are going to drop to our lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",

                    },
                    "mild": {
                        "Clear":"We're headed into a beautiful mild {time_period}; the {weather_description} and our temperatures will range from lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Clouds":"Some mild grey days are ahead for us, with {weather_description} and temperatures ranging from lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Rain":"Cool {weather_description} is coming to {location} this {time_period}, with {precipitation} expected to drop. Meanwhile, our highs will range from {temp_min}°F at night to {temp_max}°F in the morning, with a RealFeel of {temp}°F.",
                        "Snow":"Get your snow-tires checked, {location}, as we're headed into {weather_description} this {time_period}. Our temperatures will range from lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",

                    },
                    "hot": {
                        "Clear": "summer's coming early to {location} this {time_period}; the {weather_description} and we're going to see temperatures ranging from our lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Clouds":"We've got some cloudy summer days in winter coming up this {time_period}, with {weather_description}. We're going to have lows of {temp_min}°F, highs of {temp_max}°F, and a humidity percentage of {humidity}, so be sure to keep yourself cool, with a RealFeel of {temp}°F.",
                        "Rain":"Some unseasonably warm rain is in {location}'s future this {time_period}, with {weather_description} and temperatures ranging from our lows at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                        "Snow":"It's HOT and SNOWING?! The end of days has come to {location}, clearly. This {time_period} we can expect {weather_description}. Despite that, our lows are at {temp_min}°F to highs of {temp_max}°F, with a RealFeel of {temp}°F.",
                    } 
                },
        }
    
    @staticmethod
    def get_template(season, temp, weather):
        templates = report_template.load_template()
        #chained dictionary lookup, gives us empty dict values if lookup isn't valid
        return templates.get(season, {}).get(temp, {}).get(weather, "Invalid dictionary chain in report_template.py: Did you pass the right season/temp type/weather?") 
    
class weather_data:
    def __init__(self, data):
        #second value is the fall-back if there's nothing found in data for the first-value
        #default week weather in new portsmouth is mild with a clear sky
        self.location = data.get("location", "New Portsmouth")
        self.time_period = data.get("time_period", "week")
        self.weather_description = data.get("weather_description", "sky is clear")
        self.temp_min = data.get("temp_min", 70.0)
        self.temp_max = data.get("temp_max", 75.0)
        self.temp = data.get("temp", 73.0)
        self.precipitation = data.get("precipitation", 0.0)
        self.season = data.get("season", "spring")
        self.temp_type = data.get("temp_type", "mild")
        self.weather = data.get("weather", "Clear")

class weather_report:
    def generate_report(self, weather_data):
            #grabs the right dictionary string given our season/temp type/weather (eg, spring/mild/clear)
            template = report_template.get_template(weather_data.season, weather_data.temp_type, weather_data.weather)
            #format replaces the {variables} in the string w the right ones stored in weather_data
            return template.format(
                location=weather_data.location,
                time_period=weather_data.time_period,
                weather_description=weather_data.weather_description,
                temp_min=weather_data.temp_min,
                temp_max=weather_data.temp_max,
                temp=weather_data.temp,
                precipitation=weather_data.precipitation,
            )
    
    def generate_combined_report(self, weather_data1, weather_data2=None):
        report1 = self.generate_report(weather_data1)
        if weather_data2:
            report2 = self.generate_report(weather_data2)
            return f"{report1}. Later, {report2}"
        return report1

        


