from sqlalchemy import inspect

from models import Teacher, Class, Subject, Course, Icon


def add_to_dict_method(cls):
    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        if hasattr(self, '__mapper__'):
            for relationship_name, relationship_obj in inspect(self.__mapper__).relationships.items():
                if relationship_obj.lazy == "joined" and getattr(self, relationship_name):
                    result[relationship_name] = getattr(self, relationship_name).to_dict()

        return result

    cls.to_dict = to_dict
    return cls


for model in (Teacher, Class, Subject, Course, Icon):
    add_to_dict_method(model)
