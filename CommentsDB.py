from google.appengine.ext import ndb

class CommentsDB(ndb.Model):
    commenting_User = ndb.StringProperty(repeated=True)
    comment = ndb.StringProperty(repeated=True)
