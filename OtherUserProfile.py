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

class OtherUserProfile(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'
        OtherUserEmail = self.request.get('OtherUserEmail')
        posts_Data = []
        image_Data = []
        followers_count = 0
        following_count = 0
        NumberOfPosts = 0
        OtherUserProfile = []
        userLoggedIn = users.get_current_user()
        current_User_Following_Decision = 0
        if userLoggedIn: # If any user is logged in, there will be some data in userLoggedIn variable.
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            if userLoggedIn.email() == OtherUserEmail:
                self.redirect('/ProfilePage')
            else:
                OtherUserProfile = ndb.Key('UsersDB',OtherUserEmail).get() # Here I am fetching record of user data on which currently loggedin user have clicked.
                CurrentUserProfile = ndb.Key('UsersDB',userLoggedIn.email()).get() # Here I am fetching record of user currently loggedin.
                if CurrentUserProfile.following_List != None:
                    for i in range(0,len(CurrentUserProfile.following_List)):
                        if OtherUserEmail == CurrentUserProfile.following_List[i]:
                            current_User_Following_Decision = 1
                            break
                else:
                    current_User_Following_Decision = 0
                posts_Data = PostsDB.query(PostsDB.user_Email == OtherUserProfile.user_Email).get()
                if posts_Data != None:
                    NumberOfPosts = len(posts_Data.post_Caption)
                    for i in range(0,NumberOfPosts):
                        image_Data.append(get_serving_url(posts_Data.post_Image[i]))
                if OtherUserProfile.followers_List != None:
                    followers_count = len(OtherUserProfile.followers_List) # Here count of followers will be fetched.
                if OtherUserProfile.following_List != None:
                    following_count = len(OtherUserProfile.following_List) # Here count of followings will be fetched.
        else: # If no user is logged in, there will be no data in userLoggedIn variable.
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'
            self.redirect('/ProfilePage')

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'otherUserProfile' : OtherUserProfile,
            'posts_Data' : posts_Data,
            'followers_count' : followers_count,
            'following_count' : following_count,
            'NumberOfPosts' : NumberOfPosts,
            'image_Data' : image_Data,
            'current_User_Following_Decision' : current_User_Following_Decision
        }
        template = JINJA_ENVIRONMENT.get_template('OtherUserProfile.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user()
        CurrentUserProfile = ndb.Key('UsersDB', userLoggedIn.email()).get()
        OtherUserEmail = self.request.get('user_Email')
        OtherUserProfile = ndb.Key('UsersDB', OtherUserEmail).get()
        ButtonOption = self.request.get('submitButton')
        if ButtonOption == "Follow": # This is functionality of following user.
            CurrentUserProfile.following_List.append(OtherUserEmail)
            OtherUserProfile.followers_List.append(userLoggedIn.email())
            CurrentUserProfile.put()
            OtherUserProfile.put()
            self.redirect('/otherUserProfile?OtherUserEmail='+OtherUserEmail)
        elif ButtonOption == 'Unfollow':
            for i in range(0,len(CurrentUserProfile.following_List)):
                if CurrentUserProfile.following_List[i] == OtherUserEmail:
                    del CurrentUserProfile.following_List[i]
                    CurrentUserProfile.put()
                    break
            for j in range(0,len(OtherUserProfile.followers_List)):
                if OtherUserProfile.followers_List[j] == CurrentUserProfile.user_Email:
                    del OtherUserProfile.followers_List[j]
                    OtherUserProfile.put()
                    break
            self.redirect('/otherUserProfile?OtherUserEmail='+OtherUserEmail)

app = webapp2.WSGIApplication([
    ('/otherUserProfile',OtherUserProfile),
], debug=True)
