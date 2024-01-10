import pymysql.cursors
import boto3
from googleapiclient.discovery import build
import requests
import httplib2
import json
from googleapiclient.discovery import build
import requests
from requests.auth import HTTPBasicAuth
import httplib2
import boto3
import pickle
import pymysql.cursors
import json
import os.path
import email.mime.text
import base64
import datetime   
import pickle
import os.path
import email.mime.text
import base64
from datetime import datetime
import calendar
import urllib3
from requests.auth import HTTPBasicAuth
import datetime
from datetime import date
import os
import email
import time
from collections import OrderedDict 
from pymysql import NULL
import re
import pymysql
from  aws_xray_sdk.core import recorder 
from aws_xray_sdk.core import patch_all
import jwt
from email import message
import logging
import mailbox
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from hdbcli import dbapi

atoken = ""
flg = ""


def enable_xray(event):
    if "Authorization" in event["params"]["header"]:
        atoken = event["params"]["header"]["Authorization"]

    if atoken != "":
        flg = requests.get(
            "https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/getemail",
            headers={"Content-Type": "application/json", "Authorization": atoken},
        )

    return json.loads(flg.text)["body"]

def convertValuesTodict(desc , values ):
    res=[]
    if len(values) == 1 :
        if type(values)==list:
            values=values[0]
        val =  {column.lower(): value for column, value in zip(values.column_names, values.column_values)}
        res.append(val.copy())
    else :
        for i in values:
            val1 =  {column.lower(): value for column, value in zip(i.column_names, i.column_values)}
            res.append(val1.copy())
    
    return res

def hdbcliConnect():
    mydb = dbapi.connect(
        address='27ac90fc-3667-4494-941a-01c999afd2de.hana.prod-us20.hanacloud.ondemand.com',
        port=443,
        user='DBADMIN',
        password='Peol@072023',
        encrypt='True' )
    return mydb


# Rules :

