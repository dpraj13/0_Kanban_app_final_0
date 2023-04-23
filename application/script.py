
from email import message
from application.models import Lists ,Cards ,Users
import csv
from werkzeug.utils import secure_filename
import pandas as pd
import datetime
from datetime import datetime


ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


def date_validation(date):
    format="%Y-%m-%d"
    res = True
    # using try-except to check for truth value
    try:
        res = bool(datetime.strptime(date, format))
    except ValueError:
        res = False
    return res
    
def Valid(filename,user_id):
    error="Improper data format"
    flag=True
    lists=Lists.query.filter_by(l_user_id=user_id).all()
    names=[]
    for list in lists:
        names.append(list.name)
    file = open("static/"+filename)
    csvreader = csv.reader(file)
    list_header = next(csvreader)
    list_header_default=['List Name', 'List Description']
    card_header_default=['title', 'content', 'start', 'deadline', 'complete', 'update']
    #print(list_header)
    list_details=next(csvreader)
    #print(list_details)
    card_header=next(csvreader)
    #print(card_header)
    rows = []
    valid=True
    res=True
    try:
        for row in csvreader:
            rows.append(row)
            if len(row)<6:
                res=False
                error="Less attributes provided for card data"
                raise StopIteration
            #print(len(row))
            #print(row)
            #print(row[2],row[3],row[4],row[5])
            k=date_validation(row[2])
            k1=date_validation(row[3])
            if row[4]=='0':
                k2=True
            else:
                k2=date_validation(row[4])
            if row[5]=='' or row[5]=='None':
                k3=True
            else:
                k3=date_validation(row[5])
            if k and k1 and k2 and k3 :
                pass
            else:
                res=False
                error="Improper date format"
                raise StopIteration
    except StopIteration:
        print("iteration stopped")
    #print(res)
    valid=res

    #print(rows)
    file.close()
    if (len(list_details)>=2) and valid :
        if (list_details[0] not in names) :
            return flag ,error
        else:
            error="List with similar name already exists"
            flag=False
            return flag ,error
    else:
        flag=False
        return flag,error