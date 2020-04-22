from google.appengine.ext import ndb

class UsersDB(ndb.Model):
    user_Email = ndb.StringProperty()
    user_Name = ndb.StringProperty()
    followers_List = ndb.StringProperty(repeated = True)
    following_List = ndb.StringProperty(repeated = True)
