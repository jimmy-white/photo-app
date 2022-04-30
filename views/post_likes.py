from flask import Response, request
from flask_restful import Resource
from models import LikePost, db, Post
import json
from . import can_view_post, get_authorized_user_ids

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "following" record based on the data posted in the body
        try: 
            post_id = int(post_id)

        except: 
            return Response(json.dumps({'message': 'DELETE: not an integer'}), mimetype="application/json", status=400)

        #get likes for post
        likes = Post.query.get(post_id)
        if not likes: 
            return Response(json.dumps({'message': 'DELETE: id does not exist'}), mimetype="application/json", status=404)

        elif likes.user_id not in get_authorized_user_ids(self.current_user): 
             return Response(json.dumps({'message': 'DELETE: unauthorizedt'}), mimetype="application/json", status=404)
        try: 
            likes = LikePost(self.current_user.id, post_id)
            db.session.add(likes)
            db.session.commit()
        except: 
             return Response(json.dumps({'message': 'DELETE: like id not created'}), mimetype="application/json", status=400)
        return Response(json.dumps(likes.to_dict()), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'invalid ID'}), mimetype="application/json", status=400)
            # a user can only delete their own post:
        likes = LikePost.query.get(id)
        if not likes:
            return Response(json.dumps({'message': 'like does not exist'}), mimetype="application/json", status=404)
        
        if not can_view_post(likes.user_id, self.current_user.id):
            return Response(json.dumps({'message': 'unauthorized'}), mimetype="application/json", status=404)
    
        # delete "like_post" where "id"=id
        LikePost.query.filter_by(id=id).delete()
        db.session.commit()
        s_data = {
            'message': 'Post {0} deleted successfully'.format(id)
        }
        return Response(json.dumps(s_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/likes', 
        '/api/posts/likes/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/likes/<int:id>', 
        '/api/posts/likes/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
