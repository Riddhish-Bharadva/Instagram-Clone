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
        userLoggedIn = users.get_current_user() # Here I am getting all details of logged in user.
        Following_Users = []
        temp_Timeline_Post_Captions = []
        temp_Timeline_Post_Image_Urls = []
        temp_Timeline_Post_Key = []
        temp_Post_Caption = []
        temp_Post_Urls = []
        temp_Post_Key = []
        timeline_Post_Count = 0
        timeline_Post_Captions = []
        timeline_Post_Image_Urls = []
        timeline_Post_Key = []
        timeline_Post_Users = []
        Following_Users_Posts_Count = []
        NumberOfUsers = 0
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
            Following_Users.append(userLoggedIn.user_Email) # Here, I am appending currently logged in user's email id as we want to display his own posts as well in timeline.
            for user in userLoggedIn.following_List: # In this for loop, all users followed by currently loggedin user are appended in list.
                Following_Users.append(user)
            NumberOfUsers = len(Following_Users)
            for i in Following_Users: # I am going to first put all data of all users followed by currently loggedin user into single list.
                post_Data = ndb.Key('PostsDB',i).get()
                if post_Data != None:
                    Following_Users_Posts_Count.append(len(post_Data.post_Image))
                    for j in range(len(post_Data.post_Image)-1,-1,-1): # I am running this loop in descending order to fetch latest data first in list.
                        temp_Post_Caption.append(post_Data.post_Caption[j])
                        temp_Post_Urls.append(get_serving_url(post_Data.post_Image[j]))
                        temp_Post_Key.append(post_Data.post_Image[j])
                        timeline_Post_Count = timeline_Post_Count + 1
                    # Now I am appending the above fetched data into temporary lists.
                    temp_Timeline_Post_Captions.append(temp_Post_Caption)
                    temp_Timeline_Post_Image_Urls.append(temp_Post_Urls)
                    temp_Timeline_Post_Key.append(temp_Post_Key)
                    # Now I will empty below temporary lists to fetch data for next user in next iteration of this for loop.
                    temp_Post_Caption = []
                    temp_Post_Urls = []
                    temp_Post_Key = []
                else:
                    # Now I am appending 0 and blank list in case there are no posts.
                    Following_Users_Posts_Count.append(0)
                    temp_Timeline_Post_Captions.append([])
                    temp_Timeline_Post_Image_Urls.append([])
                    temp_Timeline_Post_Key.append([])
            if Following_Users_Posts_Count != []:
                Max_Loop_Run = max(Following_Users_Posts_Count) # Here, I am defining maximum times my below for loop will run. This is because I want to run my loop for maximum number of post a user is having amongst list of users in Following_Users list.
                for i in range(0,Max_Loop_Run):
                    for j in range(0,NumberOfUsers):
                        if i < len(temp_Timeline_Post_Captions[j]):
                            timeline_Post_Captions.append(temp_Timeline_Post_Captions[j][i]) # I am appending caption of 1st user then 2nd user then 3rd user and so on till for loop ends.
                            timeline_Post_Image_Urls.append(temp_Timeline_Post_Image_Urls[j][i]) # I am appending Image URLs of 1st user then 2nd user then 3rd user and so on till for loop ends.
                            timeline_Post_Key.append(temp_Timeline_Post_Key[j][i]) # I am appending Image Keys of 1st user then 2nd user then 3rd user and so on till for loop ends.
                if timeline_Post_Count > 50: # In case number of Posts in defined list is more then 50, it will set timeline_Post_Count to 50 as we want to display only last 50 posts in reverse chronological order.
                    timeline_Post_Count = 50
                # Below if logic to fetch users of each posts.
                image_URLs = timeline_Post_Image_Urls
                for i in range(0,timeline_Post_Count):
                    temp_Reference = PostsDB.query(PostsDB.post_Image == timeline_Post_Key[i]).fetch()
                    timeline_Post_Users.append(temp_Reference[0].user_Email)
                # Below is logic of fetching comments.
                for i in range(0,len(timeline_Post_Key)):
                    comments_Data = ndb.Key('CommentsDB',str(timeline_Post_Key[i])).get()
                    if comments_Data != None:
                        Comments.append(comments_Data.comment)
                        Commenting_User.append(comments_Data.commenting_User)
                        NumberOfComments.append(len(comments_Data.comment))
                    else:
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
            'NumberOfUsers' : NumberOfUsers,
            'Following_Users' : Following_Users,
            'Following_Users_Posts_Count' : Following_Users_Posts_Count,
            'timeline_Post_Count' : timeline_Post_Count,
            'timeline_Post_Captions' : timeline_Post_Captions,
            'timeline_Post_Image_Urls' : timeline_Post_Image_Urls,
            'image_Key' : timeline_Post_Key,
            'timeline_Post_Users' : timeline_Post_Users,
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