def getRuleDetails(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client('secretsmanager')
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute("select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on: 
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    patch_all()
                    print(event)	
            
            if "rule_id" in event["params"]["querystring"]:
                
                rule_id = event["params"]["querystring"]["rule_id"]
                rule = {}
                
                mycursor.execute("SELECT a.*, b.rule_name " \
                    "FROM rule a " \
                    "inner join rule_snro b " \
                    "on a.rule_id = b.rule_id " \
                    "where a.rule_id = ?", rule_id)
                rule_list = mycursor.fetchall()
             
                criteria = []
                approval_type = ""
                ec_isgroup = ""
                escelator = ""
                ifnot_withindays = ""
                comments = ""
                due_notification = ""
                due_reminder = ""
                overdue_notification = ""
                overdue_reminder = ""
                
                for row in rule_list:
                    
                    approval_type = row["approval_type"]
                    ec_isgroup = row["ec_isgroup"]
                    escelator = row["escelator"]
                    ifnot_withindays = row["ifnot_withindays"]
                    comments = row["comments"]
                    rule_name = row["rule_name"]
                    due_notification = row["due_notification"]
                    due_reminder = row["due_reminder"]
                    overdue_notification = row["overdue_notification"]
                    overdue_reminder = row["overdue_reminder"]
                        
                    if row["decider_type"] == "number":
                        data = {
                            "decider" : row["decider"],
                            "operator" : row["operator"], 
                            "d_value" : int( row["d_value"] ), 
                            "d_value2" : int( row["d_value2"] ), 
                            "decider_type" : row["decider_type"]
                        }
                        criteria.append(data)
                        
                    else:
                        data = {
                            "decider" : row["decider"],
                            "operator" : row["operator"], 
                            "d_value" : row["d_value"], 
                            "d_value2" : row["d_value2"],
                            "decider_type" : row["decider_type"]
                        }
                        criteria.append(data)
               
                mycursor.execute("select * from rule_approver where rule_key = ?", rule_id)
                approver = mycursor.fetchall()
                
                approver_final = [] 
                groupid = []
                memberid = []
                approver = convertValuesTodict(mycursor.description, approver)
                
                for row in approver:
                    if row["isgroup"] == 'y':
                        groupid.append(row["approver"])
                    elif row["isgroup"] == 'n':
                        memberid.append(row["approver"])
                
                if groupid and len(groupid) > 1:
                    mycursor.execute('select group_id, name from "GROUP" where group_id in {}'.format(tuple(groupid)))
                    
                    
                elif groupid and len(groupid) == 1:
                    group = (groupid[0])
                    sqlQuery = 'select group_id, name from "GROUP" where group_id = ?'
                    mycursor.execute(sqlQuery, group)
                
                temp=convertValuesTodict(mycursor.description,mycursor.fetchall())  
                for row in temp:
                    temp1 = {
                        "isgroup": "y",
                        "approver": row["group_id"],
                        "name": row["name"],
                        "position": ""
                    }
                    approver_final.append(temp1)
             
                if memberid and len(memberid) > 1:
                    mycursor.execute("select member_id, fs_name, ls_name, position from member where member_id in {}".format(tuple(memberid)))
                    
                elif memberid and len(memberid) == 1:
                    member = (memberid[0])
                    sqlQuery = "select member_id, fs_name, ls_name, position from member where member_id = ?"
                    mycursor.execute(sqlQuery, member) 
                
                temp=convertValuesTodict(mycursor.description,mycursor.fetchall())  
                for row in temp:
                    temp1 = {
                        "isgroup": "n",
                        "approver": row["member_id"],
                        "name": row["fs_name"] + " " + row["ls_name"],
                        "position": row["position"]
                    }
                    approver_final.append(temp1)
           
                app = []
                for data in approver:
                    
                    for row in approver_final:
                        
                        if row["approver"] == data["approver"] and row["isgroup"] == data["isgroup"]:
                            
                            temp = {
                                "isgroup" : row["isgroup"],
                                "approver" : row["approver"],
                                "name": row["name"],
                                "level" : data["level"],
                                "position": row["position"]
                            }
                            app.append(temp)
                            
                    if str(data["approver"]) == "999999999" and data["isgroup"] == "y":
                            temp = {
                                "isgroup" : data["isgroup"],
                                "approver" : data["approver"],
                                "name": "To ERP",
                                "level" : data["level"],
                                "position": ""  
                            }
                            app.append(temp)
                            
                rule_detail = {
                    "rule_id": rule_id,
                    "rule_name": rule_name,
                    "approval_type" : approval_type, 
                    "due_notification" : due_notification,
                    "due_reminder" : due_reminder,
                    "overdue_notification" : overdue_notification,
                    "overdue_reminder" : overdue_reminder,
                    "ec_isgroup" : ec_isgroup, 
                    "escelator" : escelator, 
                    "es_name" : "",
                    "ifnot_withindays" : ifnot_withindays, 
                    "comments" : comments,
                    "criteria" : criteria,
                    "approvers" : app
                }
                
            else:
                
                is_approval = 'y'
                
                if "is_approval" in event["params"]["querystring"]:
                    is_approval = event["params"]["querystring"]["is_approval"]
                    
                rule_detail = []
                
                mycursor.execute("SELECT a.*, b.rule_name, c.department_name " \
                	"FROM rule a " \
                	"inner join rule_snro b " \
                	"on a.rule_id = b.rule_id " \
                    "left join departmental_budget_master c " \
                    "on a.d_value = cast(c.department_id as nvarchar)" \
                	"where b.is_approval = ? " \
                	"order by a.rule_id", is_approval)
                rules = mycursor.fetchall()
                rules = convertValuesTodict(mycursor.description , rules)	
                
                dict_rule = rules
                rule_keys = []
                escalator = []
                distinct_rule = []
                
                for row in rules:
                    temp = {
                        "is_on": row["is_on"],
                        "rule_id": row["rule_id"],
                        "rule_name": row["rule_name"],
                        "approval_type" : row["approval_type"], 
                        "ec_isgroup" : row["ec_isgroup"], 
                        "escelator" : row["escelator"], 
                        "es_name" : "",
                        "ifnot_withindays" : row["ifnot_withindays"], 
                        "comments" : row["comments"],
                        "due_notification" : row["due_notification"],
                        "due_reminder" : row["due_reminder"],
                        "overdue_notification" : row["overdue_notification"],
                        "overdue_reminder" : row["overdue_reminder"]
                    }
                    distinct_rule.append(temp)
                
                    
                res_list = [] 
                approvers_list = []
                
                for i in range(len(distinct_rule)): 
                    if distinct_rule[i] not in distinct_rule[i + 1:]: 
                        res_list.append(distinct_rule[i]) 
                
                for each in rules:
                    rule_keys.append(each['rule_id'])
                
                if rule_keys and len(rule_keys) > 1:
                    mycursor.execute("SELECT * FROM rule_approver where rule_key in {}".format(tuple(rule_keys)))
                    approvers_list = mycursor.fetchall()
                    
                elif len(rule_keys) == 1:
                    key = (rule_keys[0])
                    sqlQuery = "select * from rule_approver where rule_key = ?"
                    mycursor.execute(sqlQuery, key)
                    approvers_list = mycursor.fetchall()
                
                groupid = []
                memberid = []
                approvers_list = convertValuesTodict(mycursor.description, approvers_list)
                
                for row in approvers_list:
                    if row["isgroup"] == 'y':
                        groupid.append(row["approver"])
                    elif row["isgroup"] == 'n':
                        memberid.append(row["approver"])
            
                approver_final = []  
                
                if groupid and len(groupid) > 1:
                
                    mycursor.execute('select group_id, name from "GROUP" where group_id in {}'.format(tuple(groupid)))
                    
                elif len(groupid) == 1:
                    group = (groupid[0])
                    sqlQuery = 'select group_id, name from "GROUP" where group_id = ?'
                    mycursor.execute(sqlQuery, group)
                
                temp=convertValuesTodict(mycursor.description,mycursor.fetchall())  
                for row in temp:
                    temp1 = {
                        "isgroup": "y",
                        "approver": row["group_id"],
                        "name": row["name"],
                        "position": ""
                    }
                    approver_final.append(temp1)
         
                if memberid and len(memberid) > 1:
                    mycursor.execute("select member_id, fs_name, ls_name, position from member where member_id in {}".format(tuple(memberid)))
                
                elif len(memberid) == 1:
                    member = (memberid[0])
                    sqlQuery = "select member_id, fs_name, ls_name, position from member where member_id = ?"
                    mycursor.execute(sqlQuery, member) 
                
                temp=convertValuesTodict(mycursor.description,mycursor.fetchall())    
                for row in temp:
                    temp1 = {
                        "isgroup": "n",
                        "approver": row["member_id"],
                        "name": row["fs_name"] + " " + row["ls_name"],
                        "position": row["position"]
                    }
                    approver_final.append(temp1)
         
                for row in res_list:
                    approvers = []
                    criteria = []
                    
                    for data in approvers_list:
                        
                        if row["rule_id"] == data["rule_key"]:
                            
                            for temp1 in approver_final:
                                
                                if data["approver"] == temp1["approver"] and data["isgroup"] == temp1["isgroup"]:
                                    temp = {
                                        "isgroup" : temp1["isgroup"],
                                        "approver" : data["approver"],
                                        "name": temp1["name"],
                                        "level" : data['level'],
                                        "position": temp1["position"]
                                    }
                                    approvers.append(temp)
                                    
                                elif str(data["approver"]) == "999999999" and data["isgroup"] == "y":
                                    temp = {
                                        "isgroup" : temp1["isgroup"],
                                        "approver" : data["approver"],
                                        "name": "To ERP",
                                        "level" : data['level'],
                                        "position": ""
                                    }
                                    approvers.append(temp)
                                    break
                                
                            approvers = sorted(approvers, key = lambda i: i['level'])      
                            
                    for value in dict_rule:
                        
                        decider = ""
                        if row["rule_id"] == value["rule_id"]:
                            
                            if value["decider_type"] == "string":
                                
                                if value["decider"] == "discount" and value["operator"] != "between":
                                    decider = "Discount" + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "discount" and value["operator"] == "between":
                                    decider = "Discount between " + value["d_value"] + " and " + value["d_value2"]
                                    
                                elif value["decider"] == "amount" and value["operator"] != "between":
                                    decider = "Amount " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "amount" and value["operator"] == "between":
                                    decider = "Amount between " + value["d_value"] + " and " + value["d_value2"]
                                    
                                elif value["decider"] == "gl_account" and value["operator"] != "between":
                                    decider = "G/L account " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "currency" and value["operator"] != "between":
                                    decider = "Currency " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "cost_center":
                                    decider = "Cost center " + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "npo":
                                    decider = "NPO " + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "vendor_no":
                                    decider = "Vendor No. " + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "department_id":
                                    if value["department_name"] == None :
                                        value["department_name"] = ''
                                    decider = "Department " + " " + value["operator"] + " " + value["department_name"]
                                
                                elif value["decider"] == "item_category":
                                    decider = "Item Category " + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "invoice_type":
                                    decider = "Invoice Type" + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "supplier_type	":
                                    decider = "Supplier Type" + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "jurisdiction_code": #EPDS-69
                                    decider = "jurisdiction code" + " " + value["operator"] + " " + value["d_value"] #EPDS-69
                                    
                                elif value["decider"] == "document_type":
                                    rule_value = " "
                                    if value["d_value"] == 'RE':
                                        rule_value = "Invoice" 
                                    elif value["d_value"] == 'KG':
                                        rule_value = "Credit Memo" 
                                    elif value["d_value"] == 'SU':
                                        rule_value = "Debit Memo"
                                        
                                    decider = "Document Type" + " " + value["operator"] + " " + rule_value
                                    
                                elif value["decider"] == "default":
                                    decider = "Default"
                                
                                val = {
                                    "rule" : decider,
                                    "decider_type" : value["decider_type"]
                                }
                                criteria.append(val)
                                
                            else:
                                
                                if value["decider"] == "discount" and value["operator"] != "between":
                                    decider = "Discount" + " " + value["operator"] + " " + str(int(value["d_value"]))
                                    
                                elif value["decider"] == "discount" and value["operator"] == "between":
                                    decider = "Discount between " + " " + str(int(value["d_value"])) + " and " + str(int(value["d_value2"]))
                                    
                                elif value["decider"] == "amount" and value["operator"] != "between":
                                    decider = "Amount " + " " + str(value["operator"]) + " " + str(int(value["d_value"]))
                                    
                                elif value["decider"] == "amount" and value["operator"] == "between":
                                    decider = "Amount between " + str(int(value["d_value"])) + " and " + str(int(value["d_value2"]))
                                    
                                elif value["decider"] == "gl_account" and value["operator"] != "between":
                                    decider = "G/L account " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "currency" and value["operator"] != "between":
                                    decider = "Currency " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "cost_center":
                                    decider = "Cost center " + " " + value["operator"] + " " + value["d_value"]
                                
                                elif value["decider"] == "npo":
                                    decider = "NPO " + " " + value["operator"] + " " + value["d_value"]
                                
                                elif value["decider"] == "vendor_no":
                                    decider = "Vendor No. " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "department_id":
                                    decider = "Department " + " " + value["operator"] + " " + value["department_name"]
                                    
                                elif value["decider"] == "item_category":
                                    decider = "Item Category " + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "invoice_type":
                                    decider = "Invoice Type" + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "supplier_type	":
                                    decider = "Supplier Type" + " " + value["operator"] + " " + value["d_value"]
                                    
                                elif value["decider"] == "Jurisdiction_code": #EPDS-69
                                    decider = "jurisdiction code" + " " + value["operator"] + " " + value["d_value"] #EPDS-69
                                
                                elif value["decider"] == "default":
                                    decider = "Default"
                                    
                                val = {
                                    "rule": decider,
                                    "decider_type" : value["decider_type"]
                                }
                                criteria.append(val)
                        
                    record = {
                        "is_on": row["is_on"],
                        "rule_id": row["rule_id"],
                        "rule_name": row["rule_name"],
                        "approval_type" : row["approval_type"], 
                        "ec_isgroup" : row["ec_isgroup"], 
                        "escelator" : row["escelator"], 
                        "es_name" : row["es_name"],
                        "ifnot_withindays" : row["ifnot_withindays"], 
                        "comments" : row["comments"],
                        "due_notification" : row["due_notification"],
                        "due_reminder" : row["due_reminder"],
                        "overdue_notification" : row["overdue_notification"],
                        "overdue_reminder" : row["overdue_reminder"],
                        "criteria": criteria,
                        "approvers" : approvers
                    }
                    rule_detail.append(record) 
        
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Fail")
        }            
                
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': rule_detail
    }


