from flask import render_template, url_for, flash, redirect, request, jsonify
from urllib.request import urlopen
from VacAPI import db, ma, app, bcrypt, mail, api
from VacAPI.models import User, Test
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask_restful import Resource
from VacAPI.schema import user_schema, test_schema,tests_schema
import googlemaps
import geocoder
from googleplaces import GooglePlaces, types
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyCee7-FHwxX05iBtQgm-IP-BsTwORgtPfw')
google_places = GooglePlaces(key='AIzaSyBDfNHKqNBi7ni5nj-xAuy9XjUsRrrJT8c')


def define_location():
    location = gmaps.geolocate()
    lat = location['location']['lat']
    long = location['location']['lng']
    decoded = geocoder.google([lat, long], method='reverse')
    vals = decoded.json
    location = vals['address']
    return location

def define_vaccinations_centre(location):
    results=[]
    nearby_centres = google_places.nearby_search(location=location, type='hospital' ,keyword='vaccination centre', radius=5000)
    for item in nearby_centres.places:
        results.append(item.name)
        return results

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

            return test_schema.dumps(tests)

    def get(self, id_of_user):
        user = User.query.get_or_404(id_of_user)
        t = Test.query.filter_by(user_id=id_of_user).all()
        return tests_schema.dumps(t)

api.add_resource(TestResource, '/testing/<id_of_user>')







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

api.add_resource(UserResource, '/user/<id_of_user>')

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
        user = User(username=request.json['username'], email=request.json['email'], password=hashed_password, health_status=request.json['health_status'], location=defined_location)
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user)

api.add_resource(UserLogin_Create, '/user')





@app.route("/")
@app.route("/Dashboard/<id_of_user>")
def home(id_of_user):
    return jsonify(posts)


@app.route("/company_updates")
def about():
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
def wallet(id_of_user):

    user = User.query.get_or_404(id_of_user)
    loc = user.location
    results = define_vaccinations_centre(loc)
    return jsonify(results)


