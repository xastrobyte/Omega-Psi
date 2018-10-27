from datetime import datetime
import json

COUNTRIES = "util/weather/countries.json"
DIRECTIONS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
]

def kelvinToFahrenheit(kelvin):
    """Converts a temperature in Kelvin (K) to Fahrenheit (F)
    """
    return int((kelvin - 273.15) * (9/5) + 32)

def kelvinToCelsius(kelvin):
    """Converts a temperature in Kelvin (K) to Celsius (C)
    """
    return int(kelvin - 273.15)

def mpsToMph(metersPerSecond):
    """Converts M/S to M/H
    """
    return int(metersPerSecond * (3600 / 1609.34))

def degreeToCardinal(degrees):
    """Converts a meteorological direction to a cardinal direction
    """

    # Divide degrees by 16-wind compass value (22.5)
    point = int(degrees / 22.5) % 16 # Keep it between 0 and 15 (inclusive)
    return DIRECTIONS[point]

def getCity(weatherJson):
    """Returns the City Name from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    """
    return weatherJson["name"]

def getCountry(weatherJson):
    """Returns the Country Name from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    """
    
    # Load countries.json
    with open(COUNTRIES, "r") as countriesFile:
        countries = json.load(countriesFile)
    
    # Search for country code in countries
    for country in countries:
        if country["code"] == weatherJson["sys"]["country"]:
            return country["name"]
    
    return None

def getCurrentTemp(weatherJson, metric = True):
    """Returns the current temperature from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    metric - Whether or not to get the temperature in celsius.\n
    """
    if metric:
        return kelvinToCelsius(weatherJson["main"]["temp"])
    return kelvinToFahrenheit(weatherJson["main"]["temp"])

def getHighTemp(weatherJson, metric = True):
    """Returns the max temperature from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    metric - Whether or not to get the temperature in celsius.\n
    """
    if metric:
        return kelvinToCelsius(weatherJson["main"]["temp_max"])
    return kelvinToFahrenheit(weatherJson["main"]["temp_max"])

def getLowTemp(weatherJson, metric = True):
    """Returns the minimum temperature from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    metric - Whether or not to get the temperature in celsius.\n
    """
    if metric:
        return kelvinToCelsius(weatherJson["main"]["temp_min"])
    return kelvinToFahrenheit(weatherJson["main"]["temp_min"])

def getSky(weatherJson):
    """Returns the description of the sky from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    """
    return weatherJson["weather"][0]["main"] + " - " + weatherJson["weather"][0]["description"]

def getLongitude(weatherJson):
    """Returns the longitude of the city from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    """
    longitude = round(weatherJson["coord"]["lon"], 2)
    return "{}°{}".format(
        longitude, "W" if longitude < 0 else "E"
    )

def getLatitude(weatherJson):
    """Returns the latitude of the city from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    """
    latitude = round(weatherJson["coord"]["lat"], 2)
    return "{}°{}".format(
        abs(latitude), "S" if latitude < 0 else "N"
    )

def getWindSpeed(weatherJson, metric = True):
    """Returns the wind speed from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    metric - Whether or not to get the wind speed in m/s or m/h.\n
    """
    if metric:
        return weatherJson["wind"]["speed"]
    return mpsToMph(weatherJson["wind"]["speed"])

def getWindDirection(weatherJson, degree = True):
    """Returns the wind direction from the Weather JSON response.\n

    weatherJson - The Weather JSON response to use.\n
    degree - Whether or not to get the direction in degrees or a cardinal direction.\n
    """
    if degree:
        return weatherJson["wind"]["deg"]
    return degreeToCardinal(weatherJson["wind"]["deg"])

def getLastUpdated(weatherJson):
    """Returns the date and time of the Weather JSON response.\n
    """
    return weatherJson["dt"]

def getWeatherIcon(weatherJson):
    """Returns the icon that describes the Weather JSON response.\n
    """
    return "http://openweathermap.org/img/w/{}.png".format(weatherJson["weather"][0]["icon"])