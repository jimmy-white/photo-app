from flask import Response, request
from flask_restful import Resource
from models import Following, User, db, following
import json

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # people who are following the current user
        followings = Following.query.filter_by(user_id=self.current_user.id).all()
        following_dict = [following.to_dict_following() for following in followings]
        return Response(json.dumps(following_dict), mimetype="application/json", status=200)
        # return all of the "following" records that the current user is following
        #return Response(json.dumps([]), mimetype="application/json", status=200)

    def post(self):
        req = request.get_json()
        if not req:
            return Response(json.dumps({'message': 'bad data'}), mimetype="application/json", status=400)
        following_id = req.get('user_id')
        if not str(following_id).isdigit():
            return Response(json.dumps({'message': 'invalid user_id'}), mimetype="application/json", status=400)
        try:
            user = User.query.get(following_id)
        except:
            return Response(json.dumps({'message': 'bad user id'}), mimetype="application/json", status=400)
        if not user:
            return Response(json.dumps({'message': 'user does not exist'}), mimetype="application/json", status=404)
        try:
            following = Following(self.current_user.id, following_id)
            db.session.add(following)
            db.session.commit()
        except:
            return Response(json.dumps({'message': 'error'}), mimetype="application/json", status=400)
        
        return Response(json.dumps(following.to_dict_following()), mimetype="application/json", status=201)
        
        # create a new "following" record based on the data posted in the body 
        #body = request.get_json()
        #print(body)
        #return Response(json.dumps({}), mimetype="application/json", status=201)

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "following" record where "id"=id
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'invalid ID'}), mimetype="application/json", status=400)
        following = Following.query.get(id)
        if not following:
            return Response(json.dumps({'message': 'following does not exist'}), mimetype="application/json", status=404)
        if following.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'not authorized'}), mimetype="application/json", status=404)
        
        Following.query.filter_by(id=id).delete()
        db.session.commit()
        s_data = {
            'message': 'Post {0} deleted successfully'.format(id)
        }
        return Response(json.dumps(s_data), mimetype="application/json", status=200)
        #print(id)
        #return Response(json.dumps({}), mimetype="application/json", status=200)




def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<int:id>', 
        '/api/following/<int:id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
