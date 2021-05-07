from flask import Flask
from flask import render_template
from flask import request
import requests
import time
import sys

app = Flask(__name__)


def get_weather_of_city(city):
    data = None
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=a9f150cd03e25092a78c5c2cea652352"
    r = requests.get(url)
    if r:
        result = r.json()
        local_time = time.gmtime().tm_hour + int(result['timezone']) // 3600
        # if 6 <= local_time <= 9 or 17 <= local_time <= 19:
        #     back_image = 'evening-morning'
        if 9 < local_time < 17:
            back_image = 'day'
        elif 20 > local_time <= 23 or 0 < local_time < 6:
            back_image = 'night'
        else:
            back_image = 'evening-morning'

        data = {'city': result['name'], 'temp': result['main']['temp'], 'timezone': back_image,
                'weather': result['weather'][0]['main']}
    return data


default_cities_weather = [get_weather_of_city('conakry'), get_weather_of_city('paris'), get_weather_of_city('dortmund')]
cities_weather = []


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        city_name = request.form['city_name']
        if get_weather_of_city(city_name):
            cities_weather.append(get_weather_of_city(city_name))
        return render_template('index.html', data=default_cities_weather + cities_weather)
    else:
        cities_weather.clear()
        return render_template('index.html', data=default_cities_weather)


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run('127.0.0.1', '80', debug=True, load_dotenv=True)
