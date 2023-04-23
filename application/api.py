from email import message
from ftplib import all_errors
from json import JSONEncoder
from flask_restful import Resource, Api
from flask_restful import fields, marshal_with
from flask_restful import reqparse
from application.validation import BusinessValidationError, NotFoundError,SchemaValidationError
from application.models import Users,Lists,Cards
from application.database import db
from flask import current_app as app
import werkzeug
from flask import abort ,request,jsonify,json,url_for,send_file,render_template
from sqlalchemy.orm import Session
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as pltt

def check_date(date):
    # initializing string
    test_str = date
    
    # printing original string
    #print("The original string is : " + str(test_str))
    
    # initializing format
    format="%Y-%m-%d"
    
    # checking if format matches the date
    res = True
    
    # using try-except to check for truth value
    try:
        res = bool(datetime.strptime(test_str, format))
    except ValueError:
        res = False
    
    # printing result
    return res



register_user_parser = reqparse.RequestParser()
register_user_parser.add_argument("username")
register_user_parser.add_argument("password")
register_user_parser.add_argument("name")

update_list_parser = reqparse.RequestParser()
update_list_parser.add_argument("list_id")
update_list_parser.add_argument("l_user_id")
update_list_parser.add_argument("name")
update_list_parser.add_argument("description")

create_list_parser = reqparse.RequestParser()
create_list_parser.add_argument("l_user_id")
create_list_parser.add_argument("name")
create_list_parser.add_argument("description")

update_card_parser = reqparse.RequestParser()
update_card_parser.add_argument("card_id")
update_card_parser.add_argument("c_list_id")
update_card_parser.add_argument("title")
update_card_parser.add_argument("content")
update_card_parser.add_argument("start")
update_card_parser.add_argument("deadline")
update_card_parser.add_argument("complete")

create_card_parser = reqparse.RequestParser()
create_card_parser.add_argument("c_list_id")
create_card_parser.add_argument("title")
create_card_parser.add_argument("content")
create_card_parser.add_argument("start")
create_card_parser.add_argument("deadline")
create_card_parser.add_argument("complete")


login_fields = {
    'user_id':   fields.Integer,
    'name':    fields.String
}
register_fields = {
    'user_id':   fields.Integer,
    'name':    fields.String,
    'username':    fields.String,
    'password':    fields.String
}
list_fields={
    "list_id": fields.Integer,
    "l_user_id": fields.Integer,
    "name": fields.String,
    "description": fields.String
  
}
card_fields={
    "card_id": fields.Integer,
    "c_list_id": fields.Integer,
    "title": fields.String,
    "content": fields.String,
    "start": fields.String,
    "deadline": fields.String,
    "complete": fields.String 
}






class UserAPI(Resource):
    @marshal_with(login_fields)
    def get(self):
        #check if username exists 
        #then check if password is correct i.e more than 8 characters
        #format return JSON
        #then return user_id and name 
        args=request.args
        UN = args.get("username")
        PASS = args.get("password")
        #print(UN,PASS)
        #print("Login new user ")
        if UN is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="Username is required")
        if PASS is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="Password is required")
        if len(PASS)<8:
            raise SchemaValidationError(status_code=400, error_code="SE1001", error_message="Invalid password. Password should contain atleast 8 characters")

        if Users.query.filter_by(username = UN).first() == None:
                raise BusinessValidationError(status_code=404, error_code="BE1004", error_message="User Not Found")
                
        elif Users.query.filter_by(username = UN,password = PASS).first() == None:
            raise SchemaValidationError(status_code=400, error_code="SE1003", error_message="Incorrect password")
        elif Users.query.filter_by(username = UN,password = PASS).first() != None:
            user= Users.query.filter_by(username=UN).first()
            user_id=user.user_id
            name=user.name
            return user


    @marshal_with(register_fields)      
    def post(self):
        args = register_user_parser.parse_args()
        name=args.get("name", None)
        UN=args.get("username", None)
        PASS=args.get("password", None)
        #print(name,UN,PASS)
        if name is None:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="Name is required")
        if UN is None or UN == "":
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="Username is required")
        if PASS is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="Password is required")
        if len(PASS)<8:
            raise SchemaValidationError(status_code=400, error_code="SE1001", error_message="Invalid password. Password should contain atleast 8 characters")
        if Users.query.filter_by(username = UN).first() != None:
                raise SchemaValidationError(status_code=409, error_code="SE1002", error_message="Username already exist")
                
        elif Users.query.filter_by(username = UN,password = PASS).first() == None:
            u1 = Users(username =UN,password = PASS,name = name)
            db.session.add(u1)
            db.session.commit()
            return u1
        
    def delete(self,username):
        #args=request.args
        #UN = args.get("username")
        UN=username
        #print(UN)
        # if len(UN)<8:
        #     raise SchemaValidationError(status_code=400, error_code="SE1001", error_message="Invalid username. Username should contain atleast 8 characters")
        if Users.query.filter_by(username = UN).first() == None:
                raise BusinessValidationError(status_code=404, error_code="BE1004", error_message="User Not Found")
        else:
            u1=Users.query.filter_by(username = UN).first()
            user_id=u1.user_id
            all_lists= Lists.query.filter_by(l_user_id=user_id).all()
            for list1 in all_lists:
                list_id=list1.list_id
                all_cards = Cards.query.filter_by(c_list_id = list_id).all() 
                for card in all_cards:
                    db.session.delete(card)
                db.session.delete(list1)
            db.session.delete(u1)
            db.session.commit()
            return None


