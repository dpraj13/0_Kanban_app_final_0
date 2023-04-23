
from operator import truediv
from sqlalchemy import select
from flask import Flask, flash, redirect, render_template, \
    request,url_for,Response
from flask import current_app as app
from application.models import Lists ,Cards ,Users
from .database import db
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as pltt
import io,os
import csv
from werkzeug.utils import secure_filename
import pandas as pd
from application.script import ALLOWED_EXTENSIONS ,allowed_file,Valid




engine = create_engine("sqlite:///db_directory/kb.sqlite3", echo=True, future=True)

@app.route('/', methods = ["GET","POST"] )
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        user_name = request.form["username"]
        
        pass_word = request.form["password"]
        
        if Users.query.filter_by(username = user_name).first() == None:
            flash(' INCORRECT USERNAME ')
            return redirect("/")
        elif Users.query.filter_by(username = user_name,password = pass_word).first() == None:
            flash(' INCORRECT PASSWORD ')
            return redirect("/")
        elif Users.query.filter_by(username = user_name,password = pass_word).first() != None:
            user= Users.query.filter_by(username=user_name).first()
            user_id=user.user_id
            link="/" + str(user_id) +"/board"
            return redirect(link)

@app.route('/register', methods = ["GET","POST"] )
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        user_name = request.form["username"]
        pass_word = request.form["password"]
        NAME = request.form["name"]
        
        print(user_name, pass_word)
        user= Users.query.filter_by(username=user_name).first()
        if user != None:
            # the query has returned a user
            flash('Username already exist please use difffernt username')
            return render_template("register.html")

        u1 = Users(username =user_name,password = pass_word,name = NAME)
        db.session.add(u1)
        db.session.commit()
        
        return redirect("/")

@app.route("/<user_id>/board", methods=["GET", "POST"])
def board(user_id):
    user=Users.query.filter_by(user_id=user_id).first()
    b_name=user.name
    lists=Lists.query.filter_by(l_user_id=user_id).all()
    #print(lists)
    length=len(lists)
    return render_template("board.html",lists=lists,user_id=user_id,b_name=b_name,length=length)


@app.route("/<user_id>/list/create", methods=["GET", "POST"])
def create_list(user_id):
    if request.method == "GET":
        lists=Lists.query.filter_by(l_user_id=user_id).all()
        # if len(lists)<5:
        return render_template("list_form.html",user_id=user_id)
        # else:
        #     error="No More lists"
        #     return render_template("update_error.html",error=error,user_id=user_id)
    else :
        name = request.form["name"]
        x=name.strip()
        dis=request.form["dis"]
        similarlists=Lists.query.filter_by(l_user_id=user_id,name=x).first()
        if similarlists :
           
            error="List name already exists . Please choose another one "
            return render_template("update_error.html",error=error,user_id=user_id)
        else:
            new_name = request.form["name"]
            y=new_name.strip()
            new_dis= request.form["dis"]
            
            l1=Lists(l_user_id=user_id,name=y, description=new_dis)
            db.session.add(l1)  
            db.session.commit()
            link="/"+str(user_id)+"/board"
            return redirect(link)


@app.route("/<user_id>/list/<list_id>/update", methods=["GET", "POST"])
def update_list(user_id,list_id):
    list1= Lists.query.filter_by(l_user_id=user_id,list_id = list_id).first()
    id_list=list_id
    if request.method == "GET":
        l_name=list1.name
        l_des=list1.description
        return render_template("list_update_form.html",list = list1,l_name=l_name,l_des=l_des,user_id=user_id)
    else:
        new_name = request.form["name"]
        new_dis= request.form["dis"]
        names=[]
        list1.name=new_name
        list1.description=new_dis
        db.session.commit()
        link="/"+str(user_id)+"/board"
        return redirect(link)


@app.route("/<user_id>/list/<list_id>/download", methods=["GET", "POST"])
def export_list(user_id,list_id):
    list1= Lists.query.filter_by(list_id = list_id).first()
    cards=Cards.query.filter_by(c_list_id=list_id).all()
    if (len(cards)>0):
        output=io.StringIO()
        writer=csv.writer(output)
        line1=["List Name","List Description"]
        writer.writerow(line1)
        line2=[str(list1.name),str(list1.description)]
        writer.writerow(line2)
        line3=["title","content","start","deadline","complete","update"]
        writer.writerow(line3)
        for card in cards:
            line=[str(card.title),str(card.content),(str(card.start))[0:10],str(card.deadline),str(card.complete),str(card.update)]
            writer.writerow(line)
        output.seek(0)
        filename=str(list1.name)+"_list.csv"
        return Response(output,mimetype="text/csv",headers={"Content-Disposition":"attachment;filename="+filename})
        
    else:
        error=str(list1.name)+" list does not have any card"
        return render_template("update_error.html",error=error,user_id=user_id)



