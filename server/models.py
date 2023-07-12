#  

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

# Add relationship

    signups = db.relationship('Signup', backref='activity', cascade='all, delete-orphan')

# researched and used cascade='all, delete-orphan' 
# this option helps keep everything tidy by 
# automatically getting rid of child objects when we remove parent objects.
    campers = association_proxy('signups', 'camper')
    
# Add serialization rules

    serializer_rules = ("-signups.activity",)

    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

# Add relationship

    signups = db.relationship('Signup', backref='camper', cascade='all, delete-orphan')
    
# Add serialization rules

    serializer_rules = ("-signups.camper",)
    
# Add validations

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Camper must have a name")
        return name

    @validates('age')
    def validate_age(self, key, age):
        if age is not None and (age < 8 or age > 18):
            raise ValueError("Camper age must be between 8 and 18")
        return age
    
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

# Add relationships

    camper_id = db.Column(db.Integer, ForeignKey('campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, ForeignKey('activities.id'), nullable=False)
    
# Add serialization rules

    serializer_rules = ("-camper.signups", "-activity.signups")
    
# Add validation

    @validates('time')
    def validate_time(self, key, time):
        if time is not None and (time < 0 or time > 23):
            raise ValueError("Signup time must be between 0 and 23")
        return time
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.

# **********************************************************
# DRY CODE
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import MetaData, ForeignKey
# from sqlalchemy.orm import validates
# from sqlalchemy.ext.associationproxy import association_proxy
# from sqlalchemy_serializer import SerializerMixin

# convention = {
#     "ix": "ix_%(column_0_label)s",
#     "uq": "uq_%(table_name)s_%(column_0_name)s",
#     "ck": "ck_%(table_name)s_%(constraint_name)s",
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#     "pk": "pk_%(table_name)s"
# }

# metadata = MetaData(naming_convention=convention)

# db = SQLAlchemy(metadata=metadata)


# class BaseModel(db.Model, SerializerMixin):
#     __abstract__ = True

#     @classmethod
#     def get_all(cls):
#         return cls.query.all()

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

#     def delete(self):
#         db.session.delete(self)
#         db.session.commit()

# # The BaseModel class is an abstract base class that extends db.Model (from SQLAlchemy) and SerializerMixin. 
# # It provides common functionality that can be inherited by other models in your application.


# class Activity(BaseModel):
#     __tablename__ = 'activities'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     difficulty = db.Column(db.Integer)

#     signups = db.relationship('Signup', backref='activity', cascade='all, delete-orphan')
#     campers = association_proxy('signups', 'camper')

#     serializer_rules = ("-signups.activity",)

#     def __repr__(self):
#         return f'<Activity {self.id}: {self.name}>'


# class Camper(BaseModel):
#     __tablename__ = 'campers'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     age = db.Column(db.Integer)

#     signups = db.relationship('Signup', backref='camper', cascade='all, delete-orphan')

#     serializer_rules = ("-signups.camper",)

#     @validates('name')
#     def validate_name(self, key, name):
#         if not name:
#             raise ValueError("Camper must have a name")
#         return name

#     @validates('age')
#     def validate_age(self, key, age):
#         if age is not None and (age < 8 or age > 18):
#             raise ValueError("Camper age must be between 8 and 18")
#         return age

#     def __repr__(self):
#         return f'<Camper {self.id}: {self.name}>'


# class Signup(BaseModel):
#     __tablename__ = 'signups'

#     id = db.Column(db.Integer, primary_key=True)
#     time = db.Column(db.Integer)

#     camper_id = db.Column(db.Integer, ForeignKey('campers.id'), nullable=False)
#     activity_id = db.Column(db.Integer, ForeignKey('activities.id'), nullable=False)

#     serializer_rules = ("-camper.signups", "-activity.signups")

#     @validates('time')
#     def validate_time(self, key, time):
#         if time is not None and (time < 0 or time > 23):
#             raise ValueError("Signup time must be between 0 and 23")
#         return time

#     def __repr__(self):
#         return f'<Signup {self.id}>'


