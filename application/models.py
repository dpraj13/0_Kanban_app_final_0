from .database import db

class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer , autoincrement = True , primary_key = True)
    username = db.Column(db.String , unique = True, nullable = False)
    password = db.Column(db.String , nullable = False)
    name = db.Column(db.String , nullable = False)
    relationship1 = db.relationship("Lists")

class Lists(db.Model):
    __tablename__ = 'lists'
    list_id = db.Column(db.Integer ,autoincrement=True, primary_key=True,unique=True)
    l_user_id=db.Column(db.Integer , db.ForeignKey("users.user_id"))
    name = db.Column(db.String)
    description=db.Column(db.String)
    cards=db.relationship("Cards" ,backref="lists",cascade="all,delete",passive_deletes=True )
    
class Cards(db.Model):
    __tablename__ = 'cards'
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True,unique=True)
    c_list_id=db.Column(db.Integer , db.ForeignKey("lists.list_id"))
    title = db.Column(db.String)
    content = db.Column(db.String)
    start= db.Column(db.String)
    deadline=db.Column(db.String)
    complete=db.Column(db.String)
    update=db.Column(db.String)