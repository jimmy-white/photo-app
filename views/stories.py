from flask import Response
from flask_restful import Resource
from models import Story
from views import get_authorized_user_ids
import json

class StoriesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        '''
        Get all stories
        '''
        stories_ids = get_authorized_user_ids(self.current_user)
        stories = Story.query.filter(Story.user_id.in_(stories_ids)).all()
        stories_dict = [story.to_dict() for story in stories]
        return Response(json.dumps(stories_dict), mimetype="application/json", status=200)
        # get stories created by one of these users:
        # print(get_authorized_user_ids(self.current_user))
        #return Response(json.dumps([]), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        StoriesListEndpoint, 
        '/api/stories', 
        '/api/stories/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
