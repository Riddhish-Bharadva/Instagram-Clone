import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
from UsersDB import UsersDB
from PostsDB import PostsDB

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class SearchUser(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'
        self.redirect('/ProfilePage')

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user() # Here I am getting all details of logged in user.
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
        else: # If no user is logged in, there will be no data in userLoggedIn variable.
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'
            self.redirect('/ProfilePage')

        UserSearchKeyword = self.request.get('UserSearchKeyword')
        Query = UsersDB.query().fetch()
        QueryResults = []
        for i in range(0,len(Query)):
            if Query[i].user_Email.find(UserSearchKeyword) != -1:
                QueryResults.append(Query[i].user_Email)
            elif Query[i].user_Name.find(UserSearchKeyword) != -1:
                QueryResults.append(Query.user_Email[i])

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'Results' : QueryResults
        }
        template = JINJA_ENVIRONMENT.get_template('SearchUser.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/SearchUser',SearchUser),
], debug=True)