class ListsAPI(Resource):

    @marshal_with(list_fields)
    def get(self):
        args=request.args
        user_id= args.get("user_id")
        user=Users.query.filter_by(user_id=user_id).first()
        if user==None:
            raise SchemaValidationError(status_code=404, error_code="SE1004", error_message="No user exist for user_id == "+str(user_id))
        all_lists= Lists.query.filter_by(l_user_id=user_id).all()
        if len(all_lists)<1:
            raise BusinessValidationError(status_code=400, error_code="BE2001", error_message="User does not have any list")
        return all_lists


class ListAPI(Resource):
    @marshal_with(list_fields)
    def get(self):
        args=request.args
        list_id= args.get("list_id")
        list=Lists.query.filter_by(list_id=list_id).first()
        print(list_id)
        if list==None:
            raise SchemaValidationError(status_code=404, error_code="SE2001", error_message="List does not exist ")
        return list 

    @marshal_with(list_fields)
    def put(self):
        args = update_list_parser.parse_args()
        name=args.get("name", None)
        user_id=args.get("l_user_id", None)
        list_id=args.get("list_id", None)
        description=args.get("description", None)
        #print(name,user_id,list_id,description)
        u1=Users.query.filter_by(user_id = user_id).first()
        if u1==None:
            raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="User Not Found.")
        l1=Lists.query.filter_by(list_id=list_id).first()
        if l1==None:
            raise SchemaValidationError(status_code=404, error_code="SE2001", error_message="List does not exist.")
        l2=Lists.query.filter_by(list_id=list_id,l_user_id=user_id).first()
        if l2==None:
            raise SchemaValidationError(status_code=404, error_code="BE2002", error_message="List does not belong to user")
        else:
            l2.name=name
            l2.description=description
            db.session.commit()
            l3=Lists.query.filter_by(list_id=list_id,l_user_id=user_id).first()
            return l3

    @marshal_with(list_fields)
    def post(self):
        args = create_list_parser.parse_args()
        name=args.get("name", None)
        user_id=args.get("l_user_id", None)
        description=args.get("description", None)
        u1=Users.query.filter_by(user_id = user_id).first()
        if u1==None:
            raise BusinessValidationError(status_code=404, error_code="BE1004", error_message="User Not Found.")
        all_lists=Lists.query.filter_by(l_user_id=user_id).all()
        #print(len(all_lists))
        l1=Lists.query.filter_by(name=name,l_user_id = user_id).first()
        if l1!=None:
            raise SchemaValidationError(status_code=400, error_code="SE2002", error_message="List with similar name exist.")
        else:    
            new_list=Lists(l_user_id=user_id,name=name, description=description)
            db.session.add(new_list)  
            db.session.commit()
            l2=Lists.query.filter_by(name=name).first()
            return l2
        
    def delete(self):
        args=request.args
        list_id= args.get("list_id")
        list1=Lists.query.filter_by(list_id=list_id).first()
        #print(list_id)
        if list1==None:
            raise SchemaValidationError(status_code=404, error_code="SE2001", error_message="List does not exist ")
        else:
            all_cards = Cards.query.filter_by(c_list_id = list_id).all() 
            for card in all_cards:
                db.session.delete(card) 
            db.session.delete(list1)
            db.session.commit()
        


