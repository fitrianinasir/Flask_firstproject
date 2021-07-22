from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class VideoModel(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  likes = db.Column(db.Integer, nullable=False)
  views = db.Column(db.Integer, nullable=False)

  def __repr__(self):
    return f"Video(name = {self.name}, likes = {self.likes}, views = {self.views})"

# db.create_all()

video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_put_args.add_argument("views", type=str, help="Views of the video is required", required=True)
video_put_args.add_argument("likes", type=str, help="Likes on the video is required", required=True)

videos = {}

def abort_if_video_id_doesnt_exist(video_id):
  if video_id not in videos:
    abort(404,message='Video id is not exist..')

def abort_if_video_exist(video_id):
  if video_id in videos:
    abort(409, message='Video already exist')

class GetData(Resource):
  def get(self):
    return videos, 200

class Video(Resource):
  def get(self, video_id):
    abort_if_video_id_doesnt_exist(video_id)
    return videos[video_id], 200

  def post(self, video_id):
    abort_if_video_exist(video_id)
    args = video_put_args.parse_args()
    videos[video_id] = args
    return videos[video_id], 201

  def delete(self, video_id):
    abort_if_video_id_doesnt_exist(video_id)
    del videos[video_id]
    return {'message' : 'Successfully deleted'}, 200


api.add_resource(Video, "/video/<int:video_id>")
api.add_resource(GetData, "/videos")


if __name__ == "__main__":
  app.run(debug=True)