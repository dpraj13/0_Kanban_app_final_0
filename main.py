import os
from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from flask_restful import Resource ,Api


app = None
api=None

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api=Api(app)
    app.app_context().push()
    return app,api

app,api = create_app()

# Import all the controllers so they are loaded
from application.controllers import *
#Add all restful controllers)
from application.api import UserAPI,ListsAPI,ListAPI,CardsAPI,CardsListAPI,CardAPI,statsAPI, timeline,barChart,trendline

api.add_resource(UserAPI,"/api/user/login","/api/user/register","/api/user/<string:username>")
api.add_resource(ListsAPI,"/api/all_lists")
api.add_resource(ListAPI,"/api/list")
api.add_resource(CardsAPI,"/api/all_cards_by_user")
api.add_resource(CardsListAPI,"/api/all_cards_by_list")
api.add_resource(CardAPI,"/api/card")
api.add_resource(statsAPI,"/api/stats")
api.add_resource(timeline,"/api/timeline")
api.add_resource(barChart,"/api/stats/image")
api.add_resource(trendline,"/api/trendline")



if __name__ == '__main__':
  # Run the Flask app
  app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
  app.debug=True
  app.run(host='0.0.0.0',port=8080)
