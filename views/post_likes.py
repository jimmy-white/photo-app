from flask import Response, request
from flask_restful import Resource
from models import LikePost, db, Post
import json
from . import can_view_post, get_authorized_user_ids

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self, post_id):
        try: 
            post_id = int(post_id)

        except: 
            return Response(json.dumps({'message': 'DELETE: not an int'}), mimetype="application/json", status=400)

        likes = Post.query.get(post_id)
        if not likes: 
            return Response(json.dumps({'message': 'DELETE: id doenst exist'}), mimetype="application/json", status=404)

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
    
    def delete(self, post_id, id):
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'DELETE: bad id'}), mimetype="application/json", status=400)
        post_likes = LikePost.query.get(id)
        
        if not post_likes: 
            return Response(json.dumps({'message': 'DELETE: doesnt exist'}), mimetype="application/json", status=404)  

        if not can_view_post(post_likes.user_id,self.current_user):
            return Response(json.dumps({'message': 'DELETE: not authorized 404'}), mimetype="application/json", status=404)

        LikePost.query.filter_by(id=id).delete()
        db.session.commit()
        s_data = {
            'message': 'Post {0} successfully delete.'.format(id)
        }
        return Response(json.dumps(s_data), mimetype="application/json", status= 200)



def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/<post_id>/likes', 
        '/api/posts/<post_id>/likes/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/<post_id>/likes/<id>', 
        '/api/posts/<post_id>/likes/<id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
