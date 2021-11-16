from VacAPI import db, ma
from VacAPI.models import User, Test

class TestSchema(ma.Schema):
    class Meta:
        fields = ('test_result', 'date_result_recieved')
        model = Test

test_schema = TestSchema()
tests_schema = TestSchema(many=True)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'email', 'health_status')
        model = User

user_schema = UserSchema()