#tested working fine with event tested
def postRuleDetails(event , context):
    global dbScehma 
    dbScehma = 'DBADMIN'
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )
    
    secret = event["stage-variables"]["secreat"]
    resp = client.get_secret_value(
        SecretId= secret
    )
    secretDict = json.loads(resp['SecretString'])

    mydb = dbapi.connect(
        address='7bd70c10-e2c3-4b6f-aaea-9d9d067bd91d.hana.trial-us10.hanacloud.ondemand.com',
        port=443,
        user='DBADMIN',
        password='Vinod@123',
        encrypt='True' )

    record = {
        "rule": "",
        "rule_name": "",
        "approval_type": "",
        "is_approval": "y",   #change to "" once front end peep makes changes
        "ec_isgroup": "",
        "escelator": "",
        "ifnot_withindays": "",
        "due_notification" : "",
        "due_reminder" : "",
        "overdue_notification" : "",
        "overdue_reminder" : "",
        "comments": ""
    }

    approvers = []

    try:
        if "is_approval" in event["params"]["querystring"]:
            record["is_approval"] = event["params"]["querystring"]["is_approval"]
        
        if "rule_name" in event["params"]["querystring"]:
            record["rule_name"] = event["params"]["querystring"]["rule_name"]

        if "approvers" in event["body-json"]:
            for approver in event["body-json"]["approvers"]:
                app = {
                    'level': approver['level'],
                    'isgroup': approver['isgroup'],
                    'approver': approver['approver']
                }
                approvers.append(app)
                
                if "members" in event["body-json"]["approvers"]:
                    for member in approver["members"]:
                        mem = {
                            'level': approver['level'],
                            'isgroup': 'n',
                            'approver': member
                        }
                        approvers.append(mem)

        criteria = []
        print(event)
        if 'criteria' in event["body-json"]:
            for each in event["body-json"]['criteria']:
                if str(each["type"]) == "number":
                    value1 = '0' * (11 - len(str(each['value1']))) + str(each['value1'])
                    value2 = '0' * (11 - len(str(each['value2']))) + str(each['value2'])
                else:
                    value1 = each['value1']
                    value2 = each['value2']

                cat = {
                    "decider": each['decider'],
                    "operator": each['operator'],
                    "value1": value1,
                    "value2": value2,
                    "type": each['type']
                }
                criteria.append(cat)

        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]

        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on=mycursor.fetchone()
            # on = convertValuesTodict(mycursor.description , on)	
            # for row in on:
            if on['value1'] =='on':
                    chk = enable_xray(event)
                    patch_all()
                    print(event)	

            dup = []
            for row in criteria:

                if row['decider'] == "default":
                    values = (row['decider'],)
                    sqlQuery = "select rule_id from rule where decider = ?"
                    mycursor.execute(sqlQuery, values)
                    defu = mycursor.fetchall()
                    if defu:
                        raise pymysql.err.IntegrityError
                        
                if row['decider'] == "default_assignment":
                    values = (row['decider'],)
                    sqlQuery = "select rule_id from rule where decider = ?"
                    mycursor.execute(sqlQuery, values)
                    defu = mycursor.fetchall()
                    if defu:
                        raise pymysql.err.IntegrityError
                
                if row['decider'] != "npo":
                    values = (row['decider'], row['operator'], row['value1'], row['value2'])
                    #values = dict(values)
                    sqlQuery = "select rule_id from rule where decider = ? and operator = ? and d_value = ? and d_value2 = ?"
                    mycursor.execute(sqlQuery, values)
                    result = mycursor.fetchall()
                    if not result:
                        dup = []
                        break
        
                    ruleIds = [sub['rule_id'] for sub in result]
                    if not dup:
                        dup = ruleIds
                    else:
                        dup = [value for value in dup if value in ruleIds]
                
            if dup:
                for each in dup:
                    values = (each,)
                    sqlQuery = "select rule_id from rule where rule_id = ?"
                    mycursor.execute(sqlQuery, values)
                    result = mycursor.fetchall()

                    if result and len(criteria) == len(result):
                        raise pymysql.err.IntegrityError

            sqlQuery = "INSERT INTO rule_snro (rule_name, approval_type, is_approval) VALUES {}"
            values = ( record["rule_name"], record["approval_type"], record["is_approval"])
            mycursor.execute(sqlQuery.format(tuple(values)))

            mycursor.execute("select count(*) from rule_snro")
            rule_key = mycursor.fetchone()

            sqlQuery = "INSERT INTO rule ( rule_id, decider, operator, d_value, d_value2, approval_type, ec_isgroup, escelator, ifnot_withindays, comments, " \
                       "decider_type, due_notification, due_reminder, overdue_notification, overdue_reminder) VALUES " \
                       "{}"

            values = []
            for row in criteria:
                tup = (rule_key[0], row['decider'], row['operator'], row['value1'], row['value2'], record["approval_type"], record["ec_isgroup"], record["escelator"], 
                    record["ifnot_withindays"], record["comments"], row['type'], record["due_notification"], record["due_reminder"], record["overdue_notification"],
                    record["overdue_reminder"])
                mycursor.execute(sqlQuery.format(tuple(tup)))

            values = []

            for index, each in enumerate(approvers):
                tup = (rule_key[0], each['isgroup'], each['approver'], each["level"])
                sqlQuery = "INSERT INTO rule_approver (rule_key, isgroup, approver, level) VALUES {}"
                mycursor.execute(sqlQuery.format(tuple(tup)))

            mydb.commit()

    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Duplicate Rule")
        }

    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Sucessfully Added New Rule")
    }

