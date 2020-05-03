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

class Timeline(webapp2.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/html'

        # Declaration of required variables start here.
        Following_Users = []
        DateTime = []
        Last50DateTime = []
        timeline_Post_Count = 0
        timeline_Post_Users = []
        timeline_Post_Image_Key = []
        timeline_Post_Image_Urls = []
        timeline_Post_Captions = []
        Comments = []
        Commenting_User = []
        NumberOfComments = []
        # Declaration of required variables ends here.

        userLoggedIn = users.get_current_user() # Here I am getting all details of logged in user.
        if userLoggedIn: # If any user is logged in, there will be some data in userLoggedIn variable.
            loginLink = users.create_logout_url(self.request.uri)
            loginStatus = 'Logout'

            Following_Users.append(userLoggedIn.email()) # Here, I am appending currently logged in user's email id as we want to display his own posts as well in timeline.
            userDB_Reference = ndb.Key('UsersDB', userLoggedIn.email()).get() # Here I am checking if current user already have record in my DB or not.
            for i in range(0,len(userDB_Reference.following_List)): # In this for loop, all users followed by currently loggedin user are appended in list.
                Following_Users.append(userDB_Reference.following_List[i])
            for i in range(0,len(Following_Users)): # This loop handles to collect all post data.
                post_Data = ndb.Key('PostsDB',Following_Users[i]).get()
                if post_Data != None:
                    for j in range(0,len(post_Data.post_DateTime)):
                        DateTime.append(post_Data.post_DateTime[j])
            DateTime.sort(reverse=True)

            if len(DateTime) <= 50: # Incase post count of currently logged in user and it's following users is less than or equal to 50.
                timeline_Post_Count = len(DateTime)
            else: # Incase post count of currently logged in user and it's following users is more than 50.
                timeline_Post_Count = 50

            for i in range(0,timeline_Post_Count): # Pulling only last 50 DateTime data from all date time data list.
                Last50DateTime.append(DateTime[i])
            DateTime = []
            for i in range(0,timeline_Post_Count): # Converting Post DateTime in required Format to display on Web Page.
                DateTime.append(Last50DateTime[i].strftime('%d-%m-%Y at %X'))
            i = 0
            while i < timeline_Post_Count: # This while loop runs for total number of posts if < 50 else runs for 50 iterations.
                DataMatch = False # This initializes counter for each post.
                j = 0
                while j < len(Following_Users): # This while loop runs for total number of users following currently loggedin user plus for logged in user.
                    if DataMatch == False: # Below code will run only if post is not found in any user previously.
                        post_Data = ndb.Key('PostsDB',Following_Users[j]).get()
                        if post_Data != None:
                            k = 0
                            while k < len(post_Data.post_DateTime): # This while loop runs to total number of Posts each user is having.
                                if post_Data.post_DateTime[k] == Last50DateTime[i]:
                                    timeline_Post_Users.append(Following_Users[j])
                                    timeline_Post_Image_Key.append(str(post_Data.post_Image[k]))
                                    timeline_Post_Image_Urls.append(get_serving_url(post_Data.post_Image[k]))
                                    timeline_Post_Captions.append(post_Data.post_Caption[k])
                                    DataMatch = True # In case post if found in any user, counter will be set to True. Hence, no loop will run for same post again.
                                    break # In case post is found in any user, while loop will break.
                                else:
                                    k = k + 1
                        j = j + 1
                    else:
                        break # Checking if counter is True, break loop.
                i = i + 1 # This handles to move on to next post in list.
            # Below is logic of fetching comments.
            for i in range(0,len(timeline_Post_Image_Key)):
                comments_Data = ndb.Key('CommentsDB',str(timeline_Post_Image_Key[i])).get()
                if comments_Data != None: # In case post is commented by any user, fetch and append them into below variables.
                    Comments.append(comments_Data.comment)
                    Commenting_User.append(comments_Data.commenting_User)
                    NumberOfComments.append(len(comments_Data.comment))
                else: # In case post is not commented by any user, append blanks.
                    Comments.append([])
                    Commenting_User.append([])
                    NumberOfComments.append(0)
        else: # If no user is logged in, there will be no data in userLoggedIn variable.
            loginLink = users.create_login_url(self.request.uri)
            loginStatus = 'Login'
            self.redirect('/ProfilePage')

        template_values = {
            'loginLink' : loginLink,
            'loginStatus' : loginStatus,
            'userLoggedIn' : userLoggedIn,
            'Following_Users' : Following_Users,
            'timeline_Post_Count' : timeline_Post_Count,
            'DateTime' : DateTime,
            'timeline_Post_Users' : timeline_Post_Users,
            'timeline_Post_Image_Key' : timeline_Post_Image_Key,
            'timeline_Post_Image_Urls' : timeline_Post_Image_Urls,
            'timeline_Post_Captions' : timeline_Post_Captions,
            'Comments' : Comments,
            'Commenting_User' : Commenting_User,
            'NumberOfComments' : NumberOfComments,
        }
        template = JINJA_ENVIRONMENT.get_template('Timeline.html')
        self.response.write(template.render(template_values))

    def post(self):
        self.response.headers['content-type'] = 'text/html'
        userLoggedIn = users.get_current_user()
        userLoggedIn = ndb.Key('UsersDB',userLoggedIn.email()).get()
        image_Key = self.request.get('image_Key')
        CommentBox = self.request.get('CommentBox')
        comments_Data = ndb.Key('CommentsDB',image_Key).get()
        if comments_Data == None:
            comments_Data = CommentsDB(id=str(image_Key))
        comments_Data.commenting_User.append(userLoggedIn.user_Name)
        comments_Data.comment.append(CommentBox)
        comments_Data.put()
        self.redirect('/timeline')

app = webapp2.WSGIApplication([
    ('/timeline',Timeline),
], debug=True)
