from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db
import json
from . import can_view_post, get_authorized_user_ids
class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        bookmarks = Bookmark.query.filter_by(
            user_id=self.current_user.id).order_by('id').all()
        bookmark_list_of_dictionaries = [
            bookmark.to_dict() for bookmark in bookmarks
        ]
        return Response(json.dumps(bookmark_list_of_dictionaries), mimetype="application/json", status=200)

        # Your code here
                # Your code here
        # bookmarks = Bookmark.query.filter_by(user_id = self.current_user.id).order_by('by').all()
        # # print(bookmarks)

        # bookmark_list_of_dictionaries = [
        #     bookmark.to_dict() for bookmark in bookmarks
        # ]

        # return Response(json.dumps(bookmark_list_of_dictionaries), mimetype="application/json", status=200)

    def post(self):
        req = request.get_json()
        # if not req:
        #     return Response(json.dumps({'message' : 'Post: bad data'}), mimetype="application/json", status=400)

        post_id = req.get('post_id')
        try: 
            bookmark = Bookmark(self.current_user.id, post_id)
            db.session.add(bookmark)
            db.session.commit()
        except Exception: 
            import sys
            print(sys.exc_info()[1])
            return Response(
                json.dumps({
                    'message': 'Database inert error. is post = {0} already bookmarked by user = {1}.'.format(post_id,self.current_user.id)}
                ),
                mimetype = "application/json",
                status= 400

            )
            

        

        # if not str(post_id).isdigit(): 
        #     return Response(json.dumps({'message' : 'Post: invalid format for postid'}), mimetype="application/json", status=400)

        # if not can_view_post(post_id, self.current_user):
        #     return Response(json.dumps({'message' : 'Post: unauthorized '}), mimetype="application/json", status=404)

        # try: 
        #     bookmark = Bookmark(self.current_user.id, post_id)
        #     db.session.add(bookmark)
        #     db.session.commit()
        # except: 
        #     return Response(json.dumps({'message' : 'Post: No Duplicates '}), mimetype="application/json", status=400)
        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)


####
##
###

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # Your code here
        if not str(id).isdigit():
             return Response(json.dumps({'message': 'invalid ID'}), mimetype="application/json", status=400)
        bookmark = Bookmark.query.get(id)
        if not bookmark or bookmark.user_id != self.current_user.id:
            return Response(json.dumps({'message' : 'Post: doesnt exist '}), mimetype="application/json", status=404)

        # if not bookmark:
        #     return Response(json.dumps({'message' : 'Post: doesnt exist '}), mimetype="application/json", status=404)

        # elif bookmark.user_id not in get_authorized_user_ids(self.current_user):
        #     return Response(json.dumps({'message': 'Post: not authorized'}), mimetype="application/json", status= 404)

        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        s_data = {
            'message' : 'Post {0} successfully delete.'.format(id)
        }
        return Response(json.dumps(s_data), mimetype="application/json", status=200)

        # try: 
        #     id = int(id)
        # except: 
        #     return Response(json.dumps({'message': 'DELETE: bad id'}), mimetype="application/json", status=400)
        # bookmarks = Bookmark.query.get(id)
        # if not bookmarks: 
        #     return Response(json.dumps({'message': 'comment doesnt exist'}), mimetype="application/json", status=404)
        # if not bookmarks.text:
        #     return Response(json.dumps({'message': 'no text'}), mimetype="application/json", status=400)
        
        # if bookmarks.user_id != self.current_user.id:
        #     response= {
        #     'message': 'no comment id= {0}'.format(id)
        # }
        #     return Response(json.dumps(response), mimetype="application/json", status=404)  


def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<id>', 
        '/api/bookmarks/<id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
