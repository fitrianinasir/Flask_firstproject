from flask import Flask
import werkzeug, os, time, copy
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
UPLOAD_DIR = "E:/_PROJECT/flask_tutorial/files"
ALLOWED_EXTENSIONS = {'csv'}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class VideoModel(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  likes = db.Column(db.Integer, nullable=False)
  views = db.Column(db.Integer, nullable=False)
  file = db.Column(db.String(100), nullable=False)

  def __repr__(self):
    return f"Video(name = {self.name}, likes = {self.likes}, views = {self.views}, file = {self.file})"

db.create_all()

video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_put_args.add_argument("views", type=str, help="Views of the video is required", required=True)
video_put_args.add_argument("likes", type=str, help="Likes on the video is required", required=True)
video_put_args.add_argument("file", type=werkzeug.datastructures.FileStorage, location='files', help="File is required", required=True)

video_up_args = reqparse.RequestParser()
video_up_args.add_argument("name", type=str)
video_up_args.add_argument("views", type=str)
video_up_args.add_argument("likes", type=str)
video_up_args.add_argument("file", type=werkzeug.datastructures.FileStorage, location='files')


resource_fields = {
  'id': fields.Integer,
  'name': fields.String,
  'views': fields.Integer,
  'likes': fields.Integer,
  'file': fields.String
}


class GetData(Resource):
  @marshal_with(resource_fields)
  def get(self):
    result = VideoModel.query.all()
    return result

class Video(Resource):
  @marshal_with(resource_fields)
  def get(self, video_id):
    result = VideoModel.query.filter_by(id=video_id).first()
    if not result:
      abort(404,message='Video id is not exist..')
    return result, 200

  def post(self, video_id):
    args = video_put_args.parse_args()
    result = VideoModel.query.filter_by(id=video_id).first()
    if result:
      abort(409, message="File already exist")
    file = args['file']
    file_name = file.filename.replace('.csv', f'_{str(time.time())}.csv')
    video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'], file=file_name)

    if not os.path.isdir(UPLOAD_DIR):
      os.mkdir(UPLOAD_DIR)

    file.save(UPLOAD_DIR + '/' + file_name)
    db.session.add(video)
    db.session.commit()
    return {"message": "Data Created Successfully"}

  @marshal_with(resource_fields)
  def patch(self, video_id):
    args = video_up_args.parse_args()
    file = args['file']
    file_name = file.filename.replace('.csv', f'_{str(time.time())}.csv')

    result = VideoModel.query.filter_by(id=video_id).first()  

    if not result:
      abort(404, message="File doesn't exist")
    if args['name']:
        result.name = args['name']
    if args['likes']:
      result.likes = args['likes']
    if args['views']:
      result.views = args['views']
    if file:
      os.remove(UPLOAD_DIR + '/' + result.file)
      result.file = file_name
     

    file.save(UPLOAD_DIR + '/' + file_name)
    db.session.commit()
    return result
    
  def delete(self, video_id):
    result = VideoModel.query.filter_by(id=video_id).first()
    if not result:
      abort(404, message="Video doesn't exist")
    os.remove(UPLOAD_DIR + '/' + result.file)
    db.session.delete(result)
    db.session.commit()
    return {'message' : 'Successfully deleted'}, 200
    


api.add_resource(Video, "/video/<int:video_id>")
api.add_resource(GetData, "/videos")


if __name__ == "__main__":
  app.run(debug=True)