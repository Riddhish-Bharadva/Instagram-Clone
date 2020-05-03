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

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class ViewAllComments(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user()
        user_Details = []
        post_Caption = ""
        post_Image_URL = ""
        Comments = []
        Commenting_User = []
        NumberOfComments = 0
        user_Email = self.request.get('user_Email') # Getting user email id passed in url.
        image_Key = self.request.get('image_Key') # Getting image key passed in url.
        post_Image_URL = get_serving_url(image_Key) # Storing image url of passed image Key.
        if userLoggedIn: # If any user is logged in, there will be some data in userLoggedIn variable.
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'
            user_Details = ndb.Key('UsersDB',user_Email).get() # Fetching data from UsersDB to get all details of user.
            post_Data = ndb.Key('PostsDB',user_Email).get() # Fetching data from PostsDB to get all posts information of user.
            for i in range(0,len(post_Data.post_Caption)):
                if post_Data.post_Image[i] == image_Key: # I am comparing image key to get position of caption in caption list.
                    post_Caption = post_Data.post_Caption[i]
                    break
            comments_Data = ndb.Key('CommentsDB',image_Key).get()
            if comments_Data != None:
                for i in range(len(comments_Data.comment)-1,-1,-1):
                    Commenting_User.append(comments_Data.commenting_User[i])
                    Comments.append(comments_Data.comment[i])
                NumberOfComments = len(Comments)
        else: # If no user is logged in, there will be no data in userLoggedIn variable.
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'
            self.redirect('/ProfilePage')

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'user_Email' : user_Email,
            'post_Caption' : post_Caption,
            'user_Details' : user_Details,
            'post_Image_URL' : post_Image_URL,
            'Comments' : Comments,
            'Commenting_User' : Commenting_User,
            'image_Key' : image_Key,
            'NumberOfComments' : NumberOfComments,
        }
        template = JINJA_ENVIRONMENT.get_template('ViewAllComments.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user()
        userLoggedIn = ndb.Key('UsersDB',userLoggedIn.email()).get()
        user_Email = self.request.get('user_Email')
        image_Key = self.request.get('image_Key')
        CommentBox = self.request.get('CommentBox')
        comments_Data = ndb.Key('CommentsDB',image_Key).get()
        if comments_Data == None:
            comments_Data = CommentsDB(id=str(image_Key))
        comments_Data.commenting_User.append(userLoggedIn.user_Name)
        comments_Data.comment.append(CommentBox)
        comments_Data.put()
        self.redirect('/ViewAllComments?user_Email='+user_Email+'&image_Key='+image_Key)

app = webapp2.WSGIApplication([
    ('/ViewAllComments',ViewAllComments),
], debug=True)
