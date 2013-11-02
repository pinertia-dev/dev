from pymongo import MongoClient
from bson.objectid import ObjectId
import hashlib


class User:

    client = MongoClient(host=db_config.host, port=db_config.port)
    db = client.pinertia_app
    users = db.users

    def __init__(self, *args, **kwargs):
        self.user_info = dict()
        self.user_info['type'] = kwargs.get('type')
        try:
            units = int(kwargs.get('units'))
            self.user_info['units'] = units
        except:
            self.user_info['units'] = 0
        self.user_info['username'] = kwargs.get('username')
        self.user_info['bio'] = dict()
        self.user_info['teams'] = []
        self.user_info['sports'] = {}
        if 'password' in kwargs.keys():
            m = hashlib.md5()
            m.update(kwargs.get('password'))
            self.user_info['password'] = m.hexdigest()
        self.client = self.__class__.client
        self.db = self.__class__.db
        self.users = self.__class__.users

    def add_team(self, team):
        if 'teams' not in self.user_info.keys():
            self.user_info['teams'] = []
        self.user_info['teams'].append(team)

    def add_sport(self, sport):
        if 'sports' not in self.user_info.keys():
            self.user_info['sports'] = {}
        if sport not in self.user_info.get('sports').keys():
            self.user_info['sports'][sport] = 0

    def incr_units(self, sport=None):
        if not self.user_info.get('units'):
            self.user_info['units'] = 0
        self.user_info['units'] = self.user_info['units'] + 1
        if sport:
            self.user_info['sports'][sport] = self.user_info['sports'][sport] + 1

    def add_to_bio(self, **kwargs):
        for k, v in kwargs.items():
            self.user_info['bio'][k] = v

    def dump_to_json(self):
        from StringIO import StringIO
        import json
        io = StringIO()
        json.dump(self.user_info, io)
        return io.getvalue()

    def save(self):
        if '_id' in self.user_info.keys():
            raise type("%sSaveException"%self.__class__.__name__, (Exception,), {})('Object Alread Exists')
        user_id = self.users.insert(self.user_info)
        return self.users.find_one(dict(_id=user_id))

    def set(self, **kwargs):
        for k, v in kwargs.items():
            self.user_info[k] = v

    def update(self):
        _id = self.user_info.pop('_id')
        self.users.update({'_id': _id}, {'$set': self.user_info}, upsert=False, multi=False)
        return self.users.find_one(dict(_id=self.user_info.get('_id')))

    @staticmethod
    def _loader(**kwargs):
        user = User()
        user.user_info = kwargs
        return user
    
    @staticmethod
    def load_all(**kwargs):
        db_users = []
        for user in User.users.find(**kwargs):
            db_users.append(User._loader(**user))
        return db_users

    @staticmethod
    def load(user_id):
        user = User()
        db_user = User.users.find_one(dict(_id=ObjectId(user_id)))
        user.user_info = db_user
        return user

    @staticmethod
    def find_by_units(**kwargs):
        param_dict = {}
        db_users = []
        if 'gt' in kwargs.keys():
            param_dict['$gt'] = kwargs.get('gt')
        if 'lt' in kwargs.keys():
            param_dict['$lt'] = kwargs.get('lt')
        for user in User.users.find({'units': param_dict}):
            db_users.append(User._loader(**user))
        return db_users
    
    @staticmethod
    def find_by_sport(sport):
        db_users = []
        for user in User.users.find({'sports': {'$in': [sport]}}):
            db_users.append(User._loader(**user))
        return db_users

    @staticmethod
    def remove(user_id):
        User.users.remove({'_id': ObjectId(user_id)})

