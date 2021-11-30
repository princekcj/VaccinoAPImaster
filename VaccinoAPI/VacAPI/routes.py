import json
from urllib.request import urlopen
from VacAPI import db, ma, app, bcrypt, mail, api
from VacAPI.models import User, Test, Vaccination
from flask_mail import Message
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_restful import Resource
from VacAPI.schema import user_schema, test_schema,tests_schema,vaccination_schema, vaccinations_schema
import requests
import googlemaps
import geocoder
from googleplaces import GooglePlaces, types
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyCee7-FHwxX05iBtQgm-IP-BsTwORgtPfw')
google_places = GooglePlaces('AIzaSyBDfNHKqNBi7ni5nj-xAuy9XjUsRrrJT8c')

Apikey = 'AIzaSyCee7-FHwxX05iBtQgm-IP-BsTwORgtPfw'

posts = [
    {
        'author': 'Vaccino',
        'title': 'how to change password',
        'content': 'please click on forgot password button',
        'date_posted': 'November 21, 2021'
    },
    {
        'author': 'Vaccino',
        'title': 'How often does updates refresh?',
        'content': 'updates completed daily',
        'date_posted': 'April 21, 2021'
    }
]


def define_location():
    location = gmaps.geolocate()
    lat = location['location']['lat']
    long = location['location']['lng']
    decoded = gmaps.reverse_geocode((lat, long))
    d = decoded[0]
    location_values = d['address_components']
    local = location_values[1]
    location_name = local['long_name']
    location =[lat, long]
    location_content = {                  
        "location": location,
        "location_name" : location_name
    }

    return location_content

def define_vaccinations_centre(location_content):
    results=[]
    nearby_centres = gmaps.places_nearby(location=location_content["location"],keyword="hospital",radius=8046, language="en")
    nearby_centres = nearby_centres['results']
    for item in nearby_centres:
        results.append(item['name'])
     

    return results

def pharmacy_location(location_content):
     nearby_centres = gmaps.places_nearby(location=location_content["location"],keyword='pharmacy', radius=8046)
     results = []
     nearby_centres = nearby_centres['results']
     for item in nearby_centres:
         results.append(item['name'])


     return results


class Preserialize:
   def as_dict(self):
       return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}







class TestResource(Resource):
    def post(self, id_of_user):
        user = User.query.get_or_404(id_of_user)
        if bcrypt.check_password_hash(user.password, request.json['password']):
            tests = Test(user_id=id_of_user, test_result=request.json['test_result'] )
            db.session.add(tests)
            db.session.commit()
            if request.json['test_result'] == "positive":
                user.health_status = 'red'
            return test_schema.jsonify(tests)

    def get(self, id_of_user):
        user = User.query.get_or_404(id_of_user)
        t = Test.query.filter_by(user_id=id_of_user).all()
        return tests_schema.jsonify(t)

api.add_resource(TestResource, '/api/testing/<id_of_user>')



class VaccinationResource(Resource):
    def post(self, id_of_user):
        user = User.query.get_or_404(id_of_user)
        vaccine = request.json['name_of_vaccine']
        number_of_dose = request.json['dose_number']
        country_of_vaccination = request.json['country_of_vaccination']
        vac = Vaccination(user_id=id_of_user, vaccine = vaccine, number_of_dose = number_of_dose,country_of_vaccination = country_of_vaccination)
        db.session.add(vac)
        db.session.commit()
        return vaccination_schema.jsonify(vac)

    def get(self, id_of_user):
        user = User.query.get_or_404(id_of_user)
        v = Vaccination.query.filter_by(user_id=id_of_user).all()
        return vaccinations_schema.jsonify(v)

api.add_resource(VaccinationResource, '/api/vaccination/<id_of_user>')



class UserResource(Resource):
    def get(self, id_of_user):
        user = User.query.get_or_404(id_of_user)
        return user_schema.dump(user)

    def put(self, id_of_user):
        user = User.query.get_or_404(id_of_user)

        if 'username' in request.json:
            user.username = request.json['username']
        if 'email' in request.json:
            user.email = request.json['email']
        if 'health_status' in request.json :
            user.health_status = request.json['health_status']

        db.session.commit()
        return user_schema.dump(user)

    def delete(self, id_of_user):
        user = User.query.get_or_404(id_of_user)
        db.session.delete(user)
        db.session.commit()
        return '', 204

api.add_resource(UserResource, '/api/user/<id_of_user>')

class UserLogin_Create(Resource):
    def get(self):
        user = User.query.filter_by(email=request.json['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.json['password']):
            return user_schema.dump(user)
        else:
            return '', 404

    def post(self):
        hashed_password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
        defined_location = define_location()
        user = User (gender = request.json['gender'],full_name=request.json['username'], email=request.json['email'], password=hashed_password, health_status=request.json['health_status'], residential_location=defined_location["location_name"], passport_number = request.json['passport_number'], phone_number=request.json['phone_number'], country=request.json['country'], date_of_birth=request.json['date_of_birth'])
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user)

api.add_resource(UserLogin_Create, '/api/user')



@app.route("/")
@app.route("/api/dashboard/<id_of_user>", methods =['GET'])
def home(id_of_user):
    user = User.query.get_or_404(id_of_user)
    name = user.full_name
    Greeting = f'Hello, {name}'
    return jsonify(Greeting)


@app.route("/api/faqs", methods =['GET'])
def faqs():
    return jsonify(posts)




#@app.route("/logout")
#def logout():
 #   logout_user()
  #  return redirect(url_for('home'))




def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}

    If you did not make request then simply ignore this email and no changes will be made
    '''
    return token

@app.route("/api/reset_password", methods=['GET', 'POST'])
def reset_request():
        user = User.query.filter_by(email=request.json['email']).first()
        token= send_reset_email(user)
        results = {"token": token}
        return jsonify(results)


@app.route("/api/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        return '', 404
    else:
        hashed_password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
    return jsonify(user)


@app.route("/api/<id_of_user>/vaccinationcentres/", methods=['GET'])
def vac_centres(id_of_user):

    user = User.query.get_or_404(id_of_user)
    loc = define_location()
    results = define_vaccinations_centre(loc)
    return jsonify(results)

@app.route("/api/<id_of_user>/pharmacies/", methods=['GET'])
def pharma(id_of_user):
    import json

    user = User.query.get_or_404(id_of_user)
    loc = define_location()
    results = pharmacy_location(loc)
    return json.dumps(results)

@app.route("/api/covid_updates/", methods=['GET'])
def updates():
    url = "https://covid-19-data.p.rapidapi.com/country"
    querystring = {"name":"uk"}
    headers = {
         'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
         'x-rapidapi-key': "a662b8b6d1mshbf604cd25a5bb8ap1d5915jsn0063bd6dd731"
         }

    response = requests.request("GET", url, headers=headers, params=querystring)


    return response.text
