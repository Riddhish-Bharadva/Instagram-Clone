from google.appengine.ext import ndb

class PostsDB(ndb.Model):
    user_Email = ndb.StringProperty()
    post_Caption = ndb.StringProperty(repeated = True)
    post_Image = ndb.BlobKeyProperty(repeated = True)
    post_DateTime = ndb.DateTimeProperty(repeated = True)
    comments = ndb.StringProperty(repeated = True)
    commenting_User = ndb.StringProperty(repeated = True)