@app.route("/<user_id>/list/upload", methods=["GET", "POST"])   
def import_list(user_id):
    if request.method == "POST":
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename=secure_filename(file.filename)
            new_filename=f'{filename.split(".")[0]}_{(str(datetime.datetime.now()))[0:10]}.csv'
            #print(new_filename)
            file.save("static/"+new_filename)
            #print(Valid(new_filename,user_id))
            flag,message=Valid(new_filename,user_id)
            if flag:
                file = open("static/"+new_filename)
                csvreader = csv.reader(file)
                list_header = next(csvreader)
                #print(list_header)
                list_details=next(csvreader)
                #print(list_details)
                card_header=next(csvreader)
                #print(card_header)
                rows = []
                for row in csvreader:
                    rows.append(row)
                #print(rows)
                file.close()
                l1=Lists(l_user_id=user_id,name=list_details[0], description=list_details[1])
                db.session.add(l1)  
                db.session.commit()
                list2=Lists.query.filter_by(l_user_id=user_id,name=list_details[0]).first()
                for row in rows:
                    
                    l1=Cards(c_list_id=list2.list_id,title=row[0], content=row[1],start=row[2],deadline=row[3],complete=row[4])
                    db.session.add(l1) 
                db.session.commit()
                return redirect("/"+str(user_id)+"/board")
            else:
                error=message
                return render_template("update_error.html",error=error,user_id=user_id)
    return render_template("upload.html",user_id=user_id)
    

@app.route("/<user_id>/list/<list_id>/delete", methods=["GET", "POST"])
def delete_list(user_id,list_id):
    if request.method == "POST":
        list2= Lists.query.filter_by(l_user_id=user_id,list_id = list_id).first()
        all_cards = Cards.query.filter_by(c_list_id = list_id).all() 
        for card in all_cards:
            db.session.delete(card) 
        #print(list2)
        db.session.delete(list2)
        db.session.commit()
        link="/"+str(user_id)+"/board"
        return redirect(link)
    elif request.method=="GET":
        #print(user_id)
        list1= Lists.query.filter_by(l_user_id=user_id,list_id = list_id).first()
        error="Warning!!!!!!!!!!!!!!!!!!!!!  Deleting List will delete all cards in them . Proceed "
        return render_template("warning_delete.html",error=error,list_id=list_id,obj_name=list1.name,object="list",user_id=user_id)


@app.route("/<user_id>/card/<list_id>/create", methods=["GET", "POST"])
def Form_card(user_id,list_id):
    if request.method == "GET":
        list_details = Lists.query.filter_by(list_id = list_id).first()
        return render_template("card_form.html",list_id=list_id,list_d=list_details,user_id=user_id)
    else :
        title = request.form["title"]
        y=title.strip()
        content= request.form["content"]
        similarcards=Cards.query.filter_by(title=y,c_list_id=list_id).first()
        deadline=request.form["deadline"]
        if similarcards :
           
            error="Card name already exists . Please choose another one "
            return render_template("update_error.html",error=error)
        else:
            complete=0
            date = datetime.datetime.now()
            start=date

            l1=Cards(c_list_id=list_id,title=y, content=content,complete=complete,start=start,deadline=deadline)
            db.session.add(l1)  
            db.session.commit()
            link="/"+str(user_id)+"/board"
            return redirect(link)


@app.route("/card/<list_id>/<card_id>/complete", methods=["GET", "POST"])
def Status_complete(list_id,card_id):
    card1 = Cards.query.filter_by(card_id=card_id,c_list_id=list_id).first()
    list1=Lists.query.filter_by(list_id = list_id).first()
    user_id=list1.l_user_id
    if request.method == "GET":
        return render_template("complete_date.html",list_id=list_id,card_id=card_id,user_id=list1.l_user_id,card=card1)
    else:
        date=request.form["complete_date"]
        card1.complete=date
        db.session.commit()
        link="/" + str(user_id) +"/board"
        return redirect(link)