#working fine for event
def patchRuleDetails(event, context):
    global dbScehma
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    #     "secretsmanager",
    #     region_name="eu-central-1",
    #     aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
    #     aws_secret_access_key="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",
    # )

    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(SecretId=secret)
    # secretDict = json.loads(resp["SecretString"])

    mydb = hdbcliConnect()

    record = {
        "rule_id": "",
        "rule_name": "",
        "approval_type": "",
        "ec_isgroup": "",
        "escelator": "",
        "ifnot_withindays": "",
        "due_notification": "",
        "due_reminder": "",
        "overdue_notification": "",
        "overdue_reminder": "",
        "comments": "",
    }
    msg = "Update Unsucessful!"
    approvers = []
    rule = ""

    try:
        print(event)
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]

        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            mycursor.execute(
                " select value1 from elipo_setting where key_name = 'config_trace' "
            )
            on = mycursor.fetchone()
            if on["value1"] == "on":
                chk = enable_xray(event)
                if chk["Enable"] == True:
                    patch_all()
                    print(event)

            rule = event["params"]["querystring"]["rule_id"]

            if "rule_name" in event["params"]["querystring"]:
                record["rule_name"] = event["params"]["querystring"]["rule_name"]

            data = []

            if "rule_id" in event["params"]["querystring"]:
                sqlQuery = "UPDATE rule_snro set rule_name = ? WHERE rule_id = ?"
                values = (record["rule_name"], rule)
                mycursor.execute(sqlQuery, values)

                for row in event["body-json"]["criteria"]:
                    if str(row["type"]) == "number":
                        value1 = "0" * (11 - len(str(row["value1"]))) + str(
                            row["value1"]
                        )
                        value2 = "0" * (11 - len(str(row["value2"]))) + str(
                            row["value2"]
                        )
                    else:
                        value1 = row["value1"]
                        value2 = row["value2"]

                    cri = {
                        "rule_id": rule,
                        "decider": row["decider"],
                        "operator": row["operator"],
                        "d_value": value1,
                        "d_value2": value2,
                        "approval_type": record["approval_type"],
                        "ec_isgroup": record["ec_isgroup"],
                        "escelator": record["escelator"],
                        "ifnot_withindays": record["ifnot_withindays"],
                        "comments": record["comments"],
                        "due_notification": record["due_notification"],
                        "due_reminder": record["due_reminder"],
                        "overdue_notification": record["overdue_notification"],
                        "overdue_reminder": record["overdue_reminder"],
                        "decider_type": row["type"],
                    }
                    data.append(cri)

                sqlQuery = (
                    "insert into rule (rule_id, decider, operator, d_value, d_value2, approval_type, ec_isgroup, escelator, ifnot_withindays, comments, "
                    "decider_type, due_notification, due_reminder, overdue_notification, overdue_reminder ) values (?, ?, ?, ?, ?, ?, ?, "
                    "?, ?, ?, ?, ?, ?, ?, ?)"
                )

                default = None

                if data:
                    values = []
                    for row in data:
                        if row["decider"] == "default_assignment":
                            value = ("default_assignment",)
                            mycursor.execute(
                                "select * from rule where decider = ?", value
                            )
                            default = mycursor.fetchone()

                            if default:
                                if int(default["rule_id"]) != int(row["rule_id"]):
                                    return {
                                        "statuscode": 500,
                                        "body": json.dumps(
                                            "Default Rule already exist!"
                                        ),
                                    }

                        tup = (
                            row["rule_id"],
                            row["decider"],
                            row["operator"],
                            row["d_value"],
                            row["d_value2"],
                            row["approval_type"],
                            row["ec_isgroup"],
                            row["escelator"],
                            row["ifnot_withindays"],
                            row["comments"],
                            row["decider_type"],
                            row["due_notification"],
                            row["due_reminder"],
                            row["overdue_notification"],
                            row["overdue_reminder"],
                        )
                        values.append(tup)

                if values:
                    mycursor.execute("delete from rule where rule_id = ?", rule)
                    mycursor.executemany(sqlQuery, values)

                if "approvers" in event["body-json"]:
                    for approver in event["body-json"]["approvers"]:
                        app = {
                            "level": approver["level"],
                            "isgroup": approver["isgroup"],
                            "approver": approver["approver"],
                        }
                        approvers.append(app)

                        if "members" in approver:
                            for members in approver["members"]:
                                mem = {
                                    "level": approver["level"],
                                    "isgroup": "n",
                                    "approver": members,
                                }
                                approvers.append(mem)

                sqlQuery = "delete from rule_approver where rule_key = ?"
                mycursor.execute(sqlQuery, rule)

                values = []

                for index, each in enumerate(approvers):
                    tup = (rule, each["isgroup"], each["approver"], each["level"])
                    values.append(tup)

                sqlQuery = "INSERT INTO rule_approver (rule_key, isgroup, approver, level) VALUES ( ?, ?, ?, ?)"

                if values:
                    mycursor.executemany(sqlQuery, values)

                mydb.commit()
                msg = "Successfully Updated!"

    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {"statuscode": 500, "body": json.dumps("Duplicate Rule")}

    except:
        return {"statuscode": 500, "body": msg}

    finally:
        mydb.close()

    return {"statuscode": 200, "body": msg}

# event = {'body-json': {'comments': 'testingssssssssss', 'approvers': [{'level': '', 'isgroup': 'n', 'approver': 39}], 'criteria': [{'decider': 'document_type', 'operator': '=', 'value1': 'RE', 'value2': '', 'type': 'string'}]}, 'params': {'path': {}, 'querystring': {'rule_id': '279', 'rule_name': 'Rule'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImE4ZTg0NmEwLTJmMGYtNDEwMC1iMTFiLTU5ZGVjMjg2YzU3ZiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg1NDQyMzc3LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg1NDQ1OTc3LCJpYXQiOjE2ODU0NDIzNzcsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.D5xUEUGhWZXXbfSy6sJDGZa-MzvYdIIfZw7sOvcQxFx71rP3Fh0Iyw0vQg1FA1j9B3Tp58a47tV7vGEPB1r-h8gBCJRYZCHQIRDWT2AYxXIDPy0-WEXntUrAtLP1alzgRz4umWzWUBdPmbzt_raa4kA3XefRnrYRmRyMzTo5eJVrn8Qc4o3FmO2WFbbbuKHx6YwG4FRPENMaTbF38a4NoeaHLFMnRrJJvfD-yfpo_fg59GvIkIv7TYl5AL-NE93MElcJqtC2VymryW4EDNrpgizarI3pw9vMPiI_O94yzsaWpPnRIuZY18s49OwU6PGQaLwLwsJBDi31xDxX_mzsbQ', 'content-type': 'application/json', 'Host': 'overview.peoltechnologies.net', 'origin': 'https://port4200-workspaces-ws-svqb9.us10.trial.applicationstudio.cloud.sap', 'referer': 'https://port4200-workspaces-ws-svqb9.us10.trial.applicationstudio.cloud.sap/', 'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6475d23d-6d66b525166db2b95a4887ad', 'X-Forwarded-For': '49.207.53.153', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '5ud4f0kv53', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'einvoice-v1', 'source-ip': '49.207.53.153', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'c4350536-df49-4767-89bc-da347429faba', 'resource-id': '39vsp4', 'resource-path': '/rules'}}
# print(patchRuleDetails(event, ' '))