class CardsAPI(Resource):

    @marshal_with(card_fields)
    def get(self):
        args=request.args
        user_id= args.get("user_id")
        user=Users.query.filter_by(user_id=user_id).first()
        if user==None:
            raise SchemaValidationError(status_code=404, error_code="SE1004", error_message="No user exist for user_id == "+str(user_id))
        all_lists= Lists.query.filter_by(l_user_id=user_id).all()
        list_ids=[]
        all_card=[]
        for l in all_lists:
            list_ids.append(l.list_id)
        for c in list_ids:
            cards=Cards.query.filter_by(c_list_id=c).all()
            #print(cards)
            all_card.extend(cards)
        #print(all_card)


        if len(all_card)<1:
            raise BusinessValidationError(status_code=400, error_code="BE3001", error_message="User does not have any card.")
        return all_card

class CardsListAPI(Resource):

    @marshal_with(card_fields)
    def get(self):
        args=request.args
        list_id= args.get("list_id")
        list= Lists.query.filter_by(list_id=list_id).first()
        if list==None:
            raise SchemaValidationError(status_code=404, error_code="SE2001", error_message="List does not exist ")
        all_card=Cards.query.filter_by(c_list_id=list_id).all()
        if len(all_card)<1:
            raise BusinessValidationError(status_code=400, error_code="BE3002", error_message="List does not have any card.")
        return all_card

