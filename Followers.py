import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
from UsersDB import UsersDB
from PostsDB import PostsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class Followers(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user() # Here I am getting all details of logged in user.
        UserEmail = ''
        UserProfile = []
        if userLoggedIn: # If any user is logged in, there will be some data in userLoggedIn variable.
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            userDB_Reference = ndb.Key('UsersDB', userLoggedIn.email()).get() # Here I am checking if current user already have record in my DB or not.
            if userDB_Reference == None: # If user record does not exist in DB, variable will be None.
                userDB_Reference = UsersDB(id=userLoggedIn.email())
                userDB_Reference.user_Email = userLoggedIn.email()
                userDB_Reference.put()
            UserEmail = self.request.get('user_Email') # If any value is passed in url for user email id, it will be fetched here.
            if UserEmail == '': # In case no user email is sent in url from previous page, email id taken will be currently logged in user's email id.
                UserEmail = userLoggedIn.email()
            UserProfile = ndb.Key('UsersDB',UserEmail).get()

        else: # If no user is logged in, there will be no data in userLoggedIn variable.
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'
            self.redirect('/ProfilePage')

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'UserProfile' : UserProfile
        }
        template = JINJA_ENVIRONMENT.get_template('Followers.html')
        self.response.write(template.render(template_values))


    def post(self):
        self.redirect('/ProfilePage')

app = webapp2.WSGIApplication([
    ('/followers',Followers),
], debug=True)