#event not found
def deleteRuleDetails(event, context):
    global dbScehma
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    #     "secretsmanager",
    #     region_name="eu-central-1",
    #     aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
    #     aws_secret_access_key="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",
    # )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(SecretId=secret)

    # secretDict = json.loads(resp["SecretString"])

    mydb = hdbcliConnect()

    msg = "Data not deleted!"

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            if "rule_id" in event["params"]["querystring"]:
                sqlQuery = "DELETE FROM rule WHERE rule_id = ?"
                values = event["params"]["querystring"]["rule_id"]
                mycursor.execute(sqlQuery, values)

                sqlQuery = "DELETE FROM rule_approver WHERE rule_key = ?"
                values = event["params"]["querystring"]["rule_id"]
                mycursor.execute(sqlQuery, values)

                sqlQuery = "DELETE FROM rule_snro WHERE rule_id = ?"
                values = event["params"]["querystring"]["rule_id"]
                mycursor.execute(sqlQuery, values)

                mydb.commit()
                msg = "Data deleted!"

    except:
        return {"statuscode": 500, "body": json.dumps("Unable to delete")}

    finally:
        mydb.close()

    return {
        "statuscode": 200,
        "body": msg,
    }


# enablexraytraces:


def EnableXrayLambda(tracing):
    client = boto3.client(
        "lambda",
        aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
        aws_secret_access_key="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",
        region_name="eu-central-1",
    )
    response = client.list_functions()
    NextMarker = response["NextMarker"]
    nof = len(response["Functions"])
    fun = []

    if len(response["Functions"]) != 0:
        count = len(response["Functions"])
        count1 = 0
        while count != count1:
            fun.append(response["Functions"][count1]["FunctionName"])
            count1 = count1 + 1

    while NextMarker != "":
        response = client.list_functions(Marker=NextMarker)
        if "Functions" in response:
            temp = len(response["Functions"])
            nof = nof + temp
        if len(response["Functions"]) != 0:
            count = len(response["Functions"])
            count1 = 0
            while count != count1:
                fun.append(response["Functions"][count1]["FunctionName"])
                count1 = count1 + 1
        if "NextMarker" in response:
            NextMarker = response["NextMarker"]
        else:
            NextMarker = ""

    for i in fun:
        response = client.update_function_configuration(
            # FunctionName  = 'getfunctionnames',
            FunctionName=i,
            TracingConfig={"Mode": tracing},  # PassThrough #Active
        )


def EnableXrayApi(tracing):
    devstages = ["dev", "einvoice-v1", "einvoice-dev"]

    client = boto3.client(
        "apigateway",
        aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
        aws_secret_access_key="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",
        region_name="eu-central-1",
    )
    # code to get all the api in a perticualr region
    response = client.get_rest_apis()
    # code to get api stage names

    for api in response["items"]:
        response1 = client.get_stages(restApiId=api["id"])

        rapiid = api["id"]
        stagename = ""
        for stage in response1["item"]:
            if stage["stageName"] in devstages:
                stagename = stage["stageName"]
        if stagename != "":
            response = client.update_stage(
                restApiId=rapiid,
                stageName=stagename,
                patchOperations=[
                    {"op": "replace", "path": "/tracingEnabled", "value": tracing},
                ],
            )
        stagename = ""
        rapiid = ""


def EnableXRayTraces(event, context):
    try:
        print(event)
        check = event["params"]["header"]["opetion"]

        if check == "on":
            tracing = "Active"
        else:
            tracing = "PassThrough"

        if tracing != "":
            EnableXrayLambda(tracing)

        if check == "on":
            tracing = "True"
        else:
            tracing = "False"

        if tracing != "":
            EnableXrayApi(tracing)

    except:
        return {"statuscode": 500, "body": json.dumps("Internal Failure!")}

    return {"statusCode": 200, "body": json.dumps("Xray Enabled successfully")}


def decode_jwt_token(Authorization):
    header1 = jwt.decode(Authorization, options={"verify_signature": False})
    if "email" in header1:
        return header1["email"]
    else:
        return ""


# getemail:


def GetUserEmails(event, context):
    atoken = ""
    op = ""
    enable = ""
    if "Authorization" in event["params"]["header"]:
        atoken = event["params"]["header"]["Authorization"]
    global dbScehma
    dbScehma = 'DBADMIN'

    client = boto3.client("secretsmanager")
    secret = event["stage-variables"]["secreat"]
    resp = client.get_secret_value(SecretId=secret)
    secretDict = json.loads(resp["SecretString"])

    mydb = dbapi.connect(
        address='7bd70c10-e2c3-4b6f-aaea-9d9d067bd91d.hana.trial-us10.hanacloud.ondemand.com',
        port=443,
        user='DBADMIN',
        password='Vinod@123',
        encrypt='True' )

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            print(event)

            Flag = mycursor.execute(
                " select value1 from elipo_setting where key_name = 'config_trace' "
            )
            if Flag == 1:
                mycursor.execute("SELECT userid from email where flag = 'True' ")
                all_emails = mycursor.fetchall()
                all_emails=convertValuesTodict(mycursor.description,all_emails)
                if atoken != "":
                    op = decode_jwt_token(atoken)
                    if op == "":
                        all_emails = {}
                        enable = False
                    for ch in all_emails:
                        if op == ch["userid"]:
                            enable = True
                            break
                        else:
                            enable = False
                else:
                    enable = False
                    all_emails = {}
            else:
                enable = False
                all_emails = {}

    except:
        return {"statuscode": 500, "body": json.dumps("Internal Failure")}

    finally:
        mydb.close()

    return {
        "statusCode": 200,
        # 'body': {'Enable' : enable}
        "body": {"Enable": enable, "email": op},
    }


# attachment:

#event not found
def deleteAttachment(event, context):
    global dbScehma

    # client = boto3.client(
    #     "secretsmanager",
    #     region_name="eu-central-1",
    #     aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
    #     aws_secret_access_key="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",
    # )

    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(SecretId=secret)
    # secretDict = json.loads(resp["SecretString"])

    mydb = hdbcliConnect()

    try:
        with mydb.cursor() as mycursor:
            dbScehma = ' DBADMIN '

            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            mycursor.execute(
                " select value1 from elipo_setting where key_name = 'config_trace' "
            )
            on = mycursor.fetchone()
            if on["value1"] == "on":
                chk = enable_xray(event)
                if chk["Enable"] == True:
                    patch_all()
                    print(event)

            attachment = event["params"]["querystring"]["attachment_id"]
            email = event["params"]["querystring"]["userid"]

            mycursor.execute(
                "select member_id, (fs_name|| ' '||ls_name) as member_name from member where email = ?",
                email,
            )
            member = mycursor.fetchone()

            values = (attachment,)
            mycursor.execute(
                "SELECT * FROM file_storage where attach_id = ?",
                values,
            )
            attachment_det = mycursor.fetchone()

            mycursor.execute(
                "select in_status from invoice_header where invoice_no = ?",
                attachment_det["file_id"],
            )
            invoice_header = mycursor.fetchone()

            mycursor.execute(
                "DELETE FROM file_storage WHERE attach_id = ?",
                values,
            )

            msg_cmnt = (
                attachment_det["name"]
                + " attachment deleted by "
                + member["member_name"]
            )
            temp = (
                attachment_det["file_id"],
                invoice_header["in_status"],
                invoice_header["in_status"],
                member["member_id"],
                msg_cmnt,
            )
            sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values {}"
            mycursor.execute(sqlQuery.format(tuple(temp)))

            if attachment_det:
                s3 = boto3.client("s3")
                s3.delete_object(
                    Bucket=attachment_det["file_path"], Key=attachment_det["name"]
                )

                mydb.commit()

                return {"statuscode": 200, "body": json.dumps("Deleted Successfully!")}

            return {"statuscode": 200, "body": json.dumps("Attachment not Found")}
    except:
        return {"statuscode": 500, "body": json.dumps("Internal Error!")}

    finally:
        mydb.close()


def downloadAttachments(event, context):
    print(event)
    global dbScehma
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    #     "secretsmanager",
    #     region_name="eu-central-1",
    #     aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
    #     aws_secret_access_key="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",
    # )

    # secret = event["stageVariables"]["secreat"]
    # bucket = event["stageVariables"]["non_ocr_attachment"]
    # stage = event["stageVariables"]["lambda_alias"]

    # resp = client.get_secret_value(SecretId=secret)

    # secretDict = json.loads(resp["SecretString"])

    mydb = hdbcliConnect()
    
    try:
        print(event)
        content_type = ""

        s3 = boto3.client("s3")

        file_name = event["queryStringParameters"]["file_name"]

        if "email" in event["queryStringParameters"]:  # changed
            email = event["queryStringParameters"]["email"]
            if (
                email == "abhishek.p@peolsolutions.com"
                or email == "pramod.b@peolsolutions.com"
            ):
                file_name = "old-dev/heda-plywood.png"
            else:
                file_name = event["queryStringParameters"]["file_name"]
                # file_name = 'old-dev/Archidply-logo.png' #changed

        bucket_used = event["stageVariables"]["non_ocr_attachment"]
        print(file_name, bucket_used)

        if "userid" in event["queryStringParameters"]:
            userid = event["queryStringParameters"]["userid"]
            invoice_no = event["queryStringParameters"]["invoice_no"]

            with mydb.cursor() as mycursor:
                defSchemaQuery = "set schema " + dbScehma
                print("dnaksjhdksjdhaskd")
                mycursor.execute(defSchemaQuery)

                mycursor.execute(
                    " select value1 from elipo_setting where key_name = 'config_trace' "
                )
                on = mycursor.fetchone()
                on = convertValuesTodict(mycursor.description , on)	
                for row in on:
                    if row['value1'] =='on':
                        chk = enable_xray(event)
                        patch_all()
                        print(event)

                mycursor.execute(
                    "select (fs_name||' '||ls_name) as member_name, member_id from member where email = ?",
                    userid,
                )
                member = mycursor.fetchone()
                member = convertValuesTodict(mycursor.description, member)
                member = member[0]

                msg_cmnt = (
                    file_name + " attachment downloaded by " + member["member_name"]
                )
                temp = (invoice_no, "", "", member["member_id"], msg_cmnt)
                sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values {}"
                mycursor.execute(sqlQuery.format(tuple(temp)))

                mydb.commit()

        download = False

        if "download" in event["queryStringParameters"]:
            download = True

        if "bucket" in event["queryStringParameters"]:
            bucket_name = event["queryStringParameters"]["bucket"]

        else:
            bucket_name = bucket_used

        file_obj = s3.get_object(Bucket=bucket_name, Key=file_name)
        file_content = file_obj["Body"].read()

        filenamett, file_extension = os.path.splitext(file_name)

        if file_extension == ".pdf":
            content_type = "application/pdf"
        elif file_extension == ".png":
            content_type == "image/png"
        elif file_extension == ".jpg":
            content_type == "image/jpg"
        elif file_extension == ".jpeg":
            content_type == "image/jpg"

        conte = ""

        if download:
            conte = """ attachment; filename=""" + file_name

        return {
            "headers": {
                "Content-Type": content_type,
                "Content-Disposition": conte,
                "Access-Control-Allow-Origin": "*",
                "filename": "jhghjd.pdf",
            },
            "statusCode": 200,
            "body": base64.b64encode(file_content),
            "isBase64Encoded": True,
        }

    except Exception as e:
        return {
            "headers": {
                "Content-Type": content_type,
                "Access-Control-Allow-Origin": "*",
            },
            #   'body' : json.dumps("No file Found"),
            "body": json.dumps(str(e)),
            "statusCode": 500,
        }


