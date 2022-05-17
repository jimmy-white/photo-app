from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
                # Your code here
        followings = Following.query.filter_by(user_id = self.current_user.id).all()
        # print(bookmarks)

        following_list_of_dictionaries = [
            following.to_dict_following() for following in followings
        ]
        return Response(json.dumps(following_list_of_dictionaries), mimetype="application/json", status=200)

    def post(self):
        req = request.get_json()
        if not req: 
            return Response(json.dumps({'message': 'Post: bad data'}), mimetype="application/json", status=400)

        followingid = req.get('user_id')

        if not str(followingid).isdigit(): 
            return Response(json.dumps({'message': 'Post: bad user_id'}), mimetype="application/json", status=400)

        try: 
            user = User.query.get(followingid)
        
        except: 
            return Response(json.dumps({'message': 'Post: bad user_id'}), mimetype="application/json", status=400)

        if not user: 
            return Response(json.dumps({'message': 'Post: bad user_id 404'}), mimetype="application/json", status=404)  

        try: 
            following = Following(self.current_user.id, followingid) 
            db.session.add(following)
            db.session.commit()

        except: 
            return Response(json.dumps({'message': 'Post: No Repeats'}), mimetype="application/json", status=400)  

        return Response(json.dumps(following.to_dict_following()), mimetype="application/json", status=201)  


class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # Your code here
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'DELETE: bad id'}), mimetype="application/json", status=400)
        following = Following.query.get(id)
        
        if not following: 
            return Response(json.dumps({'message': 'DELETE: doesnt exist'}), mimetype="application/json", status=404)  

        if following.user_id != self.current_user.id: 
            return Response(json.dumps({'message': 'DELETE: not authorized 404'}), mimetype="application/json", status=404)


        Following.query.filter_by(id=id).delete()
        db.session.commit()
        s_data = {
            'message': 'Post {0} successfully delete.'.format(id)
        }
        return Response(json.dumps(s_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<id>', 
        '/api/following/<id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