class CardAPI(Resource):

    @marshal_with(card_fields)
    def get(self):
        args=request.args
        card_id= args.get("card_id")
        card=Cards.query.filter_by(card_id=card_id).first()
        if card==None:
            raise SchemaValidationError(status_code=404, error_code="SE3001", error_message="Card does not exist ")
        return card

    @marshal_with(card_fields)
    def put(self):
        args = update_card_parser.parse_args()

        card_id=args.get("card_id", None)
        c_list_id=args.get("c_list_id", None)
        title=args.get("title", None)
        content=args.get("content", None)
        start=args.get("start", None)
        deadline=args.get("deadline", None)
        complete=args.get("complete", None)

        #print(start,deadline,complete)

        l1=Lists.query.filter_by(list_id=c_list_id).first()
        c1=Cards.query.filter_by(card_id=card_id).first()
        #print("PRevious CARD---------------------",c1,l1)
       
        if l1==None:
            raise SchemaValidationError(status_code=404, error_code="SE2001", error_message="List does not exist.")
        elif c1==None:
            raise SchemaValidationError(status_code=404, error_code="SE3001", error_message="Card does not exist.")


        prev_list_id=c1.c_list_id
        prev_list=Lists.query.filter_by(list_id=prev_list_id).first()
        prev_user_id=prev_list.l_user_id
        if l1.l_user_id!=prev_user_id:
            raise BusinessValidationError(status_code=404, error_code="BE2002", error_message="List does not belong to user")
        if check_date(str(start))==False:
            raise SchemaValidationError(status_code=400, error_code="SE3002", error_message="Incorrect date format for "+"start attribute.")
        elif check_date(str(deadline))==False:
            raise SchemaValidationError(status_code=400, error_code="SE3002", error_message="Incorrect date format for "+"deadline attribute")
        
        elif check_date(str(complete))==False and complete!="0":
            double_quotes = "complete"+"="+"0"
            mssg="If INCOMPLETE use "+double_quotes
            raise SchemaValidationError(status_code=400, error_code="SE3002", error_message="Incorrect date format for "+"complete attribute."+mssg)
        
        dd=datetime.strptime(deadline, '%Y-%m-%d')
        st=datetime.strptime(start, '%Y-%m-%d')
        
        if dd<st :
            raise BusinessValidationError(status_code=400, error_code="BE3004", error_message="Deadline before Start date")
        elif complete!="0" :
            com=datetime.strptime(complete, '%Y-%m-%d')
            if com<st:
                raise BusinessValidationError(status_code=400, error_code="BE3005", error_message="Complete date befor Start date")
        c1.c_list_id=c_list_id
        c1.title=title
        c1.content=content
        c1.start=start
        c1.deadline=deadline
        c1.complete=complete
        db.session.commit()
        card = Cards.query.filter_by(card_id=card_id).first()
        #print("Updated CARD---------------------",card)
        return  card

    @marshal_with(card_fields)
    def post(self):
        args = create_card_parser.parse_args()
        c_list_id=args.get("c_list_id", None)
        title=args.get("title", None)
        content=args.get("content", None)
        start=args.get("start", None)
        deadline=args.get("deadline", None)
        complete=args.get("complete", None)
        #print(c_list_id,title)
        l1=Lists.query.filter_by(list_id=c_list_id).first()
        c1=Cards.query.filter_by(title=title,c_list_id=c_list_id).first()
        #print("existing card",c1)
        if c1!=None:
            raise BusinessValidationError(status_code=400, error_code="BE3008", error_message="Card with Similar Name Exists in same list")
        if l1==None:
            raise SchemaValidationError(status_code=404, error_code="SE2001", error_message="List does not exist.")
        if check_date(str(start))==False:
            raise SchemaValidationError(status_code=400, error_code="SE3002", error_message="Incorrect date format for "+"start attribute.")
        elif check_date(str(deadline))==False:
            raise SchemaValidationError(status_code=400, error_code="SE3002", error_message="Incorrect date format for "+"deadline attribute")
        
        elif check_date(str(complete))==False and complete!="0":
            double_quotes = "complete"+"="+"0"
            mssg="If INCOMPLETE use "+double_quotes
            raise SchemaValidationError(status_code=400, error_code="SE3002", error_message="Incorrect date format for "+"complete attribute."+mssg)
        
        dd=datetime.strptime(deadline, '%Y-%m-%d')
        st=datetime.strptime(start, '%Y-%m-%d')
        
        if dd<st :
            raise BusinessValidationError(status_code=400, error_code="BE3004", error_message="Deadline before Start date")
        elif complete!="0" :
            com=datetime.strptime(complete, '%Y-%m-%d')
            if com<st:
                raise BusinessValidationError(status_code=400, error_code="BE3005", error_message="Complete date befor Start date")
        c1=Cards(c_list_id=c_list_id,title=title, content=content,complete=complete,start=start,deadline=deadline)
        db.session.add(c1)  
        db.session.commit()
        card=Cards.query.filter_by(title=title,c_list_id=c_list_id).first()
        return  card

    def delete(self):
        args=request.args
        card_id= args.get("card_id")
        card=Cards.query.filter_by(card_id=card_id).first()
        if card==None:
            raise SchemaValidationError(status_code=404, error_code="SE3001", error_message="Card Does not exist")
        else:
            db.session.delete(card) 
            db.session.commit()

class statsAPI(Resource):
    def get(self):
        args=request.args
        list_id= args.get("list_id")
        list1=Lists.query.filter_by(list_id=list_id).first()
        if list1==None:
            raise SchemaValidationError(status_code=404, error_code="SE2001", error_message="List does not exist ")
        lcards=list1.cards
        completed_tasks=0
        not_completed_tasks=0
        deadline_passed=0
        current_date=datetime.now()
        Total_tasks=len(lcards)
        for card in lcards:
            if card.complete==0:
                not_completed_tasks+=1
                dd=datetime.strptime(card.deadline, '%Y-%m-%d')
                cd=datetime.strptime((str(current_date))[0:10], '%Y-%m-%d')
                #print(cd,dd)
                if dd<cd:
                    deadline_passed+=1
            else:
                completed_tasks+=1
                #complete_date=datetime.strptime((str(card.complete))[0:10], '%Y-%m-%d')
            
        data = {'Total Cards':Total_tasks,'Completed Cards':completed_tasks,"Incomplete Cards":not_completed_tasks, 'Cards whose deadline has passed':deadline_passed}
        return data

