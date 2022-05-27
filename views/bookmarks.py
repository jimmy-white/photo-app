from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db
import json
from views import can_view_post
import flask_jwt_extended

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def get(self):
        # return all of the "bookmarks" records that the current user is following
        bookmarks = Bookmark.query.filter_by(
            user_id=self.current_user.id).order_by('id').all()
        bookmark_dict = [bookmark.to_dict() for bookmark in bookmarks]
        return Response(json.dumps(bookmark_dict), mimetype="application/json", status=200)
        # get all bookmarks owned by the current user

    @flask_jwt_extended.jwt_required()
    def post(self):
        req = request.get_json()
        # create a new "bookmark" record based on the data posted in the body
        post_id = req.get('post_id')
        if not str(post_id).isdigit(): 
            return Response(json.dumps({'message' : 'Post: invalid format for postid'}), mimetype="application/json", status=400)

        if not can_view_post(post_id, self.current_user):
            return Response(json.dumps({'message' : 'Post: unauthorized '}), mimetype="application/json", status=404)

        try: 
            bookmark = Bookmark(self.current_user.id, post_id)
            db.session.add(bookmark)
            db.session.commit()
        except: 
            return Response(json.dumps({'message' : 'Post: No Duplicates '}), mimetype="application/json", status=400)
        #create a new "bookmark" based on the data posted in the body 
        #body = request.get_json()
        #print(body)
        #return Response(json.dumps({}), mimetype="application/json", status=201)
        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        if not str(id).isdigit():
            return Response(json.dumps({'message': 'invalid ID'}), mimetype="application/json", status=400)
        bookmark = Bookmark.query.get(id)
        if not bookmark or bookmark.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'bookmark does not exist'}), mimetype="application/json", status=404)
        # delete "bookmark" where "id"=id
        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        s_data = {
            'message': 'Bookmark {0} deleted successfully'.format(id)
        }
        return Response(json.dumps(s_data), mimetype="application/json", status=200)
            # a user can only delete their own post:
            
        # delete "bookmark" record where "id"=id
        #print(id)
        #return Response(json.dumps({}), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<int:id>', 
        '/api/bookmarks/<int:id>',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