# .........................................................................................................
#working fine
def uploadAttachments(event, context):
    global dbScehma
    dbScehma = '"DBADMIN"'

    # client = boto3.client(
    #     "secretsmanager",
    #     region_name="eu-central-1",
    #     aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
    #     aws_secret_access_key="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",
    # )

    # secret = event["stageVariables"]["secreat"]
    bucket = event["stageVariables"]["non_ocr_attachment"]

    # resp = client.get_secret_value(SecretId=secret)
    # secretDict = json.loads(resp["SecretString"])

    mydb = hdbcliConnect()

    s3 = boto3.client("s3")
    invoice_no = ""

    try:
        if "body" in event and event["body"]:
            post_data = base64.b64decode(event["body"])
            if "Content-Type" in event["headers"]:
                content_type = event["headers"]["Content-Type"]
                ct = "Content-Type: " + content_type + "\n"

            elif "content-type" in event["headers"]:
                content_type = event["headers"]["content-type"]
                ct = "content-type: " + content_type + "\n"

            if ct:
                msg = email.message_from_bytes(ct.encode() + post_data)

                if msg.is_multipart():
                    multipart_content = {}

                    for part in msg.get_payload():
                        multipart_content[
                            part.get_param("name", header="content-disposition")
                        ] = part.get_payload(decode=True)

                    file_id = " ".join(
                        re.findall(
                            "(?<=')[^']+(?=')", str(multipart_content["file_id"])
                        )
                    )
                    file_name = " ".join(
                        re.findall(
                            "(?<=')[^']+(?=')", str(multipart_content["file_name"])
                        )
                    )
                    mime_type = " ".join(
                        re.findall(
                            "(?<=')[^']+(?=')", str(multipart_content["mime_type"])
                        )
                    )

                    up_file_name = str(file_id) + file_name

                    s3_upload = s3.put_object(
                        Bucket=bucket, Key=up_file_name, Body=multipart_content["file"]
                    )

                    var_path = (
                        "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/dev/attachment?file_name="
                        + up_file_name
                    )

                    with mydb.cursor() as mycursor:
                        defSchemaQuery = "set schema " + dbScehma
                        mycursor.execute(defSchemaQuery)

                        mycursor.execute(
                            "select value1 from elipo_setting  where key_name = ?",'config_trace' 
                        )
                        on = mycursor.fetchone()
                        # on = convertValuesTodict(mycursor.description , on)
                        # for row in on:
                        if on['value1'] =='on':
                                chk = enable_xray(event)
                                patch_all()
                                print(event)

                        sqlQuery = "INSERT INTO file_storage (file_id, name, mime_type, file_path, file_link) VALUES {}"
                        values = (file_id, up_file_name, mime_type, bucket, var_path)
                        mycursor.execute(sqlQuery.format(tuple(values)))

                        mydb.commit()

    except Exception as e:
        mydb.rollback()
        return {
            "statusCode": 500,
            "headers": {
                "Content-type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps(str(e)),
        }

    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            "statusCode": 500,
            "headers": {
                "Content-type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps(str(e)),
        }

    finally:
        mydb.close()

    return {
        "statusCode": 200,
        "headers": {
            "Content-type": "application/json",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,X-Amz-Security-Token,Authorization,X-Api-Key,X-Requested-With,Accept,Access-Control-Allow-Methods,Access-Control-Allow-Origin,Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
            "X-Requested-With": "*",
        },
        "body": json.dumps("File uploaded successfully!"),
    }


# member-profile-upload:

#event not found might raise error for length of profile photo in table member
def uploadUserProfilePhoto(event, context):
    global dbScehma
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    #     "secretsmanager",
    #     region_name="eu-central-1",
    #     aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
    #     aws_secret_access_key="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",
    # )

    secret = event["stageVariables"]["secreat"]
    bucket = event["stageVariables"]["non_ocr_attachment"]
    stage = event["requestContext"]["stage"]

    # resp = client.get_secret_value(SecretId=secret)

    # secretDict = json.loads(resp["SecretString"])

    mydb = hdbcliConnect()

    s3 = boto3.client("s3")

    try:
        print(event)
        if "body" in event and event["body"]:
            post_data = base64.b64decode(event["body"])
            # print(event["body"])
            # print("hu")
            if "Content-Type" in event["headers"]:
                # print("123")
                content_type = event["headers"]["Content-Type"]
                ct = "Content-Type: " + content_type + "\n"
                # print("1ok")

            elif "content-type" in event["headers"]:
                # print("123")
                content_type = event["headers"]["content-type"]
                ct = "content-type: " + content_type + "\n"
                # print("1ok")

            if ct:
                msg = email.message_from_bytes(ct.encode() + post_data)

                if msg.is_multipart():
                    multipart_content = {}

                    # print("2ok")
                    for part in msg.get_payload():
                        multipart_content[
                            part.get_param("name", header="content-disposition")
                        ] = part.get_payload(decode=True)

                    # print("Multipart Content", multipart_content)

                    member_id = " ".join(
                        re.findall(
                            "(?<=')[^']+(?=')", str(multipart_content["member_id"])
                        )
                    )
                    file_name = " ".join(
                        re.findall(
                            "(?<=')[^']+(?=')", str(multipart_content["file_name"])
                        )
                    )
                    # print(member_id, file_name)

                    filenamett, file_extension = os.path.splitext(file_name)
                    up_file_name = str(member_id) + file_name
                    # print(up_file_name)

                    file_name = "profile_photo/" + up_file_name
                    # s3_upload = s3.put_object(Bucket="einvoice-attachments", Key=file_name, Body=multipart_content["file"])
                    s3_upload = s3.put_object(
                        Bucket=bucket, Key=file_name, Body=multipart_content["file"]
                    )

                    var_path = (
                        "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/"
                        + stage
                        + "/attachment?file_name=profile_photo/"
                        + up_file_name
                        + "&bucket="
                        + bucket
                    )
                    # print(var_path)

                    with mydb.cursor() as mycursor:
                        defSchemaQuery = "set schema " + dbScehma
                        mycursor.execute(defSchemaQuery)

                        mycursor.execute(
                            " select value1 from elipo_setting where key_name = 'config_trace' "
                        )
                        on = mycursor.fetchone()
                        if on["value1"] == "on":
                            chk = enable_xray(event)
                            if chk["Enable"] == True:
                                patch_all()
                                print(event)

                        sqlQuery = (
                            "update member set profile_photo = ? where member_id = ?"
                        )
                        values = (var_path, member_id)
                        mycursor.execute(sqlQuery, values)

                        mydb.commit()

    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps(str(e)),
        }

    except Exception as e:
        mydb.rollback()
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps(str(e)),
        }

    finally:
        mydb.close()

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps("File uploaded successfully!"),
    }


# ocr-b64-image:


def getTextFromImage(event, context):
    eventBody = json.loads(json.dumps(event))["body"]

    imageBase64 = json.loads(eventBody)["Image"]

    # Amazon Textract client
    textract = boto3.client(
        "textract",
        region_name="eu-central-1",
        aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
        aws_secret_access_key="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",
    )

    # Call Amazon Textract
    response = textract.detect_document_text(
        Document={"Bytes": base64.b64decode(imageBase64)}
    )

    detectedText = ""

    # Print detected text
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            detectedText += item["Text"] + "\n"

    return {"statusCode": 200, "body": json.dumps(detectedText)}


# flask-gmail:

s3 = boto3.client(
    "s3",
    region_name="eu-central-1",
    aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
    aws_secret_access_key="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",
)
creds = None
file_name = "token.pickle"
bucket_name = "file-bucket-emp"
state = ""
CLIENTSECRETS_LOCATION = "client_secret.json"
REDIRECT_URI = "https://localhost:4200/inbox"
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    # Add other requested scopes.
]


class GetCredentialsException(Exception):
    """Error raised when an error occurred while retrieving credentials.

    Attributes:
      authorization_url: Authorization URL to redirect the user to in order to
                         request offline access.
    """

    def __init__(self, authorization_url):
        """Construct a GetCredentialsException."""
        self.authorization_url = authorization_url


class CodeExchangeException(GetCredentialsException):
    """Error raised when a code exchange has failed."""


class NoRefreshTokenException(GetCredentialsException):
    """Error raised when no refresh token has been found."""


class UnknownExceotion(Exception):
    """"""


class NoUserIdException(Exception):
    """Error raised when no user ID could be retrieved."""


class NoStoredCredentials(Exception):
    """"""


def get_stored_credentials(user_id):
    try:
        # fetching from bucket
        encoded_file = s3.get_object(Bucket=bucket_name, Key=user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
    except Exception as excep:
        creds = None
        raise NoUserIdException(excep)
        # if excep.response['Error']['Code'] == 'NoSuchKey':
        #     raise NoUserIdException(excep)
        # else:
        #     raise UnknownExceotion(excep)


def store_credentials(user_id, credentials):
    try:
        fileBody = pickle.dumps(credentials)
        s3.put_object(Bucket=bucket_name, Key=user_id, Body=fileBody)

    except Exception as e:
        raise NotImplementedError(e)


def exchange_code(authorization_code):
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, " ".join(SCOPES))
    flow.redirect_uri = REDIRECT_URI

    try:
        credentials = flow.step2_exchange(authorization_code)
        return credentials
    except FlowExchangeError as error:
        logging.error("An error occurred: ?", error)
        raise CodeExchangeException(None)