class timeline(Resource):
    def get(self):
        args=request.args
        user_id= args.get("user_id")
        u1=Users.query.filter_by(user_id = user_id).first()
        if u1==None:
            raise BusinessValidationError(status_code=404, error_code="BE1004", error_message="User Not Found.")
        all_lists= Lists.query.filter_by(l_user_id=user_id).all()
        list_ids=[]
        all_card=[]
        for l in all_lists:
            list_ids.append(l.list_id)
        for c in list_ids:
            cards=Cards.query.filter_by(c_list_id=c).all()
            #print(cards)
            all_card.extend(cards)
        #print(all_card)


        if len(all_card)<1:
            raise BusinessValidationError(status_code=400, error_code="BE3001", error_message="User does not have any card.")
        lists=Lists.query.filter_by(l_user_id=user_id).all()
        user=Users.query.filter_by(user_id=user_id).first()
        user_name=user.name
        #print(lists)
        fig_dict={}
        complete_task_date_list=[]
        for list1 in lists:
            list_id=list1.list_id
            lcards=list1.cards
            no_of_Tasks=len(lcards)
            completed_tasks=0
            not_completed_tasks=0
            deadline_passed=0
            current_date=datetime.now()
            Total_tasks=len(lcards)
            for card in lcards:
                if card.complete==0:
                    not_completed_tasks+=1
                    dd=datetime.strptime(card.deadline, '%Y-%m-%d')
                    cd=datetime.strptime((str(current_date))[0:10], '%Y-%m-%d')
                    #print(cd,dd)
                    if dd<cd:
                        deadline_passed+=1
                else:
                    completed_tasks+=1
                    complete_date=datetime.strptime((str(card.complete))[0:10], '%Y-%m-%d')
                    complete_task_date_list.append(complete_date)
                

        #print(completed_tasks)
        #print(not_completed_tasks)
        #print(no_of_Tasks)
        #print(deadline_passed)
        #link="/"+str(user_id)+"/summary"
        #print(complete_task_date_list)
        complete_task_date_list.sort()
        #print(complete_task_date_list)
        no_of_tasks=len(complete_task_date_list)
        t_dict={}
        k=1
        for i in complete_task_date_list:
            t_dict[str(i)]=k
        timeline=[]
        for time in t_dict.keys():
            obj={}
            obj["time"]=time
            obj["no_of_completed_cards"]=t_dict[time]
            timeline.append(obj)
        #print(timeline)
        if len(timeline)<1:
            raise BusinessValidationError(status_code=400, error_code="BE3006", error_message="NO CARD IS YET COMPLETED")
        return timeline

    """
        # create a dataframe
        trendline = {"Date":list(t_dict.keys()),
        "No of Tasks":list(t_dict.values())
        }
        
        df = pd.DataFrame(trendline)
        #print(df)
        
        # to plot the graph
        df.plot(x="Date", y="No of Tasks", kind="line")
        pltt.xlabel("Date of task completed")
        pltt.ylabel("No of Tasks")
        pltt.title("Summary of Tasks for "+user_name)
        fig_loc=str(user_id)+"_trendline.png"
        trendline_path=url_for('static',filename=fig_loc)
        pltt.savefig("static/"+fig_loc)"""
        #eturn render_template("summary.html",fig_dict=fig_dict,list_names=list(fig_dict.keys()),user_name=user_name,user_id=user_id,trendline_path=trendline_path)

class barChart(Resource):
    def get(self):
        args=request.args
        list_id= args.get("list_id")
        list1=Lists.query.filter_by(list_id=list_id).first()
        if list1==None:
            raise SchemaValidationError(status_code=404, error_code="SE2001", error_message="List does not exist ")
        lcards=list1.cards
        if len(lcards)<1:
            raise BusinessValidationError(status_code=400, error_code="BE3001", error_message="List does not have any card.")
        completed_tasks=0
        not_completed_tasks=0
        deadline_passed=0
        current_date=datetime.now()
        Total_tasks=len(lcards)
        for card in lcards:
            if card.complete==0:
                not_completed_tasks+=1
                dd=datetime.strptime(card.deadline, '%Y-%m-%d')
                cd=datetime.strptime((str(current_date))[0:10], '%Y-%m-%d')
                #print(cd,dd)
                if dd<cd:
                    deadline_passed+=1
            else:
                completed_tasks+=1
                #complete_date=datetime.strptime((str(card.complete))[0:10], '%Y-%m-%d')
            
        data = {'Total Cards':Total_tasks,'Completed Cards':completed_tasks,"Incomplete Cards":not_completed_tasks, 'Cards whose deadline has passed':deadline_passed}
        if data['Total Cards']>0:
            category = list(data.keys())
            values = list(data.values())
            fig = plt.figure(figsize = (10, 5))
            plt.bar(category, values, color ='maroon',
                width = 0.4)
        
            plt.xlabel("Category of Cards")
            plt.ylabel("No of Cards")
            plt.title("Summary of Cards for "+str(list1.name))
            fig_location="_summary_bar_plot_"+str(list_id)+".png"
            source="static/"+fig_location
            plt.savefig("static/"+fig_location)
            return send_file(source, mimetype='image/gif')
    