@app.route("/card/<list_id>/<card_id>/incomplete", methods=["GET", "POST"])
def Status_incomplete(list_id,card_id):
    session = db.session
    stmt = select(Cards).where(Cards.card_id==card_id)
    card1= session.scalars(stmt).one()
    card1.complete=0
    db.session.commit()
    return redirect(request.referrer)

@app.route("/<user_id>/card/<list_id>/<card_id>/delete", methods=["GET", "POST"])
def delete_card(user_id,list_id,card_id):
    card = Cards.query.filter_by(card_id=card_id).first()
    if request.method=="GET":
        return render_template("warning_delete2.html",list_id=list_id,obj_name=card.title,object="card",user_id=user_id,card_id=card.card_id)
    else:
        list = Lists.query.filter_by(list_id = list_id).first()
        db.session.delete(card) 
        db.session.commit()
        link="/"+str(user_id)+"/board"
        return redirect(link)



@app.route("/<user_id>/card/<list_id>/<card_id>/update", methods=["GET", "POST"])
def update_card(user_id,list_id,card_id):
    card = Cards.query.filter_by(card_id=card_id).first()
    if request.method == "GET":
        c_title=card.title
        c_content=card.content
        c_deadline=card.deadline
        list_details = Lists.query.filter_by(list_id = list_id).first()
        return render_template("card_update_form.html",user_id=user_id,list_d=list_details,card_id=card_id,c_title=c_title,c_content=c_content,c_deadline=c_deadline)
    else:
        new_title = request.form["title"]
        new_content= request.form["content"]
        new_deadline=request.form["deadline"]
        card.title=new_title
        card.content=new_content
        card.deadline=new_deadline
        date = (str(datetime.datetime.now()))[0:10]
        card.update=date
        db.session.commit()
        link="/"+str(user_id)+"/board"
        return redirect(link)


@app.route("/<user_id>/card/<list_id>/<card_id>/move", methods=["GET", "POST"])
def Move_card(user_id,list_id,card_id):
    card = Cards.query.filter_by(card_id=card_id).first()
    card.c_list_id=list_id
    db.session.commit()
    link="/"+str(user_id)+"/board"
    return redirect(link)


@app.route("/<user_id>/summary", methods=["GET", "POST"])
def summary(user_id):
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
        current_date=datetime.datetime.now()
        Total_tasks=len(lcards)
        for card in lcards:
            if card.complete==0:
                not_completed_tasks+=1
                dd=datetime.datetime.strptime(card.deadline, '%Y-%m-%d')
                cd=datetime.datetime.strptime((str(current_date))[0:10], '%Y-%m-%d')
                #print(cd,dd)
                if dd<cd:
                    deadline_passed+=1
            else:
                completed_tasks+=1
                complete_date=datetime.datetime.strptime((str(card.complete))[0:10], '%Y-%m-%d')
                complete_task_date_list.append(complete_date)
            
        
        data = {'Total Tasks':Total_tasks,'Completed Tasks':completed_tasks,"Incomplete Tasks":not_completed_tasks, 'Tasks whose deadline has passed':deadline_passed}
        
        if data['Total Tasks']>0:
            category = list(data.keys())
            values = list(data.values())
            fig = plt.figure(figsize = (10, 5))
            plt.bar(category, values, color ='maroon',
                width = 0.4)
        
            plt.xlabel("Category of Tasks")
            plt.ylabel("No of Tasks")
            plt.title("Summary for Tasks")
            fig_location="summary_bar_plot_"+str(list_id)+".png"
            source=url_for('static',filename=fig_location)
            fig_dict[list1.name]=str(source)
            plt.savefig("static/"+fig_location)
        else:
            fig_dict[list1.name]="no card"

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
        t_dict[i]=k
        k+=1
    trendline = {"Date":list(t_dict.keys()),
    "No of Tasks":list(t_dict.values())
    }
    #print(trendline)
    df = pd.DataFrame(trendline)
    #print(df)
    # print(complete_task_date_list)
    # to plot the graph
    if len(complete_task_date_list)>1:
        df.plot(x="Date", y="No of Tasks", kind="line")
        pltt.xlabel("Date of task completed")
        pltt.ylabel("No of Tasks")
        pltt.title("Summary of Tasks for "+user_name)
        fig_loc=str(user_id)+"_trendline.png"
        trendline_path=url_for('static',filename=fig_loc)
        pltt.savefig("static/"+fig_loc)

    else:
        trendline_path="no card"
    return render_template("summary.html",fig_dict=fig_dict,list_names=list(fig_dict.keys()),user_name=user_name,user_id=user_id,trendline_path=trendline_path)

