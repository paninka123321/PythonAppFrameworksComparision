from flask_marshmallow import Marshmallow
from models import User, Task, Bill, BusinessDefinition, Role
from marshmallow import fields

ma = Marshmallow()

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role

class UserSchema(ma.SQLAlchemyAutoSchema):
    # We add a custom field 'is_admin' for React
    is_admin = fields.Method("get_is_admin")

    def get_is_admin(self, obj):
        # Returns True if user has 'Manager' role
        return obj.has_role('Manager')

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "is_admin")

class TaskSchema(ma.SQLAlchemyAutoSchema):
    assigned_to = fields.Nested(UserSchema, many=True)
    assigned_to_ids = fields.List(fields.Integer(), load_only=True)

    class Meta:
        model = Task
        include_fk = True

class BillSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Bill

class BusinessDefinitionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BusinessDefinition