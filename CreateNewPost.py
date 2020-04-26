import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import get_serving_url
from UsersDB import UsersDB
from PostsDB import PostsDB
from datetime import datetime

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class CreateNewPost(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user() # Here I am getting all details of logged in user.
        followers_count = 0
        following_count = 0
        ImageUpload = blobstore.create_upload_url("/createNewPost")
        if userLoggedIn: # If any user is logged in, there will be some data in userLoggedIn variable.
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            userDB_Reference = ndb.Key('UsersDB', userLoggedIn.email()).get() # Here I am checking if current user already have record in my DB or not.
            if userDB_Reference == None: # If user record does not exist in DB, variable will be None.
                userDB_Reference = UsersDB(id=userLoggedIn.email())
                userDB_Reference.user_Email = userLoggedIn.email()
                userDB_Reference.put()
                userLoggedIn = userDB_Reference
            else: # If user record exist in DB, variable will not be None.
                userLoggedIn = userDB_Reference
            if userLoggedIn.followers_List != None:
                followers_count = len(userLoggedIn.followers_List) # Here count of followers will be fetched.
            if userLoggedIn.following_List != None:
                following_count = len(userLoggedIn.following_List) # Here count of followings will be fetched.
        else: # If no user is logged in, there will be no data in userLoggedIn variable.
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'followers_count' : followers_count,
            'following_count' : following_count,
            'ImageUpload' : ImageUpload
        }
        template = JINJA_ENVIRONMENT.get_template('CreateNewPost.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user()
        post_Caption = self.request.get('NewPostCaption')
        if post_Caption == "":
            post_Caption = "No caption given"
        DateTimeValue = datetime.now()
        Image = self.get_uploads()[0]
        PostsDB_Reference = PostsDB.query(PostsDB.user_Email == userLoggedIn.email()).get()
        if PostsDB_Reference == None:
            PostsDB_Reference = PostsDB(id = userLoggedIn.email())
            PostsDB_Reference.user_Email = userLoggedIn.email()
        PostsDB_Reference.post_Caption.append(post_Caption)
        PostsDB_Reference.post_DateTime.append(DateTimeValue)
        PostsDB_Reference.post_Image.append(Image.key())
        PostsDB_Reference.put()
        self.redirect('/ProfilePage?notification=NewPostCreatedSuccessfully')

app = webapp2.WSGIApplication([
    ('/createNewPost',CreateNewPost),
], debug=True)
