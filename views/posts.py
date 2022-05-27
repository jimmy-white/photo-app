from flask import Response, request
from flask_restful import Resource
from models import Post, db, Following
from views import get_authorized_user_ids, can_view_post

import json
import flask_jwt_extended

def get_path():
    return request.host_url + 'api/posts/'

class PostListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    @flask_jwt_extended.jwt_required()
    def get(self):
        ids_for_me_and_my_friends = get_authorized_user_ids(self.current_user)
        posts = Post.query.filter(Post.user_id.in_(ids_for_me_and_my_friends))
        limit = request.args.get('limit')

        if limit: 
            try: 
                limit = int(limit)
            except: 
                return Response(json.dumps({'message': 'must be b/w 1 and 50'}), mimetype="application/json", status=400)

            if limit > 50 or limit <1: 
                return Response(json.dumps({'message': 'must be b/w 1 and 50'}), mimetype="application/json", status=400)
        else: 
            limit = 20 
        posts = posts.order_by(Post.pub_date.desc()).limit(limit)
        data = [
            item.to_dict(user=self.current_user) for item in posts.all()
        ]
        return Response(json.dumps(data), mimetype="application/json", status=200)
        # 1. No security implemented; 
        # 2. limit is hard coded (versus coming from the query parameter)
        # 3. No error checking
    
        
        #return Response(json.dumps([]), mimetype="application/json", status=200)
    
    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new post based on the data posted in the body 
        body = request.get_json()
        print(body)
        if not body: 
            return Response(json.dumps({'message': 'bad data'}), mimetype="application/json", status=400)


        image_url = body.get('image_url')
        caption = body.get('caption')
        alt_text = body.get('alt_text')
        user_id = self.current_user.id # id of the user who is logged in
        
        # create post:
        post = Post(image_url, user_id, caption, alt_text)
        db.session.add(post)
        db.session.commit()
        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=201)
        
class PostDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        
    @flask_jwt_extended.jwt_required()
    def patch(self, id):
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'Invalid ID '}), mimetype="application/json", status=400)
        post = Post.query.get(id)

        # a user can only edit their own post:
        if not post or post.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
       

        body = request.get_json()
        post.image_url = body.get('image_url') or post.image_url
        post.caption = body.get('caption') or post.caption
        post.alt_text = body.get('alt_text') or post.alt_text
        
        # commit changes:
        db.session.commit()        
        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        if not str(id).isdigit(): 
            return Response(json.dumps({'message': 'invalid Id '}), mimetype="application/json", status=400)
        # a user can only delete their own post:
        post = Post.query.get(id)
        if not post or post.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
       

        Post.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Post {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    def get(self, id):
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'invalid ID'}), mimetype="application/json", status=400)
        post = Post.query.get(id)

        # if the user is not allowed to see the post or if the post does not exist, return 404:
        if not post:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
        # if not can_view_post(post.id, self.current_user):
        #     return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)

        if post.user_id not in get_authorized_user_ids(self.current_user) :
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
        return Response(json.dumps(post.to_dict(user=self.current_user)), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        PostListEndpoint, 
        '/api/posts', '/api/posts/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
    api.add_resource(
        PostDetailEndpoint, 
        '/api/posts/<int:id>', '/api/posts/<int:id>/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )