import requests
import time
import sys

from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slBnLfa70xYt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weater.db'
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.name


db.create_all()


def get_weather_of_city(id_city, city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid=a9f150cd03e25092a78c5c2cea652352"
    r = requests.get(url)
    if r:
        result = r.json()
        local_time = time.gmtime().tm_hour + int(result['timezone']) // 3600
        if 10 <= local_time <= 16:
            back_image = 'day'
        elif 20 >= local_time <= 23 or 0 <= local_time <= 5:
            back_image = 'night'
        else:
            back_image = 'evening-morning'

        return {'id': id_city, 'name': result['name'], 'temp': result['main']['temp'],
                'timezone': back_image, 'weather': result['weather'][0]['main']}
    else:
        return None


@app.route('/')
def index():
    data = [get_weather_of_city(city.id, city.name) for city in City.query.all()]
    return render_template('index.html', data=data)


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        city_name = request.form['city_name']
        if get_weather_of_city(None, city_name):
            try:
                city = City(name=city_name)
                db.session.add(city)
                db.session.commit()
            except:
                db.session.rollback()
                flash("The city has already been added to the list!")
        else:
            flash("The city doesn't exist!")
    return redirect('/')


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        city_id = request.form['id']
        city = City.query.filter_by(id=city_id).first()
        db.session.delete(city)
        db.session.commit()
    return redirect('/')


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run('127.0.0.1', '80', debug=True, load_dotenv=True)
