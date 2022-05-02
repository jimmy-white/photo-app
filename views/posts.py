from flask import Response, request
from flask_restful import Resource
from models import Post, db, Following
from views import get_authorized_user_ids

import json

def get_path():
    return request.host_url + 'api/posts/'

class PostListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):
        userAndFriendsIds = get_authorized_user_ids(self.current_user)
        posts = Post.query.filter(Post.user_id.in_(userAndFriendsIds))
        limit = request.args.get('limit')

        if limit: 
            try: 
                limit = int(limit)
            except: 
                return Response(json.dumps({'message': 'invalid limit'}), mimetype="application/json", status=400)

            if limit > 50 or limit < 1: 
                return Response(json.dumps({'message': 'number of posts must be between 1 and 50'}), mimetype="application/json", status=400)
        else: 
            limit = 20

        posts = posts.order_by(Post.pub_date.desc()).limit(limit)
        data = [item.to_dict() for item in posts.all()]

        return Response(json.dumps(data), mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()
        
        if not body: 
            return Response(json.dumps({'message': 'bad data'}), mimetype="application/json", status=400)

        image_url = body.get('image_url')
        caption = body.get('caption')
        alt_text = body.get('alt_text')
        user_id = self.current_user.id
        post = Post(image_url, user_id, caption, alt_text)

        db.session.add(post)
        db.session.commit()
        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=201)
        
class PostDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        

    def patch(self, id):
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'Invalid ID '}), mimetype="application/json", status=400)

        post = Post.query.get(id)

        if not post or post.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
       
        body = request.get_json()
        post.image_url = body.get('image_url') or post.image_url
        post.caption = body.get('caption') or post.caption
        post.alt_text = body.get('alt_text') or post.alt_text
        
        db.session.commit()        
        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)


    def delete(self, id):
        if not str(id).isdigit(): 
            return Response(json.dumps({'message': 'invalid Id '}), mimetype="application/json", status=400)
        
        post = Post.query.get(id)
        if not post or post.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
       

        Post.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Post {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)


    def get(self, id):
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'invalid ID'}), mimetype="application/json", status=400)
        
        post = Post.query.get(id)

        if not post or post.user_id not in get_authorized_user_ids(self.current_user):
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
        
        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        PostListEndpoint, 
        '/api/posts', '/api/posts/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        PostDetailEndpoint, 
        '/api/posts/<int:id>', '/api/posts/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )