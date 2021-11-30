from VacAPI import db, ma
from VacAPI.models import User, Test, Vaccination

class TestSchema(ma.Schema):
    class Meta:
        fields = ('test_result', 'date_result_recieved')
        model = Test

test_schema = TestSchema()
tests_schema = TestSchema(many=True)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'full_name', 'email', 'health_status')
        model = User

user_schema = UserSchema()

class VaccineSchema(ma.Schema):
    class Meta:
        fields = ('vaccine', 'number_of_dose')
        model = Vaccination

vaccination_schema = VaccineSchema()
vaccinations_schema = VaccineSchema(many=True)

