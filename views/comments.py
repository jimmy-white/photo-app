from tempfile import tempdir
from flask import Response, request
from flask_restful import Resource
from . import can_view_post, get_authorized_user_ids
import json
from models import db, Comment, Post

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        req = request.get_json()
        post_id= req.get('post_id')
        text = req.get('text')
        if not post_id:
            return Response(json.dumps({'message': 'Post: doesnt exist '}), mimetype="application/json", status= 404)

        if not text: 
            return Response(json.dumps({'message': 'Post: no text '}), mimetype="application/json", status= 400)

        try: 
            post_id = int(post_id)
        except: 
            return Response(json.dumps({'message': 'Post: no int '}), mimetype="application/json", status= 400)
        temp = Post.query.get(post_id)

        if not temp: 
            return Response(json.dumps({'message': 'Post: doesnt exist '}), mimetype="application/json", status= 404)

        elif temp.user_id not in get_authorized_user_ids(self.current_user):
            return Response(json.dumps({'message': 'Post: not authorized'}), mimetype="application/json", status= 404)
        comment = Comment(text, self.current_user.id, post_id )
        if not comment: 
            return Response(json.dumps({'message': 'Post: comment doesnt exist '}), mimetype="application/json", status= 404)

        try: 
            db.session.add(comment)
            db.session.commit()
        except: 
            return Response(json.dumps({'message': 'Post: id not created'}), mimetype="application/json", status= 400)
        return Response(json.dumps(comment.to_dict()), mimetype="application/json", status= 201)

class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
  
    def delete(self, id):
        try: 
            id = int(id)
        except: 
            return Response(json.dumps({'message': 'DELETE: bad id'}), mimetype="application/json", status=400)
        comments = Comment.query.get(id)
        if not comments: 
            return Response(json.dumps({'message': 'comment doesnt exist'}), mimetype="application/json", status=404)
        if not comments.text:
            return Response(json.dumps({'message': 'no text'}), mimetype="application/json", status=400)
        
        if comments.user_id != self.current_user.id:
            response= {
            'message': 'no comment id= {0}'.format(id)
        }
            return Response(json.dumps(response), mimetype="application/json", status=404)  



        Comment.query.filter_by(id=id).delete()
        db.session.commit()
        s_data = {
            'message': 'Post {0} successfully delete.'.format(id)
        }
        return Response(json.dumps(s_data), mimetype="application/json", status= 200)


def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': api.app.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<id>', 
        '/api/comments/<id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