def get_user_info(credentials):
    user_info_service = build(
        serviceName="oauth2", version="v2", http=credentials.authorize(httplib2.Http())
    )
    print("Service is ok")

    user_info = None

    try:
        user_info = user_info_service.userinfo().get().execute()
    except errors.HttpError as e:
        logging.error("An error occurred: %s", e)
    if user_info and user_info.get("id"):
        return user_info
    else:
        raise NoUserIdException()


def get_authorization_url(email_address=None, state=None):
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, " ".join(SCOPES))
    flow.params["access_type"] = "offline"
    flow.params["approval_prompt"] = "force"
    if email_address:
        flow.params["user_id"] = email_address
    if state:
        flow.params["state"] = state
    return flow.step1_get_authorize_url(redirect_uri=REDIRECT_URI)


def get_credentials(authorization_code=None, state=None, user_id=None):
    email_address = ""
    try:
        if authorization_code:
            credentials = exchange_code(authorization_code)
            user_info = get_user_info(credentials)
            email_address = user_info.get("email")
            user_id = user_info.get("id")
            if credentials.refresh_token is not None:
                store_credentials(user_id, credentials)
                return credentials

        elif user_id:
            credentials = get_stored_credentials(user_id)
            if credentials and credentials.refresh_token is not None:
                return credentials

    except CodeExchangeException as error:
        logging.error("An error occurred during code exchange.")
        # Drive apps should try to retrieve the user and credentials for the current
        # session.
        # If none is available, redirect the user to the authorization URL.
        authorization_url = get_authorization_url(email_address, state)
        raise CodeExchangeException(authorization_url)

    except NoUserIdException:
        logging.error("No user ID could be retrieved.")
        # No refresh token has been retrieved.
        authorization_url = get_authorization_url(email_address, state)
        raise NoRefreshTokenException(authorization_url)


def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build("gmail", "v1", http=http)


def search_messages(service, user_id, search_query):
    try:
        search_id = (
            service.users().messages().list(userId=user_id, q=search_query).execute()
        )
        print(search_id)
        no_result = search_id["resultSizeEstimate"]

        final_list = []
        if no_result > 0:
            message_ids = search_id["messages"]

            for ids in message_ids:
                final_list.append(ids["id"])

            return final_list

    except Exception as error:
        print("An error occurred: ", error)


def fetch_attachments(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        # print("fetch attchments encoded",message)
        attachments = []

        for part in message["payload"]["parts"]:
            if part["filename"]:
                if "data" in part["body"]:
                    data = part["body"]["data"]
                else:
                    att_id = part["body"]["attachmentId"]
                    att = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId=user_id, messageId=msg_id, id=att_id)
                        .execute()
                    )
                    data = att["data"]

                file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
                # file_data = '"'+file_data+'"'

                file = {
                    "partId": part["partId"],
                    "mimeType": part["mimeType"],
                    "filename": part["filename"],
                    "filedata": str(file_data),
                }

                attachments.append(file)

        return {
            "snippet": message["snippet"],
            "headers": message["payload"]["headers"],
            "attachments": attachments,
        }

    except Exception as error:
        print("An error occurred: ", error)


def getEmailDetails(event, context):
    try:
        if "code" in event["params"]["querystring"]:
            cred = get_credentials(
                user_id=event["params"]["querystring"]["user_id"],
                authorization_code=event["params"]["querystring"]["code"],
                state=state,
            )
        elif "user_id" in event["params"]["querystring"]:
            cred = get_credentials(
                user_id=event["params"]["querystring"]["user_id"], state=state
            )

        if cred:
            service = build_service(credentials=cred)
            email_msges = search_messages(service, "me", "newer_than:10d")
            emails = []
            for em_msg in email_msges:
                emails.append(fetch_attachments(service, "me", em_msg))

            print(emails)
            return emails

    except NoRefreshTokenException as ex:
        print("NoRefreshTokenException")
        return ex.authorization_url
    except CodeExchangeException as ex:
        print("CodeExchangeException")
        return ex.authorization_url


# gmail:


def fetchEmailData(event, context):
    pass


# multi-tenant:

#no event to test might raise an error
def multiTenentDemo(event, context):
    client = boto3.client(
        "secretsmanager",
        region_name="eu-central-1",
        aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
        aws_secret_access_key="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",
    )
    secret = "test/einvoice/secret"
    resp = client.get_secret_value(SecretId=secret)
    secretDict = json.loads(resp["SecretString"])

    mydb = dbapi.connect(
        address='7bd70c10-e2c3-4b6f-aaea-9d9d067bd91d.hana.trial-us10.hanacloud.ondemand.com',
        port=443,
        user='DBADMIN',
        password='Vinod@123',
        encrypt='True' )

    try:
        with mydb.cursor() as mycursor:
            if "tenant_id" in event["params"]["querystring"]:
                mycursor.execute(
                    "select * from deault_schema.teneant_details where teneant_id = %s",
                    event["params"]["querystring"]["tenant_id"],
                )
                schema = mycursor.fetchone()

                defSchemaQuery = "set schema DBADMIN "
                mycursor.execute(defSchemaQuery)

                mycursor.execute(
                    " select value1 from elipo_setting where key_name = 'config_trace' "
                )
                on = mycursor.fetchone()
                
                on = convertValuesTodict(mycursor.description , on)	
                for row in on:
                    if row['value1'] =='on':
                        chk = enable_xray(event)
                        patch_all()
                        print(event)

                mycursor.execute("select * from state_code")
                records = mycursor.fetchall()
                records=convertValuesTodict(mycursor.description, records)

    except:
        return {"statuscode": 500, "body": json.dumps("Internal Failure")}

    finally:
        mydb.close()

    return {"statuscode": 200, "body": records}


# rolemaster:

# no event to test might raise an error
def RDSQueryExample(event, context):
    client = boto3.client(
        "secretsmanager",
        region_name="eu-central-1",
        aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
        aws_secret_access_key="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",
    )
    resp = client.get_secret_value(SecretId="test/einvoice/secret")

    secretDict = json.loads(resp["SecretString"])

    mydb = dbapi.connect(
        address='7bd70c10-e2c3-4b6f-aaea-9d9d067bd91d.hana.trial-us10.hanacloud.ondemand.com',
        port=443,
        user='DBADMIN',
        password='Vinod@123',
        encrypt='True' )

    try:
        with mydb.cursor() as mycursor:
            mycursor.execute("select * from Role_master")
            records = []
            temp=convertValuesTodict(mycursor.description,mycursor.fetchall())
            for row in temp:
                record = {
                    "UserName": row["User_ID"],
                    "Role": row["Role_id"],
                    "Date": row["Valid_Upto"],
                }
                records.append(record)
    finally:
        mydb.close()

    return {
        "statuscode": 200,
        "body": records,
    }