class trendline(Resource):
    def get(self):
        args=request.args
        user_id= args.get("user_id")
        #print(user_id)
        u1=Users.query.filter_by(user_id = user_id).first()
        if u1==None:
            raise BusinessValidationError(status_code=404, error_code="BE1004", error_message="User Not Found.")
        all_lists= Lists.query.filter_by(l_user_id=user_id).all()
        list_ids=[]
        all_card=[]
        for l in all_lists:
            list_ids.append(l.list_id)
        for c in list_ids:
            cards=Cards.query.filter_by(c_list_id=c).all()
            #print(cards)
            all_card.extend(cards)
        #print(all_card)


        if len(all_card)<1:
            raise BusinessValidationError(status_code=400, error_code="BE3001", error_message="User does not have any card.")
        lists=Lists.query.filter_by(l_user_id=user_id).all()
        user=Users.query.filter_by(user_id=user_id).first()
        user_name=user.name
        #print(lists)
        fig_dict={}
        complete_task_date_list=[]
        for list1 in lists:
            list_id=list1.list_id
            lcards=list1.cards
            no_of_Tasks=len(lcards)
            completed_tasks=0
            not_completed_tasks=0
            deadline_passed=0
            current_date=datetime.now()
            Total_tasks=len(lcards)
            for card in lcards:
                if card.complete==0:
                    dd=datetime.strptime(card.deadline, '%Y-%m-%d')
                    cd=datetime.strptime((str(current_date))[0:10], '%Y-%m-%d')
                    #print(cd,dd)
                    
                else:
                    completed_tasks+=1
                    complete_date=datetime.strptime((str(card.complete))[0:10], '%Y-%m-%d')
                    complete_task_date_list.append(complete_date)
                

        #print(completed_tasks)
        #print(not_completed_tasks)
        #print(no_of_Tasks)
        #print(deadline_passed)
        #link="/"+str(user_id)+"/summary"
        #print(complete_task_date_list)
        complete_task_date_list.sort()
        #print(complete_task_date_list)
        no_of_tasks=len(complete_task_date_list)
        t_dict={}
        k=1
        for i in complete_task_date_list:
            t_dict[datetime.strptime((str(i))[0:10], '%Y-%m-%d')]=k
            k+=1
        timeline=[]
        for time in t_dict.keys():
            obj={}
            obj["time"]=time
            obj["no_of_completed_cards"]=t_dict[time]
            timeline.append(obj)
        #print(timeline)
        if len(timeline)<1:
            raise BusinessValidationError(status_code=400, error_code="BE3006", error_message="NO CARD IS YET COMPLETED")
        if len(timeline)<2:
            raise BusinessValidationError(status_code=400, error_code="BE3007", error_message="Atleast two cards need to be completed")
        trendline = {"Date":list(t_dict.keys()),
                    "No of Tasks":list(t_dict.values())
                    }
        #print(trendline)
        df = pd.DataFrame(trendline)
        df.plot(x="Date", y="No of Tasks", kind="line")
        pltt.xlabel("Date of task completed")
        pltt.ylabel("No of Tasks")
        pltt.title("Summary of Tasks for "+user_name)
        fig_loc=str(user_id)+"_trendline.png"
        trendline_path="static/"+fig_loc
        pltt.savefig("static/"+fig_loc)
        return send_file(trendline_path, mimetype='image/gif')




