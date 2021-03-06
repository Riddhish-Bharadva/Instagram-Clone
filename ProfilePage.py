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
from CommentsDB import CommentsDB
from datetime import datetime
from SearchUser import SearchUser
from CreateNewPost import CreateNewPost
from OtherUserProfile import OtherUserProfile
from Followers import Followers
from Following import Following
from Timeline import Timeline
from ViewAllComments import ViewAllComments

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ProfilePage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user() # Here I am getting all details of logged in user.
        posts_Data = []
        image_Data = []
        image_Key = []
        notification = ""
        followers_count = 0
        following_count = 0
        NumberOfPosts = 0
        temp_Comment = []
        Comments = []
        Commenting_User = []
        NumberOfComments = []
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
            posts_Data = PostsDB.query(PostsDB.user_Email == userLoggedIn.user_Email).get()
            if posts_Data != None:
                NumberOfPosts = len(posts_Data.post_Caption)
                for i in range(0,NumberOfPosts):
                    image_Data.append(get_serving_url(posts_Data.post_Image[i]))
                    image_Key.append(posts_Data.post_Image[i])
            for i in range(0,len(image_Key)):
                comments_Data = ndb.Key('CommentsDB',str(image_Key[i])).get()
                if comments_Data != None:
                    Comments.append(comments_Data.comment)
                    Commenting_User.append(comments_Data.commenting_User)
                    NumberOfComments.append(len(comments_Data.comment))
                else:
                    Comments.append([])
                    Commenting_User.append([])
                    NumberOfComments.append(0)
            notification = self.request.get('notification')
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
            'posts_Data' : posts_Data,
            'notification' : notification,
            'followers_count' : followers_count,
            'following_count' : following_count,
            'NumberOfPosts' : NumberOfPosts,
            'image_Data' : image_Data,
            'image_Key' : image_Key,
            'Comments' : Comments,
            'Commenting_User' : Commenting_User,
            'NumberOfComments' : NumberOfComments,
        }
        template = JINJA_ENVIRONMENT.get_template('ProfilePage.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user()
        ButtonOption = self.request.get('submitButton')
        if ButtonOption == "Select": # This is functionality of selecting user name for first time.
            FirstTimeUserName = self.request.get('FirstTimeUserName')
            FirstTimeUserName = FirstTimeUserName.lower()
            UsersDB_Reference = UsersDB.query(UsersDB.user_Name == FirstTimeUserName).get()
            if UsersDB_Reference == None:
                UsersDB_Reference = ndb.Key('UsersDB',userLoggedIn.email()).get()
                UsersDB_Reference.user_Name = FirstTimeUserName
                UsersDB_Reference.put()
                self.redirect("/ProfilePage?notification=Username Selected")
            else:
                self.redirect("/ProfilePage?notification=Username Already Exist")
        elif ButtonOption == "Comment":
            userLoggedIn = ndb.Key('UsersDB',userLoggedIn.email()).get()
            image_Key = self.request.get('image_Key')
            CommentBox = self.request.get('CommentBox')
            comments_Data = ndb.Key('CommentsDB',image_Key).get()
            if comments_Data == None:
                comments_Data = CommentsDB(id=str(image_Key))
            comments_Data.commenting_User.append(userLoggedIn.user_Name)
            comments_Data.comment.append(CommentBox)
            comments_Data.put()
            self.redirect('/ProfilePage?notification=CommentAddedSuccessfully')

app = webapp2.WSGIApplication([
    ('/',ProfilePage),
    ('/ProfilePage',ProfilePage),
    ('/createNewPost',CreateNewPost),
    ('/SearchUser',SearchUser),
    ('/otherUserProfile',OtherUserProfile),
    ('/followers',Followers),
    ('/following',Following),
    ('/timeline',Timeline),
    ('/ViewAllComments',ViewAllComments),
], debug=True)
