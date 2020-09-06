# (C) 2017 IBM
# Author: Henrik Loeser
#
# Very short sample app used with Db2 Warehouse on Cloud to demonstrate
# how to use a SQL Cloud Database with a web app.
#

import os
from flask import Flask,redirect,render_template,request
import urllib
import datetime
import json
import sys
import ibm_db
import requests, json

app = Flask(__name__)

with open(sys.argv[1]) as json_file:    
    data = json.load(json_file)

db2infor = data["db2infor"]
scoring_endpoint = data["scoring_endpoint"]
token = data["token"]

# handle database request and query customer information
def customer(ID=None):
    # connect to DB2
    db2conn=ibm_db.connect(db2infor, "", "")
    headers_obj={"Cache-Control": "no-cache", "Content-Type": "application/json", "Authorization":token}
    if db2conn:
        # we have a Db2 connection, query the database
        sql1="select * from enhanced_customers where ID=?"
        sql2="select * from CUSTOMER_ACTIVITY_HISTORY where ID=?"
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.
        stmt1 = ibm_db.prepare(db2conn,sql1)
        stmt2 = ibm_db.prepare(db2conn,sql2)
        ibm_db.bind_param(stmt1, 1, ID)
        ibm_db.bind_param(stmt2, 1, ID)
        ibm_db.execute(stmt1)
        ibm_db.execute(stmt2)
        rows1=[]
        rows2=[]
        rows3=[]
        prediction=0
        probabilities=0
        
        # fetch the result
        result1 = ibm_db.fetch_assoc(stmt1)
        result2 = ibm_db.fetch_assoc(stmt2)
        while result1 != False:
            rows1.append(result1.copy())
            result1 = ibm_db.fetch_assoc(stmt1)
        while result2 != False:
            rows2.append(result2.copy())
            result2 = ibm_db.fetch_assoc(stmt2)
        # close database connection
        print(rows1)
        print(rows2)

	### read possible marketing offers to be presented ####
        sql3="select * from marketing_offers "
        stmt3 = ibm_db.prepare(db2conn,sql3)
        ibm_db.execute(stmt3)
        rows3=[]
        result3 = ibm_db.fetch_assoc(stmt3)
        while result3 != False:
            rows3.append(result3.copy())
            result3 = ibm_db.fetch_assoc(stmt3)
        print(rows3)
        ibm_db.close(db2conn)
	########## display results  ############
    return render_template('customer_legacy.html', ci1=rows1,ci2=rows2,ci3=rows3,prediction=prediction, probabilities=probabilities)

# main page to dump some environment information
@app.route('/')
def index():
   return render_template('index.html',app="")

@app.route('/search', methods=['GET'])
def searchroute():
    ID = request.args.get('ID', '')
    return customer(ID)

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
