from VacAPI import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(20), nullable =False)
    gender = db.Column(db.String(20), nullable =False)
    passport_number = db.Column(db.Integer, unique = True)
    phone_number = db.Column(db.String(20), unique=True, nullable =False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    health_status = db.Column(db.String(60), nullable=False)
    residential_location = db.Column(db.String(60), nullable=False)
    country = db.Column(db.String(20), unique=True, nullable =False)
    covid_tests = db.relationship('Test', backref='patient', lazy=True)
    vaccinations = db.relationship('Vaccination', backref='testee', lazy = True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)



    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.health_status}', '{self.residential_location}')"

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_result = db.Column(db.String, nullable=False)
    date_result_recieved = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
       return f"Test('{self.test_result}', '{self.date_result_recieved})"

class Vaccination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vaccine = db.Column(db.String,nullable=False)
    number_of_dose = db.Column(db.String ,nullable=False)
    country_of_vaccination = db.Column(db.String, nullable=False)

    def __repr__(self):
       return f"Vaccination('{self.vaccine}', '{self.number_of_dose},'{self.country_of_vaccination}')"
