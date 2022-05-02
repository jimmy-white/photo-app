from flask import Response, request
from flask_restful import Resource
import json
from models import db, Comment, Post
from views import get_authorized_user_ids
class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        req = request.get_json()
        post_id = req.get('post_id')
        text = req.get('text')
        if not post_id:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
        if not text:
            return Response(json.dumps({'message': 'Text is required'}), mimetype="application/json", status=400)
        try:
            post_id = int(post_id)
        except:
            return Response(json.dumps({'message': 'Post ID is not an integer'}), mimetype="application/json", status=400)
        temp = Post.query.get(post_id)

        if not temp:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)
        
        elif temp.user_id not in get_authorized_user_ids(self.current_user):
            return Response(json.dumps({'message': 'Unauthorized'}), mimetype="application/json", status=404)
        
        comment = Comment(text, self.current_user.id, post_id)
        if not comment:
            return Response(json.dumps({'message': 'Comment not created'}), mimetype="application/json", status=404)
        try:
            db.session.add(comment)
            db.session.commit()
        except:
            return Response(json.dumps({'message': 'Post id not created'}), mimetype="application/json", status=400)
        return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=201)
        # create a new "Comment" based on the data posted in the body 
        #body = request.get_json()
        #print(body)
        #return Response(json.dumps({}), mimetype="application/json", status=201)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
  
    def delete(self, id):
        # delete "Comment" record where "id"=id
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'invalid ID'}), mimetype="application/json", status=400)
            # a user can only delete their own post:
        comment = Comment.query.get(id)
        if not comment:
            return Response(json.dumps({'message': 'comment does not exist'}), mimetype="application/json", status=404)
        if not comment.text:
            return Response(json.dumps({'message': 'no text'}), mimetype="application/json", status=400)
        
        if comment.user_id != self.current_user.id:
            response = {
                'message': 'no comment id= {0}'.format(id)
            }
            return Response(json.dumps(response), mimetype="application/json", status=404)

        Comment.query.filter_by(id=id).delete()
        db.session.commit()
        s_data = {
            'message': 'comment id= {0} deleted successfully'.format(id)
        }
        return Response(json.dumps(s_data), mimetype="application/json", status=200)
        #print(id)
        #return Response(json.dumps({}), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': api.app.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<int:id>', 
        '/api/comments/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
