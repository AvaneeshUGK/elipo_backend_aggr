import pymysql.cursors
import boto3
import json
import base64
import os
from collections import OrderedDict 
import requests
from  aws_xray_sdk.core import recorder 
from aws_xray_sdk.core import patch_all
from datetime import date
import jwt
import email
import re
from fuzzywuzzy import fuzz
import math
import datetime
from calendar import monthrange
from ast import Pass
from googleapiclient.discovery import build
import httplib2
import pickle
from datetime import datetime
import email.mime.text
import urllib.parse
import os
import time
from botocore.client import Config
from aws_xray_sdk.core import patcher
from hdbcli import dbapi


atoken = ''
flg = ''
patcher.patch_all()

# client = boto3.client('events')

def enable_xray(event):
    if 'Authorization' in event['params']['header'] :
       atoken =  event['params']['header']['Authorization']
    
    if atoken != '':
        flg = requests.get("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/getemail", headers={"Content-Type":"application/json", "Authorization":atoken})

    return json.loads(flg.text)['body']

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

#Rules : 

def getRuleDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
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

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if "rule_id" in event["params"]["querystring"]:
                
                rule_id = event["params"]["querystring"]["rule_id"]
                rule = {}
                
                mycursor.execute("SELECT a.*, b.rule_name " \
                    "FROM rule a " \
                    "inner join rule_snro b " \
                    "on a.rule_id = b.rule_id " \
                    "where a.rule_id = %s", rule_id)
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
               
                mycursor.execute("select * from rule_approver where rule_key = %s", rule_id)
                approver = mycursor.fetchall()
                
                approver_final = [] 
                groupid = []
                memberid = []
                
                for row in approver:
                    if row["isgroup"] == 'y':
                        groupid.append(row["approver"])
                    elif row["isgroup"] == 'n':
                        memberid.append(row["approver"])
                
                if groupid and len(groupid) > 1:
                    mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in {}".format(tuple(groupid)))
                    
                elif groupid and len(groupid) == 1:
                    group = (groupid[0])
                    sqlQuery = "select group_id, name from " + dbScehma + ".group where group_id = %s"
                    mycursor.execute(sqlQuery, group)
                    
                for row in mycursor:
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
                    sqlQuery = "select member_id, fs_name, ls_name, position from member where member_id = %s"
                    mycursor.execute(sqlQuery, member) 
                    
                for row in mycursor:
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
                    "on a.d_value = c.department_id " \
                	"where b.is_approval = %s " \
                	"order by a.rule_id", is_approval)
                rules = mycursor.fetchall()
                
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
                    sqlQuery = "select * from rule_approver where rule_key = %s"
                    mycursor.execute(sqlQuery, key)
                    approvers_list = mycursor.fetchall()
                
                groupid = []
                memberid = []
                
                for row in approvers_list:
                    if row["isgroup"] == 'y':
                        groupid.append(row["approver"])
                    elif row["isgroup"] == 'n':
                        memberid.append(row["approver"])
            
                approver_final = []  
                
                if groupid and len(groupid) > 1:
                
                    mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in {}".format(tuple(groupid)))
                    
                elif len(groupid) == 1:
                    group = (groupid[0])
                    sqlQuery = "select group_id, name from " + dbScehma + ".group where group_id = %s"
                    mycursor.execute(sqlQuery, group)
                    
                for row in mycursor:
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
                    sqlQuery = "select member_id, fs_name, ls_name, position from member where member_id = %s"
                    mycursor.execute(sqlQuery, member) 
                    
                for row in mycursor:
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

def postRuleDetails(event , context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
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

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 	

            dup = []
            for row in criteria:

                if row['decider'] == "default":
                    values = (row['decider'],)
                    sqlQuery = "select rule_id from rule where decider = %s"
                    mycursor.execute(sqlQuery, values)
                    defu = mycursor.fetchall()
                    if defu:
                        raise pymysql.err.IntegrityError
                        
                if row['decider'] == "default_assignment":
                    values = (row['decider'],)
                    sqlQuery = "select rule_id from rule where decider = %s"
                    mycursor.execute(sqlQuery, values)
                    defu = mycursor.fetchall()
                    if defu:
                        raise pymysql.err.IntegrityError
                
                if row['decider'] != "npo":
                    values = (row['decider'], row['operator'], row['value1'], row['value2'])
                    sqlQuery = "select rule_id from rule where decider = %s and operator = %s and d_value = %s and d_value2 = %s"
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
                    sqlQuery = "select rule_id from rule where rule_id = %s"
                    mycursor.execute(sqlQuery, values)
                    result = mycursor.fetchall()

                    if result and len(criteria) == len(result):
                        raise pymysql.err.IntegrityError

            sqlQuery = "INSERT INTO rule_snro (rule_name, approval_type, is_approval) VALUES ( %s, %s, %s)"
            values = ( record["rule_name"], record["approval_type"], record["is_approval"])
            mycursor.execute(sqlQuery, values)

            rule_key = mycursor.lastrowid

            sqlQuery = "INSERT INTO rule ( rule_id, decider, operator, d_value, d_value2, approval_type, ec_isgroup, escelator, ifnot_withindays, comments, " \
                       "decider_type, due_notification, due_reminder, overdue_notification, overdue_reminder) VALUES " \
                       "( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            values = []
            for row in criteria:
                tup = (rule_key, row['decider'], row['operator'], row['value1'], row['value2'], record["approval_type"], record["ec_isgroup"], record["escelator"], 
                    record["ifnot_withindays"], record["comments"], row['type'], record["due_notification"], record["due_reminder"], record["overdue_notification"],
                    record["overdue_reminder"])
                values.append(tup)
            mycursor.executemany(sqlQuery, values)

            values = []

            for index, each in enumerate(approvers):
                tup = (rule_key, each['isgroup'], each['approver'], each["level"])
                values.append(tup)

            sqlQuery = "INSERT INTO rule_approver (rule_key, isgroup, approver, level) VALUES ( %s, %s, %s, %s)"

            if values:
                mycursor.executemany(sqlQuery, values)

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

def patchRuleDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
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

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    record = {
        "rule_id": "",
        "rule_name": "",
        "approval_type": "",
        "ec_isgroup": "",
        "escelator": "",
        "ifnot_withindays": "",
        "due_notification" : "",
        "due_reminder" : "",
        "overdue_notification" : "",
        "overdue_reminder" : "",
        "comments": ""
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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
        
            rule = event["params"]["querystring"]["rule_id"]
            
            if "rule_name" in event["params"]["querystring"]:
                record["rule_name"] = event["params"]["querystring"]["rule_name"]
            
            data = []
            
            if "rule_id" in event["params"]["querystring"]:
                
                sqlQuery = "UPDATE rule_snro set rule_name = %s WHERE rule_id = %s"
                values = ( record["rule_name"], rule)
                mycursor.execute(sqlQuery, values)
                
                for row in event["body-json"]["criteria"]:
                    
                    if str(row['type']) == "number":
                        value1 = '0' * (11 - len(str(row['value1']))) + str(row['value1'])
                        value2 = '0' * (11 - len(str(row['value2']))) + str(row['value2'])
                    else:
                        value1 = row['value1']
                        value2 = row['value2']
                        
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
                        "due_notification" : record["due_notification"],
                        "due_reminder" : record["due_reminder"],
                        "overdue_notification" : record["overdue_notification"],
                        "overdue_reminder" : record["overdue_reminder"],
                        "decider_type": row["type"]
                    }
                    data.append(cri)
                
                sqlQuery = "insert into rule (rule_id, decider, operator, d_value, d_value2, approval_type, ec_isgroup, escelator, ifnot_withindays, comments, " \
                    "decider_type, due_notification, due_reminder, overdue_notification, overdue_reminder ) values (%s, %s, %s, %s, %s, %s, %s, " \
                    "%s, %s, %s, %s, %s, %s, %s, %s)"
                   
                default = None
                
                if data:
                    
                    values = []
                    for row in data:
                        
                        if row["decider"] == 'default_assignment': 
                            value = ('default_assignment',)
                            mycursor.execute("select * from rule where decider = %s", value)
                            default = mycursor.fetchone()
                            
                            if default:
                                if int(default["rule_id"]) != int(row["rule_id"]): 
                                    return {   
                                        'statuscode': 500,
                                        'body': json.dumps('Default Rule already exist!')
                                    }
                            
                            
                        tup = (row["rule_id"], row["decider"], row["operator"], row["d_value"], row["d_value2"], row["approval_type"], row["ec_isgroup"],
                            row["escelator"], row["ifnot_withindays"], row["comments"], row["decider_type"], row["due_notification"], row["due_reminder"], 
                            row["overdue_notification"], row["overdue_reminder"])
                        values.append(tup)
                    
                if values:
                    mycursor.execute("delete from rule where rule_id = %s", rule)
                    mycursor.executemany(sqlQuery, values)
                
                if "approvers" in event["body-json"]:
                    for approver in event["body-json"]["approvers"]:
                        app = {
                            'level' : approver['level'],
                            'isgroup' : approver['isgroup'],
                            'approver' : approver['approver']
                        }
                        approvers.append(app)
                        
                        if "members" in approver:
                            for members in approver["members"]:
                                mem = {
                                    'level' : approver["level"],
                                    'isgroup': 'n',
                                    'approver' : members
                                }
                                approvers.append(mem)
                
                sqlQuery = "delete from rule_approver where rule_key = %s"
                mycursor.execute(sqlQuery, rule)
                
                values = []
                
                for index, each in enumerate(approvers):
                    tup = (rule, each['isgroup'], each['approver'], each['level'])
                    values.append(tup)
                
                sqlQuery = "INSERT INTO rule_approver (rule_key, isgroup, approver, level) VALUES ( %s, %s, %s, %s)"
                
                if values:
                    mycursor.executemany(sqlQuery, values)
                
                mydb.commit()
                msg = "Successfully Updated!"
    
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Duplicate Rule")
        }
    
    except:
        return {
            'statuscode': 500,
            'body': msg
        }
                
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': msg
    }

def deleteRuleDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
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

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    msg = "Data not deleted!"
    
    try:
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            if "rule_id" in event["params"]["querystring"]:
                
                sqlQuery = ("DELETE FROM rule WHERE rule_id = %s")
                values = ( event["params"]["querystring"]["rule_id"] )
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = ("DELETE FROM rule_approver WHERE rule_key = %s")
                values = ( event["params"]["querystring"]["rule_id"] )
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = ("DELETE FROM rule_snro WHERE rule_id = %s")
                values = ( event["params"]["querystring"]["rule_id"] )
                mycursor.execute(sqlQuery, values)
                
                mydb.commit()
                msg = "Data deleted!"
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Unable to delete")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': msg,
    }

def EnableXrayLambda(tracing):
    
    client = boto3.client('lambda', aws_access_key_id='AKIAXUCMAX6S27NZCRFL',aws_secret_access_key='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',region_name='eu-central-1')
    response = client.list_functions()
    NextMarker = response['NextMarker']
    nof = len(response['Functions'])
    fun = []

    if len(response['Functions']) != 0:
        count = len(response['Functions'])
        count1 = 0
        while(count != count1):
            fun.append(response['Functions'][count1]['FunctionName'])
            count1 = count1 + 1

    while(NextMarker != '' ):
        response = client.list_functions(Marker = NextMarker)
        if 'Functions' in response :
            temp = len(response['Functions'])
            nof = nof + temp
        if len(response['Functions']) != 0:
            count = len(response['Functions'])
            count1 = 0
            while(count != count1):
                fun.append(response['Functions'][count1]['FunctionName'])
                count1 = count1 + 1
        if 'NextMarker' in response :
            NextMarker = response['NextMarker']
        else:
            NextMarker = ''

    for i in fun:
        response = client.update_function_configuration(
        # FunctionName  = 'getfunctionnames',
        FunctionName  = i,
        TracingConfig = {'Mode':tracing}   #PassThrough #Active
        )
    
def EnableXrayApi(tracing):
    
    devstages = [ 'dev' , 'einvoice-v1' , 'einvoice-dev' ]

    client = boto3.client('apigateway', aws_access_key_id='AKIAXUCMAX6S27NZCRFL',aws_secret_access_key='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',region_name='eu-central-1')
    #code to get all the api in a perticualr region 
    response = client.get_rest_apis()
   # code to get api stage names 

    for api in response['items'] :
        response1 = client.get_stages(
        restApiId=api['id'])

        rapiid = api['id']
        stagename = ''
        for stage in response1['item']:
            if stage['stageName'] in devstages:
                stagename = stage['stageName']
        if stagename != '':
            response = client.update_stage(
                restApiId=rapiid,
                stageName=stagename,
                patchOperations=[
                    {
                        'op': 'replace',
                        'path': '/tracingEnabled',
                        'value': tracing
                    },
                ])
        stagename = ''
        rapiid = ''

def EnableXRayTraces(event, context):

    try:
        print(event)
        check = event['params']['header']['opetion']

        if check == 'on':
            tracing = 'Active'
        else:
            tracing = 'PassThrough'
        
        if tracing != '':
            EnableXrayLambda(tracing)

        if check == 'on':
            tracing = 'True'
        else:
            tracing = 'False'
        
        if tracing != '':
            EnableXrayApi(tracing)

    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure!")
        }


    return {
        'statusCode': 200,
        'body': json.dumps('Xray Enabled successfully')
    }

def decode_jwt_token(Authorization):
    header1 =  jwt.decode(Authorization , options={"verify_signature": False})
    if 'email' in header1:
        return header1['email']
    else:
        return ''

#queries working fine
def GetUserEmails(event, context):
    
    atoken = ''
    op = ''
    enable = ''
    # if 'Authorization' in event['params']['header']:
    #     atoken = event['params']['header']['Authorization']
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
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            print(event)
            
            Flag = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            if Flag == 1:
                mycursor.execute("SELECT userid from email where flag = 'True' ")
                all_emails = mycursor.fetchall()
                if atoken != '':
                    op = decode_jwt_token(atoken)
                    if op == '':
                        all_emails = {}
                        enable = False
                    for ch in all_emails:
                        if op == ch['userid'] :
                            enable = True
                            break
                        else :
                           enable = False 
                else:
                    enable = False
                    all_emails = {} 
            else:
                enable = False
                all_emails = {}
        
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure")   
        }  
        
    finally:
        mydb.close()
         
    
    return {
        'statusCode': 200,
        # 'body': {'Enable' : enable}
        'body': {'Enable' : enable , 'email' : op}
    }

def deleteAttachment(event, context):
    
    global dbScehma 
    
    client = boto3.client('secretsmanager')
    secret = event["stage-variables"]["secreat"]
    resp = client.get_secret_value(
        SecretId= secret
    )
    secretDict = json.loads(resp['SecretString'])

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with mydb.cursor() as mycursor:
            dbScehma = event["stage-variables"]["schema"]
            
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            attachment = event["params"]["querystring"]['attachment_id']
            email = event["params"]["querystring"]["userid"]
            
            mycursor.execute("select member_id, concat(fs_name, ' ', ls_name) as member_name from einvoice_db_portal.member where email = %s", email)
            member = mycursor.fetchone()
            
            values = (attachment,)
            mycursor.execute('SELECT * FROM einvoice_db_portal.file_storage where attach_id = %s', values)
            attachment_det = mycursor.fetchone()
            
            mycursor.execute("select in_status from einvoice_db_portal.invoice_header where invoice_no = %s", attachment_det["file_id"])
            invoice_header = mycursor.fetchone()
            
            mycursor.execute('DELETE FROM einvoice_db_portal.file_storage WHERE attach_id = %s', values)
            
            msg_cmnt = attachment_det["name"] + " attachment deleted by " + member["member_name"]
            temp = (attachment_det["file_id"], invoice_header["in_status"], invoice_header["in_status"], member['member_id'], msg_cmnt)
            sqlQuery = "insert into einvoice_db_portal.invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
            mycursor.execute(sqlQuery, temp)
            
            if attachment_det:
                
                s3 = boto3.client("s3")
                s3.delete_object(Bucket=attachment_det['file_path'], Key=attachment_det['name'])
                
                mydb.commit()
                
                return {
                    'statuscode': 200,
                    'body': json.dumps("Deleted Successfully!")
                }
                
            return {
                    'statuscode': 200,
                    'body': json.dumps("Attachment not Found")
                }
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
    
    finally:
        mydb.close()

def downloadAttachments(event, context):
    print(event)
    global dbScehma 
    dbScehma = event["stageVariables"]["schema"]
    
    client = boto3.client('secretsmanager')
            
    secret = event["stageVariables"]["secreat"]
    bucket = event["stageVariables"]["non_ocr_attachment"]
    stage = event["stageVariables"]["lambda_alias"]
            
    resp = client.get_secret_value(
        SecretId= secret
    )
        
    secretDict = json.loads(resp['SecretString'])
    
    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        print(event)
        content_type = ""  
    
        s3 = boto3.client("s3")
        
        file_name = event["queryStringParameters"]["file_name"]
        
        if('email' in event['queryStringParameters']):  #changed
            email = event['queryStringParameters']['email']
            if(email == 'abhishek.p@peolsolutions.com' or email == 'pramod.b@peolsolutions.com'):
                file_name = 'old-dev/heda-plywood.png'
            else:
                file_name = event["queryStringParameters"]["file_name"]
                # file_name = 'old-dev/Archidply-logo.png' #changed
        
        bucket_used = event["stageVariables"]["non_ocr_attachment"]
        print(file_name, bucket_used)
        
        if "userid" in event["queryStringParameters"]:
            userid = event["queryStringParameters"]["userid"]
            invoice_no = event["queryStringParameters"]["invoice_no"]
            
            with mydb.cursor() as mycursor:
                defSchemaQuery = "use " + dbScehma
                print("dnaksjhdksjdhaskd")
                mycursor.execute(defSchemaQuery)
                
                mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                on = mycursor.fetchone()
                if on['value1'] == 'on':
                    chk = enable_xray(event)
                    if chk['Enable'] == True:
                        patch_all() 
                        print(event)
                
                mycursor.execute("select concat(fs_name, ' ', ls_name) as member_name, member_id from member where email = %s", userid)
                member = mycursor.fetchone()
                
                msg_cmnt = file_name + " attachment downloaded by " + member["member_name"]
                temp = (invoice_no, "", "", member['member_id'], msg_cmnt)
                sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                mycursor.execute(sqlQuery, temp)
                
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
            conte = ''' attachment; filename=''' + file_name
            
        return {
              'headers': { "Content-Type": content_type, 'Content-Disposition' : conte,  'Access-Control-Allow-Origin': '*', 'filename': "jhghjd.pdf" }, 
              'statusCode': 200,
              'body': base64.b64encode(file_content),
              'isBase64Encoded': True
            }
        
    except Exception as e:
        return {
          'headers': { "Content-Type": content_type, 'Access-Control-Allow-Origin': '*' }, 
        #   'body' : json.dumps("No file Found"),
            'body' : json.dumps(str(e)),
            'statusCode': 500
        }
    
   #.........................................................................................................
# einvoice attachament

#event not found might get error for value length in table elipo setting
def einvoice_upload_company_logo(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    ocr_folder = "old-dev/"
    
    bucket = "einvoice-company-logo"
    secret = "test/einvoice/secret"
    stage = "dev"
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    s3 = boto3.client("s3",region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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')
    
    try:
        if "body" in event and event["body"]:
            
            post_data = base64.b64decode(event["body"])
            if "Content-Type" in event["headers"]:
                content_type = event["headers"]["Content-Type"]
                ct = "Content-Type: "+content_type+"\n"
                
            elif "content-type" in event["headers"]:
                content_type = event["headers"]["content-type"]
                ct = "content-type: "+content_type+"\n"
                
            if ct:
                msg = email.message_from_bytes(ct.encode()+post_data)
                
                if msg.is_multipart():
                    
                    multipart_content = {}
                    
                    for part in msg.get_payload():
                        multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
                    
                    file_name = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["file_name"])))
                    
                    filenamett, file_extension = os.path.splitext(file_name)
                    
                    s3_upload = s3.put_object(Bucket=bucket, Key=ocr_folder+file_name, Body=multipart_content["file"])
                    
                    var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + stage + "/attachment?file_name=" + ocr_folder+file_name + "&bucket=" + bucket 
                    
                    with mydb.cursor() as mycursor:
                        defSchemaQuery = "set schema " + dbScehma
                        mycursor.execute(defSchemaQuery)
                        
                        mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                        on = mycursor.fetchone()
                        if on['value1'] == 'on':
                            chk = enable_xray(event)
                            if chk['Enable'] == True:
                                patch_all() 
                                print(event)
                        
                        sqlQuery = "update elipo_setting set value1 = ? where key_name = 'company_logo'"
                        values = (var_path,)
                        mycursor.execute(sqlQuery, values)
                        
                        mydb.commit()

                else :

                    # multipart_content = {}
                    
                    # for part in msg.get_payload():
                    #     multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
                    
                    file_name = " ".join(re.findall("(?<=')[^']+(?=')", str(event["form"]['file_name'])))
                    
                    filenamett, file_extension = os.path.splitext(file_name)
                    
                    s3_upload = s3.put_object(Bucket=bucket, Key=ocr_folder+file_name, Body= event['body'] )
                    
                    var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + stage + "/attachment?file_name=" + ocr_folder+file_name + "&bucket=" + bucket 
                    
                    with mydb.cursor() as mycursor:
                        defSchemaQuery = "set schema " + dbScehma
                        mycursor.execute(defSchemaQuery)
                        
                        mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                        on = mycursor.fetchone()
                        if on['value1'] == 'on':
                            chk = enable_xray(event)
                            if chk['Enable'] == True:
                                patch_all() 
                                print(event)
                        
                        sqlQuery = "update elipo_setting set value1 = ? where key_name = 'company_logo'"
                        values = (var_path,)
                        mycursor.execute(sqlQuery, values)
                        
                        mydb.commit()


    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(e))
        }
        
    except Exception as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(e))
        }
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('File uploaded successfully!')
    }

#working fine i changed length of file name 
def supplier_ocr_attch_upload(event, context):

    print(event) 
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    ocr_folder = event["stageVariables"]["ocr_bucket_folder"]
    
    from_supplier = ""
       
    if event["queryStringParameters"] and "from_supplier" in event["queryStringParameters"]:
        from_supplier = event["queryStringParameters"]["from_supplier"]
    
    else:
        from_supplier = "yes"
      
    try:
        if "body" in event and event["body"]:
    
            # client = boto3.client('secretsmanager',
            # region_name='eu-central-1',
            # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
            # aws_secret_access_key='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')
            
            secret = event["stageVariables"]["secreat"]
            bucket = event["stageVariables"]["ocr_bucket"]
            stage = event["stageVariables"]["lambda_alias"]
            
            # resp = client.get_secret_value(
            #     SecretId= secret
            # )
        
            # secretDict = json.loads(resp['SecretString'])
        
            mydb = hdbcliConnect()
            
            s3 = boto3.client(
                "s3",
                region_name="eu-central-1",
                aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
                aws_secret_access_key="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",
            )
        
            # decoding form-data into bytes
            post_data = base64.b64decode(event['body'])
            
            if "Content-Type" in event["headers"]:
                content_type = event["headers"]["Content-Type"]
                ct = "Content-Type: "+content_type+"\n"
                        
            elif "content-type" in event["headers"]:
                content_type = event["headers"]["content-type"]
                ct = "content-type: "+content_type+"\n"
        
            msg = email.message_from_bytes(ct.encode()+post_data)
        
            print("Multipart check : ", msg.is_multipart())
            
            if msg.is_multipart():
                multipart_content = {}
                for part in msg.get_payload():
                    multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
        
                mime_type = str(multipart_content["mime_type"].decode("utf-8") )
                file_id = str(multipart_content["file_id"].decode("utf-8") )
                email_id = str(multipart_content["userid"].decode("utf-8") )
                vendor = str(multipart_content["vendor"].decode("utf-8") )
                
                with mydb.cursor() as mycursor:
                    defSchemaQuery = "set schema " + dbScehma
                    mycursor.execute(defSchemaQuery)
                    
                    mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                    on = mycursor.fetchone()
                    if on['value1'] == 'on':
                        chk = enable_xray(event)
                        if chk['Enable'] == True:
                            patch_all() 
                            print(event)

                    
                    values = (email_id,)
                    mycursor.execute("SELECT * FROM member where email = ?", values)
                    userinfo = mycursor.fetchone()
                    
                    # key_id = str(vendor) + "+" + str(userinfo['member_id'])
                    
                    if from_supplier == "yes":
                        key_id = str(vendor) + "+" + str(userinfo['member_id'])
                    else:
                        key_id = str(userinfo['member_id'])  
                    
                    curDateTime = datetime.now()
                    timestamp = str(datetime.timestamp(curDateTime))
                    unwanted = [' ', '-', '(', ')', ',']
                    
                    fileKey = timestamp + "___"
                    # + str(part["filename"])
                    temp = ""
                    
                    for c in str(file_id):
                        if c == '.':
                            temp += c
                        if c.isalnum():
                            temp += c
                    
                    temp = temp.lower()
                    
                    if from_supplier == "yes":
                        fileKey = ocr_folder + "S" + fileKey + temp   
                    else:
                        fileKey = ocr_folder + "I" + fileKey + temp 
                    
                    values = (email_id, key_id, vendor, 'y', fileKey )
                    mycursor.execute("INSERT INTO mail_message (user_id, message_id, recieved_from, is_processed, "
                                     "filename) VALUES {}".format(tuple(values)))
                    
                    #u uploading file to S3
                    s3_upload = s3.put_object(Bucket=bucket, Key=fileKey, Body=multipart_content["file"]) 
                    
                    print(bucket + "  :  " + fileKey)  
                    
                    # var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + stage + "/attachment?file_name=" + fileKey + "&bucket=" + bucket 
            
                    
                    # sqlQuery = "INSERT INTO file_storage (file_id, name, mime_type, file_path, file_link) VALUES (%s, %s, %s, %s, %s)"
                    # values = (file_id, fileKey, mime_type, bucket, var_path )
                    # mycursor.execute(sqlQuery, values)
                            
                        # mycursor.execute("select member_id, concat(fs_name, ' ', ls_name) as member_name from member where email = %s", email_id)
                        # member = mycursor.fetchone()
                            
                        # mycursor.execute("select in_status from invoice_header where invoice_no = %s", file_id)
                        # invoice_header = mycursor.fetchone()
                            
                        # msg_cmnt = file_name + " attachment uploaded by " + member["member_name"]
                        # temp = (file_id, invoice_header["in_status"], invoice_header["in_status"], member['member_id'], msg_cmnt)
                        # sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                        # mycursor.execute(sqlQuery, temp)
                        
                            
                    mydb.commit()
                            
                    body = {
                            'statuscode': 200,
                            # 'path': var_path,
                            'fileKey' : fileKey
                    }
                                    
                    # on upload success
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-type': 'application/json', 
                            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'OPTIONS,POST'
                        },
                        'body': json.dumps(body)
                    }
                    
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps('IntegrityError') 
        }
                
    except Exception as e:  
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-type': 'application/json', 
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps('Server Error')   
        }
        
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 205,  
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,X-Amz-Security-Token,Authorization,X-Api-Key,X-Requested-With,Accept,Access-Control-Allow-Methods,Access-Control-Allow-Origin,Access-Control-Allow-Headers',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'X-Requested-With': '*'
        },
        'body': json.dumps('Failed to upload!')   
    }   

#working fine
def einvoice_upload_attachment(event, context):     
    
    print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '
  
    try:
        if "body" in event and event["body"]:
    
    #         client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
            
            secret = "test/einvoice/secret"
            bucket = "einvoice-attachments"
            stage = "dev"
            
            # resp = client.get_secret_value(
            #     SecretId= secret
            # )
        
            # secretDict = json.loads(resp['SecretString'])
        
            mydb = hdbcliConnect()
            
            s3 = boto3.client(
                "s3",
                region_name="eu-central-1",
                aws_access_key_id="AKIAXUCMAX6S27NZCRFL",
                aws_secret_access_key="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",
            )
        
            # decoding form-data into bytes
            post_data = base64.b64decode(event['body'])
            # post_data = event['body']

            
            if "Content-Type" in event["headers"]:
                content_type = event["headers"]["Content-Type"]
                ct = "content-Type: "+content_type+"\n"
                        
            elif "content-type" in event["headers"]:
                content_type = event["headers"]["content-type"]
                ct = "content-type: "+content_type+"\n"
        
            msg = email.message_from_bytes(ct.encode()+post_data)
        
            # checking if the message is multipart
            print("Multipart check : ", msg.is_multipart())
            
            if msg.is_multipart():
                
                multipart_content = {}
                for part in msg.get_payload():
                    multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
        
                # filename from form-data
                file_name = str(multipart_content["file_name"].decode("utf-8") )  
                mime_type = str(multipart_content["mime_type"].decode("utf-8") )
                file_id = str(multipart_content["file_id"].decode("utf-8") )
                email_id = str(multipart_content["userid"].decode("utf-8") )
                
                #u uploading file to S3
                s3_upload = s3.put_object(Bucket=bucket, Key=file_name, Body=multipart_content["file"]) 
                
                var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + stage + "/attachment?file_name=" + file_name + "&bucket=" + bucket 
        
                with mydb.cursor() as mycursor:
                    defSchemaQuery = "set schema  " + dbScehma
                    mycursor.execute(defSchemaQuery)
                    
                    mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                    on = mycursor.fetchone()
                    if on['value1'] == 'on':
                        chk = enable_xray(event)
                        if chk['Enable'] == True:
                            patch_all() 
                            print(event)

                    sqlQuery = "INSERT INTO file_storage (file_id, name, mime_type, file_path, file_link) VALUES {}"
                    values = (file_id, file_name, mime_type, bucket, var_path )
                    mycursor.execute(sqlQuery.format(tuple(values)))
                        
                    mycursor.execute("select member_id, (fs_name||' '|| ls_name) as member_name from member where email = ?", email_id)
                    member = mycursor.fetchone()
                        
                    mycursor.execute("select in_status from invoice_header where invoice_no = ?", file_id)
                    invoice_header = mycursor.fetchone()
                        
                    msg_cmnt = file_name + " attachment uploaded by " + member["member_name"]
                    temp = (file_id, invoice_header["in_status"], invoice_header["in_status"], member['member_id'], msg_cmnt)
                    sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values {}"
                    mycursor.execute(sqlQuery.format(tuple(temp)))
                        
                    mydb.commit()
                        
                    body = {
                            'statuscode': 200,
                            'path': var_path
                    }
                                
                    # on upload success
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-type': 'application/json', 
                            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'OPTIONS,POST'
                        },
                        'body': json.dumps('File uploaded successfully!')
                    }
                
            else :

                file_name = str(event['form']['file_name'] )  
                mime_type = str(event['form']['mime_type'] )
                file_id = str(event['form']['file_id'] )
                email_id = str(event['form']['userid'] )

                s3_upload = s3.put_object(Bucket=bucket, Key=file_name, Body=event['body']) 

                var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + stage + "/attachment?file_name=" + file_name + "&bucket=" + bucket
                
                with mydb.cursor() as mycursor:
                    defSchemaQuery = "set schema  " + dbScehma
                    mycursor.execute(defSchemaQuery)
                    
                    mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                    on = mycursor.fetchone()
                    if on['value1'] == 'on':
                        chk = enable_xray(event)
                        if chk['Enable'] == True:
                            patch_all() 
                            print(event)

                    sqlQuery = "INSERT INTO file_storage (file_id, name, mime_type, file_path, file_link) VALUES {}"
                    values = (file_id, file_name, mime_type, bucket, var_path )
                    mycursor.execute(sqlQuery.format(tuple(values)))
                        
                    mycursor.execute("select member_id, (fs_name||' '|| ls_name) as member_name from member where email = ?", email_id)
                    member = mycursor.fetchone()
                        
                    mycursor.execute("select in_status from invoice_header where invoice_no = ?", file_id)
                    invoice_header = mycursor.fetchone()
                        
                    msg_cmnt = file_name + " attachment uploaded by " + member["member_name"]
                    temp = (file_id, invoice_header["in_status"], invoice_header["in_status"], member['member_id'], msg_cmnt)
                    sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values {}"
                    mycursor.execute(sqlQuery.format(tuple(temp)))
                        
                    mydb.commit()
                        
                    body = {
                            'statuscode': 200,
                            'path': var_path
                    }
                                
                    # on upload success
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-type': 'application/json', 
                            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'OPTIONS,POST'
                        },
                        'body': json.dumps('File uploaded successfully!')
                    }
                

    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps('IntegrityError') 
        }
                
    except Exception as e:  
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-type': 'application/json', 
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps('Server Error')   
        }
        
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 205,  
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,X-Amz-Security-Token,Authorization,X-Api-Key,X-Requested-With,Accept,Access-Control-Allow-Methods,Access-Control-Allow-Origin,Access-Control-Allow-Headers',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'X-Requested-With': '*'
        },
        'body': json.dumps('Failed to upload!')   
    }   


# event = {'resource': '/upload', 'path': '/upload', 'httpMethod': 'POST', 'headers': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryN6r6noiC7i8dquhG', 'Host': '0uawz56ial.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6530c159-01b247a654ff1ee9769933b5', 'X-Forwarded-For': '49.206.135.95', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'accept': ['application/json, text/plain, */*'], 'accept-encoding': ['gzip, deflate, br'], 'accept-language': ['en-US,en;q=0.9'], 'content-type': ['multipart/form-data; boundary=----WebKitFormBoundaryN6r6noiC7i8dquhG'], 'Host': ['0uawz56ial.execute-api.eu-central-1.amazonaws.com'], 'origin': ['https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com'], 'referer': ['https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/'], 'sec-ch-ua': ['"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"'], 'sec-ch-ua-mobile': ['?0'], 'sec-ch-ua-platform': ['"Windows"'], 'sec-fetch-dest': ['empty'], 'sec-fetch-mode': ['cors'], 'sec-fetch-site': ['same-site'], 'User-Agent': ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'], 'X-Amzn-Trace-Id': ['Root=1-6530c159-01b247a654ff1ee9769933b5'], 'X-Forwarded-For': ['49.206.135.95'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': {'schema': 'einvoice_db_portal', 'non_ocr_attachment': 'einvoice-attachments', 'lambda_alias': 'dev', 'company_logo': 'einvoice-company-logo', 'ocr_bucket': 'textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db', 'ocr_bucket_folder': 'old-dev/', 'enquiry_bucket': 'einvoice-dev-enquiry', 'secreat': 'test/einvoice/secret'}, 'requestContext': {'resourceId': '8b3ovx', 'resourcePath': '/upload', 'httpMethod': 'POST', 'extendedRequestId': 'NCMmIEicFiAFaZw=', 'requestTime': '19/Oct/2023:05:40:42 +0000', 'path': '/einvoice-dev/upload', 'accountId': '524145442725', 'protocol': 'HTTP/1.1', 'stage': 'einvoice-dev', 'domainPrefix': '0uawz56ial', 'requestTimeEpoch': 1697694042189, 'requestId': 'bc6cdde6-6f35-4e2b-b2c1-dadc46644c3e', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '49.206.135.95', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36', 'user': None}, 'domainName': '0uawz56ial.execute-api.eu-central-1.amazonaws.com', 'apiId': '0uawz56ial'}, 'body': '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ZG9iZS5jb20vcGRmLzEuMy8iCiAgICAgICAgICAgIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIKICAgICAgICAgICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIgogICAgICAgICAgICB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyI+CiAgICAgICAgIDxwZGY6UHJvZHVjZXI+TWljcm9zb2Z0wq4gRXhjZWzCriBmb3IgTWljcm9zb2Z0IDM2NTwvcGRmOlByb2R1Y2VyPgogICAgICAgICA8ZGM6Zm9ybWF0PmFwcGxpY2F0aW9uL3BkZjwvZGM6Zm9ybWF0PgogICAgICAgICA8ZGM6Y3JlYXRvcj4KICAgICAgICAgICAgPHJkZjpTZXE+CiAgICAgICAgICAgICAgIDxyZGY6bGk+VXNlcjE8L3JkZjpsaT4KICAgICAgICAgICAgPC9yZGY6U2VxPgogICAgICAgICA8L2RjOmNyZWF0b3I+CiAgICAgICAgIDx4bXA6Q3JlYXRvclRvb2w+TWljcm9zb2Z0wq4gRXhjZWzCriBmb3IgTWljcm9zb2Z0IDM2NTwveG1wOkNyZWF0b3JUb29sPgogICAgICAgICA8eG1wOkNyZWF0ZURhdGU+MjAyMC0xMS0yMlQxNjoxMDoxNiswNDowMDwveG1wOkNyZWF0ZURhdGU+CiAgICAgICAgIDx4bXA6TW9kaWZ5RGF0ZT4yMDIwLTExLTIyVDE2OjEwOjQzKzA0OjAwPC94bXA6TW9kaWZ5RGF0ZT4KICAgICAgICAgPHhtcDpNZXRhZGF0YURhdGU+MjAyMC0xMS0yMlQxNjoxMDo0MyswNDowMDwveG1wOk1ldGFkYXRhRGF0ZT4KICAgICAgICAgPHhtcE1NOkRvY3VtZW50SUQ+dXVpZDpGNjI2OEQwQi0xMUUwLTQ4MUEtOTA2Mi0zNTEyMzczQkFDQzI8L3htcE1NOkRvY3VtZW50SUQ+CiAgICAgICAgIDx4bXBNTTpJbnN0YW5jZUlEPnV1aWQ6NDI5NmExOGUtOTI3YS00M2M5LWFhNDEtMjRhNTI0N2IyYjJhPC94bXBNTTpJbnN0YW5jZUlEPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSJ3Ij8+DQplbmRzdHJlYW0NZW5kb2JqDTUgMCBvYmoNPDwvRmlsdGVyL0ZsYXRlRGVjb2RlL0ZpcnN0IDYvTGVuZ3RoIDUyL04gMS9UeXBlL09ialN0bT4+c3RyZWFtDQpo3jIyMlcwULCx0XfOL80rUTDU985MKY42MjYEigbF6odUFqTqBySmpxbb2QEEGAD6WwxDDQplbmRzdHJlYW0NZW5kb2JqDTYgMCBvYmoNPDwvRmlsdGVyL0ZsYXRlRGVjb2RlL0ZpcnN0IDYvTGVuZ3RoIDEyNC9OIDEvVHlwZS9PYmpTdG0+PnN0cmVhbQ0KaN4yMrJQMFCwsdF3LC3JyC/SCC1OLTLU1HcuSk0syczPc0ksSdVwsTIyMDIwNDQyMjQzNDA00zYwUTcwUIeqAmryzUwuyi/OTytZp+BakZyas04hLb9IAS6qYGxmqqnvm5+CxTQTY7hpAUX5KaXJqcQZZ2cHEGAAWJI5TQ0KZW5kc3RyZWFtDWVuZG9iag03IDAgb2JqDTw8L0RlY29kZVBhcm1zPDwvQ29sdW1ucyA1L1ByZWRpY3RvciAxMj4+L0ZpbHRlci9GbGF0ZURlY29kZS9JRFs8MEI4RDI2RjZFMDExMUE0ODkwNjIzNTEyMzczQkFDQzI+PEVFNkEzNDExQkI4N0Y5NDY5QzMyOERFRkNBMUYxMUQ5Pl0vSW5mbyAyMjggMCBSL0xlbmd0aCA3My9Sb290IDIzMCAwIFIvU2l6ZSAyMjkvVHlwZS9YUmVmL1dbMSAzIDFdPj5zdHJlYW0NCmjeYmIAASZGpsU7GJgYGNgEQCTLZxDJFA0ieX1AJMMEEMl4E6jyn7MZWISBcZQcJalJMs4dDYdRcjikK6Z3YHsZAAIMAJ1iCtMNCmVuZHN0cmVhbQ1lbmRvYmoNc3RhcnR4cmVmDQoxMTYNCiUlRU9GDQoNCi0tLS0tLVdlYktpdEZvcm1Cb3VuZGFyeU42cjZub2lDN2k4ZHF1aEcNCkNvbnRlbnQtRGlzcG9zaXRpb246IGZvcm0tZGF0YTsgbmFtZT0iZmlsZV9uYW1lIg0KDQpzaW52b2ljZS5wZGYNCi0tLS0tLVdlYktpdEZvcm1Cb3VuZGFyeU42cjZub2lDN2k4ZHF1aEcNCkNvbnRlbnQtRGlzcG9zaXRpb246IGZvcm0tZGF0YTsgbmFtZT0iZmlsZV9pZCINCg0KOTI4Ng0KLS0tLS0tV2ViS2l0Rm9ybUJvdW5kYXJ5TjZyNm5vaUM3aThkcXVoRw0KQ29udGVudC1EaXNwb3NpdGlvbjogZm9ybS1kYXRhOyBuYW1lPSJtaW1lX3R5cGUiDQoNCmFwcGxpY2F0aW9uL3BkZg0KLS0tLS0tV2ViS2l0Rm9ybUJvdW5kYXJ5TjZyNm5vaUM3aThkcXVoRw0KQ29udGVudC1EaXNwb3NpdGlvbjogZm9ybS1kYXRhOyBuYW1lPSJ1c2VyaWQiDQoNCmVpbnZvaWNlcG9ydGFsQGdtYWlsLmNvbQ0KLS0tLS0tV2ViS2l0Rm9ybUJvdW5kYXJ5TjZyNm5vaUM3aThkcXVoRy0tDQo=', 'isBase64Encoded': True}
# print(einvoice_upload_attachment(event , ''))

#event not found
def deleteEnquiryAttachment(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client('secretsmanager',
    #                        region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' 
    #                       )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            attachment = event["params"]["querystring"]['attachment_id']
            
            values = (attachment,)
            mycursor.execute('SELECT * FROM enquiry_attachement where attach_id = ?', values)
            attachment_det = mycursor.fetchone()
            
            mycursor.execute('DELETE FROM enquiry_attachement WHERE attach_id = ?', values)
            
            if attachment_det:
                
                s3 = boto3.client("s3")
                s3.delete_object(Bucket=attachment_det['file_path'], Key=attachment_det['name'])
                
                mydb.commit()
                
                return {
                    'statuscode': 200,
                    'body': json.dumps("Deleted Successfully!")
                }
                
            return {
                    'statuscode': 200,
                    'body': json.dumps("Attachment not Found")
                }
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
    
    finally:
        mydb.close()

#event not found
def einvoice_upload_enquiry_attachment(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
      
    try:
        if "body" in event and event["body"]:
            
            secret = event["stageVariables"]["secreat"]
            bucket = event["stageVariables"]["enquiry_bucket"]
            stage = event["stageVariables"]["lambda_alias"]
            
    #         client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    #         resp = client.get_secret_value(
    #             SecretId= secret
    #         )
    #         secretDict = json.loads(resp['SecretString'])
        
            mydb = hdbcliConnect()
            
            s3 = boto3.client("s3")
        
            # decoding form-data into bytes
            post_data = base64.b64decode(event['body'])
            
            if "Content-Type" in event["headers"]:
                content_type = event["headers"]["Content-Type"]
                ct = "Content-Type: "+content_type+"\n"
                        
            elif "content-type" in event["headers"]:
                content_type = event["headers"]["content-type"]
                ct = "content-type: "+content_type+"\n"
        
            # parsing message from bytes
            msg = email.message_from_bytes(ct.encode()+post_data)
        
            # checking if the message is multipart
            print("Multipart check : ", msg.is_multipart())
            
            # if message is multipart
            if msg.is_multipart():
                multipart_content = {}
                
                # retrieving form-data
                for part in msg.get_payload():
                    multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
        
                # filename from form-data
                file_name = str(multipart_content["file_name"].decode("utf-8") )  
                mime_type = str(multipart_content["mime_type"].decode("utf-8") )
                enquiry_no = str(multipart_content["enquiry_no"].decode("utf-8") )
                
                #u uploading file to S3
                s3_upload = s3.put_object(Bucket=bucket, Key=file_name, Body=multipart_content["file"]) 
                
                var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + stage + "/attachment?file_name=" + file_name + "&bucket=" + bucket 
        
                with mydb.cursor() as mycursor:
                    defSchemaQuery = "set schema " + dbScehma
                    mycursor.execute(defSchemaQuery)
                    
                    mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                    on = mycursor.fetchone()
                    if on['value1'] == 'on':
                        chk = enable_xray(event)
                        if chk['Enable'] == True:
                            patch_all() 
                            print(event)
                    
                    sqlQuery = "INSERT INTO enquiry_attachement (enquiry_no, name, mime_type, file_path, file_link) VALUES {}"
                    values = (enquiry_no, file_name, mime_type, bucket, var_path )
                    mycursor.execute(sqlQuery.format(tuple(values)))
                    mycursor.execute("select count(*) from enquiry_attachment")
                    attachment_id = mycursor.fetchone()
                    mydb.commit()
                    
                    record = {
                        'statuscode': 200,
                        'msg': "File uploaded successfully!",
                        'file_link': var_path,
                        'attachment_id': attachment_id
                    }
                    
                    # on upload success
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-type': 'application/json', 
                            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Methods': 'OPTIONS,POST'
                        },
                            'body': json.dumps(record)
                    }
                
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps('IntegrityError')
            # 'body': { 'statuscode' : 500, 'msg': 'IntegrityError'}   
        }
                
    except Exception as e:  
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-type': 'application/json', 
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps('Server Error')   
        }
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 205,  
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,X-Amz-Security-Token,Authorization,X-Api-Key,X-Requested-With,Accept,Access-Control-Allow-Methods,Access-Control-Allow-Origin,Access-Control-Allow-Headers',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST',
            'X-Requested-With': '*'
        },
        'body': json.dumps('Failed to upload!')   
    }        

#event not found 
def einvoice_upload_profile_photo(event, context):
    global dbScehma 
    
    dbScehma = ' DBADMIN '
    secret = event["stageVariables"]["secreat"]
    bucket = event["stageVariables"]["non_ocr_attachment"]
    stage = event["stageVariables"]["lambda_alias"] 
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    s3 = boto3.client("s3")
    
    try:
        if "body" in event and event["body"]:
            
            post_data = base64.b64decode(event["body"])
            if "Content-Type" in event["headers"]:
                content_type = event["headers"]["Content-Type"]
                ct = "Content-Type: "+content_type+"\n"
                
            elif "content-type" in event["headers"]:
                content_type = event["headers"]["content-type"]
                ct = "content-type: "+content_type+"\n"
                
            if ct:
                
                msg = email.message_from_bytes(ct.encode()+post_data)
                
                if msg.is_multipart():
                    
                    multipart_content = {}
                    
                    for part in msg.get_payload():
                        
                        multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
                    
                    member_id = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["member_id"])))
                    file_name = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["file_name"])))
                    
                    filenamett, file_extension = os.path.splitext(file_name) 
                    up_file_name = str(member_id) + file_name
                    
                    file_name = "profile_photo/" + up_file_name
                    s3_upload = s3.put_object(Bucket=bucket, Key=file_name, Body=multipart_content["file"])
                    
                    var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + stage + "/attachment?file_name=profile_photo/" + up_file_name + "&bucket=" + bucket 
                    
                    with mydb.cursor() as mycursor:
                        defSchemaQuery = "set schema " + dbScehma
                        mycursor.execute(defSchemaQuery)
                    
                        mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                        on = mycursor.fetchone()
                        if on['value1'] == 'on':
                            chk = enable_xray(event)
                            if chk['Enable'] == True:
                                patch_all() 
                                print(event)
                        
                        sqlQuery = "update member set profile_photo = ? where member_id = ?"
                        values = (var_path, member_id)
                        mycursor.execute(sqlQuery, values)
                        
                        mydb.commit()
        
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(e))
        }
        
    except Exception as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(e))
        }
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('File uploaded successfully!')
    }    

#einvoice masters

#event not found
def setDefaultDepartment(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    output1 = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if "sr_no" in event["params"]["querystring"] and "member_id" in event["params"]["querystring"]:
                sqlQuery = "update department_master set default_master_check = ? where member_id = ?"
                values = ('n', event["params"]["querystring"]["member_id"])
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = "update department_master set default_master_check = ? where sr_no = ?"
                values = ('y', event["params"]["querystring"]["sr_no"])
                mycursor.execute(sqlQuery, values)
                
                mycursor.execute("select department_id from department_master where sr_no = ?", event["params"]["querystring"]["sr_no"])
                depID = mycursor.fetchone()
                
                sqlQuery = "update member set department_id = ? where member_id = ?"
                values = (depID["department_id"], event["params"]["querystring"]["member_id"])
                mycursor.execute(sqlQuery, values)
            
            mydb.commit()
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Default Department not set")
        }
        
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Default Department set")
    }
    


# master table is not yet created test after master table created
def getDefaultMasters(event, context):
    country = ''
    print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    records = []

    try:
        # print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    patch_all()
                    print(event)	
            
            mycursor.execute("select value1, value2, value3 from dropdown where drop_key = 'default-master-detail' ")
            raw_data = mycursor.fetchall()
            raw_data = convertValuesTodict(mycursor.description, raw_data)


            for row in raw_data:
                master_value = None
                master_value2 = None
                
                if row["value1"] == 'tds_per':
                    mycursor.execute("select value2, value3 from dropdown where drop_key = 'vendor_tds' and value1 = ? ", row["value2"])
                    data = mycursor.fetchone()
                    if data:
                        data = convertValuesTodict(mycursor.description, data)
                        data = data[0]
                        master_value = data["value2"]
                        master_value2 = data["value3"]

                elif row["value1"] == 'country':   #changed
                    mycursor.execute("SELECT value1 FROM elipo_setting where key_name = 'country';")
                    data = mycursor.fetchone()
                    data = convertValuesTodict(mycursor.description, data)
                    data = data[0]
                    if data:
                        row["value2"] = data["value1"]
                        country = data["value1"]


                elif row["value1"] == 'plant':
                    mycursor.execute("select description FROM master where master_id = '7' and code = ? ", row["value2"])
                    data = mycursor.fetchone()
                    data = convertValuesTodict(mycursor.description, data)
                    data = data[0]
                    if data:
                        master_value = data["description"]
                
                else:
                    master_value = row["value2"]
                    
                if row["value1"] == 'plant':
                    record = {
                        "master_name": row["value1"],
                        "master_value": row["value2"],
                        "value": master_value,
                        "value2": ""
                    }
                    records.append(record)
                
                elif row["value1"] == 'tds_per':
                    record = {
                        "master_name": row["value1"],
                        "master_value": row["value2"],
                        "value": master_value,
                        "value2": master_value2
                    }
                    records.append(record)
                    
                elif row["value1"] == 'document_type':
                    record = {
                        "master_name": row["value1"],
                        "master_value": row["value2"],
                        "value": master_value,
                        "value2": row["value3"]
                    }
                    records.append(record)
                
                else:
                    record = {
                        "master_name": row["value1"],
                        "master_value": master_value,
                        "value": row["value2"],
                        "value2": ""
                    }
                    records.append(record)

            mycursor.execute("SELECT company_code FROM default_master where country = ?" , country) #changed
            final = mycursor.fetchone()
            final = convertValuesTodict(mycursor.description, final)
            final = final[0]
            records[0]['value'] = final['company_code']
            records[0]['master_value'] = final['company_code']
            
            if(records[2]['value']  != ''): #changed
                con = records[2]['value']
                mycursor.execute("SELECT currency FROM default_master where country  = ?" , con)
                final = mycursor.fetchone()
                final = convertValuesTodict(mycursor.description, final)
                final = final[0]
                records[3]['value'] = final['currency']
                records[3]['master_value'] = final['currency']



    # except:
    #     return {
    #         'statuscode': 500,
    #         'body': json.dumps("Internal Failure")
    #     }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImEzOWJjMGNjLTNiYmEtNDQyZi04OTBmLTIwZTRjYzczYTRlOCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjUyMTU5NTkxLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjUyMTYzMTkxLCJpYXQiOjE2NTIxNTk1OTEsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.Jxc3eGyA1sRXod5EZYhBcC3lh9YIfoIj8VN9bmjBZntYo4hb9ge41S0ZxJxNfk3e4gaqRzZweHIRcJQ2jSDi9UKZ3D0pfXCiWmbI_mtLZo8xQ9dCjUlOxxPH_7v46-PeXCrwbaApvhxnpG4GHamkJW0p7y3j6FUJ39LmifgkPDROqZDT9IDeS0PpIL9SZfbudYkMPxYRFQxWI3X8vIOikJeHTyXXazk3XjNf7ZcNEyiBW3QBk35aXntECwRiGuQlM1jVwBFEzT2SRYYdKxyG0sVNmaoqVpO94UTkx9MJlQN8AV0ybbdsEshXOv7QwjcX_m6qETsbJbyhcp0r0HD6Xw', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'origin': 'http://localhost:4200', 'referer': 'http://localhost:4200/', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6279f561-3246d82f1e3cd1cf4387775c', 'X-Forwarded-For': '49.207.207.48', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'GET', 'stage': 'master-v1', 'source-ip': '49.207.207.48', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36', 'user-arn': '', 'request-id': '920984c6-8280-404c-8f0f-bd07b116f75b', 'resource-id': 'drd1md', 'resource-path': '/default-master'}}

# print(lambda_handler(event , ''))

#working fine for event passed
def deleteDefaultMaster(event, context):
    # print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
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
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if event["params"]["querystring"]["company_code"]:
                sqlQuery = "Delete from default_master where company_code = ?"
                values = (event["params"]["querystring"]["company_code"])
                mycursor.execute(sqlQuery,values)
            
        
                
        mydb.commit()
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Delete Unsuccessful!")  
        }  
           
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Delete Successful!")
    }
# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'company_code': '3002'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjAxNzE3OWM2LTNkYzAtNDYzZS05N2ZiLWVmZDViYjg1Yzc4MCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjUwODk0NTU4LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjUwODk4MTU3LCJpYXQiOjE2NTA4OTQ1NTgsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.JpPJXHcq5gHrvXX2LqdEvhnZZjjVyp-IL2HorQPmhudLZHRBZE65c3y4_kSnaoPmqy1o-RbPupwgrodhXoF15OiPbudgaC12DS3PrhHJJSr1OpWPCKXqo3k869y1Je_2G0zId4x0cBbWjpJY1gWYG3fLJ0egMVRyCWKVK73Q0N4_VpwBAaBvZKZJ2bcE9E8IJz49taDeYTSGMlILb11yx-7oLyh_JNKQUCNsaCpj5za6TQIjwp5NXDs2ISS7c60Zu1ZiAEH7gbzwz-oUw92cu0xjdnAk_Vr4KW3tRWcfjqT4Wi0R-GufnmQ7LDq4T4xr9Io-QC-zbgnfr7W9zgM0uQ', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6266a76c-6cadd8fb6dac9cd226c23f45', 'X-Forwarded-For': '27.7.152.165', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'DELETE', 'stage': 'master-v1', 'source-ip': '27.7.152.165', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36', 'user-arn': '', 'request-id': '2a9138a4-b714-49b4-a2b7-a24f8610163b', 'resource-id': 'j3j4c0', 'resource-path': '/default_master1'}}
# print(deleteDefaultMaster(event, ' '))
#tested 
def getAllDefaultMaster(event, context):
    print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    records = []

    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)                   
                    if chk['Enable'] == True:
                        patch_all()
                        print(event)
            
            mycursor.execute("SELECT * FROM default_master where country = (SELECT value1 FROM elipo_setting  where key_name = 'country')" )
            raw_data = mycursor.fetchall()
            raw_data = convertValuesTodict(mycursor.description, raw_data)
            default_master = []
            for raw in raw_data:
                record = {
                    "company_code" : raw["company_code"],
                    
                    "country" : raw["country"],
                    "payment_method" : raw["payment_method"],
                    "currency" : raw["currency"],
                    "gl_account_header": raw["gl_account_header"],
                    "supplier_id" : raw["supplier_id"],
                    "tax_per" : raw["tax_per"],
                    "tds_per" : raw["tds_per"],
                    "plant" : raw["plant"],
                    "document_type" : raw["document_type"]
                    
                }
                records.append(record)




            # for row in values:

            
                
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

#event not found
def patchDefaultMasterDetail(event, context): 
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client('secretsmanager',
    #                        region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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'
    #                       )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    record = {
        "company_code": None,
        "country": None,
        "payment_terms": None,
        "payment_method": None,
        "currency": None,
        "gl_account_header": None,
        "cost_center": None,
        "tax_per": None,
        "tds_per": None,
        "gl_account_item": None,
        "plant": None,
        "supplier_id" : None,
        "date_range": None,
        "document_type": None
    }

    try:
        # print(event)
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            
            if "company_code" in event["params"]["querystring"]:
                defSchemaQuery = "set schema " + dbScehma
                mycursor.execute(defSchemaQuery)
                
                mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                on = mycursor.fetchone()
                if on['value1'] == 'on':
                    chk = enable_xray(event)
                    if chk['Enable'] == True:
                        patch_all() 
                        print(event)
                        
                company_code = event["params"]["querystring"]["company_code"]
                
                sqlQuery = "update default_master set country = ?, payment_terms = ?, payment_method = ?, currency = ?, gl_account_header = ?, " \
                    "cost_center = ?, tax_per = ?, tds_per = ?, gl_account_item = ?, plant = ?, supplier_id = ?, date_range = ? , document_type = ? where company_code = ?"
                    
                values = (record["country"],record["payment_terms"],record["payment_method"], \
                    record["currency"],record["gl_account_header"],record["cost_center"],record["tax_per"],record["tds_per"], \
                    record["gl_account_item"],record["plant"],record["supplier_id"],record["date_range"],record["document_type"],company_code)               
                mycursor.execute(sqlQuery, values)
                
                mydb.commit()  
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Updated Unuccessfully!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Updated Successfully!")
    }

#event not found
def deleteDepartmentMaster(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)

            
            if "querystring" in event["params"]:
                if "sr_no" in event["params"]["querystring"]:
                    if len(event["params"]["querystring"]["sr_no"].split(',')) == 1:
                        mycursor.execute("select * from department_master WHERE sr_no = ? ",event["params"]["querystring"]["sr_no"])
                        data = mycursor.fetchone()
                        
                        mycursor.execute("DELETE FROM department_master WHERE sr_no = ? ",event["params"]["querystring"]["sr_no"])
                        
                        values = ( None, data["member_id"] )
                        mycursor.execute("UPDATE member SET department_id = ? WHERE member_id = ?", values)
                        
                    else:
                        values = event["params"]["querystring"]["sr_no"].split(',')
                        mycursor.execute("delete from department_master where sr_no in {}".format(tuple(values)))
            
        mydb.commit()
    
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Unable to delete")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Data deleted!")
    }

#not tested event not found
def getDepartmentMaster(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '


    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable'] == 'True':
                        patch_all()
                        print(event)

            
            if "userid" in event["params"]["querystring"]:
                mycursor.execute("select member_id, (fs_name||' '||ls_name) as mem_name from member where email = ?", event["params"]["querystring"]["userid"])
                member = mycursor.fetchone()
                # member = convertValuesTodict(mycursor.description, member)
                # member = member[0]
                
                if member:
                    mycursor.execute("select * from department_master where member_id = ? order by member_id", member["member_id"])
                    data = mycursor.fetchall()
                    data = convertValuesTodict(mycursor.description, data)
                    
                    for row in data:
                        record = {
                            "sr_no": row["sr_no"],
                            "department_id": row["department_id"],
                            "department_name": row["department_name"],
                            "cost_center": row["cost_center"],
                            "gl_account": row["gl_account"],
                            "member_id": row["member_id"],
                            "internal_order": row["internal_order"],
                            "member_name": member["mem_name"],
                            "default_master_check": row["default_master_check"]
                        }
                        records.append(record)
            
            elif "userid_dep" in event["params"]["querystring"]:
                mycursor.execute("select member_id from member where email = ?", event["params"]["querystring"]["userid_dep"])
                member = mycursor.fetchone()
                # member = convertValuesTodict(mycursor.description, member)
                # member = member[0]
                
                if member:
                    mycursor.execute("select * from department_master where member_id = ?", member["member_id"])
                    data = mycursor.fetchall()
                    data = convertValuesTodict(mycursor.description, data)
                    
                    values = []
                    for row in data:
                        record = {
                            "department_id": row["department_id"],
                            "department_name": row["department_name"],
                            "default_master_check": row["default_master_check"]
                        }
                        values.append(record)
                    
                    records = [i for n, i in enumerate(values) if i not in values[n + 1:]]
                
            else:
                mycursor.execute("select a.*, (b.fs_name||' '||b.ls_name) as mem_name, b.email " \
                	"from department_master a " \
                    "left join member b " \
                    "on a.member_id = b.member_id " \
                    "order by mem_name, department_id")
                temp = convertValuesTodict(mycursor.description,mycursor.fetchall())
                    
                for row in temp:
                    record = {
                        "sr_no": row["sr_no"],
                        "department_id": row["department_id"],
                        "department_name": row["department_name"],
                        "cost_center": row["cost_center"],
                        "gl_account": row["gl_account"],
                        "member_id": row["member_id"],
                        "internal_order": row["internal_order"],
                        "member_name": row["mem_name"],
                        "email": row["email"],
                        "default_master_check": row["default_master_check"]
                    }
                    records.append(record)
    
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Internal failure!")
        }
        
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

#event not found
def patchDepartmentMaster(event, context): 
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    record = {
        "department_id": "",
        "department_name": "", 
        "cost_center": "", 
        "gl_account": "", 
        "member_id": "", 
        "internal_order": ""
    }

    try:
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            
            if "sr_no" in event["params"]["querystring"]:
                defSchemaQuery = "set schema " + dbScehma
                mycursor.execute(defSchemaQuery)
                
                mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                on = mycursor.fetchone()
                if on['value1'] == 'on':
                    chk = enable_xray(event)
                    if chk['Enable'] == True:
                        patch_all() 
                        print(event)             

                    
                    
                sr_no = event["params"]["querystring"]["sr_no"]
                
                sqlQuery = "update department_master set department_id = ?, department_name = ?, cost_center = ?, " \
                    "gl_account = ?, member_id = ?, internal_order = ? where sr_no = ?"
                    
                values = ( record["department_id"], record["department_name"], record["cost_center"], record["gl_account"], record["member_id"], record['internal_order'], sr_no )
                mycursor.execute(sqlQuery, values)
                
                mydb.commit()  
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Updated Unuccessfully!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Updated Successfully!")
    }

#event not found
def postDepartmentMaster(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    list_item = []
    
    try:
        # print(event)
        for row in event["body-json"]:
            record = {
                "department_id": "",
                "department_name": "", 
                "cost_center": "", 
                "gl_account": "", 
                "member_id": "", 
                "email": "",
                "internal_order": ""
            }
            
            for value in row:
                if value in record:
                    record[value] = row[value]
                    
            list_item.append(record)
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema  " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
                
            if "sr_no" not in event["params"]["querystring"]:
                values = []
                
                if "import_entries" in event["params"]["querystring"]:
                    mycursor.execute("DELETE FROM department_master")
                    
                    emails = []
                    dep_name = []
                    
                    for row in list_item:
                        emails.append(row["email"])
                        dep_name.append(row["department_name"])
                        
                    emails = set(emails)
                    emails = list(emails)
                    
                    dep_name = set(dep_name)
                    dep_name = list(dep_name)
                    
                    format_strings_email = ','.join(['?'] * len(emails))
                    format_strings_depName = ','.join(['?'] * len(dep_name))
                    
                    sqlQuery = "select member_id, email from member where email in ({})".format(format_strings_email)
                    mycursor.execute(sqlQuery, tuple(emails))
                    memberEmail = mycursor.fetchall()
                    
                    sqlQuery = "select department_id, department_name from departmental_budget_master where department_name in ({})".format(format_strings_depName)
                    mycursor.execute(sqlQuery, tuple(dep_name))
                    depName = mycursor.fetchall()
                    
                    for row in list_item:
                        memberID = None
                        departmentID = None
                        
                        for mem in memberEmail:
                            # if mem["email"] == row["email"]:
                            fuz_dist = fuzz.ratio(mem["email"].lower(), row["email"].lower())
                            if fuz_dist >= 75:
                                memberID = mem["member_id"]
                                break
                            
                        for dep in depName:
                            # if dep["department_name"] == row["department_name"]:
                            fuz_dist = fuzz.ratio(dep["department_name"].lower(), row["department_name"].lower())
                            if fuz_dist >= 75:
                                departmentID = dep["department_id"]
                                break 
                        if departmentID == None:
                            departmentID = 0
                        if row["gl_account"] == '':
                            row["gl_account"] = 0
                        touple = (departmentID, row["department_name"], row["cost_center"], row["gl_account"], memberID, row["internal_order"])
                        values.append(touple) 
                        
                    sqlQuery = "select count(*) as count from department_master where department_id = ? and department_name = ? " \
                        "and cost_center = ? and gl_account = ? and member_id = ? and internal_order = ?"
                    
                    #error
                    for i in values:
                        mycursor.execute(sqlQuery, i)
                    dup = mycursor.fetchone()
                    
                    msg = "Duplicate Entry!"
                        
                    if dup["count"] != 1:
                        sqlQuery = "insert into department_master (department_id, department_name, cost_center, gl_account, member_id, internal_order) " \
                            "values (?, ?, ?, ?, ?, ?)"
                        
                        for i in values:
                            mycursor.execute(sqlQuery, i)
                        msg = "Inserted Successfully!"
                    
                else:
                    for row in list_item:
                        touple = (row["department_id"], row["department_name"], row["cost_center"], row["gl_account"], row["member_id"], row["internal_order"])
                        values.append(touple)
                    
                    sqlQuery = "select count(*) as count from department_master where department_id = ? and department_name = ? " \
                        "and cost_center = ? and gl_account = ? and member_id = ? and internal_order = ?"
                    for i in values:
                        temp = i
                        mycursor.execute(sqlQuery, temp)
                        dup = mycursor.fetchone()
                        msg = "Duplicate Entry!"
                        
                    if dup["count"] != 1:
                        sqlQuery = "insert into department_master (department_id, department_name, cost_center, gl_account, member_id, internal_order) " \
                            "values (?, ?, ?, ?, ?, ?)"

                        for j in  values:
                            temp = j   
                            mycursor.executemany(sqlQuery, values)
                            msg = "Inserted Successfully!"
            
            else:
                sr_no = event["params"]["querystring"]["sr_no"]
                
                sqlQuery = "update department_master set department_id = ?, department_name = ?, cost_center = ?, " \
                    "gl_account = ?, member_id = ?, internal_order = ? where sr_no = ?"
                    
                values = ( record["department_id"], record["department_name"], record["cost_center"], record["gl_account"], record["member_id"], record['internal_order'], sr_no )
                # print(sqlQuery, values)
                mycursor.execute(sqlQuery, values)
                        
                msg = "Updated Successfully!"
                
            mydb.commit()
            
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Duplicate entry code")
        }
            
    except Exception as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps(str(e))
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': msg
    }

#event not passed
def deleteDepartmentalBudgetMaster(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            if "querystring" in event["params"]:
                
                if "department_id" in event["params"]["querystring"]:
                    
                    if len(event["params"]["querystring"]["department_id"].split(',')) == 1:
                        values = event["params"]["querystring"]["department_id"]
                        mycursor.execute("DELETE FROM departmental_budget_master WHERE department_id = ? ", values)
                        
                    else:
                        values = event["params"]["querystring"]["department_id"].split(',')
                        mycursor.execute("delete from departmental_budget_master where department_id in {}".format(tuple(values)))
            
        mydb.commit()
    
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Unable to delete")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Data deleted!")
    }

#not tested event not found
def getDepartmentalBudgetMaster(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
                        print(event)
            
            mycursor.execute("select * from departmental_budget_master")
            temp = convertValuesTodict(mycursor.description,mycursor.fetchall())
                    
            for row in temp:
                record = {
                    "department_id": row["department_id"],
                    "department_name": row["department_name"],
                    "budget": row["budget"],
                    "warning_per": row["warning_per"],
                    "limit_per": row["limit_per"],
                    "valid_from": str(row["valid_from"]),
                    "valid_to": str(row["valid_to"])
                }
                records.append(record)
    
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure!")
        }
        
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

#event not found
def patchDepartmentalBudgetMaster(event, context): 
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    record = {
        "department_name": "", 
        "budget": "", 
        "warning_per": "", 
        "limit_per": "",
        "valid_from": "",
        "valid_to": ""
    }

    try:
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)


            if "department_id" in event["params"]["querystring"]:
                
                department_id = event["params"]["querystring"]["department_id"]
                
                sqlQuery = "update departmental_budget_master set department_name = ?, budget = ?, limit_per = ?, warning_per = ?, valid_from = ?, valid_to = ? where department_id = ?"
                    
                values = ( record["department_name"], record["budget"], record["limit_per"], record["warning_per"], record["valid_from"], record["valid_to"], department_id )
                
                mycursor.execute(sqlQuery, values)
                
                mydb.commit()  
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Updated Unuccessfully!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Updated Successfully!")
    }

#event not found
def postDepartmentalBudgetOrder(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    list_item = []
    
    try:
        for row in event["body-json"]:
            record = {
                "department_name": "", 
                "budget": "", 
                "warning_per": "", 
                "limit_per": "",
                "valid_from": "",
                "valid_to": ""
            }
            
            for value in row:
                if value in record:
                    record[value] = row[value]
                    
            list_item.append(record)
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if "import_entries" in event["params"]["querystring"]:
                mycursor.execute("DELETE FROM departmental_budget_master;")
                
            values = [] 
            dep_names = []
                
            for row in list_item:
                dep_names.append(row["department_name"])
                touple = (row["department_name"], row["budget"], str(row["warning_per"]), str(row["limit_per"]), row["valid_from"], row["valid_to"])
                values.append(touple)
                
            dep_names = set(dep_names)
            dep_names = list(dep_names)
            
            mycursor.execute("select department_name from departmental_budget_master")
            dep_detail = mycursor.fetchall()
            
            for each in dep_names:
                for row in dep_detail:
                    if each.lower() == row["department_name"].lower():
                        mydb.rollback()
                        return {
                            'statuscode': 500,
                            'body': json.dumps("Duplicate Department Name")
                        }
                    
            sqlQuery = "insert into departmental_budget_master (department_name, budget, warning_per, limit_per, valid_from, valid_to) values (?, ?, ?, ?, ?, ?)"

            for i in values:
                mycursor.execute(sqlQuery, i)

            msg = "Inserted Successfully"
            
            mydb.commit()
        
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Duplicate entry code")
        }
            
    except Exception as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': str(e)
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': msg
    }

#not tested events not found
def getSapMaterials(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client('secretsmanager',
    #                        region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    s3 = boto3.client("s3")
    
    reocrds = {}
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
                        print(event)

            if "po_number" in event["params"]["querystring"]:
                po_number = event["params"]["querystring"]["po_number"]
                
                mycursor.execute("select material, material_desc, item_no from po_detail where po_number = ? order by item_no", po_number)
                records = mycursor.fetchall()
                records = convertValuesTodict(mycursor.description , records)
                
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Fail")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

#tested queries working correctly
def getIrnDetails(event=None, context=None):
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId=secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    irn = event["params"]["querystring"]["irn"]

    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
                        print(event)

            mycursor.execute("SELECT * FROM elipo_setting where key_name = 'master_gst_details'")
            mastergst = mycursor.fetchall()
            mastergst = convertValuesTodict(mycursor.description, mastergst)

            if mastergst:
                mastergst_t = mastergst
                mastergst = {}

                for each in mastergst_t:
                    mastergst[each['value1']] = each['value2']

                del mastergst_t

                base_url = mastergst['baseurl']

                params = {
                    'email': mastergst['email']
                }
                headers = {
                    'username': mastergst['username'],
                    'password': mastergst['password'],
                    'ip_address': mastergst['ip_address'],
                    'client_id': mastergst['client_id'],
                    'client_secret': mastergst['client_secret'],
                    'gstin': mastergst['gstin']
                }

                responce = requests.get(url=base_url+'/einvoice/authenticate', params=params, headers=headers)

                if responce:
                    responce = responce.json()

                    if responce['status_cd'] == 'Sucess':

                        auth_token = responce['data']['AuthToken']

                        params = {
                            'email': mastergst['email'],
                            'param1': irn
                        }
                        headers = {
                            'username': mastergst['username'],
                            'auth-token': auth_token,
                            'ip_address': mastergst['ip_address'],
                            'client_id': mastergst['client_id'],
                            'client_secret': mastergst['client_secret'],
                            'gstin': mastergst['gstin']
                        }

                        responce = requests.get(url=base_url + '/einvoice/type/GETIRN/version/V1_03', params=params, headers=headers)
                        
                        if responce:
                            print(responce)
                            if responce.status_code == 200:
                                responce = responce.json()

                                if 'data' in responce:

                                    return {
                                        'statuscode': 200,
                                        'body': responce['data']
                                    }

                                else:
                                    return {
                                        'statuscode': 402,
                                        'body': json.dumps('Requested IRN data is not available.')
                                    }

                            elif responce.status_code == 404:
                                return {
                                    'statuscode': 404,
                                    'body': json.dumps("Requested entity is not found or if requested API is not found.")
                                }
                            else:
                                return {
                                    'statuscode': 500,
                                    'body': json.dumps('Internal server error')
                                }


    except Exception as e:
        print(e)
        return {
            'statuscode': 500,
            'body': json.dumps('Internal Error')
        }

    finally:
        mydb.close()

def deleteMaterialMasterDetails(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            if "querystring" in event["params"]:
                if "material_no" in event["params"]["querystring"]:
                    if len(event["params"]["querystring"]["material_no"].split(',')) == 1:
                        
                        mycursor.execute("DELETE FROM material_master WHERE material_no = ? ",event["params"]["querystring"]["material_no"])
                    else:
                        
                        values = event["params"]["querystring"]["material_no"].split(',')
                        mycursor.execute("delete from material_master where material_no in {}".format(tuple(values)))
            
        mydb.commit()
    
    except Exception as e:
        return {
            'statuscode': 500,
            'body': json.dumps(str(e))
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Data deleted!")
    }

#column names not yet converted
def getMasterMasterDetails(event, context):
    print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
                        print(event)
            
            if "material_no" in event["params"]["querystring"]:
                
                material_no = event["params"]["querystring"]["material_no"]
                mycursor.execute("select mm.*, m.description from material_master mm left join master m on mm.uom = m.code " \
                    "where material_no = ?", int(material_no))
                # temp=convertValuesTodict(mycursor.description, mycursor.fetchall())
                
                for row in mycursor:
                    record = {
                        "material_no": row["material_no"].rstrip(),
                        "material_name": row["material_name"].rstrip(),
                        "gst_per": row["gst_per"],
                        "unit_price": row["unit_price"],
                        "gl_account": row["gl_account"],
                        "uom" : row["uom"],
                        "uom_description" : row['description'],
                        "hsn_code": row["hsn_code"]
                    }
                    records.append(record)
                
            else:
            
                mycursor.execute("select mm.*, m.description from material_master mm left join master m on mm.uom = m.code order by material_no")
                # temp=convertValuesTodict(mycursor.description, mycursor.fetchall())
                
                for row in mycursor:
                    record = {
                        "material_no": row["material_no"].rstrip(),
                        "material_name": row["material_name"].rstrip(),
                        "gst_per": row["gst_per"],
                        "unit_price": row["unit_price"],
                        "gl_account": row["gl_account"],
                        "uom" : row["uom"],
                        "uom_description" : row['description'],
                        "hsn_code": row["hsn_code"]
                    }
                    records.append(record)
                
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

#working fine foe event passed
def patchMaterialMasterDetails(event, context):
    print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    record = {
        "material_name": "", 
        "gst_per": "", 
        "unit_price": "", 
        "gl_account": "",
        "uom" : "",
        "hsn_code": ""
    }

    try:
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
                
            if "material_no" in event["params"]["querystring"]:
                
                material_no = event["params"]["querystring"]["material_no"]
                
                sqlQuery = "update material_master set material_name = ?, gst_per = ?, unit_price = ?, gl_account = ?, uom = ?, hsn_code = ? where material_no = ?"
                    
                values = ( record["material_name"], record["gst_per"], record["unit_price"], record["gl_account"], record['uom'], record["hsn_code"], material_no )
                            
                mycursor.execute(sqlQuery, values)
                
                mydb.commit()  
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Updated Unuccessfully!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Updated Successfully!")
    }
# event = {'body-json': {'material_name': 'TRAINING-FIRST RESPONDER AWARENESS LEVEL', 'gst_per': '', 'hsn_code': '', 'unit_price': 3400, 'gl_account': 0, 'uom': '10', 'uom_description': 'Day(s)'}, 'params': {'path': {}, 'querystring': {'material_no': '50065678'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImQyODRjNDFiLWNmZmItNGIzNC04OGVmLTQyOGQ3MTczNGU4NCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg1MTcwMzk0LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg1MTczOTk0LCJpYXQiOjE2ODUxNzAzOTQsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.ankVrJuxvXDkiuRCGwJoXgo-rAs9rVriGwaQo7dHwNWkBwBIS3j1vfBaHXqpJEiRsE44wBIfW7kjfLnVvwy4Gp7qy4q1EwZh1nqAAWGeW4ljq3QErtWx_2y7GlbFYWaR0ujYgt8VM20vhrxBVli6btz_bGabdRTkxA_PB_FtUWLnzr6gyUrNAYrJVUXFX-20aLMPSD6KtyJDhTtRzfTy6EQy9nOjhdr0lohfYHXfp0-9ASFtU7PL-PVE8xKXzy_MLwObDQpG53JEV1djWbQXtAnSQrpOrbh5iOSuWttBl80AeeMM8mLkakUoke5VkdoMbSH1w_YzIooNMx3c1ivYSA', 'content-type': 'application/json', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6471b709-775caede736539bb2443ccca', 'X-Forwarded-For': '49.205.140.242', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'master-v1', 'source-ip': '49.205.140.242', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': '85d18c57-3c04-4b87-87b5-98eb869866d9', 'resource-id': 'fonxww', 'resource-path': '/material-master'}}
# print(patchMaterialMasterDetails(event, ' '))
#working fine for event passed
def postMaterialMasterDetails(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    list_item = []
    
    try:
        print(event)
        for row in event["body-json"]:

            if 'gl_account' in event["body-json"][0] :
                if event["body-json"][0]['gl_account'] == '':
                    event["body-json"][0]['gl_account'] = 0

            record = {
                "material_no":"", 
                "material_name":"", 
                "gst_per":"", 
                "unit_price":"", 
                "gl_account":0, 
                "uom":"",
                "hsn_code": ""
            }
            
            for value in row:
                if value in record:
                    record[value] = row[value]
                    
            list_item.append(record)
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "import_entries" in event["params"]["querystring"]:
                mycursor.execute("TRUNCATE material_master")
            
            values = []
            
            for row in list_item:
                touple = (row["material_no"], row["material_name"], row["gst_per"], row["unit_price"], row["gl_account"], row["uom"], row["hsn_code"])
                values.append(touple)
                
            sqlQuery = "insert into material_master (material_no, material_name, gst_per, unit_price, gl_account, uom, hsn_code)" \
                "values (?, ?, ?, ?, ?, ?, ?)"
                        
            mycursor.executemany(sqlQuery, values)
            
            print('done execution')
                        
            mydb.commit()
            
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Duplicate entry code")
        }
            
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Insertion failed!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Inserted Successfully!")
    }

# event = {'body-json': [{'material_no': '50065678', 'material_name': 'TRAINING-FIRST RESPONDER AWARENESS LEVEL', 'gst_per': '', 'unit_price': 3400, 'gl_account': '', 'uom': 'Day(s)', 'uom_description': 'Day(s)'}], 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImZmYWM0NWM2LTVkMDctNDY0Ni1iZjllLTQ2Mzk1NDcwYjhhZCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg1MTA1MzcyLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg1MTA4OTcyLCJpYXQiOjE2ODUxMDUzNzIsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.doSrgFIeGmaaXQWGvr-1szP13IRl5mltCXHUDSHglBMIuvyhG-Mfw8LFrzsyMcEvRxxy2-zbwU6apnwT54xKIubPzWrtqQr4OcAH7sJmtRFed_2CiR_S_G0dY5sIYIoQPWXkaiLkWtAPQ32n_JaHCmVDBqb9M9fI7qcGvebGfpqh0s9_sBLnwCc9-oAJjWmtCoLAcyBEg6n7g0_6dc9XJSy5F9l8K9A9rS7kiH0VVyXB1bbllmxGYgAMiayNHUD-XDzodqTIhaBPqcKw6vLDY3EbI4md2yuYKEDtFNKVTRFZlq8lKu5cQdIuNJXChUWB37LpmV_NCq9TeLYMJVdgvQ', 'content-type': 'application/json', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6470ab8a-5d12e5b5622f266647855ba2', 'X-Forwarded-For': '49.205.140.18', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'master-v1', 'source-ip': '49.205.140.18', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'ce579e0b-10a2-4a52-bf17-55c30851b0ff', 'resource-id': 'fonxww', 'resource-path': '/material-master'}}
# print(postMaterialMasterDetails(event, ' '))

#column names not yet converted
def getMaterialMasterSearchHelp(event, context):
    print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
                        print(event)
        
            mycursor.execute("select material_no, material_name from material_master")
            
            for row in mycursor:
                record = {
                    "material_no": row["material_no"],
                    "material_name": row["material_name"]
                }
                records.append(record)
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure")   
        }
        
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

def deleteTaxCodeMaster(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
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

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if "company_code" in event["params"]["querystring"] and "tax_code" in event["params"]["querystring"]:
                company_code = event["params"]["querystring"]["company_code"]
                tax_code = event["params"]["querystring"]["tax_code"]
                
                values = (company_code, tax_code)
                mycursor.execute("DELETE FROM tax_code WHERE company_code = ? and tax_code = ?", values)
            
            elif "tax_codes" in event["body-json"]:
                for row in event["body-json"]["tax_codes"]:
                    company_code = row["company_code"]
                    tax_code = row["tax_code"]
                    
                    values = (company_code, tax_code)
                    mycursor.execute("DELETE FROM tax_code WHERE company_code = ? and tax_code = ?", values)
            
            mydb.commit()
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("unable to delete")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Delete Successful")
    }

#tested
def getTaxCodeMaster(event, context): 
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    records = []
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
            
            if "companyCode" in event["params"]["querystring"]:
                companyCode = event["params"]["querystring"]["companyCode"]
                
                mycursor.execute("select * from tax_code where  company_code = ?", companyCode)
                records = mycursor.fetchall()
                records=convertValuesTodict(mycursor.description, records)
                
            else:
                mycursor.execute("select * from tax_code")
                records = mycursor.fetchall()
                records=convertValuesTodict(mycursor.description, records)
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

#event not found
def patchTaxCodeMaster(event, context): 
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    record = {
        "company_code": "",
        "tax_code" : "",
        "tax_per": "",
        "description": ""
    }

    try:
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 	
            
            if "company_code" in event["params"]["querystring"] and "tax_code" in event["params"]["querystring"]:
                company_code = event["params"]["querystring"]["company_code"]
                tax_code = event["params"]["querystring"]["tax_code"]
                
                sqlQuery = "update tax_code set company_code = ?, tax_code = ?, tax_per = ?, description = ? where company_code = ? and tax_code = ?"
                values = ( record["company_code"], record["tax_code"], record["tax_per"], record["description"], company_code, tax_code )
                mycursor.execute(sqlQuery, values)
                
                mydb.commit()  
    
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Duplicate Error!")
        } 
    
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Updated Unsuccessfully!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Updated Successfully!")
    }

#statements are working fine
def postTaxCodeMaster(event, context):
    print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    list_item = []
    
    try:
        
        for row in event["body-json"]:
            record = {
                "company_code": "",
                "tax_code" : "",
                "tax_per": "",
                "description": ""
            }
            
            for value in row:
                if value in record:
                    record[value] = row[value]
                    
            list_item.append(record)
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if "import_entries" in event["params"]["querystring"]:
                mycursor.execute("TRUNCATE TABLE tax_code")
            
            values = []
            
            sqlQuery = "insert into tax_code (company_code, tax_code, tax_per, description) values (?, ?, ?, ?)"
            for row in list_item:
                touple = (row["company_code"], row["tax_code"], row["tax_per"], row["description"])
                values.append(touple)
                mycursor.execute(sqlQuery, touple)
                        
            mydb.commit()
            
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Duplicate Entry!")
        }
            
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Insertion Failed!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Inserted Successfully!")
    }

# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'page': '2'}, 'header': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'Postman-Token': '115df6e9-eb76-429b-bc77-60580fce26cf', 'User-Agent': 'PostmanRuntime/7.29.2', 'X-Amzn-Trace-Id': 'Root=1-6316d0c8-3a15754e456047e83fe25c0f', 'X-Forwarded-For': '182.72.219.94', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'master-v1', 'source-ip': '182.72.219.94', 'user': '', 'user-agent': 'PostmanRuntime/7.29.2', 'user-arn': '', 'request-id': '26818fa2-706a-44ad-a5ed-1b38af9e5e5c', 'resource-id': 'brjcg6', 'resource-path': '/tax-code'}}
# print(postTaxCodeMaster(event,' '))

#event not found
def getVendor(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    # TODO implement

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    record = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
                        print(event)

            vendor = None

            if "vendor_no" in event["params"]["querystring"]:
                vendor_no = event["params"]["querystring"]["vendor_no"]
            
                mycursor.execute("SELECT v.*, d.value2 " \
                    "FROM vendor_master v " \
                    "left join dropdown d " \
                    "on v.gst_treatment = d.value1 " \
                    "where v.vendor_no = ? and d.drop_key = 'vendor_gst_treatment'", vendor_no)
                record = mycursor.fetchall()
                record = convertValuesTodict(mycursor.description, record)

            elif 'userid' in event["params"]["querystring"]:
                values = (event["params"]["querystring"]["userid"],)
                sqlQuery = "select member_id from member where email = ?"
                mycursor.execute(sqlQuery, values)
                member = mycursor.fetchone()
                # member = convertValuesTodict(mycursor.description, member)

                if member:
                    values = (member['member_id'],)
                    mycursor.execute(
                        "SELECT v.*, d.value2 FROM vendor_master v "
                        "left join dropdown d on v.gst_treatment = d.value1 "
                        "where v.member_id = ? and d.drop_key = 'vendor_gst_treatment'",
                        values)
                    vendor = mycursor.fetchone()
                    # vendor = convertValuesTodict(mycursor.description, vendor)

                    if vendor:
                        record = {
                            "vendor_no": vendor["vendor_no"],
                            "name": vendor["vendor_name"],
                            "currency": vendor["currency"],
                            "payment_terms": str(vendor["payment_terms"]), 
                            "tds": vendor["tds"],
                            "gst_type": vendor["gst_per"],
                            "gstin_uin": vendor["gstin_uin"]
                        }

    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()

    return {
        'statusCode': 200,
        'body': record
    }

# event = {
#     "params" : {
#         "querystring" : {
#             "userid" : "theon@got.com"
#         }
#     }
# }
# context = ""
# responce = lambda_handler(event, context)
# print(responce)

#working fine for event passed
def getVendorList(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    print(event)
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    records = []
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
                        print(event)
            
            if "unassigned_vednor" in event["params"]["querystring"]:
                mycursor.execute("SELECT vendor_no, vendor_name FROM vendor_master where member_id = NULL")
                
            elif "jurisdiction" in event["params"]["querystring"]:
                value = event["params"]["querystring"]["jurisdiction"]
                mycursor.execute("SELECT vendor_no, vendor_name FROM vendor_master where jurisdiction_code = ?", value)
                
            elif "vendor_no" in event["params"]["querystring"]:
                value = event["params"]["querystring"]["vendor_no"]
                mycursor.execute("SELECT jurisdiction_code from vendor_master where vendor_no = ?", value)
                
            # elif "refponumber" in event["params"]["querystring"] or "vendorcode" in event["params"]["querystring"]: #BOC changed
            #     refponumber = event["params"]["querystring"]["refponumber"]
            #     vendorcode = event["params"]["querystring"]["vendorcode"]

            #     if  refponumber == '' :
            #         mycursor.execute("SELECT vendor_no, vendor_name FROM vendor_master")
            #     else :
            #         sqlquery = "SELECT vendor_no, vendor_name FROM vendor_master where vendor_no = ? "
            #         mycursor.execute(sqlquery , vendorcode) #EOC changed
                
            else:
                mycursor.execute("SELECT vendor_no, vendor_name FROM vendor_master") 
                
                
            search_help = []
            #temp = convertValuesTodict(mycursor.description, mycursor.fetchall())
            for vendor in mycursor:
                record = {
                    "code" : vendor["vendor_no"],
                    "description" : vendor["vendor_name"]
                }
                records.append(record)
                    
                # records["search_help"] = search_help
            
    # except :
        
    #     return {
    #         'statusCode': 500,
    #         'body': json.dumps("Internal Failure")
    #     }
            
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': records
    }

#event not found
def deleteVendorMasterDetails(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if "vendor_no" in event["params"]["querystring"]:
                
                if len(event["params"]["querystring"]["vendor_no"].split(',')) == 1:
                    mycursor.execute("DELETE FROM vendor_master WHERE vendor_no = ? ",event["params"]["querystring"]["vendor_no"])
                    mycursor.execute("DELETE FROM vendor_user WHERE vendor_no = ? ",event["params"]["querystring"]["vendor_no"])
                else:
                    mycursor.execute("delete from vendor_master where vendor_no in {}".format(tuple(event["params"]["querystring"]["vendor_no"].split(','))))
                    mycursor.execute("delete from vendor_user where vendor_no in {}".format(tuple(event["params"]["querystring"]["vendor_no"].split(','))))
            
            mydb.commit()
            
    except:
        
        return {
            'statuscode': 500,
            'body': json.dumps("unable to delete")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Delete Successful")
    }

def getVendorMasterDetails(event, context):
    global dbScehma 
    dbScehma = '"DBADMIN"'

    mydb = hdbcliConnect()

    records = []

    try:
        with mydb.cursor() as mycursor:
            
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            member_name = ""
            mycursor.execute("select a.*, b.fs_name, b.ls_name, b.email " \
                "from vendor_master a " \
                "left join member b " \
                "on a.member_id = b.member_id " \
                "order by vendor_no")
            vendor_master = mycursor.fetchall()
            
            mycursor.execute("select * from vendor_user order by vendor_no")
            vendor_email = mycursor.fetchall()
            
            for row in vendor_master:
                if row["fs_name"] == None and row["ls_name"] == None:
                    member_name = ""
                elif row["fs_name"] != None and row["ls_name"] == None:
                    member_name = row["fs_name"]
                elif row["fs_name"] == None and row["ls_name"] != None:
                    member_name = row["ls_name"]
                elif row["fs_name"] != None and row["ls_name"] != None:
                    member_name = row["fs_name"] + " " + row["ls_name"]
                    
                if row["member_id"] == None:
                    member_id = ''
                else:
                    member_id = row["member_id"]
                    
                if row["email"] == None:
                    vendorEmail = ''
                else:
                    vendorEmail = row["email"]
                    
                if row["pan"] == None:
                    pan = ''
                else:
                    pan = row["pan"]
                
                sup_emails = []
                for each in vendor_email:
                    if row["vendor_no"] == each["vendor_no"]:
                        sup_emails.append(each["email"])
                    
                record = {
                    "vendor_no" : row["vendor_no"], 
                    "vendor_name" : row["vendor_name"], 
                    "gst_treatment" : row["gst_treatment"], 
                    "gstin_uin" : row["gstin_uin"], 
                    "source_of_supply" : row["source_of_supply"], 
                    "currency" : row["currency"], 
                    "payment_terms" : str(row["payment_terms"]), 
                    "tds" : str(row["tds"]), 
                    "gst_per" : row["gst_per"],
                    "jurisdiction_code" : row["jurisdiction_code"],
                    "pan" : pan,
                    "member_id": member_id,
                    "member_name" : member_name,
                    "email": vendorEmail,
                    "international_code": row["international_code"],
                    "sup_emails": sup_emails
                }
                records.append(record)
                
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
          
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }


#working fine for event passed
def patchVendorMasterDetails(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    record = {
        "vendor_name": "", 
        "gst_treatment": "", 
        "gstin_uin": "", 
        "source_of_supply": "", 
        "jurisdiction_code":"",
        "currency": "",
        "payment_terms": "", 
        "tds": "", 
        "international_code": "",
        "gst_per": "", 
        "pan": "",
        "member_id": ""
    }

    try:
        print(event)
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)

            
            if "vendor_no" in event["params"]["querystring"]:
                vendor_no = event["params"]["querystring"]["vendor_no"]
                
                sqlQuery = "update vendor_master set vendor_name = ?, gst_treatment = ?, gstin_uin = ?, source_of_supply = ?,jurisdiction_code =?, currency = ?, " \
                    "payment_terms = ?, tds = ?, international_code = ?, gst_per = ?, pan = ?, member_id = ? where vendor_no = ?"
                    
                values = ( record["vendor_name"], record["gst_treatment"], str(record["gstin_uin"]).upper(), record["source_of_supply"],record['jurisdiction_code'], record["currency"], record["payment_terms"], 
                            record["tds"], str(record["international_code"]).upper(), record["gst_per"], str(record["pan"]).upper(), record["member_id"], vendor_no )
                            
                # print(sqlQuery, values)
                mycursor.execute(sqlQuery, values)
                
                mycursor.execute("delete from vendor_user where vendor_no = ?", vendor_no)
                
                values = []
                if "sup_emails" in event["body-json"] and event["body-json"]["sup_emails"] != []:
                    for each in event["body-json"]["sup_emails"]:
                        if each != None:
                            temp = (vendor_no, each)
                            values.append(temp)
                    
                    finalEmail_values = []
                    for i in range(len(values)):
                        if values[i] not in values[i + 1:]:
                            finalEmail_values.append(values[i])
                    
                    sqlQuery = "insert into vendor_user (vendor_no, email) values (?, ?)"
                    mycursor.executemany(sqlQuery, finalEmail_values)
                
                mydb.commit()
    
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        
        if "member_id" in str(e):
            msg = "Member ID already exists!"
        else:
            msg = "Duplicate entry!"
            
        return {
            'statuscode': 500,
            'body': json.dumps(msg)
        }        
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Data not updated!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Updated Successfully!")
    }
# event = {'body-json': {'vendor_name': 'OTV', 'gst_treatment': 'unregistered_business', 'gstin_uin': '', 'international_code': '', 'source_of_supply': '', 'jurisdiction_code': '', 'currency': 'INR', 'payment_terms': '15', 'tds': '0.0', 'gst_per': '', 'pan': '0', 'member_id': '', 'member_name': '', 'sup_emails': [None, None, None]}, 'params': {'path': {}, 'querystring': {'vendor_no': '100592'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImJiNjA0ZDI0LWM4OTItNDJmMC1hMjc1LTVlNjQ3MGJhOWIwNCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjYyNTM5NDg4LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjYyNTQzMDg4LCJpYXQiOjE2NjI1Mzk0ODgsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.NdxJz0pHqNV3JdsxIxiRKo5rAuQSH4QMyLPczYsXLhbaUarOPeUMEAu8-XTy-Y06YqVT8Fyvy7HwCZcewjSp-rPlZbqD2PmO-PmuQMlZ3UfbiM1DdJPLje__exp73AzAYaYq6O_URajIMvEJmvo5VbMTn8jxv_5hu_7Aaz2eVC2EQK_-glY_9uFHL6GwJW6xdWmEIB7DAJjurt9lP3U0pQejlBAyjZ6jUvaKKi0XEWXNiemtIPlcoFATyvyWOK_WXaKkeNl_9zfQKKIwX5S1UXha-4_TAnX2L41hlSR_dLy6-LhMFSs4E0lPJ6UchwPY5e5kjw7RTjthnXrtYYPPPA', 'content-type': 'application/json', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-63185741-5aec8826386200d855d522ad', 'X-Forwarded-For': '49.206.131.186', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'master-v1', 'source-ip': '49.206.131.186', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'b996d561-cfe8-4cd9-bf6b-9c8f23969002', 'resource-id': 'uzyudk', 'resource-path': '/vendor-master'}}

# print(patchVendorMasterDetails(event, ' '))

#working fine for event passed
def postVendorMasterDetails(event, context):
    print(event)
    
    global dbScehma
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId=secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    records = {}
    try:
        print(event)
        list_item = []
        for row in event["body-json"]:

            if 'tds' in event["body-json"][0]:
                event["body-json"][0]['tds'] = 0.0 
            item = {
                "vendor_no": "",
                "vendor_name": "",
                "gst_treatment": "",
                "gstin_uin": "",
                "email": "",
                "source_of_supply": "",
                "jurisdiction_code": "",
                "currency": "",
                "payment_terms": "",
                "tds": 0.0,
                "gst_per": "",
                "international_code": "",
                "pan": "",
                "member_id": None,
                "sup_emails": None
            }
            for value in row:
                if value in item:
                    item[value] = row[value]
            list_item.append(item)

        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            if "import_entries" in event["params"]["querystring"]:
                mycursor.execute("delete from vendor_master")
                mycursor.execute("delete from vendor_user")

            values = []
            vendor = []
            email_values = []
            emailids = []

            for row in list_item:
                emailids.append(row['email'])

            format_strings = ','.join(['?'] * len(emailids))
            sqlQuery = "select member_id, email from member where email in ({})".format(format_strings)

            mycursor.execute(sqlQuery, tuple(emailids))
            members = mycursor.fetchall()

            sqlQuery = "insert into vendor_master (vendor_no, vendor_name, gst_treatment, gstin_uin, source_of_supply,jurisdiction_code, currency, " \
                "payment_terms, tds, international_code, gst_per, pan, member_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)"
            for row in list_item:
                member_id = None

                if members:
                    for mem in members:
                        if row['email'] == mem['email']:
                            member_id = mem['member_id']
                            break

                touple = ( int(str(row["vendor_no"]).strip()), row["vendor_name"], row["gst_treatment"], str(row["gstin_uin"]).upper(), row["source_of_supply"],row["jurisdiction_code"], row["currency"], row["payment_terms"], 
                    row["tds"], row["international_code"].upper(), row["gst_per"], str(row["pan"]).upper(), member_id )
                values.append(touple)
                mycursor.execute(sqlQuery, touple)

                vendor.append(row["vendor_no"])

                if row["sup_emails"] != None or row["sup_emails"] != []:
                    for each in row["sup_emails"]:
                        if each:
                            temp = (str(row["vendor_no"]).strip(), each)
                            email_values.append(temp)

            # sqlQuery = "insert into vendor_master (vendor_no, vendor_name, gst_treatment, gstin_uin, source_of_supply,jurisdiction_code, currency, " \
            #     "payment_terms, tds, international_code, gst_per, pan, member_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)"
            # mycursor.executemany(sqlQuery, values)

            if email_values:
                finalEmail_values = []
                sqlQuery = "insert into vendor_user (vendor_no, email) values (?, ?)"
                for i in range(len(email_values)):
                    if email_values[i] not in email_values[i + 1:]:
                        finalEmail_values.append(email_values[i])
                        mycursor.execute(sqlQuery, email_values[i])
                # if finalEmail_values:
                    sqlQuery = "insert into vendor_user (vendor_no, email) values (?, ?)"
                    # mycursor.executemany(sqlQuery, finalEmail_values)

            mydb.commit()

    except pymysql.err.IntegrityError as e:
        mydb.rollback()

        if "member_id" in str(e):
            msg = "User is already assigned for another vendor!"
        elif "PRIMARY" in str(e):
            msg = "Vendor No. already exists!"
        else:
            msg = "Duplicate entry!"

        return {
            'statuscode': 500,
            'body': json.dumps(msg)
        }

    except Exception as e:
        mydb.rollback()

        return {
            'statuscode': 500,
            'body': json.dumps(str(e))
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Inserted Successfully!")
    }
    
# event = {'body-json': [{'vendor_no': '031123', 'vendor_name': 'ONCOST CASH AND CARRY', 'gst_treatment': 'unregistered_business', 'gstin_uin': '', 'international_code': '', 'source_of_supply': '', 'jurisdiction_code': '', 'currency': 'KWD', 'payment_terms': '15', 'tds': '', 'gst_per': '', 'pan': '', 'email': None, 'member_name': '', 'sup_emails': [None, None, None]}], 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjFjODZmODM0LTIwY2UtNDU3My04M2JkLTUyYzcyYTFjYjczZCIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjcyNzI1ODQ0LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjcyNzI5NDQ0LCJpYXQiOjE2NzI3MjU4NDQsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.Gu27u5SmZzaUguh5KoaTTMLQ7eCA_GvC54MCzTvu6l-8OaCbbKSfjmnuoWvJbEO30cLVMkIRIQ3zmX_NWHvBb16WCUUwS6LwDaCsmPilQjF8QcRaVQH4rJINcD5oJytk0ZoRzqk_VIIs1THon7j0wCiPby9QeQ8yOn0eu_FoJouw9vAqL0Z-ZRsGKzamw_pju51a1QgvNZn_g1qKTBQXNanPoXyMVXISNfJ89ylKdkqA17z5i2-Bgele4Y2lMmJm2kHD3oLVGhTqpoV-jvvkRz7x8POCUvFVdol8LV1WpQj05vtVYT-p0X4ZMb31Qyshc6CA7j5JqJCePV4ZTDVIUw', 'content-type': 'application/json', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-63b3c635-498971aa556c480c14a45af8', 'X-Forwarded-For': '49.206.130.114', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'master-v1', 'source-ip': '49.206.130.114', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': '4a46c953-7414-4199-a2ba-b100e3954eac', 'resource-id': 'uzyudk', 'resource-path': '/vendor-master'}}
# print(postVendorMasterDetails(event , ' '))
# event={'body-json': [{'vendor_no': '1001', 'vendor_name': 'test', 'gst_treatment': 'unregistered_business', 'gstin_uin': '', 'international_code': '', 'source_of_supply': '', 'jurisdiction_code': '1234', 'currency': 'KWD', 'payment_terms': '15', 'tds': '0', 'gst_per': '', 'pan': '', 'email': None, 'member_name': '', 'sup_emails': [None, None, None]}], 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjQzODA3MTA5LTcxZjQtNDU5Mi1iODQwLTUyYTljOTliMTU0YSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjQ2MjkzODg4LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjQ2Mjk3NDg4LCJpYXQiOjE2NDYyOTM4ODgsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.lPAUZRUBpsQNsKcKI35M0X5Y3lK1LYpmJzPdGS3RnMCgEZj_jXEgRbImU5a8GrFp3OmmZiQ6y9W9EUt-9zWy0fyps8NCSueNrN_DAcJjLvzeELctnJfZ_5QKamUEMX2otnmmNnXf0A8qg-GRX1fwrzVYH_4vVWEmvpEeGoaqCgcQzf7_53j_xDy0SvJaawuaYsScBVJ6JPFpOqBL9M8uFsj9uFDzr_j4TWOmBxRGxOLp1HMNfgTlCVxhaVZjKo_kkDfpSawfIzlpONtgm2ioAunkgkMUJFNKZIooCQKuwK8akOGtkadoP5TeSV-zBQQsbxo1kMGZ8DcZZNLRaIRXJQ', 'content-type': 'application/json', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'origin': 'http://localhost:4200', 'referer': 'http://localhost:4200/', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-62207c6c-16bf8381268dcb19585c3bac', 'X-Forwarded-For': '49.207.220.39', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'master-v1', 'source-ip': '49.207.220.39', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36', 'user-arn': '', 'request-id': '0bef8815-886a-4508-80fe-eedaee81a46a', 'resource-id': 'uzyudk', 'resource-path': '/vendor-master'}}
# print(lambda_handler(event,""))

# einvoice-reports
#might get an error for big query statement


def getAgingReportDetails(event, context):
    global dbScehma 
    dbScehma = '"DBADMIN"'
    
    mydb = hdbcliConnect()

    output1 = {}
    output2 = []
    output3 = []

    try:
        with mydb.cursor() as mycursor:        
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            val_list = []
            pos = 0
            condn = ""
            days = 30
                
            if "condn" in event["body-json"]:
                for row in event["body-json"]["condn"]:
                    if row["field"] != "interval":
                        condn = condn + " and "
                        
                        if str(row["operator"]) == "like":
                            val_list.append("%" + row["value"] + "%")
                            condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                            
                        elif str(row["operator"]) == "between":
                            val_list.append(row["value"])
                            val_list.append(row["value2"])
                            condn = condn + "a." + str(row["field"]) + " between ? and ? " 
                            
                        else:
                            val_list.append(row["value"])
                            if row["field"] == "company_code":
                                condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                            else:
                                condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                                
                    else:
                        days = 30
                        
            mycursor.execute("select * FROM elipo_setting where key_name = 'payment_status'")
            payment_status_value = mycursor.fetchone()
            
            sqlQuery = "select a.company_code, a.invoice_no, a.npo, a.ref_po_num, a.entry_date as entry_indate, a.amount, " \
                    "DAYS_BETWEEN(a.entry_date , CURRENT_DATE) as days_outstanding, b.vendor_no, b.vendor_name, " \
                    "(case when ( DAYS_BETWEEN( a.entry_date,CURRENT_DATE ) between " + str(0) + " and " + str(days) + " )then cast(a.amount as float) else 0 end) as invoice_30, " \
                    "(case when ( DAYS_BETWEEN( a.entry_date,CURRENT_DATE ) between " + str(int(days) + 1) + " and " + str(int(days) * 2) + " ) then cast(a.amount as float) else 0 end) as invoice_60, " \
                    "(case when ( DAYS_BETWEEN( a.entry_date,CURRENT_DATE ) between " + str( (int(days) * 2) + 1 ) + " and " + str( (int(days) * 3)) + " ) then cast(a.amount as float) else 0 end) as invoice_90, " \
                    "(case when ( DAYS_BETWEEN( a.entry_date,CURRENT_DATE ) > " + str( (int(days) * 3) + 1 ) + " ) then cast(a.amount as float) else 0 end) as invoice_more " \
                    "FROM invoice_header a " \
                    "inner join vendor_master b " \
                    "on a.supplier_id = b.vendor_no "
                    
            if payment_status_value and (payment_status_value['value1'] == 'on'):
                sqlQuery += "where (a.in_status in ('new', 'draft', 'inapproval') or (a.in_status = 'tosap' and a.payment_status = 'paid') ) and (a.npo != null or a.npo = '' or a.npo = 'y') and a.document_type = 'RE' " + condn
                
            else:    
                sqlQuery += "where a.in_status not in ('tosap', 'deleted') and (a.npo != null or a.npo = '' or a.npo = 'y') and a.document_type = 'RE' " + condn
            
            mycursor.execute(sqlQuery, tuple(val_list))
            raw_data = mycursor.fetchall()
                
            npo_invoice_0 = 0
            npo_invoice_31 = 0
            npo_invoice_61 = 0
            npo_invoice_91 = 0
            
            po_invoice_0 = 0
            po_invoice_31 = 0
            po_invoice_61 = 0
            po_invoice_91 = 0
            
            for row in raw_data:
                company_code = row["company_code"]
                if row["npo"] == 'y':
                    flag = 'npo'
                
                else:
                    flag = 'po'
                
                if row["days_outstanding"] != None:
                        
                    if flag == 'npo':
                        if 0 <= row["days_outstanding"] <= int(days):
                            npo_invoice_0 = npo_invoice_0 + 1
                        
                        elif ( int(days) + 1 ) <= row["days_outstanding"] <= ( int(days) * 2 ):
                            npo_invoice_31 = npo_invoice_31 + 1
                            
                        elif ( (int(days) * 2) + 1 ) <= row["days_outstanding"] <= ( int(days) * 3 ):
                            npo_invoice_61 = npo_invoice_61 + 1
                            
                        elif row["days_outstanding"] < ( (int(days) * 3) + 1 ):
                            npo_invoice_91 = npo_invoice_91 + 1
                        
                    elif flag == 'po':
                        if 0 <= row["days_outstanding"] <= int(days):
                            po_invoice_0 = po_invoice_0 + 1
                        
                        elif ( int(days) + 1 ) <= row["days_outstanding"] <= ( int(days) * 2 ):
                            po_invoice_31 = po_invoice_31 + 1
                            
                        elif ( (int(days) * 2) + 1 ) <= row["days_outstanding"] <= ( int(days) * 3 ):
                            po_invoice_61 = po_invoice_61 + 1
                            
                        elif row["days_outstanding"] < ( (int(days) * 3) + 1 ):
                            po_invoice_91 = po_invoice_91 + 1
                    
                    data = {
                        "vendor_no": row["vendor_no"],
                        "vendor_name": row["vendor_name"],
                        "invoice_no": row["invoice_no"],
                        "date": str(row["entry_indate"]),
                        "amount_due": row["amount"],
                        "days_outstanding": str(row["days_outstanding"]),
                        "invoice_0_to_30": str(row["invoice_30"]),
                        "invoice_31_to_60": str(row["invoice_60"]),
                        "invoice_61_to_90": str(row["invoice_90"]),
                        "invoice_91_or_more": str(row["invoice_more"]),
                        "flag": flag
                    }
                    output2.append(data)
                
            output1 = {
                "company_code": company_code,
                "po_0_30": po_invoice_0,
                "wpo_0_30": npo_invoice_0,
                "total_0_30": po_invoice_0 + npo_invoice_0,
                "po_30_60": po_invoice_31,
                "wpo_30_60": npo_invoice_31,
                "total_30_60": po_invoice_31 + npo_invoice_31,
                "po_60_90": po_invoice_61,
                "wpo_60_90": npo_invoice_61,
                "total_60_90": po_invoice_61 + npo_invoice_61,
                "po_ab_90": po_invoice_91,
                "wpo_ab_90": npo_invoice_91,
                "total_ab_90": po_invoice_91 + npo_invoice_91,
            }
            
            record = {
                "output1": output1,
                "output2": output2
            }
            
    # except:
    #     return {
    #         'statuscode': 500,
    #         'body': json.dumps("Internal Error!")
    #     }
        
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': record
    }

# event = {'body-json': {'condn': [{'field': 'company_code', 'operator': '=', 'value': '1000'}]}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjE2YzY1ZThiLWQ0ZjAtNDY2Ny04ZTg2LTNjODViNzVlZDA4NSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg2ODk1NDM5LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg2ODk5MDM5LCJpYXQiOjE2ODY4OTU0MzksImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.TMeOobaKZZfA-Xo4lVqi4OXpR9wm7NxjHt7kckT6GqNJAxthY4AJRF1dEsxCfsC4mLKwG1pot6gQ1q_RHYHka2Ss6XowMEtqebRFbGKCkevfCUaJw9ikUIuzpNxxGVO66WPyFiu0I1dlEkDDZ9bLlLyWL_BN_vZfIlPC32lEpM1B1PIC9NfAy-eNyPycOohzaF0FksMVGBlJYAUKEUWP9ictelXzs4NZtBgJKBVWmRKcpA4WJqZ3RKD-I7ohe2ZCd5UF-PVcP_smKffP4VyfbF6GWRL7l4J6_5D04E3gCDXdUx7EKHHEUcnEEVumwUVnn9t4haYI5SQicoNxnAQIfg', 'content-type': 'application/json', 'Host': 'wzwczc4rhd.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-648bfb93-52d0ba1021786e06423f8552', 'X-Forwarded-For': '49.207.52.67', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'wzwczc4rhd', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'einvoice-v1', 'source-ip': '49.207.52.67', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'e6d366a6-abed-4136-a0b8-8b458a95fafb', 'resource-id': 'dk4cuh', 'resource-path': '/aging-report'}}



def getDiaAnalyticReport(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    print(event)
    records = []
    responce = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            for row in on:
                if row['value1'] =='on':
                    chk = enable_xray(event)
                    if chk['Enable']=='True':
                        patch_all()
                        print(event)
            
            val_list = []
            pos = 0
            condn = ""
            
            start_idx = int(event["params"]["querystring"]['pageno'])
            end_idx = int(event["params"]["querystring"]['nooflines'])
                    
            start_idx = (start_idx -1 ) * end_idx
    
            if "condn" in event["body-json"]:
                for row in event["body-json"]["condn"]:
                    if pos != 0:
                        condn = condn + " and "
                    elif pos == 0:
                        condn = " where "
                        pos = pos + 1
        
                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                        if row["field"] == "vendor_no" or row["field"] == "vendor_name":
                            condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                        else:
                            condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                            
                    elif str(row["operator"]) == "between":
                        val_list.append(row["value"])
                        val_list.append(row["value2"])
                        condn = condn + "a." + str(row["field"]) + " between ? and ? "
                        
                    else:
                        val_list.append(row["value"])
                        if row["field"] == "vendor_no" or row["field"] == "vendor_name":
                            condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                        else:
                            condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                    
            
            sqlQuery = "SELECT a.invoice_no, a.in_status, a.ref_po_num, a.company_code, utctolocal(a.entry_date, 'UTC' ) as entry_date, a.invoice_date, a.posting_date, " \
                "a.baseline_date, a.due_date, a.ap_timespent, utctolocal(a.modified_date, 'UTC' ) as modified_date, utctolocal(a.end_date, 'UTC' ) as end_date, " \
                "a.amount, a.ispaid, a.currency, a.payment_method, a.gl_account, a.business_area, a.supplier_id, a.approver_id, a.supplier_name, a.approver_comments, a.cost_center, " \
                "a.attachment_id, a.taxable_amount, a.discount_per, a.total_discount_amount, a.tcs, a.is_igst, a.tax_per, a.cgst_tot_amt, a.sgst_tot_amt, a.igst_tot_amt, a.tds_per, " \
                "a.tds_tot_amt, a.payment_terms, a.adjustment, a.working_person,a.payment_status, a.supplier_comments, a.npo, a.internal_order, a.department_id, a.app_comment, a.faulty_invoice, " \
                "b.vendor_name, c.ls_name, c.fs_name, d.value2 as document_type " \
                "FROM invoice_header a " \
                "left join vendor_master b " \
    			"on a.supplier_id = b.vendor_no " \
                "left join dropdown d " \
    			"on a.document_type = d.value1 " \
                "left join member c " \
                "on a.working_person = c.member_id " + condn + " order by a.invoice_no desc limit ? offset ?"
        
            
            val_list.append(end_idx)
            val_list.append(start_idx)
            
            mycursor.execute(sqlQuery, tuple(val_list))
            all_invoices = mycursor.fetchall()
            all_invoices = convertValuesTodict(mycursor.description, all_invoices)
            
            
            sqlQuery = "SELECT count(*) as total_invoices " \
                "FROM invoice_header a " \
                "left join vendor_master b " \
    			"on a.supplier_id = b.vendor_no " \
                "left join member c " \
                "on a.working_person = c.member_id " + condn
                
            val_list.pop()
            val_list.pop()
            
            mycursor.execute(sqlQuery, tuple(val_list))
            count = mycursor.fetchone()
            
            invoiceIds = []
            postedInvoiceIds = []
    
            for each in all_invoices:
                if each['in_status'] == "inapproval":
                    invoiceIds.append(each['invoice_no'])
                    
                if each['in_status'] == "tosap":
                    postedInvoiceIds.append(each['invoice_no'])
    
            format_strings = ','.join(['?'] * len(invoiceIds))
            res = invoiceIds
            
            postedFormat_strings = ','.join(['?'] * len(postedInvoiceIds))
            postedRes = postedInvoiceIds
    
            groupid = []
            memberid = []
            approvers_list = []
            approversHistory_list = []
    
            if res:
                mycursor.execute("select * from approval where invoice_no in ({}) order by invoice_no, approval_level".format( format_strings), tuple(res))
    
                approvers_list = mycursor.fetchall()
                approvers_list = convertValuesTodict(mycursor.description, approvers_list)
    
                for row in approvers_list:
    
                    if row["isgroup"] == 'y':
                        groupid.append(row["approver"])
                    elif row["isgroup"] == 'n':
                        memberid.append(row["approver"])
    
                format_strings_mem = ','.join(['?'] * len(memberid))
                format_strings_group = ','.join(['?'] * len(groupid))
    
                approver_final = []
    
                if groupid:
                    mycursor.execute(' select group_id, name from "GROUP" where group_id in ({})'.format(format_strings_group), tuple(groupid))
                    temp = convertValuesTodict(mycursor.description, mycursor.fetchall())
                    for row in temp:
                        temp1 = {
                            "isgroup": "y",
                            "approver": row["group_id"],
                            "name": row["name"]
                        }
                        approver_final.append(temp1)
    
                if memberid:
                    sqlQuery = "select distinct a.approver, b.member_id, " \
                               "b.fs_name, b.ls_name from rule_approver a " \
                               "inner join member b on a.approver = b.member_id " \
                               "where a.approver in ("+ format_strings_mem+")"
    
                    mycursor.execute(sqlQuery, tuple(memberid))
                    temp = convertValuesTodict(mycursor.description, mycursor.fetchall())
                    for row in temp:
                        temp1 = {
                            "isgroup": "n",
                            "approver": row["approver"],
                            "name": row["fs_name"] + " " + row["ls_name"]
                        }
                        approver_final.append(temp1)
                
            if postedRes:
                sqlQuery = "select * from approval_history where invoice_no in ({}) order by invoice_no, approval_level"
                mycursor.execute(sqlQuery.format(postedFormat_strings), tuple(postedRes))
    
                approversHistory_list = mycursor.fetchall()
                approversHistory_list = convertValuesTodict(mycursor.description, approversHistory_list)
                
                for row in approversHistory_list:
    
                    if row["isgroup"] == 'y':
                        groupid.append(row["approver_id"])
                    elif row["isgroup"] == 'n':
                        memberid.append(row["approver_id"])
    
                format_strings_mem = ','.join(['?'] * len(memberid))
                format_strings_group = ','.join(['?'] * len(groupid))
    
                approverHistory_final = []
    
                if groupid:
                    mycursor.execute('select group_id, name from "GROUP" where group_id in ({})'.format(format_strings_group), tuple(groupid))
                    temp = convertValuesTodict(mycursor.description, mycursor.fetchall())
                    for row in temp:
                        temp1 = {
                            "isgroup": "y",
                            "approver": row["group_id"],
                            "name": row["name"]
                        }
                        approverHistory_final.append(temp1)
    
                if memberid:
                    sqlQuery = "select distinct a.approver, b.member_id, " \
                               "b.fs_name, b.ls_name from rule_approver a " \
                               "inner join member b on a.approver = b.member_id " \
                               "where a.approver in ("+ format_strings_mem+")"
    
                    mycursor.execute(sqlQuery, tuple(memberid))
                    temp = convertValuesTodict(mycursor.description, mycursor.fetchall())
                    for row in temp:
                        temp1 = {
                            "isgroup": "n",
                            "approver": row["approver"],
                            "name": row["fs_name"] + " " + row["ls_name"]
                        }
                        approverHistory_final.append(temp1)
            
            for row in all_invoices:
                approvers = []
                
                if row["in_status"] == "tosap":
                    
                    for temp in approversHistory_list:
                        if row["invoice_no"] == temp["invoice_no"]:
                            
                            for temp1 in approverHistory_final:
                                if temp["approver_id"] == temp1["approver"] and temp["isgroup"] == temp1["isgroup"]:
        
                                    status_ap = {
                                        "isgroup": temp1["isgroup"],
                                        "approver": temp1["approver"],
                                        "name": temp1["name"],
                                        "level": temp['approval_level'],
                                        "isapproved": "accepted"
                                    }
                                    approvers.append(status_ap)
                                    
                else:
                    for temp in approvers_list:
                        if row["invoice_no"] == temp["invoice_no"]:
        
                            for temp1 in approver_final:
                                if temp["approver"] == temp1["approver"] and temp["isgroup"] == temp1["isgroup"]:
        
                                    if temp["isapproved"] == "y":
                                        status = "accepted"
                                    elif temp["isapproved"] == 'n':
                                        status = "inapproval"
        
                                    status_ap = {
                                        "isgroup": temp1["isgroup"],
                                        "approver": temp1["approver"],
                                        "name": temp1["name"],
                                        "level": temp['approval_level'],
                                        # "isapproved" : temp["isapproved"]
                                        "isapproved": status
                                    }
                                    approvers.append(status_ap)
        
                entry_date = row["entry_date"].date()
                entry_time = row["entry_date"].time()
    
                update_date = row["modified_date"].date()
                update_time = row["modified_date"].time()
                
                minutes_diff = 0
                if row["end_date"] is not None:
                    end_date = row["end_date"].date()
                    end_time = row["end_date"].time()
                    
                    time_delta = (row["end_date"] - row["entry_date"])
                    total_seconds = time_delta.total_seconds()
                    minutes_diff = math.ceil(total_seconds / 60)
                    
                else:
                    end_date = ""
                    end_time = ""
    
                noOfDueDays = None
                noOfOverDueDays = None
                due_amount = 0.00
                overdue_amount = 0.00
                overdue_flag = 'n'
                due_amount = row["amount"]
    
                if type(row["due_date"]) is not str and row["due_date"]:
                    now = date.today()
                    noOfDueDays = (row["due_date"] - now).days
    
                    if noOfDueDays < 0:
                        noOfOverDueDays = abs(noOfDueDays)
                        overdue_flag = 'y'
                        overdue_amount = row["amount"]         
                        due_amount = row["amount"]
                    else:
                        due_amount = row["amount"]
                        
                    if row["in_status"] == "tosap":
                        noOfDueDays = "Paid"
                        overdue_flag = 'n'
                
                if row["ls_name"] is None and row["fs_name"] is None:
                    user_processing = None
                elif ( row["ls_name"] != None and row["fs_name"] is None ):
                    user_processing = row["ls_name"]
                elif ( row["ls_name"] is None and row["fs_name"] != None ):
                    user_processing = row["fs_name"]
                else:
                    user_processing = row["fs_name"] + " " + row["ls_name"]
    
                data = {
                    "company_code": row["company_code"],
                    # "plant": row["plant"],
                    "document_type": row["document_type"],
                    "vendor_no": row["supplier_id"],
                    "vendor_name": row["vendor_name"],
                    "invoice_no": row["invoice_no"],
                    "invoice_date": str(row["invoice_date"]),
                    "due_date": str(row["due_date"]),
                    "days_to_due": noOfDueDays,
                    "entry_date": str(entry_date),
                    "entry_time": str(entry_time),
                    "update_date": str(update_date),
                    "update_time": str(update_time),
                    "end_date": str(end_date),
                    "end_time": str(end_time),
                    "ref_po_num": row["ref_po_num"],
                    "npo_flag": row["npo"],
                    # "amount": row["amount"],
                    "amount": due_amount,
                    "currency": row["currency"],
                    "payment_terms": row["payment_terms"],
                    "overdue_flag": overdue_flag,
                    "days_overdue": noOfOverDueDays,
                    "amount_overdue": overdue_amount,
                    "document_status": row["in_status"],
                    "reason_text": row["approver_comments"],
                    "payment_status": row["payment_status"],
                    "number_of_approvers": len(approvers),
                    "approvers": approvers,
                    # "user_processing": row["working_person"],
                    "user_processing": user_processing,
                    "process_duration": minutes_diff
                }
                records.append(data)
                
            responce['records'] = records
            responce['total_invoices'] = count['total_invoices']
    
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
    
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': responce
    }

def getKeyProcessAnalyticsReport(event, context):
    global dbScehma 
    dbScehma = '"DBADMIN"'
    
    mydb = hdbcliConnect()

    records = {}
    output1 = []
    output2 = []
    output3 = []
    acc_output = {}

    try:
        with mydb.cursor() as mycursor:
            print(event) #changed
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            mycursor.execute("select * FROM elipo_setting where key_name = 'payment_status'")
            payment_status_value = mycursor.fetchone()
            
            val_list = []
            pos = 0
            condn = ""
    
            if "condn" in event["body-json"]:
                for row in event["body-json"]["condn"]:
                    
                    condn = condn + " and "
                    
                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                        condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                        
                    elif str(row["operator"]) == "between":
                        val_list.append(row["value2"])
                        val_list.append(row["value"])
                        condn = condn + "date(" + str(row["field"]) + ") between ? and ? " 
                        
                    else:
                        val_list.append(row["value"])
                        condn = condn + "" + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
               
            if 'entry_date' not in condn:
                condn = condn + " and entry_date > ADD_MONTHS(CURRENT_TIMESTAMP, -1)"
            
            sqlQuery = "select sum(cast(amount as float)) as total_amount, b.vendor_name, b.currency, b.vendor_no, b.source_of_supply " \
                "from invoice_header " \
                "inner join vendor_master b " \
                "on supplier_id = b.vendor_no "
                
            if payment_status_value and (payment_status_value['value1'] == 'on'):
                sqlQuery += " where (in_status = 'tosap' and payment_status = 'paid') and document_type = 'RE' " + condn + " group by  supplier_id , b.vendor_name , b.currency ,b.vendor_no ,b.source_of_supply order by total_amount desc, b.currency limit 5"
            else:
                sqlQuery += " where in_status = 'tosap' and document_type = 'RE' " + condn + " group by supplier_id, b.vendor_name, b.currency, b.vendor_no, b.source_of_supply order by total_amount desc, b.currency limit 5"
            
            mycursor.execute(sqlQuery, tuple(val_list))
            raw_data = mycursor.fetchall()
            
            if raw_data:
                output1 = []
                for row in raw_data:
                    data = {
                        "vendor_no": row["vendor_no"],
                        "vendor_name": row["vendor_name"],
                        "source_of_supply": row["source_of_supply"],
                        "total_amount": row["total_amount"],
                        "currency": row["currency"]
                    }
                    output1.append(data)
                
            sqlQuery = "select invoice_no, in_status, ref_po_num, due_date, amount, npo " \
                "from invoice_header " \
                "where in_status != 'deleted' and document_type = 'RE' " + condn
                
            mycursor.execute(sqlQuery, tuple(val_list))
            raw_data1 = mycursor.fetchall()
            
            sqlQuery = "select sum(cast(amount as float)) as total from invoice_header "
            
            if payment_status_value and (payment_status_value['value1'] == 'on'):
                sqlQuery += " where (in_status = 'tosap' and payment_status = 'paid') and document_type = 'RE' " + condn
            else:
                sqlQuery += " where in_status = 'tosap' and document_type = 'RE' " + condn
                
            mycursor.execute(sqlQuery, tuple(val_list))
            processed_amount = mycursor.fetchone()
            
            accuracyQuery = "select count(invoice_no) as ocr_inv, round(avg(cast(ocr_accuracy as DECIMAL(18, 2))),2) as avg_accuracy, " \
            	"sum(case when ( ocr_inv = 'y' and ocr_accuracy = 100 ) then 1 else 0 end) as acc_100, " \
            	"sum(case when ( ocr_inv = 'y' and ocr_accuracy < 100 ) then 1 else 0 end) as acc_90 " \
            	"from invoice_header " \
                "where in_status != 'deleted' and ocr_inv = 'y' and cast(ocr_accuracy as DECIMAL(18, 2)) > 0  " + condn               #added and ocr_accuracy > 0 
            mycursor.execute(accuracyQuery, tuple(val_list))
            raw_data2 = mycursor.fetchone()
            
            print(accuracyQuery  ) #changed
            print(tuple(val_list)) #changed
            
            acc_output = {
                "no_of_ocr_inv": raw_data2["ocr_inv"],
                "accuracy_avg": raw_data2["avg_accuracy"],
                "acc_100": raw_data2["acc_100"],
                "acc_90": raw_data2["acc_90"]
            }
            
            output2 = {}
            output3 = {}
            
            flag = None
            
            inprocess_po = 0
            inprocess_npo = 0
            inprocess_none = 0
            processed_po = 0
            processed_npo = 0
            processed_none = 0
            
            current_po = 0
            current_npo = 0
            current_none = 0
            overdue_po = 0
            overdue_npo = 0
            overdue_none = 0
            
            for row in raw_data1:
                today = date.today()
                flag = None
                
                if row["npo"] == 'y':
                    flag = 'npo'
                
                elif row["ref_po_num"] != '' or row["ref_po_num"] != None :
                    flag = 'po'
                
                if row["in_status"] == "new" or row["in_status"] == "draft" or row["in_status"] == "inapproval":
                    if flag == "npo":
                        inprocess_npo = inprocess_npo + 1
                    
                    elif flag == "po":
                        inprocess_po = inprocess_po + 1
                    
                elif row["in_status"] == "tosap":
                    if flag == "npo":
                        processed_npo = processed_npo + 1
                        
                    elif flag == "po":
                        processed_po = processed_po + 1
                        
                if row["due_date"] != None and type(row["due_date"]) is not str:
                    if today <= row["due_date"]:
                        if flag == "npo":
                            current_npo = current_npo + row["amount"]
                            
                        elif flag == "po":
                            current_po = current_po + row["amount"]
                        
                    elif today > row["due_date"]:
                        if flag == "npo":
                            overdue_npo = overdue_npo + row["amount"]
                            
                        elif flag == "po":
                            overdue_po = overdue_po + row["amount"]
                            
            output2 = {
                "inprocess_npo": inprocess_npo,
                "inprocess_po": inprocess_po,
                "inprocess_total":  inprocess_npo + inprocess_po,
                
                "processed_npo": processed_npo,
                "processed_po": processed_po,
                "processed_total": processed_npo + processed_po,
                
                "total_po": inprocess_po + processed_po,
                "total_npo": inprocess_npo + processed_npo,
                "total_all":  inprocess_npo + inprocess_po + processed_npo + processed_po
            }
            
            output3 = {
                "current_liability_po": current_po,
                "current_liability_npo": current_npo,
                "total_current_liability": current_po + current_npo,
                
                "overdue_po": overdue_po,
                "overdue_npo": overdue_npo,
                "total_overdue": overdue_po + overdue_npo,
                
                "total_po": current_po + overdue_po,
                "total_npo": current_npo + overdue_npo,
                "total_liability": current_po + current_npo + overdue_po + overdue_npo,
                
                "total_processed_amount": processed_amount["total"]
            }
                
            records = {
                "output1": output1,
                "output2": output2,
                "output3": output3,
                "output4": acc_output
            }
            
    # except:
    #     return {
    #         'statuscode': 500,
    #         'body': json.dumps("Internal Error!")
    #     }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

# event = {'body-json': {'condn': [{'field': 'company_code', 'operator': '=', 'value': '1000'}]}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjE4YmE4OTc5LTY0MDUtNGM2YS1hZDNkLTI0NjE2MWQ2ZmI1NyIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg2NjQ2NzQ0LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg2NjUwMzQ0LCJpYXQiOjE2ODY2NDY3NDQsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.DppCY5mPR9B2WTmpk2fnt2IBh_5_ftZpqxu--FNSBJCv2oJZMAjB-U3DTbZH_31EzQQGR-Ua1IXYFvpWZPyolpO5I5Zd9mRhMj-MSKgjkWw59-iV9IVF3lGxjUF2mToeqMSt98S-xMEko6auvO48RuGa0nLXEa3LfqkQ6y58HjSrukjy7nuUfiWrjYivAB1aoRYrX_0yfL594RsHskUQqEU4FVAehq6d9pqnA8Qn9zwweYjM8fBd6RC2W999n_W_YO0_V_e6NCJAWK9rmLOLFvmZfp-xAnLtYeNQndY4NGO-GxcUSFxHyDHMFyyNq3FXO2xRMhAp7-MjivO9GGbImA', 'content-type': 'application/json', 'Host': 'wzwczc4rhd.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6488309a-05c37f41370321ea5dae4edd', 'X-Forwarded-For': '49.207.51.54', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'wzwczc4rhd', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'einvoice-v1', 'source-ip': '49.207.51.54', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'be5dd911-f0c1-4392-a26d-161e97d62b61', 'resource-id': 'jd11id', 'resource-path': '/key-process-analytics-report'}}

def getLiabilityReportDetails(event, context):
    global dbScehma 
    dbScehma = '"DBADMIN"'
    
    mydb = hdbcliConnect()

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            val_list = []
            pos = 0
            condn = ""
    
            if "condn" in event["body-json"]:
                for row in event["body-json"]["condn"]:
                    condn = condn + " and "
                    
                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                        
                    elif str(row["operator"]) == "between":
                        val_list.append(row["value"])
                        val_list.append(row["value2"])
                        
                    else:
                        val_list.append(row["value"])
                        
                    if row["field"] == "company_code" or row["field"] == "amount":
                        if str(row["operator"]) == "between":
                            condn = condn + "b." + str(row["field"]) + " between ? and ? "
                        else:
                            condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "? "
                    else:
                        condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "? "
                        
            sqlQuery = "select a.vendor_no, a.vendor_name, b.currency " \
            	"from vendor_master a " \
            	"inner join invoice_header b " \
            	"on a.vendor_no = b.supplier_id " \
            	"where b.in_status != 'deleted' and b.document_type = 'RE' and (DAYS_BETWEEN(  CURRENT_DATE , cast(b.due_date as date)  ) < 0)  and b.in_status != 'tosap' " + condn + \
                "group by a.vendor_no, b.currency , a.vendor_name " \
                "order by a.vendor_no"
                
            mycursor.execute(sqlQuery, tuple(val_list))
            overdue_company = mycursor.fetchall()
            
            sqlQuery = "select a.vendor_no, a.vendor_name, count( b.invoice_no ) as total_no_of_invoice, b.invoice_date, b.due_date, b.company_code, b.amount, b.currency, " \
            	"sum(case when ( (DAYS_BETWEEN( cast(b.due_date as date), CURRENT_DATE ) >= 0) and b.in_status != 'tosap' )then cast(b.amount as float) else 0 end) as due_amount, " \
                "sum(case when ( (DAYS_BETWEEN( cast(b.due_date as date), CURRENT_DATE ) < 0) and b.in_status != 'tosap' )then cast(b.amount as float) else 0 end) as overdue_amount, " \
                "sum(case when ( b.in_status = 'tosap' and b.payment_status = 'unpaid' )then cast(b.amount as float) else 0 end) as processed_amount, " \
                "sum(case when ( b.in_status = 'tosap' and b.payment_status = 'paid' )then b.amount else 0 end) as paid_amount, " \
                "sum(case when ( (DAYS_BETWEEN( cast(b.due_date as date), CURRENT_DATE ) >= 0) and b.in_status != 'tosap' )then 1 else 0 end) as due_invoice, " \
                "sum(case when ( (DAYS_BETWEEN( cast(b.due_date as date), CURRENT_DATE ) < 0) and b.in_status != 'tosap' )then 1 else 0 end) as overdue_invoice, " \
                "sum(case when ( b.in_status = 'tosap' and b.payment_status = 'unpaid' )then 1 else 0 end) as processed_invoice, " \
                "sum(case when ( b.in_status = 'tosap' and b.payment_status = 'paid' )then 1 else 0 end) as paid_invoice " \
            	"from vendor_master a " \
            	"inner join invoice_header b " \
            	"on a.vendor_no = b.supplier_id " \
            	"where b.in_status != 'deleted' and b.document_type = 'RE' " + condn + \
                "group by a.vendor_no, b.currency ,a.vendor_name , b.invoice_date , B.DUE_DATE ,B.COMPANY_CODE ,B.AMOUNT " \
                "order by due_amount desc"
            
#             
                
            mycursor.execute(sqlQuery, tuple(val_list))
            
            for row in mycursor :
                overdue_flag = 'n'
                for data in overdue_company:
                    if row["vendor_no"] == data["vendor_no"] and row["currency"] == data["currency"]:
                        overdue_flag = 'y'
                        break
                
                data = {
                    "company_code": row["company_code"],
                    "vendor_no": row["vendor_no"],
                    "vendor_name": str(row["vendor_name"]) + " (" + row["currency"] + ")",
                    "total_no_of_invoice": row["due_invoice"] + row["overdue_invoice"] + row["processed_invoice"] + row["paid_invoice"],
                    "total_amount": float(row["due_amount"]) + float(row["overdue_amount"]) + float(row["processed_amount"]) + float(row["paid_amount"]),
                    "currency": row["currency"],
                    "total_amt_paid": row["processed_amount"],
                    "total_no_of_invoice_paid": row["processed_invoice"],
                    "total_due_amount":row["due_amount"] ,
                    "total_no_of_invoice_due": row["due_invoice"],
                    "total_over_due_amount": row["overdue_amount"],
                    "total_no_of_invoice_due_crossed": row["overdue_invoice"],
                    "total_paid_amount": row["paid_amount"],
                    "total_no_of_paid_invoice": row["paid_invoice"],
                    "overdue_flag": overdue_flag
                }
                records.append(data) 
                    
    # except:
    #     return {
    #         'statuscode': 500,
    #         'body': json.dumps("Internal Error!")
    #     }
                    
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

# event = {'body-json': {'condn': [{'field': 'company_code', 'operator': '=', 'value': '1000'}]}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjE4YmE4OTc5LTY0MDUtNGM2YS1hZDNkLTI0NjE2MWQ2ZmI1NyIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg2NjQ2NzQ0LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg2NjUwMzQ0LCJpYXQiOjE2ODY2NDY3NDQsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.DppCY5mPR9B2WTmpk2fnt2IBh_5_ftZpqxu--FNSBJCv2oJZMAjB-U3DTbZH_31EzQQGR-Ua1IXYFvpWZPyolpO5I5Zd9mRhMj-MSKgjkWw59-iV9IVF3lGxjUF2mToeqMSt98S-xMEko6auvO48RuGa0nLXEa3LfqkQ6y58HjSrukjy7nuUfiWrjYivAB1aoRYrX_0yfL594RsHskUQqEU4FVAehq6d9pqnA8Qn9zwweYjM8fBd6RC2W999n_W_YO0_V_e6NCJAWK9rmLOLFvmZfp-xAnLtYeNQndY4NGO-GxcUSFxHyDHMFyyNq3FXO2xRMhAp7-MjivO9GGbImA', 'content-type': 'application/json', 'Host': 'wzwczc4rhd.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6488308f-350996bc7adb4cbb3a457085', 'X-Forwarded-For': '49.207.51.54', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'wzwczc4rhd', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'einvoice-v1', 'source-ip': '49.207.51.54', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': '7d0c38aa-5518-494d-9839-2d64978ac477', 'resource-id': 'di3ixl', 'resource-path': '/liability-report'}}



def getLiabilityGraphBasedOnAmount(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    records = {}
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            print(event)
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if "fiscal_year" in event["params"]["querystring"] and "fiscal_year" != "":
                year = event["params"]["querystring"]["fiscal_year"]
                
            else:
                year = datetime.now().year
            
            if "company_code" in event["params"]["querystring"] and "company_code" != "":
                company_code = event["params"]["querystring"]["company_code"]
            
            sqlQuery = "SELECT sum(case when in_status = 'tosap' then amount else 0 end) as processed_amount, " \
                "sum(case when in_status != 'tosap' and (DAYS_BETWEEN( baseline_date , CURRENT_DATE ) < 0) then amount else 0 end) as op_overdue_amount, " \
                "sum(case when in_status != 'tosap' and (DAYS_BETWEEN( baseline_date, CURRENT_DATE ) >= 0) then amount else 0 end) as op_due_amount, " \
                "sum(case when (DAYS_BETWEEN( baseline_date , CURRENT_DATE ) < 0) then amount else 0 end) as overdue_amount, " \
                "sum(case when (DAYS_BETWEEN( baseline_date, CURRENT_DATE ) >= 0) then amount else 0 end) as due_amount " \
                "FROM invoice_header " \
                "where in_status != 'deleted' and document_type != 'RE' and year(invoice_date) = ? and company_code = ?"
            
            values = (year, company_code)
            mycursor.execute(sqlQuery, values)
            data = mycursor.fetchone()
            
            output1 = {}
            output2 = {}
            
            if data:
                if data["processed_amount"] == None or data["processed_amount"] == "":
                    processed_amount = 0
                else:
                    processed_amount = data["processed_amount"]    
                    
                if data["op_overdue_amount"] == None or data["op_overdue_amount"] == "":
                    op_overdue_amount = 0
                else:
                    op_overdue_amount = data["op_overdue_amount"]
                    
                if data["op_due_amount"] == None or data["op_due_amount"] == "":
                    op_due_amount = 0
                else:
                    op_due_amount = data["op_due_amount"]
                    
                if data["overdue_amount"] == None or data["overdue_amount"] =="":
                    overdue_amount = 0
                else:
                    overdue_amount = data["overdue_amount"]
                
                if data["due_amount"] == None or data["due_amount"] == "":
                    due_amount = 0
                else:
                    due_amount = data["due_amount"]
                
                output1 = {
                    "processed_amount": processed_amount,
                    "overdue_amount": op_overdue_amount,
                    "due_amount": op_due_amount
                }
            
                output2 = {
                    "overdue_amount": overdue_amount,
                    "due_amount": due_amount
            }
            
            sqlQuery =  "SELECT b.vendor_no, b.vendor_name, sum(a.amount) as total_amount,"\
            	"sum(case when a.in_status = 'tosap' then a.amount else 0 end) as processed_amount," \
            	"sum(case when  (DAYS_BETWEEN( a.baseline_date, CURRENT_DATE ) < 0) then a.amount else 0 end) as overdue_amount,"  \
                "sum(case when (DAYS_BETWEEN( a.baseline_date, CURRENT_DATE ) >= 0) then a.amount else 0 end) as due_amount "\
                "FROM invoice_header a "\
                "inner join vendor_master b "\
                "on a.supplier_id = b.vendor_no "\
                "where a.in_status != 'deleted' and document_type != 'RE' and year(a.invoice_date) = ? and company_code = ? "\
                "group by b.vendor_no ,b.vendor_name "\
                "order by due_amount desc, overdue_amount desc "\
                "limit 5 "
            
            values = (year, company_code)
            mycursor.execute(sqlQuery, values)
            data1 = mycursor.fetchall()
            
            output3 = []
            for row in data1:
                value = {
                    "vendor_no": row["vendor_no"],
                    "vendor_name": row["vendor_name"],
                    "total_amount": row["total_amount"],
                    "processed_amount": row["processed_amount"],
                    "overdue_amount": row["overdue_amount"],
                    "due_amount": row["due_amount"]
                }
                output3.append(value)
            
            records = {
                "TotalAccountsPayable": output1,
                "LiabilityBasedOnAmount": output2,
                "VendorLiabilityReportforCompanyCode": output3
            }
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

def overview(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    
    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # )

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    records = {}
    output4 = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
    # Invoice Overview

            sqlQuery = "SELECT count(*) as total, sum(case when in_status = 'draft' then 1 else 0 end) as draft," \
                       " sum(case when in_status = 'draft' then amount else 0 end) as draft_amount," \
                       " sum(case when in_status = 'inapproval' then 1 else 0 end) as inapproval," \
                       " sum(case when in_status = 'inapproval' then amount else 0 end) as inapproval_amount," \
                       " sum(case when in_status = 'tosap' then 1 else 0 end) as tosap," \
                       " sum(case when in_status = 'tosap' then amount else 0 end) as tosap_amount," \
                       " sum(case when in_status = 'new' then 1 else 0 end) as new," \
                       " sum(case when in_status = 'new' then amount else 0 end) as new_amount," \
                       " sum(case when in_status = 'rejected' then amount else 0 end) as rejected_amount," \
                       " sum(case when in_status = 'rejected' then 1 else 0 end) as rejected" \
                       " FROM invoice_header" \
                       " WHERE in_status != 'deleted' and document_type = 'RE'"

            mycursor.execute(sqlQuery)
            data = mycursor.fetchone()

            output1 = {
                "draft": int(data['draft']),
                "draft_amount": float(data['draft_amount']),
                "draft_per": float((data['draft'].real / data['total'].real) * 100),
                "rejected": int(data['rejected']),
                "rejected_amount": float(data['rejected_amount']),
                "rejected_per": float((data['rejected'].real / data['total'].real) * 100),
                "new": int(data['new']),
                "new_amount": float(data['new_amount']),
                "new_per": float((data['new'].real / data['total'].real) * 100),
                "inapproval": int(data['inapproval']),
                "inapproval_amount": float(data['inapproval_amount']),
                "inapproval_per": float((data['inapproval'].real / data['total'].real) * 100),
                "processed": int(data['tosap']),
                "processed_amount": float(data['tosap_amount'].real),
                "processed_per": float((data['tosap'].real / data['total'].real) * 100)
            }

    # Accounts Payable Overview

            mycursor.execute(
                "SELECT invoice_no, in_status, amount, baseline_date "
                "FROM invoice_header "
                "WHERE in_status != 'deleted' and document_type = 'RE' and MONTH(entry_date) = MONTH(CURDATE())")
            invoices2 = mycursor.fetchall()

            processed_amt = 0
            due_amount = 0
            over_due_amount = 0

            if invoices2:

                for row in invoices2:
                    today = date.today()

                    if row["in_status"] == 'tosap':
                        processed_amt = processed_amt + row["amount"]

                    elif row["baseline_date"] != None and type(row["baseline_date"]) is not str:

                        if today <= row["baseline_date"]:
                            due_amount = due_amount + row["amount"]

                        elif today > row["baseline_date"]:
                            over_due_amount = over_due_amount + row["amount"]

            output2 = {
                "processed_amt": processed_amt,
                "due_amount": due_amount,
                "over_due_amount": over_due_amount
            }

    # Productivity Overview

            # sqlQuery = "select * from approval_history where approved_date > curdate() - INTERVAL 6 MONTH"
            mycursor.execute("select * from approval_history where approved_date > curdate() - INTERVAL 6 MONTH")
            alldata = mycursor.fetchall()

            groupid = []
            memberid = []
            import dateutil
            for row in alldata:
                if row["isgroup"] == 'y':
                    groupid.append(row["approver_id"])
                elif row["isgroup"] == 'n':
                    memberid.append(row["approver_id"])

            groupid = set(groupid)
            groupid = list(groupid)

            if groupid :
                format_string_grp = ','.join(['%s'] * len(groupid))
                sqlQuery = 'select group_id, name from "GROUP" where group_id in ({})'.format(format_string_grp)
                mycursor.execute(sqlQuery, tuple(groupid))
                group = mycursor.fetchall()

            output3 = []
            if groupid:
                m = datetime.datetime.now()
                m1 = datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=1)
                m2 = datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=2)
                m3 = datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=3)
                m4 = datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=4)
                m5 = datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=5)
                m6 = datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=6)

                for each in groupid:

                    for row in group:
                        if int(each) == int(row["group_id"]):
                            grp_name = row["name"]
                            break

                    cm = cm1 = cm2 = cm3 = cm4 = cm5 = 0

                    for row in alldata:
                        if row['approver_id'] == each:
                            if m.month == row['approved_date'].month:
                                cm += 1
                            elif m1.month == row['approved_date'].month:
                                cm1 += 1
                            elif m2.month == row['approved_date'].month:
                                cm2 += 1
                            elif m3.month == row['approved_date'].month:
                                cm3 += 1
                            elif m4.month == row['approved_date'].month:
                                cm4 += 1
                            elif m5.month == row['approved_date'].month:
                                cm5 += 1

                    resu = {
                        "groupid": each,
                        "name": grp_name,
                        "invoices": [cm5, cm4, cm3, cm2, cm1, cm],
                        "months" : [m5.strftime("%B"), m4.strftime("%B"), m3.strftime("%B"), m2.strftime("%B"), m1.strftime("%B"), m.strftime("%B")]
                    }
                    output3.append(resu)

            memberid = set(memberid)
            memberid = list(memberid)

            if memberid :
                format_string_mem = ','.join(['%s'] * len(memberid))
                sqlQuery = "select member_id, fs_name, ls_name from member where member_id in ({})".format(format_string_mem)
                mycursor.execute(sqlQuery, tuple(memberid))
                memberdata = mycursor.fetchall()

            if memberid:
                for each in memberid:

                    for row in memberdata:
                        if each == row["member_id"]:
                            member_name = row["fs_name"] + " " + row["ls_name"]
                            break

                    cm = cm1 = cm2 = cm3 = cm4 = cm5 = cm6 = 0

                    for row in alldata:
                        if row['approver_id'] == each:
                            if m.month == row['approved_date'].month:
                                cm += 1
                            elif m1.month == row['approved_date'].month:
                                cm1 += 1
                            elif m2.month == row['approved_date'].month:
                                cm2 += 1
                            elif m3.month == row['approved_date'].month:
                                cm3 += 1
                            elif m4.month == row['approved_date'].month:
                                cm4 += 1
                            elif m5.month == row['approved_date'].month:
                                cm5 += 1
                            elif m6.month == row['approved_date'].month:
                                cm6 += 1

                    resu = {
                        "member_id": each,
                        "name": member_name,
                        "invoices": [cm5, cm4, cm3, cm2, cm1, cm],
                        "months" : [m5.strftime("%B"), m4.strftime("%B"), m3.strftime("%B"),
                                    m2.strftime("%B"), m1.strftime("%B"), m.strftime("%B")]
                    }
                    output3.append(resu)

    # # User Productivity

    #         if "user_id" in event["params"]["querystring"]:

    #             values = (event["params"]["querystring"]["user_id"],)
    #             mycursor.execute("select member_id from einvoice_db_portal.member where email = %s", values)
    #             memberid = mycursor.fetchone()

    #             # no_day = monthrange(2020, 9)

    #             sqlQuery = "select count(member_id) as approved, approved_date " \
    #                       "from einvoice_db_portal.approval_history " \
    #                       "where member_id = %s and approved_date > curdate() - interval 1 month " \
    #                       "group by week(approved_date)"

    #             mycursor.execute(sqlQuery, memberid["member_id"])
    #             raw_data = mycursor.fetchall()
    #             # print(raw_data)
                
    #             # today = date.today()
    #             # no_day = monthrange(int(today.strftime("%Y")), int(today.strftime("%m")))

    #             no_of_in = []
    #             temp = []
    #             week1 = [1,2,3,4,5,6,7]
    #             week2 = [8,9,10,11,12,13,14]
    #             week3 = [15,16,17,18,19,20,21]
    #             week4 = [22,23,24,25,26,27,28,29,30,31]
    #             # week5 = [29,30,31]
                
    #             w1 = 'n'
    #             w2 = 'n'
    #             w3 = 'n'
    #             w4 = 'n'
    #             # w5 = 'n'
                
    #             # for i in range(no_day[0], no_day[1] + 1):
    #             # for i in range(5):
    #                 # print(i)
    #             for row in raw_data:
    #                 if int(str(row["approved_date"])[8:10]) in week1:
    #                     data = {
    #                         "invoice_approved": row["approved"],
    #                         "week": "Week 1"
    #                     }
    #                     temp.append(data)
    #                     no_of_in.append(row["approved"])
    #                     w1 = 'y'
                        
    #                 elif int(str(row["approved_date"])[8:10]) in week2:
    #                     data = {
    #                         "invoice_approved": row["approved"],
    #                         "week": "Week 2"
    #                     }
    #                     temp.append(data)
    #                     no_of_in.append(row["approved"])
    #                     w2 = 'y'
                        
    #                 elif int(str(row["approved_date"])[8:10]) in week3:
    #                     data = {
    #                         "invoice_approved": row["approved"],
    #                         "week": "Week 3"
    #                     }
    #                     temp.append(data)
    #                     no_of_in.append(row["approved"])
    #                     w3 = 'y'
                        
    #                 elif int(str(row["approved_date"])[8:10]) in week4:
    #                     data = {
    #                     "invoice_approved": row["approved"],
    #                         "week": "Week 4"
    #                     }
    #                     temp.append(data)
    #                     no_of_in.append(row["approved"])
    #                     w4 = 'y'
                        
    #                 # elif int(str(row["approved_date"])[8:10]) in week5:
    #                 #     data = {
    #                 #         "invoice_approved": row["approved"],
    #                 #         "week": "Week 5"
    #                 #     }
    #                 #     temp.append(data)
    #                 #     no_of_in.append(row["approved"])
    #                 #     w5 = 'y'
                        
    #             if w1 == "n":
    #                 data = {
    #                     "invoice_approved": 0,
    #                     "week": "Week 1"
    #                 }
    #                 temp.append(data)
    #             if w2 == "n":
    #                 data = {
    #                     "invoice_approved": 0,
    #                     "week": "Week 2"
    #                 }
    #                 temp.append(data)
    #             if w3 == "n":
    #                 data = {
    #                     "invoice_approved": 0,
    #                     "week": "Week 3"
    #                 }
    #                 temp.append(data)
    #             if w4 == "n":
    #                 data = {
    #                     "invoice_approved": 0,
    #                     "week": "Week 4"
    #                 }
    #                 temp.append(data)
    #             # if w5 == "n":
    #             #     data = {
    #             #         "invoice_approved": 0,
    #             #         "week": "Week 5"
    #             #     }
    #             #     temp.append(data)
                            
    #             # for i in range(no_day[0], no_day[1] + 1):
    #             #     # print(i)
    #             #     for row in raw_data:
    #             #         if int(i) == int(str(row["approved_date"])[8:10]):
    #             #             data = {
    #             #                 "invoice_approved": row["approved"],
    #             #                 "day": i,
    #             #                 "approved_date": row["approved_date"].strftime("%d")
    #             #             }
    #             #             temp.append(data)
    #             #             no_of_in.append(row["approved"])
    #             #         else:
    #             #             data = {
    #             #                 "invoice_approved": 0,
    #             #                 "day": i,
    #             #                 "approved_date": "0000-00-00"
    #             #             }
    #             #             temp.append(data)
    #             #             no_of_in.append(0)
                            
    #             output4["details"] = sorted(temp, key = lambda i: i['week'])
    #             output4['records'] = no_of_in

    # # Top 5 Vendor Based on Amount

    #         output5 = []

    #         quarter1 = [4,5,6]
    #         quarter2 = [7,8,9]
    #         quarter3 = [10,11,12]
    #         quarter4 = [1,2,3]

    #     #Considering all invoices except rejected

    #         mycursor.execute("select supplier_id, amount , invoice_date from einvoice_db_portal.invoice_header "
    #                          "where invoice_date > curdate() - interval 12 month")

    #         vendors_data = mycursor.fetchall()

    #         if vendors_data:

    #             vendors = []
    #             for each in vendors_data:
    #                 # if each['supplier_id']:
    #                 vendors.append(each['supplier_id'])

    #             vendors = set(vendors)
    #             vendors = list(vendors)


    #             vendors_quat = {}
    #             vendors_all = {}
    #             for each in vendors:
    #                 vendors_quat[each] = {'q1' : 0, 'q2' : 0, 'q3' : 0, 'q4' : 0}
    #                 vendors_all[each] = 0

    #             for row in vendors_data:
    #                 vendors_all[row['supplier_id']] += float(row['amount'])
    #                 if row['invoice_date'].month in quarter1:
    #                     vendors_quat[row['supplier_id']]['q1'] += float(row['amount'])
    #                 elif row['invoice_date'].month in quarter2:
    #                     vendors_quat[row['supplier_id']]['q2'] += float(row['amount'])
    #                 elif row['invoice_date'].month in quarter3:
    #                     vendors_quat[row['supplier_id']]['q3'] += float(row['amount'])
    #                 elif row['invoice_date'].month in quarter4:
    #                     vendors_quat[row['supplier_id']]['q4'] += float(row['amount'])

    #             print(vendors_quat)
    #             print(vendors_all)
    #             del vendors_all[None]
    #             # vendors_all = sorted(vendors_all, key = lambda i: i[0])
    #             print(vendors_all)


                    # data121 = {
                    #     "vendor_no": invoices5[each]['supplier_id'],
                    #     "totalin4": int(invoices5[each]['amount']),
                    #     "vendor_name": "jgfj",
                    #     "cur_month": int((vdata['current_month'])),
                    #     "pre1mon": int(vdata['pre_1']),
                    #     "pre2mon": int(vdata['pre_2']),
                    #     "pre3mon": int(vdata['pre_3']),
                    # }
                    # output5.append(data121)
                # print("++++++++++++++++++++",output5)

            # for row in invoices5:

            #     output5.append(data)

            records = {
              "output1": output1,
              "output2": output2,
              "output3": output3
            #   "output4": output4,
            #   "output5": output5
            }

    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }


# event = {
#     "params" : {
#         "querystring"  : {
#             "user_id" : "ramesh.kumar@gmail.com"
#         }
#     }
# }

# context = ""

# print(lambda_handler(event, context))

def getAccountsPayableOverview(event, context):
    
    trace_off = ''
    global dbScehma 
    dbScehma = '"DBADMIN"'

    mydb = hdbcliConnect()

    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()

            on = convertValuesTodict(mycursor.description , on)	
            on = on[0]
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
	           # atoken =  event['params']['header']['Authorization']
	           # print(atoken)
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     trace_off = 'off'
            #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken})
            #     if json.loads(a.text)['body'] == 'on':
	           #     patch_all()
	           #     print(event)  
            
            # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            # if on == 1:
            #     chk = enable_xray(event)
            #     if chk['Enable'] == True:
            #         patch_all()

            mycursor.execute("SELECT invoice_no, in_status, amount, baseline_date "
                "FROM invoice_header "
                "WHERE in_status != 'deleted' and document_type = 'RE' and MONTH(entry_date) = MONTH(CURDATE())")
            invoices2 = mycursor.fetchall()

            invoices2 = convertValuesTodict(mycursor.description , invoices2)

            processed_amt = 0
            due_amount = 0
            over_due_amount = 0

            if invoices2:

                for row in invoices2:
                    today = date.today()

                    if row["in_status"] == 'tosap':
                        processed_amt = processed_amt + float(row["amount"])

                    elif row["baseline_date"] != None and type(row["baseline_date"]) is not str:

                        if today <= row["baseline_date"]:
                            due_amount = due_amount + row["amount"]

                        elif today > row["baseline_date"]:
                            over_due_amount = over_due_amount + row["amount"]

            records = {
                "processed_amt": processed_amt,
                "due_amount": due_amount,
                "over_due_amount": over_due_amount
            }
            
    # except:
    #     return {
    #         'statuscode': 500,
    #         'body': json.dumps("Internal Fail")
    #     }
            
    finally:
        mydb.close()
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , 'switch':'off'})
            

    return {
        'statuscode': 200,
        'body': records
    }


def getInvoiceOverview(event, context):
    trace_off = ''
    global dbScehma 
    dbScehma = '"DBADMIN"'
    
    mydb = hdbcliConnect()

    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            on = convertValuesTodict(mycursor.description , on)	
            on = on[0]
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
            #     atoken =  event['params']['header']['Authorization']
            #     print(atoken)
                
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     trace_off = 'off'
            #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
            #     if json.loads(a.text)['body'] == 'on':
            #         patch_all()
            #         print(event)
            
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            # on = mycursor.fetchone()
            # if on['value1'] == 'on':
            #     chk = enable_xray(event)
            #     if chk['Enable'] == True:
            #         # print(chk['email'])
            #         patch_all()
            #         print(event,chk['email'])

            
            sqlQuery = "select count(*) as total, sum(case when in_status = 'draft' then 1 else 0 end) as draft," \
                       " sum(case when in_status = 'draft' then cast(amount as float) else 0 end) as draft_amount," \
                       " sum(case when in_status = 'inapproval' then 1 else 0 end) as inapproval," \
                       " sum(case when in_status = 'inapproval' then cast(amount as float) else 0 end) as inapproval_amount," \
                       " sum(case when in_status = 'tosap' then 1 else 0 end) as tosap," \
                       " sum(case when in_status = 'tosap' then cast(amount as float) else 0 end) as tosap_amount," \
                       " sum(case when in_status = 'tosap' and payment_status = 'unpaid' then 1 else 0 end) as tosap_ps," \
                       " sum(case when in_status = 'tosap' and payment_status = 'unpaid' then cast(amount as float) else 0 end) as tosap_amount_ps," \
                       " sum(case when in_status = 'new' then 1 else 0 end) as new," \
                       " sum(case when in_status = 'new' then cast(amount as float) else 0 end) as new_amount," \
                       " sum(case when in_status = 'rejected' then cast(amount as float) else 0 end) as rejected_amount," \
                       " sum(case when in_status = 'rejected' then 1 else 0 end) as rejected," \
                       " sum(case when in_status = 'tosap' and payment_status = 'paid' then cast(amount as float) else 0 end) as paid_amount," \
                       " sum(case when in_status = 'tosap' and payment_status = 'paid' then 1 else 0 end) as paid" \
                       " FROM invoice_header" \
                       " where document_type = 'RE'"

            mycursor.execute(sqlQuery)
            data = mycursor.fetchone()
            
            if data and data['total']:  
                
                if not data['draft']:
                    data['draft'] = 0
                    data['draft_amount'] = 0
                    
                if not data['rejected']:
                    data['rejected'] = 0
                    data['rejected_amount'] = 0
                    
                if not data['new']:
                    data['new'] = 0
                    data['new_amount'] = 0
                    
                if not data['inapproval']:
                    data['inapproval'] = 0
                    data['inapproval_amount']
                    
                if not data['tosap']:
                    data['tosap'] = 0
                    data['tosap_amount'] = 0
                    
                    
                    
                records = {
                    "draft": int(data['draft']),
                    "draft_amount": float(data['draft_amount']),
                    "draft_per": float((data['draft'].real / data['total'].real) * 100),
                    "rejected": int(data['rejected']),
                    "rejected_amount": float(data['rejected_amount']),
                    "rejected_per": float((data['rejected'].real / data['total'].real) * 100),
                    "new": int(data['new']),
                    "new_amount": float(data['new_amount']),
                    "new_per": float((data['new'].real / data['total'].real) * 100),
                    "inapproval": int(data['inapproval']),
                    "inapproval_amount": float(data['inapproval_amount']),
                    "inapproval_per": float((data['inapproval'].real / data['total'].real) * 100),
                    "processed": int(data['tosap']),
                    "processed_amount": float(data['tosap_amount'].real),
                    "processed_per": float((data['tosap'].real / data['total'].real) * 100),
                    "paid": int(data['paid']),
                    "paid_amount": float(data['paid_amount'].real),
                    "paid_per": float((data['paid'].real/data['total'].real) * 100),
                    "processed_ps": int(data['tosap_ps']),
                    "processed_amount_ps": float(data['tosap_amount_ps'].real)
                    # "processed_per_ps": float((data['tosap_ps'].real / data['total'].real) * 100)
                }
           
            else:
                records = {
                    "draft": 0,
                    "draft_amount": 0,
                    "draft_per": 0,
                    "rejected": 0,
                    "rejected_amount": 0,
                    "rejected_per": 0,
                    "new": 0,
                    "new_amount": 0,
                    "new_per": 0,
                    "inapproval": 0,
                    "inapproval_amount": 0,
                    "inapproval_per": 0,
                    "processed": 0,
                    "processed_amount": 0,
                    "processed_per": 0,
                    "paid": 0,
                    "paid_amount": 0,
                    "paid_per": 0,
                    "processed_ps": 0,
                    "processed_amount_ps": 0
                }
                
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Fail")
        }

    finally:
        mydb.close()
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , 'switch':'off'})
            

    return {
        'statuscode': 200,
        'body': records,
    }



def getProductivityOverview(event, context):
    trace_off = ''
    global dbScehma 
    dbScehma = '"DBADMIN"'
    
    mydb = hdbcliConnect()

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
                
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     trace_off = 'off'
            #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
            #     if json.loads(a.text)['body'] == 'on':
            #         patch_all()
            #         print(event) 
            
            mycursor.execute("SELECT * FROM approval_history WHERE approved_date > ADD_DAYS(CURRENT_DATE, -180) ")
            alldata = mycursor.fetchall()
            alldata = convertValuesTodict(mycursor.description, alldata)

            groupid = []
            memberid = []
            import dateutil
            for row in alldata:
                if row["isgroup"] == 'y':
                    groupid.append(row["approver_id"])
                elif row["isgroup"] == 'n':
                    memberid.append(row["approver_id"])

            groupid = set(groupid)
            groupid = list(groupid)
            
            print(groupid)

            if groupid :
                format_string_grp = ','.join(['?'] * len(groupid))
                sqlQuery = 'select group_id, name from ' + dbScehma + '."GROUP" where group_id in ({})'.format(format_string_grp)
                mycursor.execute(sqlQuery, tuple(groupid))
                group = mycursor.fetchall()

            records = []
            if groupid:
                m = datetime.now()
                m1 = datetime.now() - dateutil.relativedelta.relativedelta(months=1)
                m2 = datetime.now() - dateutil.relativedelta.relativedelta(months=2)
                m3 = datetime.now() - dateutil.relativedelta.relativedelta(months=3)
                m4 = datetime.now() - dateutil.relativedelta.relativedelta(months=4)
                m5 = datetime.now() - dateutil.relativedelta.relativedelta(months=5)
                m6 = datetime.now() - dateutil.relativedelta.relativedelta(months=6)

                for each in groupid:

                    for row in group:
                        if int(each) == int(row["group_id"]):
                            grp_name = row["name"]
                            break

                    cm = cm1 = cm2 = cm3 = cm4 = cm5 = 0

                    for row in alldata:
                        if row['approver_id'] == each:
                            # month = datetime.strptime(row['approved_date'], '%Y-%m-%d %H:%M:%S')
                            # row['approved_date'] = month
                            if m.month == row['approved_date'].month:
                                cm += 1
                            elif m1.month == row['approved_date'].month:
                                cm1 += 1
                            elif m2.month == row['approved_date'].month:
                                cm2 += 1
                            elif m3.month == row['approved_date'].month:
                                cm3 += 1
                            elif m4.month == row['approved_date'].month:
                                cm4 += 1
                            elif m5.month == row['approved_date'].month:
                                cm5 += 1

                    resu = {
                        "groupid": each,
                        "name": grp_name,
                        "invoices": [cm5, cm4, cm3, cm2, cm1, cm],
                        "months" : [m5.strftime("%B"), m4.strftime("%B"), m3.strftime("%B"),
                                    m2.strftime("%B"), m1.strftime("%B"), m.strftime("%B")]
                    }
                    records.append(resu)

                memberid = set(memberid)
                memberid = list(memberid)
    
                if memberid :
                    format_string_mem = ','.join(['?'] * len(memberid))
                    sqlQuery = "select member_id, fs_name, ls_name from member " \
                               "where member_id in ({})".format(format_string_mem)
                    mycursor.execute(sqlQuery, tuple(memberid))
                    memberdata = mycursor.fetchall()
                    
                member_name = None
                if memberid:
                    for each in memberid:
    
                        for row in memberdata:
                            if each == row["member_id"]:
                                member_name = row["fs_name"] + " " + row["ls_name"]
                                break
    
                        cm = cm1 = cm2 = cm3 = cm4 = cm5 = cm6 = 0
    
                        for row in alldata:
                            if row['approver_id'] == each:
                                # month = datetime.strptime(row['approved_date'], '%Y-%m-%d %H:%M:%S')
                                # row['approved_date'] = month
                                if m.month == row['approved_date'].month:
                                    cm += 1
                                elif m1.month == row['approved_date'].month:
                                    cm1 += 1
                                elif m2.month == row['approved_date'].month:
                                    cm2 += 1
                                elif m3.month == row['approved_date'].month:
                                    cm3 += 1
                                elif m4.month == row['approved_date'].month:
                                    cm4 += 1
                                elif m5.month == row['approved_date'].month:
                                    cm5 += 1
                                elif m6.month == row['approved_date'].month:
                                    cm6 += 1
    
                        resu = {
                            "member_id": each,
                            "name": member_name,
                            "invoices": [cm5, cm4, cm3, cm2, cm1, cm],
                            "months" : [m5.strftime("%B"), m4.strftime("%B"), m3.strftime("%B"), m2.strftime("%B"), m1.strftime("%B"), m.strftime("%B")]
                        }
                        records.append(resu)
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Fail")
        }

    finally:
        mydb.close()
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , 'switch':'off'})
            

    return {
        'statuscode': 200,
        'body': records
    }



def getUserProductivityOverview(event, context):
    trace_off = ''
    
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
            #     atoken =  event['params']['header']['Authorization']
            #     print(atoken)
                
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     trace_off = 'off'
            #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
            #     if json.loads(a.text)['body'] == 'on':
            #         patch_all()
            #         print(event)  
            # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            # if on == 1:
            #     chk = enable_xray(event)
            #     if chk['Enable'] == True:
            #         patch_all()

            if "userid" in event["params"]["querystring"]:

                values = (event["params"]["querystring"]["userid"],)
                mycursor.execute("select member_id from member where email = ?", values)
                memberid = mycursor.fetchone()

                sqlQuery = "select count(member_id) as approved, approved_date " \
                           "from approval_history " \
                           "where member_id = ? and approved_date > add_days(current_date, -30) " \
                           "group by (approved_date)"

                mycursor.execute(sqlQuery, memberid["member_id"])
                raw_data = mycursor.fetchall()

                no_of_in = []
                temp = []
                week1 = [1,2,3,4,5,6,7]
                week2 = [8,9,10,11,12,13,14]
                week3 = [15,16,17,18,19,20,21]
                week4 = [22,23,24,25,26,27,28,29,30,31]
                
                w1 = 'n'
                w2 = 'n'
                w3 = 'n'
                w4 = 'n'
                
                for row in raw_data:
                    if int(str(row["approved_date"])[8:10]) in week1:
                        data = {
                            "invoice_approved": row["approved"],
                            "week": "Week 1"
                        }
                        temp.append(data)
                        no_of_in.append(row["approved"])
                        w1 = 'y'
                        
                    elif int(str(row["approved_date"])[8:10]) in week2:
                        data = {
                            "invoice_approved": row["approved"],
                            "week": "Week 2"
                        }
                        temp.append(data)
                        no_of_in.append(row["approved"])
                        w2 = 'y'
                        
                    elif int(str(row["approved_date"])[8:10]) in week3:
                        data = {
                            "invoice_approved": row["approved"],
                            "week": "Week 3"
                        }
                        temp.append(data)
                        no_of_in.append(row["approved"])
                        w3 = 'y'
                        
                    elif int(str(row["approved_date"])[8:10]) in week4:
                        data = {
                        "invoice_approved": row["approved"],
                            "week": "Week 4"
                        }
                        temp.append(data)
                        no_of_in.append(row["approved"])
                        w4 = 'y'
                        
                if w1 == "n":
                    data = {
                        "invoice_approved": 0,
                        "week": "Week 1"
                    }
                    temp.append(data)
                    
                if w2 == "n":
                    data = {
                        "invoice_approved": 0,
                        "week": "Week 2"
                    }
                    temp.append(data)
                    
                if w3 == "n":
                    data = {
                        "invoice_approved": 0,
                        "week": "Week 3"
                    }
                    temp.append(data)
                    
                if w4 == "n":
                    data = {
                        "invoice_approved": 0,
                        "week": "Week 4"
                    }
                    temp.append(data)
                    
                records["details"] = sorted(temp, key = lambda i: i['week'])
                records['records'] = no_of_in
    
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
                    
    finally:
        mydb.close()
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , 'switch':'off'})
            

    return {
        'statuscode': 200,
        'body': records,
    }

def getOverviewSup(event, context):
    trace_off = ''
    global dbScehma 
    dbScehma = ' DBADMIN  '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    records = {}
    output1 = {}
    output2 = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
	           # atoken =  event['params']['header']['Authorization']
	           # print(atoken)
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     trace_off = 'off'
	           # a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
	           # if json.loads(a.text)['body'] == 'on':
	           #     patch_all()
	           #     print(event)  
            
            # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            # if on == 1:
            #     chk = enable_xray(event)
            #     if chk['Enable'] == True:
            #         patch_all()
            
            if "user_id" in event["params"]["querystring"]:
                
                sqlQuery = "select b.vendor_no " \
                    "from member a " \
                	"left join vendor_master b " \
                	"on a.member_id = b.member_id " \
                	"where a.email = ?"
                mycursor.execute(sqlQuery, event["params"]["querystring"]["user_id"])
                vendor = mycursor.fetchone()
                
                if vendor:
                    
                    sqlQuery = "select invoice_no, amount, in_status from invoice_header where supplier_id = ? and from_supplier = 'y'"
                    mycursor.execute(sqlQuery, vendor["vendor_no"])
                    invoices = mycursor.fetchall()
                    
                    draft = 0
                    draft_amount = 0
                    draft_per = 0
                    rejected = 0
                    rejected_amount = 0
                    rejected_per = 0
                    new = 0
                    new_amount = 0
                    new_per = 0
                    inapproval = 0
                    inapproval_amount = 0
                    inapproval_per = 0
                    processed = 0
                    processed_amount = 0
                    processed_per = 0
                    total_no_of_invoices = 0
                        
                    if invoices:
                        for row in invoices:
                            
                            if row["in_status"] == 'draft':
                                draft = draft + 1
                                draft_amount = draft_amount + row["amount"]
                                total_no_of_invoices = total_no_of_invoices + 1
                                
                            elif row["in_status"] == 'new':
                                new = new  + 1
                                new_amount = new_amount + row["amount"]
                                total_no_of_invoices = total_no_of_invoices + 1
                                
                            elif row["in_status"] == 'rejected':
                                rejected = rejected + 1
                                rejected_amount = rejected_amount + row["amount"]
                                total_no_of_invoices = total_no_of_invoices + 1
                                
                            elif row["in_status"] == 'inapproval':
                                inapproval = inapproval + 1
                                inapproval_amount = inapproval_amount + row["amount"]
                                total_no_of_invoices = total_no_of_invoices + 1
                                
                            elif row["in_status"] == 'tosap':
                                processed = processed + 1
                                processed_amount = processed_amount + row["amount"]
                                total_no_of_invoices = total_no_of_invoices + 1
                    
                    if total_no_of_invoices != 0:     
                        draft_per = ( draft / total_no_of_invoices ) * 100
                        rejected_per = ( rejected / total_no_of_invoices ) * 100
                        inapproval_per = ( inapproval / total_no_of_invoices ) * 100
                        new_per = ( new / total_no_of_invoices ) * 100
                        processed_per = ( processed / total_no_of_invoices ) * 100
                    
                    output1 = {
                        "draft": draft,
                        "draft_amount": draft_amount,
                        "draft_per": draft_per,
                        "rejected": rejected,
                        "rejected_amount": rejected_amount,
                        "rejected_per": rejected_per,
                        "new": new,
                        "new_amount": new_amount,
                        "new_per": new_per,
                        "inapproval": inapproval,
                        "inapproval_amount": inapproval_amount,
                        "inapproval_per": inapproval_per,
                        "processed": processed,
                        "processed_amount": processed_amount,
                        "processed_per": processed_per
                    }
                
# Account recivable overview
                
                    sqlQuery = "SELECT invoice_no, in_status, amount, baseline_date " \
                        "FROM invoice_header WHERE MONTH(entry_date) = MONTH(CURDATE()) and supplier_id = ? and from_supplier = 'y'"
                    mycursor.execute(sqlQuery, vendor["vendor_no"])
                    invoices2 = mycursor.fetchall()
                    # print(invoices2)
                    
                    processed_amt = 0
                    due_amount = 0
                    over_due_amount = 0
                    
                    if invoices2:
                        
                        for row in invoices2:
                            today = date.today()
                            print(today, row["baseline_date"])
                
                            if row["in_status"] == 'tosap':
                                processed_amt = processed_amt + row["amount"]
                                
                            elif row["baseline_date"] != None and type(row["baseline_date"]) != str:
                                
                                if today <= row["baseline_date"]:
                                    due_amount = due_amount + row["amount"]
                                        
                                elif today > row["baseline_date"]:
                                    over_due_amount = over_due_amount + row["amount"]
                    
                    output2 = {
                        "processed_amt": processed_amt,
                        "due_amount": due_amount,
                        "over_due_amount": over_due_amount
                    }
                
                records = {
                    "output1": output1,
                    "output2": output2
                }
                
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
        
    finally:
        mydb.close()
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , 'switch':'off'})
            

    return {
        'statuscode': 200,
        'body': records
    }

def userauthentication(atoken):
    if 'Authorization' in e1['params']['header'] :
       atoken =  e1['params']['header']['Authorization']
    
    if atoken != '':
        userid=e1["params"]["querystring"]["userid"]
        flg = requests.get("https://5ud4f0kv53.execute-api.eu-central-1.amazonaws.com/einvoice-v1/userauthentication", headers={"Content-Type":"application/json", "Authorization":atoken},params={"userid":userid})
        print(json.loads(flg.text)['body']['Enable'])

    return json.loads(flg.text)['body']['Enable']

def getAccountsRecivableOverviewSup(event, context):
    trace_off = ''
    global dbScehma 
    global e1 
    e1=event
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    # mydb = pymysql.connect(
    #     host=secretDict['host'],
    #     user=secretDict['username'],
    #     passwd=secretDict['password'],
    #     database=secretDict['dbname'],
    #     charset='utf8mb4',
    #     cursorclass=pymysql.cursors.DictCursor
    # )

    mydb = hdbcliConnect()

    records = {
        "processed_amt": 0,
        "due_amount": 0,
        "over_due_amount": 0
    }

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            
            on = convertValuesTodict(mycursor.description , on)	
            on = on[0]
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
	           # atoken =  event['params']['header']['Authorization']
	           # print(atoken)
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     trace_off = 'off'
            #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
            #     if json.loads(a.text)['body'] == 'on':
	           #     patch_all()
	           #     print(event)  
            
            # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            # if on == 1:
            #     chk = enable_xray(event)
            #     if chk['Enable'] == True:
            #         patch_all()
            #atoken = e1['params']['header']['Authorization']
            processed_amt = 0
            due_amount = 0
            over_due_amount = 0
            
            atoken = 'asdf' 
            if "userid" in e1["params"]["querystring"] :
                # if userauthentication(atoken):
                if atoken :
                    
                    sqlQuery = "select b.vendor_no " \
                        "from member a " \
                	    "left join vendor_master b " \
                	    "on a.member_id = b.member_id " \
                	    "where a.email = ?"
                    mycursor.execute(sqlQuery, event["params"]["querystring"]["userid"])
                    vendor = mycursor.fetchone() 
                
                    if vendor["vendor_no"]:
                    
                        sqlQuery = "SELECT invoice_no, in_status, amount, baseline_date " \
                                    "FROM invoice_header " \
                                    "WHERE document_type = 'RE' and MONTH(entry_date) = MONTH(CURRENT_DATE) and supplier_id = ? and from_supplier = 'y'"
                        mycursor.execute(sqlQuery, vendor["vendor_no"])
                        invoices2 = mycursor.fetchall()
                            
                            
                        if invoices2:
                        
                            for row in invoices2:
                                today = date.today()
                            # print(today, row["baseline_date"])
                        
                                if row["in_status"] == 'tosap':
                                    processed_amt = processed_amt + float(row["amount"])
                                    
                                elif row["baseline_date"] != None and type(row["baseline_date"]) != str:
                                        
                                    if today <= row["baseline_date"]:
                                        due_amount = due_amount + float(row["amount"])
                                                
                                    elif today > row["baseline_date"]:
                                        over_due_amount = over_due_amount + float(row["amount"])

                else :
                    return{
                                'statuscode': 500,
                                'body': json.dumps("Unauthorized")  
                            } 

            records = {
                "processed_amt": processed_amt,
                "due_amount": due_amount,
                "over_due_amount": over_due_amount
            }


                    
    
                  
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
        
    finally:
        mydb.close()
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , 'switch':'off'})
            

    return {
        'statuscode': 200,
        'body': records
    }


# def getInvoiceOverviewSup(event, context):
#     # print(event)
#     trace_off = ''
#     global dbScehma 
#     dbScehma = '"DBADMIN"'
    


#     mydb = hdbcliConnect()
    

#     records = {}

#     try:
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "set schema " + dbScehma
#             mycursor.execute(defSchemaQuery)
            
#             mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
#             on = mycursor.fetchone()
#             if on['value1'] == 'on':
#                 chk = enable_xray(event)
#                 if chk['Enable'] == True:
#                     patch_all() 
#                     print(event)
            
#             # atoken = ''
#             # if 'Authorization' in event['params']['header'] :
#             #     atoken =  event['params']['header']['Authorization']
#             #     print(atoken)
                
#             # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
#             # flg = mycursor.fetchone()
#             # if flg['value1'] == 'on':
#             #     trace_off = 'off'
#             #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
#             #     if json.loads(a.text)['body'] == 'on':
#             #         patch_all()
#             #         print(event) 
            
#             # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
#             # if on == 1:
#             #     chk = enable_xray(event)
#             #     if chk['Enable'] == True:
#             #         patch_all()
            
#             if "userid" in event["params"]["querystring"]:
                
#                 sqlQuery = "select b.vendor_no " \
#                     "from member a " \
#                     "left join vendor_master b " \
#                     "on a.member_id = b.member_id " \
#                     "where a.email = ?"
#                 mycursor.execute(sqlQuery, event["params"]["querystring"]["userid"])
#                 vendor = mycursor.fetchone()
                
#                 if vendor["vendor_no"]:
#                     sqlQuery = "select invoice_no, amount, in_status from invoice_header " \
#                         "where document_type = 'RE' and supplier_id = ? and from_supplier = 'y'"
                    
#                     mycursor.execute(sqlQuery, vendor["vendor_no"])
                    
#                     invoices = mycursor.fetchall()
                    
#                     draft = 0
#                     draft_amount = 0
#                     draft_per = 0
#                     rejected = 0
#                     rejected_amount = 0
#                     rejected_per = 0
#                     new = 0
#                     new_amount = 0
#                     new_per = 0
#                     inapproval = 0
#                     inapproval_amount = 0
#                     inapproval_per = 0
#                     processed = 0
#                     processed_amount = 0
#                     processed_per = 0
#                     total_no_of_invoices = 0
                        
#                     if invoices:
#                         for row in invoices:
                            
#                             if row["in_status"] == 'draft':
#                                 draft = draft + 1
#                                 draft_amount = draft_amount + row["amount"]
#                                 total_no_of_invoices = total_no_of_invoices + 1
                                
#                             elif row["in_status"] == 'new':
#                                 new = new  + 1
#                                 new_amount = new_amount + row["amount"]
#                                 total_no_of_invoices = total_no_of_invoices + 1
                                
#                             elif row["in_status"] == 'rejected':
#                                 rejected = rejected + 1
#                                 rejected_amount = rejected_amount + row["amount"]
#                                 total_no_of_invoices = total_no_of_invoices + 1
                                
#                             elif row["in_status"] == 'inapproval':
#                                 inapproval = inapproval + 1
#                                 inapproval_amount = inapproval_amount + row["amount"]
#                                 total_no_of_invoices = total_no_of_invoices + 1
                                
#                             elif row["in_status"] == 'tosap':
#                                 processed = processed + 1
#                                 processed_amount = processed_amount + row["amount"]
#                                 total_no_of_invoices = total_no_of_invoices + 1
                    
#                     if total_no_of_invoices != 0:     
#                         draft_per = ( draft / total_no_of_invoices ) * 100
#                         rejected_per = ( rejected / total_no_of_invoices ) * 100
#                         inapproval_per = ( inapproval / total_no_of_invoices ) * 100
#                         new_per = ( new / total_no_of_invoices ) * 100
#                         processed_per = ( processed / total_no_of_invoices ) * 100
                    
#                     records = {
#                         "draft": draft,
#                         "draft_amount": draft_amount,
#                         "draft_per": draft_per,
#                         "rejected": rejected,
#                         "rejected_amount": rejected_amount,
#                         "rejected_per": rejected_per,
#                         "new": new,
#                         "new_amount": new_amount,
#                         "new_per": new_per,
#                         "inapproval": inapproval,
#                         "inapproval_amount": inapproval_amount,
#                         "inapproval_per": inapproval_per,
#                         "processed": processed,
#                         "processed_amount": processed_amount,
#                         "processed_per": processed_per
#                     }
                    
#     except:
#         return {
#             'statuscode': 500,
#             'body': json.dumps("Internal Error!")
#         }  

#     finally:
#         mydb.close()
#         # if trace_off == 'off':
#         #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , 'switch':'off'})
            

#     return {
#         'statuscode': 200,
#         'body': records
#     }
    
def getProductivityReport(event, context):
    global dbScehma 
    dbScehma = dbScehma = '"DBADMIN"'

    mydb = hdbcliConnect()

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            val_list = []
            pos = 0
            condn = ""

            if "condn" in event["body-json"]:
                for row in event["body-json"]["condn"]:
                    
                    condn = condn + " and "

                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                    else:
                        val_list.append(row["value"])
                        
                    if row["field"] == "fs_name":
                        condn = condn + "m." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                        
                    elif row["field"] == "value1": 
                        condn = condn + "d." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                        
            sqlQuery = "SELECT m.member_id, m.fs_name, m.ls_name, m.user_type, m.email, d.value2 " \
                "from member m " \
                "inner join dropdown d " \
                "on m.user_type = d.value1 " \
                "where ( m.user_type = 'app' or m.user_type = 'ssu' or m.user_type = 'cfo' ) " + condn
            
            mycursor.execute(sqlQuery, tuple(val_list))
            data = mycursor.fetchall()
            
            # print(sqlQuery, tuple(val_list))
            # print(data)
            
            validation_specialist = []
            val_specialist_data = []
            approver = []
            approver_data = []
            memberids = []

            for row in data:
                if row["user_type"] == 'app' or row["user_type"] == 'ssu':
                    validation_specialist.append(row["member_id"])
                    val_specialist_data.append(row)

                elif row["user_type"] == 'cfo':
                    approver.append(row["member_id"])
                    approver_data.append(row)

                memberids.append(row["member_id"])

            if memberids:

                format_strings_mem = ','.join(['?'] * len(memberids))
                format_strings_app = ','.join(['?'] * len(approver))
                format_strings_val = ','.join(['?'] * len(validation_specialist))

                # data for getting number for time user get delegated

                sqlQuery = "select count(*) as no_times_delegated, delegated_from " \
                           "from delegate " \
                           "where delegated_from in ({}) " \
                           "group by delegated_from " \
                           "order by delegated_from "

                sqlQuery = sqlQuery.format(format_strings_mem)
                mycursor.execute(sqlQuery, tuple(memberids))
                delegate_data = mycursor.fetchall()
                odelegate_datan = convertValuesTodict(mycursor.description , delegate_data)
                # data of approvers from approval history
                
                if format_strings_app:

                    # sqlQuery = "select a.*, ih.invoice_no, timestampdiff(MINUTE, a.entry_date, a.approved_date) as time_diff, ih.in_status, " \
                    #           "timestampdiff(MINUTE, ih.entry_date, ih.end_date) as cycle_time, " \
                    #           "timestampdiff(MINUTE, a.entry_date, ih.end_date) as approval_time, " \
                    #           "timestampdiff(MINUTE, ih.entry_date, a.entry_date) as processing_time  " \
                    #           "from approval_history a " \
                    #           "inner join invoice_header ih " \
                    #           "on a.invoice_no = ih.invoice_no " \
                    #           "where (ih.in_status != 'rejected' or ih.in_status != 'deleted') and ih.document_type = 'RE' and a.member_id in ({}) " \
                    #           "order by a.member_id "
                    
                    sqlQuery = """
                                SELECT a.*,
                                    ih.invoice_no,
                                    (SECONDS_BETWEEN(a.approved_date, a.entry_date) / 60) AS time_diff,
                                    ih.in_status,
                                    (SECONDS_BETWEEN(ih.end_date, ih.entry_date) / 60) AS cycle_time,
                                    (SECONDS_BETWEEN(ih.end_date, a.entry_date) / 60) AS approval_time,
                                    (SECONDS_BETWEEN(a.entry_date, ih.entry_date) / 60) AS processing_time
                                FROM approval_history a
                                INNER JOIN invoice_header ih ON a.invoice_no = ih.invoice_no
                                WHERE (ih.in_status != 'rejected' OR ih.in_status != 'deleted')
                                AND ih.document_type = 'RE'
                                AND a.member_id IN ({})
                                ORDER BY a.member_id;
                                """

    
                    sqlQuery = sqlQuery.format(format_strings_app)
                    mycursor.execute(sqlQuery, tuple(approver))
                    app_hist_data = mycursor.fetchall()
                    app_hist_data = convertValuesTodict(mycursor.description , app_hist_data)

                    sqlQuery = """
                            SELECT a.*, ih.invoice_no, a.entry_date, ih.in_status, ih.entry_date,
                            (SECONDS_BETWEEN(a.entry_date, ih.entry_date) / 60) AS processing_time
                            FROM approval a
                            INNER JOIN invoice_header ih ON a.invoice_no = ih.invoice_no
                            WHERE (ih.in_status != 'rejected' AND ih.in_status != 'deleted')
                            AND ih.document_type = 'RE'
                            AND a.working_person IN ({})
                            ORDER BY a.working_person;
                    """
    
                    sqlQuery = sqlQuery.format(format_strings_app)
                    mycursor.execute(sqlQuery, tuple(approver))
                    approval_data = mycursor.fetchall()
                    approval_data = convertValuesTodict(mycursor.description , approval_data)

                for user in approver_data:
                    prod_data = {
                        "total_processed": 0,
                        "time_spent": 0.00,
                        "total_approved": 0,
                        "total_rejected": 0,
                        "total_inprocessing": 0,
                        "delegated": 0,
                        "cycle_time": 0,
                        "processing_time": 0,
                        "approval_time": 0
                    }
                    time_processed = 0

                    for invoice in app_hist_data:
                        if invoice['member_id'] == user['member_id']:
                            prod_data['total_processed'] += 1   
                            if invoice['time_taken'] != None:
                                prod_data['time_spent'] += int(invoice['time_taken'])

                            if invoice['in_status'] == "approved":
                                prod_data['total_approved'] += 1
                            else:
                                prod_data['total_rejected'] += 1
                            
                            if invoice['cycle_time'] != None:
                                prod_data["cycle_time"] += int(invoice["cycle_time"])
                            
                            if invoice['approval_time'] != None:
                                prod_data["approval_time"] += int(invoice["approval_time"])
                            
                            if invoice['processing_time'] != None:    
                                prod_data['processing_time'] += invoice['processing_time']

                    for invoice in approval_data:
                        if invoice['working_person'] == user['member_id']:
                            prod_data['total_inprocessing'] += 1
        
                            prod_data['processing_time'] += invoice['processing_time']

                    for delegate in delegate_data:
                        if user['member_id'] == delegate['delegated_from']:
                            prod_data['delegated'] += delegate['no_times_delegated']

                    avg_time = 0.00
                    if prod_data['total_processed'] > 0:
                        avg_time = prod_data['time_spent'] / prod_data['total_processed']
                        
                    if prod_data["total_processed"] == 0 and prod_data["time_spent"] == 0 and prod_data["total_approved"] == 0 and prod_data["total_rejected"] == 0 and prod_data["total_inprocessing"] == 0 and prod_data["delegated"] == 0:
                        print("dont append")
                    else:

                        rec = {
                            'userid': str(user['fs_name']) + " " + str(user['ls_name']),
                            'role': user['value2'],
                            'total_processed' : prod_data['total_processed'],
                            'total_timespent' : prod_data['time_spent'],
                            'avg_time': avg_time,
                            'approved': prod_data['total_approved'],
                            'rejected': prod_data['total_rejected'],
                            'inprocessing': prod_data['total_inprocessing'],
                            'delegated': prod_data['delegated'],
                            # 'cycle_time': prod_data["cycle_time"],
                            'cycle_time': prod_data['processing_time'] + prod_data["approval_time"],
                            'processing_time': prod_data['processing_time'],
                            'approval_time': prod_data["approval_time"]
                        }
                        records.append(rec)

                processed_ap = 0
                inprocess_ap = 0
                
                processed_cfo = 0
                inprocess_cfo = 0
                
                processed_fc = 0
                inprocess_fc = 0
                
                processed_fh = 0
                inprocess_fh = 0
                
                processed_ssu = 0
                inprocess_ssu = 0
                
                for data in records:
                    if data["role"] == "AP Processor":
                        processed_ap = processed_ap + data["total_processed"]
                        inprocess_ap = inprocess_ap + data["inprocessing"]
                        
                    if data["role"] == "CFO":
                        processed_cfo = processed_cfo + data["total_processed"]
                        inprocess_cfo = inprocess_cfo + data["inprocessing"]
                        
                    if data["role"] == "Finance Controller":
                        processed_fc = processed_fc + data["total_processed"]
                        inprocess_fc = inprocess_fc + data["inprocessing"]
                        
                    if data["role"] == "Finance Head":
                        processed_fh = processed_fh + data["total_processed"]
                        inprocess_fh = inprocess_fh + data["inprocessing"]
                        
                    if data["role"] == "Shared Service User":
                        processed_ssu = processed_ssu + data["total_processed"]
                        inprocess_ssu = inprocess_ssu + data["inprocessing"]
                        
                output2 = {
                    "processed_ap": processed_ap,
                    "inprocess_ap": inprocess_ap,
                    "processed_cfo": processed_cfo,
                    "inprocess_cfo": inprocess_cfo,
                    "processed_fc": processed_fc,
                    "inprocess_fc": inprocess_fc,
                    "processed_fh": processed_fh,
                    "inprocess_fh": inprocess_fh,
                    "processed_ssu": processed_ssu,
                    "inprocess_ssu": inprocess_ssu
                }
                
                output_data = {
                    "output1": records,
                    "output2": output2
                }
                
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Fail")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': output_data
    }

# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjEwOTIwNDUyLTZhYzAtNGNmZC04OWQ3LTIwNTFkODRmNmU3MyIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg2ODA2OTkwLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg2ODEwNTg5LCJpYXQiOjE2ODY4MDY5OTAsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.lZSNWrOF-QgaJt-1PTRkdagvmASZikbd7klWEaQiBapb2wnZCRvLV6PTibHmBi8LykVCmQgzvwrrPp4QqTaFwfK7zxKrIT5RyrWxXhosKQtQ5VRyMKCDiHI0PXIYUeleYghePZLhclgPvFT1lSUhq8n0cr26LQwmWP6NT75rRCeEzo-hr3FXQQqnpMkC7erVaMe94cUcL9w1APXr3mMYJxHTG3Al9n-0gML1TMGqNzdc0Npz9OZEIkoatUPJdAKOGbye3F5AvtQMKMLCJHDZsTd5JuySLZ9OREajizjwxYvpeAzTNkRCvkzOVSN-K9wMMQ7X1teeUmfcxv_TWF7rLA', 'content-type': 'application/json', 'Host': 'wzwczc4rhd.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-648aa1da-22b484fa6231ab3557c2a361', 'X-Forwarded-For': '49.207.51.244', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'wzwczc4rhd', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'einvoice-v1', 'source-ip': '49.207.51.244', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': '07d79dd9-af32-45ab-8e00-9942d8cd6bcf', 'resource-id': 'm3tv8c', 'resource-path': '/productivity-report'}}


# event = {
#     "body-json" : ""
# }

# context = ""
# responce = lambda_handler(event, context)
# print(responce)

def getTopFiveVendors(event, context):
    global dbScehma 
    dbScehma = '"DBADMIN"'
    
    mydb = hdbcliConnect()
    

    responce = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
	           # atoken =  event['params']['header']['Authorization']
	           # print(atoken)
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
	           # a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
	           # if json.loads(a.text)['body'] == 'on':
	           #     patch_all()
	           #     print(event)  
            
            # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            # if on == 1:
            #     chk = enable_xray(event)
            #     if chk['Enable'] == True:
            #         patch_all()
            
    # Top 5 Vendor Quarterly Based on Total Amount and Invoice Date
            quarter1 = [4, 5, 6]
            quarter2 = [7, 8, 9]
            quarter3 = [10, 11, 12]
            quarter4 = [1, 2, 3]

            month = datetime.today()
            month = month.month
            
            if month in quarter1:
                quat_seq = ['q2','q3','q4','q1']
            elif month in quarter2:
                quat_seq = ['q3','q4','q1','q2']
            elif month in quarter3:
                quat_seq = ['q4','q1','q2','q3']
            elif month in quarter4:
                quat_seq = ['q1','q2','q3','q4']

        # Considering all invoices except rejected and deleted
            # mycursor.execute("select supplier_id, amount , invoice_date from invoice_header "
            #     "where document_type = 'RE' and (in_status != 'rejected' or in_status != 'deleted') and invoice_date > curdate() - interval 12 month")
            
            mycursor.execute("SELECT supplier_id, amount, invoice_date FROM invoice_header WHERE document_type = 'RE' AND (in_status <> 'rejected' OR in_status <> 'deleted') AND invoice_date > ADD_MONTHS(CURRENT_DATE, -12)")
            
            vendors_data = mycursor.fetchall()
            vendors_data.append({'supplier_id': 2000000054, 'amount': float('2528.00'), 'invoice_date': date(2022, 12, 7)})

            mycursor.execute("select vendor_no, vendor_name from vendor_master ")
            vendor_master = mycursor.fetchall()

            if vendors_data:

                vendors = []
                for each in vendors_data:
                    vendors.append(each['supplier_id'])

                vendors = set(vendors)
                vendors = list(vendors)

                vendor_names = {}

                for each in vendors:
                   for ven in vendor_master:
                        
                        if each == ven['vendor_no']:
                            vendor_names[each] = ven['vendor_name']
                            break
                        
                        else:
                            vendor_names[each] = "NO Name"

                vendors_quat = {}
                for each in vendors:
                    vendors_quat[each] = {'q1': 0, 'q2': 0, 'q3': 0, 'q4': 0}

                for row in vendors_data:
                    
                    if row['invoice_date'].month in quarter1:
                        vendors_quat[row['supplier_id']]['q1'] += float(row['amount'])
                        
                    elif row['invoice_date'].month in quarter2:
                        vendors_quat[row['supplier_id']]['q2'] += float(row['amount'])
                        
                    elif row['invoice_date'].month in quarter3:
                        vendors_quat[row['supplier_id']]['q3'] += float(row['amount'])
                        
                    elif row['invoice_date'].month in quarter4:
                        vendors_quat[row['supplier_id']]['q4'] += float(row['amount'])

                vendq1 = []
                vendq2 = []
                vendq3 = []
                vendq4 = []
                
                for each in vendors_quat:
                    
                    rec = {
                        'vendor' : vendor_names[each],
                        'amount' : vendors_quat[each]['q1']
                    }
                    vendq1.append(rec)
                    
                    rec = {
                        'vendor': vendor_names[each],
                        'amount': vendors_quat[each]['q2']
                    }
                    vendq2.append(rec)
                    
                    rec = {
                        'vendor': vendor_names[each],
                        'amount': vendors_quat[each]['q3']
                    }
                    vendq3.append(rec)
                    
                    rec = {
                        'vendor': vendor_names[each],
                        'amount': vendors_quat[each]['q4']
                    }
                    vendq4.append(rec)

                vendq1 = sorted(vendq1, key=lambda i: i['amount'], reverse= True)
                vendq2 = sorted(vendq2, key=lambda i: i['amount'], reverse= True)
                vendq3 = sorted(vendq3, key=lambda i: i['amount'], reverse= True)
                vendq4 = sorted(vendq4, key=lambda i: i['amount'], reverse= True)

                final = {
                    'q1' : {
                            "quat_name" : "Apr-May-Jun",
                            "vendors" : [vendq1[0]['vendor'], vendq1[1]['vendor'], vendq1[2]['vendor'], vendq1[3]['vendor'], vendq1[4]['vendor']],
                            "amounts" : [vendq1[0]['amount'], vendq1[1]['amount'], vendq1[2]['amount'], vendq1[3]['amount'], vendq1[4]['amount']],
                    },

                    'q2' : {
                            "quat_name": "Jul-Aug-Sep",
                            "vendors": [vendq2[0]['vendor'], vendq2[1]['vendor'], vendq2[2]['vendor'], vendq2[3]['vendor'], vendq2[4]['vendor']],
                            "amounts": [vendq2[0]['amount'], vendq2[1]['amount'], vendq2[2]['amount'], vendq2[3]['amount'], vendq2[4]['amount']],
                    },

                    'q3' : {
                            "quat_name": "Oct-Nov-Dec",
                            "vendors": [vendq3[0]['vendor'], vendq3[1]['vendor'], vendq3[2]['vendor'], vendq3[3]['vendor'], vendq3[4]['vendor']],
                            "amounts": [vendq3[0]['amount'], vendq3[1]['amount'], vendq3[2]['amount'], vendq3[3]['amount'], vendq3[4]['amount']],
                    },

                    'q4' : {
                            "quat_name": "Jan-Feb-Mar",
                            "vendors": [vendq4[0]['vendor'], vendq4[1]['vendor'], vendq4[2]['vendor'], vendq4[3]['vendor'], vendq4[4]['vendor']],
                            "amounts": [vendq4[0]['amount'], vendq4[1]['amount'], vendq4[2]['amount'], vendq4[3]['amount'], vendq4[4]['amount']],
                    }
                }
                
        # Sequencing the Quarters as per Current DATE - Current Quarter Placed at Last
                for each in quat_seq:
                    responce.append(final[each])

    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200, 
        'body': responce
    }





# mumbai region

#file handling api

def uploadAttachments(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )
    
    secret = event["stageVariables"]["secreat"]
    bucket = event["stageVariables"]["non_ocr_attachment"]
    
    resp = client.get_secret_value(
        SecretId= secret
    )
    secretDict = json.loads(resp['SecretString'])

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    s3 = boto3.client("s3")
    invoice_no = ""
    
    try:
        if "body" in event and event["body"]:
            
            post_data = base64.b64decode(event["body"])
            if "Content-Type" in event["headers"]:
                content_type = event["headers"]["Content-Type"]
                ct = "Content-Type: "+content_type+"\n"
                
            elif "content-type" in event["headers"]:
                content_type = event["headers"]["content-type"]
                ct = "content-type: "+content_type+"\n"
                
            if ct:
                
                msg = email.message_from_bytes(ct.encode()+post_data)
                
                if msg.is_multipart():
                    
                    multipart_content = {}
                    
                    for part in msg.get_payload():
                        multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
                    
                    file_id = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["file_id"])))
                    file_name = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["file_name"]))) 
                    mime_type = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["mime_type"])))
                    
                    up_file_name = str(file_id) + file_name
                    
                    s3_upload = s3.put_object(Bucket=bucket, Key=up_file_name, Body=multipart_content["file"])
                    
                    var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/dev/attachment?file_name=" + up_file_name
                    
                    with mydb.cursor() as mycursor:
                        defSchemaQuery = "use " + dbScehma
                        mycursor.execute(defSchemaQuery)
                        
                        sqlQuery = "INSERT INTO file_storage (file_id, name, mime_type, file_path, file_link) VALUES (%s, %s, %s, %s, %s)"
                        values = (file_id, up_file_name, mime_type, bucket, var_path )
                        mycursor.execute(sqlQuery, values)
                        
                        mydb.commit()
                    
    except Exception as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-type': 'application/json', 
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(e))
        }
        
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(e))
        }
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'headers': {
            'Content-type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,X-Amz-Security-Token,Authorization,X-Api-Key,X-Requested-With,Accept,Access-Control-Allow-Methods,Access-Control-Allow-Origin,Access-Control-Allow-Headers',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
            'X-Requested-With': '*'
        },
        'body': json.dumps('File uploaded successfully!')
    }    

def uploadUserProfilePhoto(event, context):
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )
    
    secret = event["stageVariables"]["secreat"]
    bucket = event["stageVariables"]["non_ocr_attachment"]
    stage = event["requestContext"]["stage"]

    resp = client.get_secret_value(
        SecretId= secret
    )

    secretDict = json.loads(resp['SecretString'])

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

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
                ct = "Content-Type: "+content_type+"\n"
                # print("1ok")
                
            elif "content-type" in event["headers"]:
                # print("123")
                content_type = event["headers"]["content-type"]
                ct = "content-type: "+content_type+"\n"
                # print("1ok")
                
            if ct:
                
                msg = email.message_from_bytes(ct.encode()+post_data)
                
                if msg.is_multipart():
                    
                    multipart_content = {}
                    
                    # print("2ok")
                    for part in msg.get_payload():
                        
                        multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
                    
                    # print("Multipart Content", multipart_content)
                    
                    member_id = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["member_id"])))
                    file_name = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["file_name"])))
                    # print(member_id, file_name)
                    
                    filenamett, file_extension = os.path.splitext(file_name) 
                    up_file_name = str(member_id) + file_name
                    # print(up_file_name)
                    
                    file_name = "profile_photo/" + up_file_name
                    # s3_upload = s3.put_object(Bucket="einvoice-attachments", Key=file_name, Body=multipart_content["file"])
                    s3_upload = s3.put_object(Bucket=bucket, Key=file_name, Body=multipart_content["file"])
                    
                    var_path = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + stage + "/attachment?file_name=profile_photo/" + up_file_name + "&bucket=" + bucket
                    # print(var_path)
                    
                    with mydb.cursor() as mycursor:
                        
                        sqlQuery = "update einvoice_db_portal.member set profile_photo = %s where member_id = %s"
                        values = (var_path, member_id)
                        mycursor.execute(sqlQuery, values)
                        
                        mydb.commit()
        
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(e))
        }
        
    except Exception as e:
        mydb.rollback()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(str(e))
        }
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('File uploaded successfully!')
    }    


def downloadFileHandlingApi(event, context):
    # TODO implement
    
    s3 = boto3.client("s3")
    
    # print(event)
    
    bucket_name = event["pathParameters"]["bucket"]
    file_name = event["queryStringParameters"]["fileQuery"]
    
    file_obj = s3.get_object(Bucket=bucket_name, Key=file_name)
    file_content = file_obj["Body"].read()
    
    
    file_type = file_obj["ResponseMetadata"]["HTTPHeaders"]["content-type"]
    print(file_type)
    
    return {
          'headers': { "Content-Type": file_type },
          'statusCode': 200,
          'body': base64.b64encode(file_content),
          'isBase64Encoded': True
        }
    # return base64.b64encode(file_content)

def uploadFileHandlingApi(event, context):
    # TODO implement
    # print(fileQuery)
    #bucket_name = event["params"]["path"]["bucket"]
    # file_name = event["params"]["querystring"]["fileQuery"]
    
    #print(bucket_name,file_name)
    
    s3 = boto3.client("s3")
    bucket = event["stageVariables"]["non_ocr_attachment"]
    get_file_content = event["content"]
    # decode_content = base64.b64decode(get_file_content)
    decode_content = get_file_content
    
    #s3_upload = s3.put_object(Buckrt=bucket_name, Key=file_name, Body=decode_content)
    s3_upload = s3.put_object(Bucket=bucket, Key="abcfdsd.pdf", Body=decode_content)
    
    return {
        'statusCode': 200,
        'body': json.dumps('File Uploaded!')
    }

#einvoice supplier enquiry
def deleteCommentTemplates(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '

    mydb = hdbcliConnect()
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "sr_no" in event["params"]["querystring"]:
                sqlQuery = "delete from comment_templates where sr_no = ?" 
                values = ( event["params"]["querystring"]["sr_no"], )
                mycursor.execute(sqlQuery, values)

            mydb.commit()
            
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure!")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Deleted Successfully") 
    }

#event not found
def getCommentTemplates(event, context):
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    records = []
    
    try:
        with mydb.cursor() as mycursor:
            
            if "sr_no" not in event["params"]["querystring"]:
                mycursor.execute("select * from comment_templates")
                comments = mycursor.fetchall()
                
                for row in comments:
                    temp = {
                        "sr_no": row["sr_no"],
                        "comment_title": row["comment_title"],
                        "comment_description": row["comment_description"]
                    }
                    records.append(temp)
                    
            elif "sr_no" in event["params"]["querystring"]:
                sr_no = event["params"]["querystring"]["sr_no"]
                mycursor.execute("select * from comment_templates where sr_no = ?", sr_no)
                comments = mycursor.fetchone()
                
                temp = {
                    "sr_no": comments["sr_no"],
                    "comment_title": comments["comment_title"],
                    "comment_description": comments["comment_description"]
                }
                records.append(temp)
                    
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure!")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

#event not found
def postCommentTemplates(event, context):
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    record = {
        "comment_title" : "",
        "comment_description" : ""
    }
    
    try:
        
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
        
        with mydb.cursor() as mycursor:
            
            if "sr_no" not in event["params"]["querystring"]:
                sqlQuery = "INSERT INTO dbadmin.comment_templates (comment_title, comment_description) VALUES (?, ?)"
                values = ( record["comment_title"], record["comment_description"] )
                mycursor.execute(sqlQuery, values)
                msg = "Inserted Successfully!"
                
            elif "sr_no" in event["params"]["querystring"]:
                sqlQuery = "update dbadmin.comment_templates set comment_title = ?, comment_description = ? where sr_no = ?" 
                values = ( record["comment_title"], record["comment_description"], event["params"]["querystring"]["sr_no"] )
                mycursor.execute(sqlQuery, values)
                msg = "Updated Successfully!"

            mydb.commit()
            
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure!")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps(msg)
    }

#event not found
def postInvoiceAssignment(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId=secret
    # )

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    record = {
        "isgroup": "",
        "app": "",
        "invoice_no": ""
    }

    try:
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "userid" in event["params"]["querystring"]:
                userid = event["params"]["querystring"]["userid"]
                mycursor.execute("select member_id, (fs_name|| ' '|| ls_name) as member_name from member where email = ?", userid)
                working_person = mycursor.fetchone()
                
            if record["isgroup"] == 'y':
                mycursor.execute('select name from "GROUP" where group_id = ?', record["app"])
                assign = mycursor.fetchone()
                msg_cmnt = "Invoice No. " + str(record["invoice_no"]) + " assigned to " + assign["name"] + " Group by " + working_person["member_name"] 
            
            else:
                mycursor.execute("select concat(fs_name, ' ', ls_name) as name from member where member_id = ?", record["app"])
                assign = mycursor.fetchone()
                msg_cmnt = "Invoice No. " + str(record["invoice_no"]) + " assigned to " + assign["name"] + " by " + working_person["member_name"]
            
            mycursor.execute("select in_status from invoice_header where invoice_no = ?", record["invoice_no"])
            invoice = mycursor.fetchone()
            
            sqlQuery = "insert into assignment (isgroup, app, invoice_no) values (?, ?, ?)"
            values = ( record["isgroup"], record["app"], record["invoice_no"] )
            mycursor.execute(sqlQuery, values)
            
            sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (?, ?, ?, ?, ?)"
            values = (record["invoice_no"], invoice["in_status"], invoice["in_status"], working_person['member_id'], msg_cmnt)
            mycursor.execute(sqlQuery, values)
             
            mydb.commit()
            
    except pymysql.err.IntegrityError as e:    
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Invoice was Already Assigned to Group/User")
        }

    except Exception as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': str(e)
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Invoice Assigned!")
    }


def get_stored_credentials(user_id):
    try:
        s3 = boto3.client("s3")

        creds = None
        encoded_file = s3.get_object(Bucket=bucket_name, Key=user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
    except Exception as excep:
        creds = None


def get_credentials(user_id=None):
    try:
        if user_id:
            credentials = get_stored_credentials(user_id)
            if credentials and credentials.refresh_token is not None:
                return credentials
            else:
                False

    except Exception as error:
        print(str(error))


def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)


def create_message(sender, to, cc, subject, message_text, threadid, reference, lastmsgid):
    # Create a message for an email.

    message = email.mime.text.MIMEText(message_text, 'html')

    message['References'] = reference
    message['In-Reply-To'] = lastmsgid
    message['subject'] = 'Re: ' + subject
    message['cc'] = cc
    message['from'] = sender
    message['to'] = to

    # message['Message-ID'] = '<CAFzz-e4Dt5z2rgec9CvZRz+ez7G4FXnoTPV8xgzcmt2aminW5w@mail.gmail.com>'
    encoded = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    # return {'raw': encoded.decode("utf-8")}
    raw = encoded.decode("utf-8")

    message = {'message': {'raw': raw, 'threadId': threadid}}
    # draft = service.users().drafts().create(userId="me", body=message).execute()
    # return {'message': {'raw': encoded, 'threadId': threadid}}.decode("utf-8")

    return message



def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        # print("Message Id: ", message['id'])
        # pprint.pprint(message)
        return message
    # except errors.HttpError as error:
    except Exception as error:
        print("An error occurred: ", error)

#event not found
def postReplyToEnquiry(event, context):
    # print(event)

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # # secret = event["stage-variables"]["secreat"]
    # secret = 'test/einvoice/secret'

    global bucket_name
    # bucket_name = event["stage-variables"]["bucket_gmail_credential"]
    bucket_name = 'file-bucket-emp'

    # resp = client.get_secret_value(
    #     SecretId=secret
    # )

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()


    try:
        with mydb.cursor() as mycursor:

            enquirieno = event["params"]["querystring"]['enquirieno']
            reply_body = event["body-json"]['reply']

            user = 'mosbyted116@gmail.com'

            # enquirieno = '176a9bde77a0e5c1'
            # reply_body = "yhbzcjhbhj zbxz jkxjbk"

            values = (enquirieno,)
            mycursor.execute('select * from enquirie_header where enquirieno = ?', values)
            thread_det = mycursor.fetchone()

            if thread_det:
                cred = get_credentials(user_id=user)

                if cred:
                    service = build_service(credentials=cred)

                    if service:
                        history = service.users().threads().get(userId='me', id=thread_det['thread_id']).execute()
                        last_msg = len(history['messages'])

                        last_msg = history['messages'][last_msg-1]

                        reference = None
                        lastmsgid = ''
                        subject = ''
                        cc = ''

                        for head in last_msg['payload']['headers']:
                            if head['name'] == 'References':
                                reference = head['value']
                            elif head['name'] == 'Message-ID':
                                lastmsgid = head['value']
                            elif head['name'] == 'Subject':
                                subject = head['value']
                            elif head['name'] == 'Cc':
                                cc = head['value']


                        if not reference:
                            reference = lastmsgid
                        else:
                            reference += ' ' + lastmsgid
                            
                            
                        message = create_message(sender=user, to='rohit.wavhal@peolsolutions.com', cc=cc,
                                                 subject=thread_det['description'], message_text=reply_body,
                                                 threadid=thread_det['thread_id'],
                                                 reference=reference, lastmsgid=lastmsgid)

                        draft = service.users().drafts().create(userId="me", body=message).execute()

                        message = service.users().drafts().send(userId='me', body={'id': draft['id']}).execute()
                        
                        if 'id' in message:
                            values = (thread_det['enquirieno'], message['id'], 'me', reply_body, 'elipo')

                            mycursor.execute('INSERT INTO enquirie_responce'
                                             '(enquirieno, mail_id, bywho, enquirie_responce, sup_mail)'
                                             ' VALUES(?,?,?,?,?) ', values)

                            values = (thread_det['enquirieno'], )

                            mycursor.execute('update enquirie_header set last_responce = '
                                             ' (CURRENT_TIMESTAMP) where enquirieno = ?', values)
                        # send_message(service=service, user_id="me", message=message)

        mydb.commit()

    except Exception as ex:
        print(str(ex))
        
        return {
            'statuscode': 200,
            'body': json.dumps('Internal Fail!')
        }

    finally:
        mydb.close()
        
    return {
        'statuscode': 200,
        'body': json.dumps('Replyed Successfully!')
    }


#tested
def getSettingParameter(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema" + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute("select value2 from dropdown where drop_key = 'my-company-details' and value1 = 'gstin' ")
            row2 = mycursor.fetchone()

            if "key_name" in event["params"]["querystring"]:
                
                key_name = event["params"]["querystring"]["key_name"]
                
                if key_name == "my_gstin":
                    mycursor.execute("select value2 from dropdown where drop_key = 'my-company-details' and value1 = 'gstin' ")
                    row2 = mycursor.fetchone()
                    records = {'drop_key':"my_gstin", "value1": row2['value2'] , "value2":""}
                    
                else:
                    mycursor.execute("SELECT * FROM elipo_setting where key_name = ?", key_name)
                    records = mycursor.fetchall()
                    records = convertValuesTodict(mycursor.description, records)

                
            else:
                mycursor.execute("SELECT * FROM elipo_setting")
                records = mycursor.fetchall()
                records = convertValuesTodict(mycursor.description, records)
                
                mycursor.execute("select value2 from dropdown where drop_key = 'my-company-details' and value1 = 'gstin' ")
                row2 = mycursor.fetchone()
                
                records.append({'key_name':"my_gstin", "value1": row2['value2'], "value2":""})
    
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
    
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

#working fine for event passed
def patchSetting(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    setting = {
        "auto_schedule_rate_value": "",
        "auto_schedule_rate_unit": "",
        "sap_password": "",
        "sap_posting_url": "",
        "sap_po_fetch_url": "",
        "sap_userid": "",
        "auto_schedule_rate_unit_paymentInfo": "",
        "auto_schedule_rate_value_paymentInfo": "",
        "sap_payment_status_url": "",
        "noti_invoice_due": "",
        "noti_invoice_due_rate_unit": "day",
        "my_gstin": "",
        "ocr_central_email":"" ,
        "npo_tcode": ""
    }

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            

            client = boto3.client('events',
            region_name='eu-central-1',
            aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
            aws_secret_access_key='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')

            # client = boto3.client('events')
            payment_status = "off"
            
            if "setting" in event["body-json"]:
                for value in event["body-json"]["setting"]:
                    if value in setting:
                        setting[value] = event["body-json"]["setting"][value]
                        
                mycursor.execute("select * from elipo_setting " \
                    "where key_name in ('auto_schedule_rate_unit', 'auto_schedule_rate_value', 'ocr_auto_schedule', 'auto_schedule_rate_unit_paymentInfo', 'auto_schedule_rate_value_paymentInfo', 'payment_status' , 'noti_invoice_due', 'noti_invoice_due_rate_unit')")
                
                for row in mycursor:
                    if row["key_name"] == "auto_schedule_rate_unit":
                        old_rate_unit = row["value1"]
                    
                    elif row["key_name"] == "auto_schedule_rate_value":
                        old_rate_value = row["value1"] 
                    
                    elif row["key_name"] == "ocr_auto_schedule":
                        ocr_auto_schedule = row["value1"] 
                        
                    elif row["key_name"] == "auto_schedule_rate_unit_paymentInfo":
                        ps_old_rate_unit = row["value1"]
                    
                    elif row["key_name"] == "auto_schedule_rate_value_paymentInfo":
                        ps_old_rate_value = row["value1"] 
                    
                    elif row["key_name"] == "payment_status":
                        payment_status = row["value1"] 
                        
                    elif row["key_name"] == "noti_invoice_due":
                        di_old_rate_value = row["value1"]
                        
                    elif row["key_name"] == "noti_invoice_due_rate_unit":
                        di_old_rate_unit = row["value1"]
                        
                for key, value in setting.items():
                    
                    if key == "my_gstin":
                        values_t = (value, )
                        mycursor.execute("update dropdown set value2 = ? where drop_key = 'my-company-details' and value1 = 'gstin'", values_t)
                    else:
                        values = ( value, key )
                        mycursor.execute("UPDATE elipo_setting SET value1 = ? WHERE key_name = ?", values)
                    
                    if key == "auto_schedule_rate_unit":
                        rate_unit = value
                    elif key == "auto_schedule_rate_value":
                        rate_value = value
                    elif key == "auto_schedule_rate_unit_paymentInfo":
                        ps_rate_unit = value
                    elif key == "auto_schedule_rate_value_paymentInfo":
                        ps_rate_value = value
                    elif key == "noti_invoice_due_rate_unit":
                        di_rate_unit = value
                    elif key == "noti_invoice_due":
                        di_rate_value = value
                
                if ocr_auto_schedule == 'on' and (str(old_rate_unit) != str(rate_unit) or str(old_rate_value) != str(rate_value)):
                    
                    if str(rate_value) == "1":
                        final_rate_unit = rate_unit.lower()
                    else:
                        final_rate_unit = rate_unit.lower() + "s"
                    
                    rateExpression = "rate(" + str(rate_value) + " " + str(final_rate_unit) + ")"
                    print(rateExpression)
                    
                    response = client.put_rule(
                        Name='einvoice-ocr-email-fetch-auto',
                        ScheduleExpression=rateExpression,
                        State='ENABLED',
                        Description='Fetch emails for ocr automaically',
                        EventBusName='default'
                    )
                    
                if payment_status == 'on' and (str(ps_old_rate_unit) != str(ps_rate_unit) or str(ps_old_rate_value) != str(ps_rate_value)):
                
                    rateExpression = None
                    
                    if str(ps_rate_value) == "1":
                        final_rate_unit = ps_rate_unit.lower()
                    else:
                        final_rate_unit = ps_rate_unit.lower() + "s"
                    
                    rateExpression = "rate(" + str(ps_rate_value) + " " + str(final_rate_unit) + ")"
                    
                    response = client.put_rule(
                        Name='get_payment_status',
                        ScheduleExpression=rateExpression,
                        State='ENABLED',
                        Description='Fetch Payment Details from SAP',
                        EventBusName='default'
                    )
                
                if payment_status == 'on' and ( (str(di_old_rate_unit) != str(di_rate_unit) or str(di_old_rate_value) != str(di_rate_value))):
                    
                    rateExpression = None
                    
                    if str(di_rate_value) == "1":
                        final_rate_unit = di_rate_unit.lower()
                    else:
                        final_rate_unit = di_rate_unit.lower() + "s"
                    
                    rateExpression = "rate(" + str(di_rate_value) + " " + str(final_rate_unit) + ")"
                    
                    response = client.put_rule(
                        Name='noti_duedate_status',
                        ScheduleExpression=rateExpression,
                        State='ENABLED',
                        Description='Send mail for due invoices',
                        EventBusName='default'
                    )
            
            else:
                key_name = event["params"]["querystring"]["key_name"]
                key_value = event["params"]["querystring"]["key_value"]
                
                values = (key_value, key_name)
                mycursor.execute("UPDATE elipo_setting SET value1 = ? WHERE key_name = ?", values)
                
                if key_name == 'ocr_auto_schedule' and key_value == 'off':
                    
                    
                    response = client.disable_rule(
                        Name='einvoice-ocr-email-fetch-auto'
                    )
                    
                elif key_name == 'ocr_auto_schedule' and key_value == 'on':
                   
                    
                    response = client.enable_rule(
                        Name='einvoice-ocr-email-fetch-auto'
                    )
                    
                if key_name == 'payment_status' and key_value == 'off':
                    
                    
                    response = client.disable_rule(
                        Name='get_payment_status'
                    )
                    
                elif key_name == 'payment_status' and key_value == 'on':
                    
                    
                    response = client.enable_rule(
                        Name='get_payment_status'
                    )
                    
            mydb.commit() 
    
    except Exception as e:
        return {
            'statuscode': 500,
            'body': json.dumps(f"An exception occurred: {str(e)}")
        }
    
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Update Successful! :) ")
    }

# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'key_name': 'ConfigTraceToggle', 'key_value': 'off'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImQyNjkzODhhLTg1ODQtNDI1NS1hZjYxLTM1MWJkNDZiN2Y1ZiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg2ODk1NDA4LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg2ODk5MDA4LCJpYXQiOjE2ODY4OTU0MDgsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.MyfffnMyMPsgtmSEp-lH5x-kO7iiRZ-mwpQwPdEvfHjjRbJiVI-IU0k0N8QjzjaCSaWt7LfU2ui62DAN_zqBSppDRTaMu59MAr0AqdqkxNdlLKQVyx8lkZdezR2jcKSjA1TJC9AlhbGKsoAHuLjHH7dOASrQXvKBbPH_vg3JqnvRZHU0DL7h-dNTMtyXpccOUv-xZ_wfmUAsyXnWyiN8vdU8ZRsQuKAvnqB-2a7PSOiGbAjte5GQETGLh4Z4YlcfGp9n5Gj6tkqriy4py7b5oEoJVgJ2QAsRISEJccqf2JzaOyGuLcDQcRqNpxCOVmUqAunK0-AByUIzMa2LCcjluQ', 'content-type': 'application/json', 'Host': 'd1zhvpkkf9.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-648bfb37-1312036d5ed315e731f197ed', 'X-Forwarded-For': '49.207.52.67', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'attachment_bucket': 'einvoice-dev-enquiry', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': 'd1zhvpkkf9', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'einvoice-v1', 'source-ip': '49.207.52.67', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': '858c102b-0787-49e5-9646-bfbdb1dd7fa8', 'resource-id': 'zn2sp7', 'resource-path': '/setting'}}
# print(patchSetting(event , ' '))

#event not found
def getDetailedSupplierEnquiry1(event, context): 
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    records = {}

    try:
        with mydb.cursor() as mycursor: 
            
            if "userid" in event["params"]["querystring"]:
                userid = event["params"]["querystring"]["userid"]
                
                mycursor.execute("select * from member where email = ?", userid)
                user = mycursor.fetchall()
                
            val_list = []
            pos = 0
            condn = ""
                
            if "condn" in event["body-json"]:
                
                for row in event["body-json"]["condn"]:
                    if pos != 0:
                        condn = condn + " and "
                        
                    elif pos == 0:
                        condn = " where "
                        pos = pos + 1
        
                    if str(row["operator"]) == "between":
                        val_list.append(row["value"])
                        val_list.append(row["value2"])
                        condn = condn+ "date("  + str(row["field"]) + ") between ? and ? " 
                        
                    else:
                        val_list.append(row["value"])
                        
                        if str(row["field"]) == "entrydate":
                            condn = condn + "date(" + str(row["field"]) + ") " + str(row["operator"]) + " " + "?"
                            
                        else:
                            condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "?"
                        
            sqlQuery = "select enquirieno, description, en_status, cast(entrydate as date) as entrydate, " \
                "cast(last_responce as date) as last_responce, supplier_no, supplier_name " \
                "from enquirie_header"
            
            if "condn" in event["body-json"]:
                sqlQuery = sqlQuery + condn + " order by enquirieno desc"
                mycursor.execute(sqlQuery, val_list)
                
            else:
                sqlQuery = sqlQuery + " order by enquirieno desc"
                mycursor.execute(sqlQuery)
                
            enquiries = mycursor.fetchall()
            
            if enquiries:
                for row in enquiries:
                    temp = {
                        "enquirie_no": row["enquirieno"],
                        "description": row["description"],
                        "status": row["en_status"],
                        "recieved_date": str(row["entrydate"]),
                        "last_responded": str(row["last_responce"]),
                        "supplier_no": row["supplier_no"],
                        "supplier_name": row["supplier_name"]
                    }
                    records.append(temp)

    except:
        return {
        'statuscode': 500,
        'body': json.dumps("Internal Failure")   
    }
            
    finally:
        mydb.close()
        
    return {
        'statuscode': 200,
        'body': records
    }

def getDetailedSupplierEnquiry(event , content):

    global dbScehma 
    dbScehma = ' DBADMIN '

    mydb = hdbcliConnect()
    
    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            userid = event["params"]["querystring"]["userid"]
            enquiry_no = event["params"]["querystring"]["enquiry_no"]
            details = {}
            history = []
            
            mycursor.execute("select * from member where email = ?", userid)
            user = mycursor.fetchone()
                
            sqlQuery = "select eh.enquirieno, eh.description, eh.en_status,  cast(eh.entrydate as date)  entrydate , er.enquirie_responce " \
            	"from enquirie_header eh " \
                "inner join enquirie_responce er " \
                "on eh.enquirieno = er.enquirieno " \
                "where eh.enquirieno = ? and er.bywho = 'supplier' " \
                "order by eh.entrydate desc " \
                "limit 1"
                
            values = (enquiry_no, )
            mycursor.execute(sqlQuery, values)
            detailEnquiry = mycursor.fetchone()
            
            sqlQuery = """
                        SELECT eh.enquirieno, eh.description, eh.en_status,
                            ADD_SECONDS(TO_TIMESTAMP(eh.entrydate), 19800) AS entrytime,
                            er.enquirie_responce, er.bywho, er.sup_mail
                        FROM enquirie_header AS eh
                        INNER JOIN enquirie_responce AS er
                        ON eh.enquirieno = er.enquirieno
                        WHERE eh.enquirieno = ?
                        ORDER BY entrytime;
                        """
            
            values = values = (enquiry_no, )
            mycursor.execute(sqlQuery, values)
            enquiryHistory = mycursor.fetchall()
            
            mycursor.execute("SELECT attach_id, enquiry_no, mail_id, name, mime_type, file_path, file_link, ADD_SECONDS(entrydate, 19800) AS entrytime FROM enquiry_attachement WHERE enquiry_no = ?;", values)
            attachments = mycursor.fetchall()
            
            if detailEnquiry:
                details = {
                    "enquiry_no": detailEnquiry["enquirieno"],
                    "description": detailEnquiry["description"],
                    "status": detailEnquiry["en_status"],
                    "recieved_date": str(detailEnquiry["entrydate"]),
                    "supplier_enquiry": detailEnquiry["enquirie_responce"]
                }
            
            for row in enquiryHistory:
                temp = {
                    "enquiry_no": row["enquirieno"],
                    "description": row["description"],
                    "status": row["en_status"],
                    "recieved_date": str(row["entrytime"]),
                    "supplier_enquiry": row["enquirie_responce"],
                    "bywho": row["bywho"],
                    "sup_mail": row["sup_mail"]
                }
                history.append(temp)
                
            files = []
            
            if attachments:
                for each in attachments:
                    files.append({
                        'attachment_id': each['attach_id'],
                        'mail_id': each['mail_id'],
                        'name': each['name'],
                        'mime_type': each['mime_type'],
                        'link': each['file_link'],
                        'date': str(each['entrytime'])
                    })
                
            records = {
                "details": details,
                "history": history,
                "attachments": files
            }
            
    # except:
    #     return {
    #     'statuscode': 500,
    #     'body': json.dumps("Internal Failure")   
    # }
            
    finally:
        mydb.close()
        
    return {
        'statuscode': 200,
        'body': records
    }

def getSupplierEnquiry(event, context): 
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # )
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    records = []

    try:
        with mydb.cursor() as mycursor: 
            defSchemaQuery = "set schema DBADMIN "
            mycursor.execute(defSchemaQuery)
            if "userid" in event["params"]["querystring"]:
                userid = event["params"]["querystring"]["userid"]
                
                mycursor.execute("select * from member where email = ?", userid)
                user = mycursor.fetchall()
                
            val_list = []
            pos = 0
            condn = ""
                
            if "condn" in event["body-json"]:
                
                for row in event["body-json"]["condn"]:
                    if pos != 0:
                        condn = condn + " and "
                        
                    elif pos == 0:
                        condn = " where "
                        pos = pos + 1
        
                    if str(row["operator"]) == "between":
                        val_list.append(row["value"])
                        val_list.append(row["value2"])
                        condn = condn+ "date("  + str(row["field"]) + ") between %s and %s " 
                        
                    else:
                        val_list.append(row["value"])
                        
                        if str(row["field"]) == "entrydate":
                            condn = condn + "date(" + str(row["field"]) + ") " + str(row["operator"]) + " " + "%s"
                            
                        else:
                            condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                        
            sqlQuery = "select enquirieno, description, en_status, cast(entrydate as date) as entrydate, " \
                "cast(last_responce as date) as last_responce, supplier_no, supplier_name " \
                "from enquirie_header"
            
            if "condn" in event["body-json"]:
                sqlQuery = sqlQuery + condn + " order by enquirieno desc"
                mycursor.execute(sqlQuery, val_list)
                
            else:
                sqlQuery = sqlQuery + " order by enquirieno desc"
                mycursor.execute(sqlQuery)
                
            enquiries = mycursor.fetchall()
            
            if enquiries:
                for row in enquiries:
                    temp = {
                        "enquirie_no": row["enquirieno"],
                        "description": row["description"],
                        "status": row["en_status"],
                        "recieved_date": str(row["entrydate"]),
                        "last_responded": str(row["last_responce"]),
                        "supplier_no": row["supplier_no"],
                        "supplier_name": row["supplier_name"]
                    }
                    records.append(temp)

    except:
        return {
        'statuscode': 500,
        'body': json.dumps("Internal Failure")   
    }
            
    finally:
        mydb.close()
        
    return {
        'statuscode': 200,
        'body': records
    }

#einvoice reports
#complex query
# def getAgingReportDetails(event, context):
#     global dbScehma 
#     dbScehma = ' DBADMIN '
    
#     # client = boto3.client(
#     # 'secretsmanager',
#     # region_name='eu-central-1',
#     # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
#     # aws_secret_access_key='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' )
#     # secret = event["stage-variables"]["secreat"]
#     # resp = client.get_secret_value(
#     #     SecretId= secret
#     # )
#     # secretDict = json.loads(resp['SecretString'])

#     mydb = hdbcliConnect()

#     output1 = {}
#     output2 = []
#     output3 = []

#     try:
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "set schema " + dbScehma
#             mycursor.execute(defSchemaQuery)
            
#             val_list = []
#             pos = 0
#             condn = ""
#             days = 30
                
#             if "condn" in event["body-json"]:
#                 for row in event["body-json"]["condn"]:
#                     if row["field"] != "interval":
#                         condn = condn + " and "
                        
#                         if str(row["operator"]) == "like":
#                             val_list.append("%" + row["value"] + "%")
#                             condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                            
#                         elif str(row["operator"]) == "between":
#                             val_list.append(row["value"])
#                             val_list.append(row["value2"])
#                             condn = condn + "a." + str(row["field"]) + " between %s and %s " 
                            
#                         else:
#                             val_list.append(row["value"])
#                             if row["field"] == "company_code":
#                                 condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
#                             else:
#                                 condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                                
#                     else:
#                         days = 30
                        
#             mycursor.execute("select * FROM elipo_setting where key_name = 'payment_status'")
#             payment_status_value = mycursor.fetchone()
            
#             sqlQuery = "select a.company_code, a.invoice_no, a.npo, a.ref_po_num, date(a.entry_date) as entry_indate, a.amount, " \
#                     "datediff( curdate(), date(a.entry_date)) as days_outstanding, b.vendor_no, b.vendor_name, " \
#                     "(case when ( datediff( curdate(), date(a.entry_date) ) between " + str(0) + " and " + str(days) + " )then a.amount else 0 end) as invoice_30, " \
#                     "(case when ( datediff( curdate(), date(a.entry_date) ) between " + str(int(days) + 1) + " and " + str(int(days) * 2) + " ) then a.amount else 0 end) as invoice_60, " \
#                     "(case when ( datediff( curdate(), date(a.entry_date) ) between " + str( (int(days) * 2) + 1 ) + " and " + str( (int(days) * 3)) + " ) then a.amount else 0 end) as invoice_90, " \
#                     "(case when ( datediff( curdate(), date(a.entry_date) ) > " + str( (int(days) * 3) + 1 ) + " ) then a.amount else 0 end) as invoice_more " \
#                     "FROM invoice_header a " \
#                     "inner join vendor_master b " \
#                     "on a.supplier_id = b.vendor_no "
                    
#             if payment_status_value and (payment_status_value['value1'] == 'on'):
#                 sqlQuery += "where (a.in_status in ('new', 'draft', 'inapproval') or (a.in_status = 'tosap' and a.payment_status = 'paid') ) and (a.npo != null or a.npo = '' or a.npo = 'y') and a.document_type = 'RE' " + condn
                
#             else:    
#                 sqlQuery += "where a.in_status not in ('tosap', 'deleted') and (a.npo != null or a.npo = '' or a.npo = 'y') and a.document_type = 'RE' " + condn
            
#             mycursor.execute(sqlQuery, tuple(val_list))
#             raw_data = mycursor.fetchall()
                
#             npo_invoice_0 = 0
#             npo_invoice_31 = 0
#             npo_invoice_61 = 0
#             npo_invoice_91 = 0
            
#             po_invoice_0 = 0
#             po_invoice_31 = 0
#             po_invoice_61 = 0
#             po_invoice_91 = 0
            
#             for row in raw_data:
#                 company_code = row["company_code"]
#                 if row["npo"] == 'y':
#                     flag = 'npo'
                
#                 else:
#                     flag = 'po'
                
#                 if row["days_outstanding"] != None:
                        
#                     if flag == 'npo':
#                         if 0 <= row["days_outstanding"] <= int(days):
#                             npo_invoice_0 = npo_invoice_0 + 1
                        
#                         elif ( int(days) + 1 ) <= row["days_outstanding"] <= ( int(days) * 2 ):
#                             npo_invoice_31 = npo_invoice_31 + 1
                            
#                         elif ( (int(days) * 2) + 1 ) <= row["days_outstanding"] <= ( int(days) * 3 ):
#                             npo_invoice_61 = npo_invoice_61 + 1
                            
#                         elif row["days_outstanding"] < ( (int(days) * 3) + 1 ):
#                             npo_invoice_91 = npo_invoice_91 + 1
                        
#                     elif flag == 'po':
#                         if 0 <= row["days_outstanding"] <= int(days):
#                             po_invoice_0 = po_invoice_0 + 1
                        
#                         elif ( int(days) + 1 ) <= row["days_outstanding"] <= ( int(days) * 2 ):
#                             po_invoice_31 = po_invoice_31 + 1
                            
#                         elif ( (int(days) * 2) + 1 ) <= row["days_outstanding"] <= ( int(days) * 3 ):
#                             po_invoice_61 = po_invoice_61 + 1
                            
#                         elif row["days_outstanding"] < ( (int(days) * 3) + 1 ):
#                             po_invoice_91 = po_invoice_91 + 1
                    
#                     data = {
#                         "vendor_no": row["vendor_no"],
#                         "vendor_name": row["vendor_name"],
#                         "invoice_no": row["invoice_no"],
#                         "date": str(row["entry_indate"]),
#                         "amount_due": row["amount"],
#                         "days_outstanding": str(row["days_outstanding"]),
#                         "invoice_0_to_30": str(row["invoice_30"]),
#                         "invoice_31_to_60": str(row["invoice_60"]),
#                         "invoice_61_to_90": str(row["invoice_90"]),
#                         "invoice_91_or_more": str(row["invoice_more"]),
#                         "flag": flag
#                     }
#                     output2.append(data)
                
#             output1 = {
#                 "company_code": company_code,
#                 "po_0_30": po_invoice_0,
#                 "wpo_0_30": npo_invoice_0,
#                 "total_0_30": po_invoice_0 + npo_invoice_0,
#                 "po_30_60": po_invoice_31,
#                 "wpo_30_60": npo_invoice_31,
#                 "total_30_60": po_invoice_31 + npo_invoice_31,
#                 "po_60_90": po_invoice_61,
#                 "wpo_60_90": npo_invoice_61,
#                 "total_60_90": po_invoice_61 + npo_invoice_61,
#                 "po_ab_90": po_invoice_91,
#                 "wpo_ab_90": npo_invoice_91,
#                 "total_ab_90": po_invoice_91 + npo_invoice_91,
#             }
            
#             record = {
#                 "output1": output1,
#                 "output2": output2
#             }
            
#     # except:
#     #     return {
#     #         'statuscode': 500,
#     #         'body': json.dumps("Internal Error!")
#     #     }
        
#     finally:
#         mydb.close()

#     return {
#         'statuscode': 200,
#         'body': record
#     }

    # def getDiaAnalyticReport(event, context):
    #     global dbScehma 
    #     dbScehma = event["stage-variables"]["schema"]
        
    #     client = boto3.client('secretsmanager')
    #     secret = event["stage-variables"]["secreat"]
    #     resp = client.get_secret_value(
    #         SecretId= secret
    #     )
    #     secretDict = json.loads(resp['SecretString'])

    #     mydb = pymysql.connect(
    #         host=secretDict['host'],
    #         user=secretDict['username'],
    #         passwd=secretDict['password'],
    #         database=secretDict['dbname'],
    #         charset='utf8mb4',
    #         cursorclass=pymysql.cursors.DictCursor
    #     )
    #     print(event)
    #     records = []
    #     responce = {}

    #     try:
    #         with mydb.cursor() as mycursor:
    #             defSchemaQuery = "use " + dbScehma
    #             mycursor.execute(defSchemaQuery)
                
    #             val_list = []
    #             pos = 0
    #             condn = ""
                
    #             start_idx = int(event["params"]["querystring"]['pageno'])
    #             end_idx = int(event["params"]["querystring"]['nooflines'])
                        
    #             start_idx = (start_idx -1 ) * end_idx
        
    #             if "condn" in event["body-json"]:
    #                 for row in event["body-json"]["condn"]:
    #                     if pos != 0:
    #                         condn = condn + " and "
    #                     elif pos == 0:
    #                         condn = " where "
    #                         pos = pos + 1
            
    #                     if str(row["operator"]) == "like":
    #                         val_list.append("%" + row["value"] + "%")
    #                         if row["field"] == "vendor_no" or row["field"] == "vendor_name":
    #                             condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
    #                         else:
    #                             condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                                
    #                     elif str(row["operator"]) == "between":
    #                         val_list.append(row["value"])
    #                         val_list.append(row["value2"])
    #                         condn = condn + "a." + str(row["field"]) + " between %s and %s "
                            
    #                     else:
    #                         val_list.append(row["value"])
    #                         if row["field"] == "vendor_no" or row["field"] == "vendor_name":
    #                             condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
    #                         else:
    #                             condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                        
                
    #             sqlQuery = "SELECT a.invoice_no, a.in_status, a.ref_po_num, a.company_code, convert_tz(a.entry_date, '+00:00','+05:30' ) as entry_date, a.invoice_date, a.posting_date, " \
    #                 "a.baseline_date, a.due_date, a.ap_timespent, convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date, convert_tz(a.end_date, '+00:00','+05:30' ) as end_date, " \
    #                 "a.amount, a.ispaid, a.currency, a.payment_method, a.gl_account, a.business_area, a.supplier_id, a.approver_id, a.supplier_name, a.approver_comments, a.cost_center, " \
    #                 "a.attachment_id, a.taxable_amount, a.discount_per, a.total_discount_amount, a.tcs, a.is_igst, a.tax_per, a.cgst_tot_amt, a.sgst_tot_amt, a.igst_tot_amt, a.tds_per, " \
    #                 "a.tds_tot_amt, a.payment_terms, a.adjustment, a.working_person,a.payment_status, a.supplier_comments, a.npo, a.internal_order, a.department_id, a.app_comment, a.faulty_invoice, " \
    #                 "b.vendor_name, c.ls_name, c.fs_name, d.value2 as document_type " \
    #                 "FROM invoice_header a " \
    #                 "left join vendor_master b " \
    #                 "on a.supplier_id = b.vendor_no " \
    #                 "left join dropdown d " \
    #                 "on a.document_type = d.value1 " \
    #                 "left join member c " \
    #                 "on a.working_person = c.member_id " + condn + " order by a.invoice_no desc limit %s, %s"
            
    #             val_list.append(start_idx)
    #             val_list.append(end_idx)
                
    #             mycursor.execute(sqlQuery, tuple(val_list))
    #             all_invoices = mycursor.fetchall()
                
                
    #             sqlQuery = "SELECT count(*) as total_invoices " \
    #                 "FROM invoice_header a " \
    #                 "left join vendor_master b " \
    #                 "on a.supplier_id = b.vendor_no " \
    #                 "left join member c " \
    #                 "on a.working_person = c.member_id " + condn
                    
    #             val_list.pop()
    #             val_list.pop()
                
    #             mycursor.execute(sqlQuery, tuple(val_list))
    #             count = mycursor.fetchone()
                
    #             invoiceIds = []
    #             postedInvoiceIds = []
        
    #             for each in all_invoices:
    #                 if each['in_status'] == "inapproval":
    #                     invoiceIds.append(each['invoice_no'])
                        
    #                 if each['in_status'] == "tosap":
    #                     postedInvoiceIds.append(each['invoice_no'])
        
    #             format_strings = ','.join(['%s'] * len(invoiceIds))
    #             res = invoiceIds
                
    #             postedFormat_strings = ','.join(['%s'] * len(postedInvoiceIds))
    #             postedRes = postedInvoiceIds
        
    #             groupid = []
    #             memberid = []
    #             approvers_list = []
    #             approversHistory_list = []
        
    #             if res:
    #                 mycursor.execute("select * from approval where invoice_no in ({}) "
    #                         "order by invoice_no, approval_level".format( format_strings), tuple(res))
        
    #                 approvers_list = mycursor.fetchall()
        
    #                 for row in approvers_list:
        
    #                     if row["isgroup"] == 'y':
    #                         groupid.append(row["approver"])
    #                     elif row["isgroup"] == 'n':
    #                         memberid.append(row["approver"])
        
    #                 format_strings_mem = ','.join(['%s'] * len(memberid))
    #                 format_strings_group = ','.join(['%s'] * len(groupid))
        
    #                 approver_final = []
        
    #                 if groupid:
    #                     mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in ({})".format(format_strings_group), tuple(groupid))
        
    #                     for row in mycursor:
    #                         temp1 = {
    #                             "isgroup": "y",
    #                             "approver": row["group_id"],
    #                             "name": row["name"]
    #                         }
    #                         approver_final.append(temp1)
        
    #                 if memberid:
    #                     sqlQuery = "select distinct a.approver, b.member_id, " \
    #                             "b.fs_name, b.ls_name from rule_approver a " \
    #                             "inner join member b on a.approver = b.member_id " \
    #                             "where a.approver in (%s)" % format_strings_mem
        
    #                     mycursor.execute(sqlQuery, tuple(memberid))
        
    #                     for row in mycursor:
    #                         temp1 = {
    #                             "isgroup": "n",
    #                             "approver": row["approver"],
    #                             "name": row["fs_name"] + " " + row["ls_name"]
    #                         }
    #                         approver_final.append(temp1)
                    
    #             if postedRes:
    #                 sqlQuery = "select * from approval_history where invoice_no in ({}) order by invoice_no, approval_level"
    #                 mycursor.execute(sqlQuery.format(postedFormat_strings), tuple(postedRes))
        
    #                 approversHistory_list = mycursor.fetchall()
                    
    #                 for row in approversHistory_list:
        
    #                     if row["isgroup"] == 'y':
    #                         groupid.append(row["approver_id"])
    #                     elif row["isgroup"] == 'n':
    #                         memberid.append(row["approver_id"])
        
    #                 format_strings_mem = ','.join(['%s'] * len(memberid))
    #                 format_strings_group = ','.join(['%s'] * len(groupid))
        
    #                 approverHistory_final = []
        
    #                 if groupid:
    #                     mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in ({})".format(format_strings_group), tuple(groupid))
        
    #                     for row in mycursor:
    #                         temp1 = {
    #                             "isgroup": "y",
    #                             "approver": row["group_id"],
    #                             "name": row["name"]
    #                         }
    #                         approverHistory_final.append(temp1)
        
    #                 if memberid:
    #                     sqlQuery = "select distinct a.approver, b.member_id, " \
    #                             "b.fs_name, b.ls_name from rule_approver a " \
    #                             "inner join member b on a.approver = b.member_id " \
    #                             "where a.approver in (%s)" % format_strings_mem
        
    #                     mycursor.execute(sqlQuery, tuple(memberid))
        
    #                     for row in mycursor:
    #                         temp1 = {
    #                             "isgroup": "n",
    #                             "approver": row["approver"],
    #                             "name": row["fs_name"] + " " + row["ls_name"]
    #                         }
    #                         approverHistory_final.append(temp1)
                
    #             for row in all_invoices:
    #                 approvers = []
                    
    #                 if row["in_status"] == "tosap":
                        
    #                     for temp in approversHistory_list:
    #                         if row["invoice_no"] == temp["invoice_no"]:
                                
    #                             for temp1 in approverHistory_final:
    #                                 if temp["approver_id"] == temp1["approver"] and temp["isgroup"] == temp1["isgroup"]:
            
    #                                     status_ap = {
    #                                         "isgroup": temp1["isgroup"],
    #                                         "approver": temp1["approver"],
    #                                         "name": temp1["name"],
    #                                         "level": temp['approval_level'],
    #                                         "isapproved": "accepted"
    #                                     }
    #                                     approvers.append(status_ap)
                                        
    #                 else:
    #                     for temp in approvers_list:
    #                         if row["invoice_no"] == temp["invoice_no"]:
            
    #                             for temp1 in approver_final:
    #                                 if temp["approver"] == temp1["approver"] and temp["isgroup"] == temp1["isgroup"]:
            
    #                                     if temp["isapproved"] == "y":
    #                                         status = "accepted"
    #                                     elif temp["isapproved"] == 'n':
    #                                         status = "inapproval"
            
    #                                     status_ap = {
    #                                         "isgroup": temp1["isgroup"],
    #                                         "approver": temp1["approver"],
    #                                         "name": temp1["name"],
    #                                         "level": temp['approval_level'],
    #                                         # "isapproved" : temp["isapproved"]
    #                                         "isapproved": status
    #                                     }
    #                                     approvers.append(status_ap)
            
    #                 entry_date = row["entry_date"].date()
    #                 entry_time = row["entry_date"].time()
        
    #                 update_date = row["modified_date"].date()
    #                 update_time = row["modified_date"].time()
                    
    #                 minutes_diff = 0
    #                 if row["end_date"] is not None:
    #                     end_date = row["end_date"].date()
    #                     end_time = row["end_date"].time()
                        
    #                     time_delta = (row["end_date"] - row["entry_date"])
    #                     total_seconds = time_delta.total_seconds()
    #                     minutes_diff = math.ceil(total_seconds / 60)
                        
    #                 else:
    #                     end_date = ""
    #                     end_time = ""
        
    #                 noOfDueDays = None
    #                 noOfOverDueDays = None
    #                 due_amount = 0.00
    #                 overdue_amount = 0.00
    #                 overdue_flag = 'n'
    #                 due_amount = row["amount"]
        
    #                 if type(row["due_date"]) is not str and row["due_date"]:
    #                     now = datetime.date.today()
    #                     noOfDueDays = (row["due_date"] - now).days
        
    #                     if noOfDueDays < 0:
    #                         noOfOverDueDays = abs(noOfDueDays)
    #                         overdue_flag = 'y'
    #                         overdue_amount = row["amount"]         
    #                         due_amount = row["amount"]
    #                     else:
    #                         due_amount = row["amount"]
                            
    #                     if row["in_status"] == "tosap":
    #                         noOfDueDays = "Paid"
    #                         overdue_flag = 'n'
                    
    #                 if row["ls_name"] is None and row["fs_name"] is None:
    #                     user_processing = None
    #                 elif ( row["ls_name"] != None and row["fs_name"] is None ):
    #                     user_processing = row["ls_name"]
    #                 elif ( row["ls_name"] is None and row["fs_name"] != None ):
    #                     user_processing = row["fs_name"]
    #                 else:
    #                     user_processing = row["fs_name"] + " " + row["ls_name"]
        
    #                 data = {
    #                     "company_code": row["company_code"],
    #                     # "plant": row["plant"],
    #                     "document_type": row["document_type"],
    #                     "vendor_no": row["supplier_id"],
    #                     "vendor_name": row["vendor_name"],
    #                     "invoice_no": row["invoice_no"],
    #                     "invoice_date": str(row["invoice_date"]),
    #                     "due_date": str(row["due_date"]),
    #                     "days_to_due": noOfDueDays,
    #                     "entry_date": str(entry_date),
    #                     "entry_time": str(entry_time),
    #                     "update_date": str(update_date),
    #                     "update_time": str(update_time),
    #                     "end_date": str(end_date),
    #                     "end_time": str(end_time),
    #                     "ref_po_num": row["ref_po_num"],
    #                     "npo_flag": row["npo"],
    #                     # "amount": row["amount"],
    #                     "amount": due_amount,
    #                     "currency": row["currency"],
    #                     "payment_terms": row["payment_terms"],
    #                     "overdue_flag": overdue_flag,
    #                     "days_overdue": noOfOverDueDays,
    #                     "amount_overdue": overdue_amount,
    #                     "document_status": row["in_status"],
    #                     "reason_text": row["approver_comments"],
    #                     "payment_status": row["payment_status"],
    #                     "number_of_approvers": len(approvers),
    #                     "approvers": approvers,
    #                     # "user_processing": row["working_person"],
    #                     "user_processing": user_processing,
    #                     "process_duration": minutes_diff
    #                 }
    #                 records.append(data)
                    
    #             responce['records'] = records
    #             responce['total_invoices'] = count['total_invoices']
        
    #     except:
    #         return {
    #             'statuscode': 500,
    #             'body': json.dumps("Internal Error!")
    #         }
        
    #     finally:
    #         mydb.close()

    #     return {
    #         'statuscode': 200,
    #         'body': responce
    #     }

# def getDiaAnalyticReport(event, context):
#     global dbScehma 
#     dbScehma = ' DBADMIN '
    
#     # client = boto3.client(
#     # 'secretsmanager',
#     # region_name='eu-central-1',
#     # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
#     # aws_secret_access_key='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' )
#     # secret = event["stage-variables"]["secreat"]
#     # resp = client.get_secret_value(
#     #     SecretId= secret
#     # )
#     # secretDict = json.loads(resp['SecretString'])

#     mydb = hdbcliConnect()
#     print(event)
#     records = []
#     responce = {}

#     try:
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "set schema " + dbScehma
#             mycursor.execute(defSchemaQuery)
            
#             val_list = []
#             pos = 0
#             condn = ""
            
#             start_idx = int(event["params"]["querystring"]['pageno'])
#             end_idx = int(event["params"]["querystring"]['nooflines'])
                    
#             start_idx = (start_idx -1 ) * end_idx
    
#             if "condn" in event["body-json"]:
#                 for row in event["body-json"]["condn"]:
#                     if pos != 0:
#                         condn = condn + " and "
#                     elif pos == 0:
#                         condn = " where "
#                         pos = pos + 1
        
#                     if str(row["operator"]) == "like":
#                         val_list.append("%" + row["value"] + "%")
#                         if row["field"] == "vendor_no" or row["field"] == "vendor_name":
#                             condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
#                         else:
#                             condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                            
#                     elif str(row["operator"]) == "between":
#                         val_list.append(row["value"])
#                         val_list.append(row["value2"])
#                         condn = condn + "a." + str(row["field"]) + " between %s and %s "
                        
#                     else:
#                         val_list.append(row["value"])
#                         if row["field"] == "vendor_no" or row["field"] == "vendor_name":
#                             condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
#                         else:
#                             condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                    
            
#             sqlQuery = "SELECT a.invoice_no, a.in_status, a.ref_po_num, a.company_code, convert_tz(a.entry_date, '+00:00','+05:30' ) as entry_date, a.invoice_date, a.posting_date, " \
#                 "a.baseline_date, a.due_date, a.ap_timespent, convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date, convert_tz(a.end_date, '+00:00','+05:30' ) as end_date, " \
#                 "a.amount, a.ispaid, a.currency, a.payment_method, a.gl_account, a.business_area, a.supplier_id, a.approver_id, a.supplier_name, a.approver_comments, a.cost_center, " \
#                 "a.attachment_id, a.taxable_amount, a.discount_per, a.total_discount_amount, a.tcs, a.is_igst, a.tax_per, a.cgst_tot_amt, a.sgst_tot_amt, a.igst_tot_amt, a.tds_per, " \
#                 "a.tds_tot_amt, a.payment_terms, a.adjustment, a.working_person,a.payment_status, a.supplier_comments, a.npo, a.internal_order, a.department_id, a.app_comment, a.faulty_invoice, " \
#                 "b.vendor_name, c.ls_name, c.fs_name, d.value2 as document_type " \
#                 "FROM invoice_header a " \
#                 "left join vendor_master b " \
#     			"on a.supplier_id = b.vendor_no " \
#                 "left join dropdown d " \
#     			"on a.document_type = d.value1 " \
#                 "left join member c " \
#                 "on a.working_person = c.member_id " + condn + " order by a.invoice_no desc limit ?, ?"
        
#             val_list.append(start_idx)
#             val_list.append(end_idx)
            
#             mycursor.execute(sqlQuery, tuple(val_list))
#             all_invoices = mycursor.fetchall()
            
            
#             sqlQuery = "SELECT count(*) as total_invoices " \
#                 "FROM invoice_header a " \
#                 "left join vendor_master b " \
#     			"on a.supplier_id = b.vendor_no " \
#                 "left join member c " \
#                 "on a.working_person = c.member_id " + condn
                
#             val_list.pop()
#             val_list.pop()
            
#             mycursor.execute(sqlQuery, tuple(val_list))
#             count = mycursor.fetchone()
            
#             invoiceIds = []
#             postedInvoiceIds = []
    
#             for each in all_invoices:
#                 if each['in_status'] == "inapproval":
#                     invoiceIds.append(each['invoice_no'])
                    
#                 if each['in_status'] == "tosap":
#                     postedInvoiceIds.append(each['invoice_no'])
    
#             format_strings = ','.join(['%s'] * len(invoiceIds))
#             res = invoiceIds
            
#             postedFormat_strings = ','.join(['%s'] * len(postedInvoiceIds))
#             postedRes = postedInvoiceIds
    
#             groupid = []
#             memberid = []
#             approvers_list = []
#             approversHistory_list = []
    
#             if res:
#                 mycursor.execute("select * from approval where invoice_no in {} "
#                         "order by invoice_no, approval_level".format( format_strings), tuple(res))
    
#                 approvers_list = mycursor.fetchall()
    
#                 for row in approvers_list:
    
#                     if row["isgroup"] == 'y':
#                         groupid.append(row["approver"])
#                     elif row["isgroup"] == 'n':
#                         memberid.append(row["approver"])
    
#                 format_strings_mem = ','.join(['%s'] * len(memberid))
#                 format_strings_group = ','.join(['%s'] * len(groupid))
    
#                 approver_final = []
    
#                 if groupid:
#                     mycursor.execute('select group_id, name from "GROUP" where group_id in {}'.format(format_strings_group), tuple(groupid))
    
#                     for row in mycursor:
#                         temp1 = {
#                             "isgroup": "y",
#                             "approver": row["group_id"],
#                             "name": row["name"]
#                         }
#                         approver_final.append(temp1)
    
#                 if memberid:
#                     sqlQuery = "select distinct a.approver, b.member_id, " \
#                                "b.fs_name, b.ls_name from rule_approver a " \
#                                "inner join member b on a.approver = b.member_id " \
#                                "where a.approver in (?)" % format_strings_mem
    
#                     mycursor.execute(sqlQuery, tuple(memberid))
    
#                     for row in mycursor:
#                         temp1 = {
#                             "isgroup": "n",
#                             "approver": row["approver"],
#                             "name": row["fs_name"] + " " + row["ls_name"]
#                         }
#                         approver_final.append(temp1)
                
#             if postedRes:
#                 sqlQuery = "select * from approval_history where invoice_no in {} order by invoice_no, approval_level"
#                 mycursor.execute(sqlQuery.format(postedFormat_strings), tuple(postedRes))
    
#                 approversHistory_list = mycursor.fetchall()
                
#                 for row in approversHistory_list:
    
#                     if row["isgroup"] == 'y':
#                         groupid.append(row["approver_id"])
#                     elif row["isgroup"] == 'n':
#                         memberid.append(row["approver_id"])
    
#                 format_strings_mem = ','.join(['%s'] * len(memberid))
#                 format_strings_group = ','.join(['%s'] * len(groupid))
    
#                 approverHistory_final = []
    
#                 if groupid:
#                     mycursor.execute('select group_id, name from "GROUP" where group_id in {}'.format(format_strings_group), tuple(groupid))
    
#                     for row in mycursor:
#                         temp1 = {
#                             "isgroup": "y",
#                             "approver": row["group_id"],
#                             "name": row["name"]
#                         }
#                         approverHistory_final.append(temp1)
    
#                 if memberid:
#                     sqlQuery = "select distinct a.approver, b.member_id, " \
#                                "b.fs_name, b.ls_name from rule_approver a " \
#                                "inner join member b on a.approver = b.member_id " \
#                                "where a.approver in (?)" % format_strings_mem
    
#                     mycursor.execute(sqlQuery, tuple(memberid))
    
#                     for row in mycursor:
#                         temp1 = {
#                             "isgroup": "n",
#                             "approver": row["approver"],
#                             "name": row["fs_name"] + " " + row["ls_name"]
#                         }
#                         approverHistory_final.append(temp1)
            
#             for row in all_invoices:
#                 approvers = []
                
#                 if row["in_status"] == "tosap":
                    
#                     for temp in approversHistory_list:
#                         if row["invoice_no"] == temp["invoice_no"]:
                            
#                             for temp1 in approverHistory_final:
#                                 if temp["approver_id"] == temp1["approver"] and temp["isgroup"] == temp1["isgroup"]:
        
#                                     status_ap = {
#                                         "isgroup": temp1["isgroup"],
#                                         "approver": temp1["approver"],
#                                         "name": temp1["name"],
#                                         "level": temp['approval_level'],
#                                         "isapproved": "accepted"
#                                     }
#                                     approvers.append(status_ap)
                                    
#                 else:
#                     for temp in approvers_list:
#                         if row["invoice_no"] == temp["invoice_no"]:
        
#                             for temp1 in approver_final:
#                                 if temp["approver"] == temp1["approver"] and temp["isgroup"] == temp1["isgroup"]:
        
#                                     if temp["isapproved"] == "y":
#                                         status = "accepted"
#                                     elif temp["isapproved"] == 'n':
#                                         status = "inapproval"
        
#                                     status_ap = {
#                                         "isgroup": temp1["isgroup"],
#                                         "approver": temp1["approver"],
#                                         "name": temp1["name"],
#                                         "level": temp['approval_level'],
#                                         # "isapproved" : temp["isapproved"]
#                                         "isapproved": status
#                                     }
#                                     approvers.append(status_ap)
        
#                 entry_date = row["entry_date"].date()
#                 entry_time = row["entry_date"].time()
    
#                 update_date = row["modified_date"].date()
#                 update_time = row["modified_date"].time()
                
#                 minutes_diff = 0
#                 if row["end_date"] is not None:
#                     end_date = row["end_date"].date()
#                     end_time = row["end_date"].time()
                    
#                     time_delta = (row["end_date"] - row["entry_date"])
#                     total_seconds = time_delta.total_seconds()
#                     minutes_diff = math.ceil(total_seconds / 60)
                    
#                 else:
#                     end_date = ""
#                     end_time = ""
    
#                 noOfDueDays = None
#                 noOfOverDueDays = None
#                 due_amount = 0.00
#                 overdue_amount = 0.00
#                 overdue_flag = 'n'
#                 due_amount = row["amount"]
    
#                 if type(row["due_date"]) is not str and row["due_date"]:
#                     now = datetime.date.today()
#                     noOfDueDays = (row["due_date"] - now).days
    
#                     if noOfDueDays < 0:
#                         noOfOverDueDays = abs(noOfDueDays)
#                         overdue_flag = 'y'
#                         overdue_amount = row["amount"]         
#                         due_amount = row["amount"]
#                     else:
#                         due_amount = row["amount"]
                        
#                     if row["in_status"] == "tosap":
#                         noOfDueDays = "Paid"
#                         overdue_flag = 'n'
                
#                 if row["ls_name"] is None and row["fs_name"] is None:
#                     user_processing = None
#                 elif ( row["ls_name"] != None and row["fs_name"] is None ):
#                     user_processing = row["ls_name"]
#                 elif ( row["ls_name"] is None and row["fs_name"] != None ):
#                     user_processing = row["fs_name"]
#                 else:
#                     user_processing = row["fs_name"] + " " + row["ls_name"]
    
#                 data = {
#                     "company_code": row["company_code"],
#                     # "plant": row["plant"],
#                     "document_type": row["document_type"],
#                     "vendor_no": row["supplier_id"],
#                     "vendor_name": row["vendor_name"],
#                     "invoice_no": row["invoice_no"],
#                     "invoice_date": str(row["invoice_date"]),
#                     "due_date": str(row["due_date"]),
#                     "days_to_due": noOfDueDays,
#                     "entry_date": str(entry_date),
#                     "entry_time": str(entry_time),
#                     "update_date": str(update_date),
#                     "update_time": str(update_time),
#                     "end_date": str(end_date),
#                     "end_time": str(end_time),
#                     "ref_po_num": row["ref_po_num"],
#                     "npo_flag": row["npo"],
#                     # "amount": row["amount"],
#                     "amount": due_amount,
#                     "currency": row["currency"],
#                     "payment_terms": row["payment_terms"],
#                     "overdue_flag": overdue_flag,
#                     "days_overdue": noOfOverDueDays,
#                     "amount_overdue": overdue_amount,
#                     "document_status": row["in_status"],
#                     "reason_text": row["approver_comments"],
#                     "payment_status": row["payment_status"],
#                     "number_of_approvers": len(approvers),
#                     "approvers": approvers,
#                     # "user_processing": row["working_person"],
#                     "user_processing": user_processing,
#                     "process_duration": minutes_diff
#                 }
#                 records.append(data)
                
#             responce['records'] = records
#             responce['total_invoices'] = count['total_invoices']
    
#     except:
#         return {
#             'statuscode': 500,
#             'body': json.dumps("Internal Error!")
#         }
    
#     finally:
#         mydb.close()

#     return {
#         'statuscode': 200,
#         'body': responce
#     }

# #complex query
# def getKeyProcessAnalyticsReport(event, context):
#     global dbScehma 
#     dbScehma = ' DBADMIN '
    
#     # client = boto3.client(
#     # 'secretsmanager',
#     # region_name='eu-central-1',
#     # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
#     # aws_secret_access_key='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' )
#     # secret = event["stage-variables"]["secreat"]
#     # resp = client.get_secret_value(
#     #     SecretId= secret
#     # )
#     # secretDict = json.loads(resp['SecretString'])

#     mydb = hdbcliConnect()

#     records = {}
#     output1 = []
#     output2 = []
#     output3 = []

#     try:
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "set schema " + dbScehma
#             mycursor.execute(defSchemaQuery)
            
#             mycursor.execute("select * FROM elipo_setting where key_name = 'payment_status'")
#             payment_status_value = mycursor.fetchone()
            
#             val_list = []
#             pos = 0
#             condn = ""
    
#             if "condn" in event["body-json"]:
#                 for row in event["body-json"]["condn"]:
                    
#                     condn = condn + " and "
                    
#                     if str(row["operator"]) == "like":
#                         val_list.append("%" + row["value"] + "%")
#                         condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                        
#                     elif str(row["operator"]) == "between":
#                         val_list.append(row["value2"])
#                         val_list.append(row["value"])
#                         condn = condn + "date(" + str(row["field"]) + ") between %s and %s " 
                        
#                     else:
#                         val_list.append(row["value"])
#                         condn = condn + "" + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
               
#             if 'entry_date' not in condn:
#                 condn = condn + " and entry_date > now() - interval 1 month"
            
#             sqlQuery = "select sum(amount) as total_amount, b.vendor_name, b.currency, b.vendor_no, b.source_of_supply " \
#                 "from invoice_header " \
#                 "inner join vendor_master b " \
#                 "on supplier_id = b.vendor_no "
                
#             if payment_status_value and (payment_status_value['value1'] == 'on'):
#                 sqlQuery += " where (in_status = 'tosap' and payment_status = 'paid') and document_type = 'RE' " + condn + " group by supplier_id order by total_amount desc, b.currency limit 5"
#             else:
#                 sqlQuery += " where in_status = 'tosap' and document_type = 'RE' " + condn + " group by supplier_id order by total_amount desc, b.currency limit 5"
            
#             mycursor.execute(sqlQuery, tuple(val_list))
#             raw_data = mycursor.fetchall()
            
#             if raw_data:
#                 output1 = []
#                 for row in raw_data:
#                     data = {
#                         "vendor_no": row["vendor_no"],
#                         "vendor_name": row["vendor_name"],
#                         "source_of_supply": row["source_of_supply"],
#                         "total_amount": row["total_amount"],
#                         "currency": row["currency"]
#                     }
#                     output1.append(data)
                
#             sqlQuery = "select invoice_no, in_status, ref_po_num, due_date, amount, npo " \
#                 "from invoice_header " \
#                 "where in_status != 'deleted' and document_type = 'RE' " + condn
                
#             mycursor.execute(sqlQuery, tuple(val_list))
#             raw_data1 = mycursor.fetchall()
            
#             sqlQuery = "select sum(amount) as total from invoice_header "
            
#             if payment_status_value and (payment_status_value['value1'] == 'on'):
#                 sqlQuery += " where (in_status = 'tosap' and payment_status = 'paid') and document_type = 'RE' " + condn
#             else:
#                 sqlQuery += " where in_status = 'tosap' and document_type = 'RE' " + condn
                
#             mycursor.execute(sqlQuery, tuple(val_list))
#             processed_amount = mycursor.fetchone()
            
#             output2 = {}
#             output3 = {}
            
#             flag = None
            
#             inprocess_po = 0
#             inprocess_npo = 0
#             inprocess_none = 0
#             processed_po = 0
#             processed_npo = 0
#             processed_none = 0
            
#             current_po = 0
#             current_npo = 0
#             current_none = 0
#             overdue_po = 0
#             overdue_npo = 0
#             overdue_none = 0
            
#             for row in raw_data1:
#                 today = date.today()
#                 flag = None
                
#                 if row["npo"] == 'y':
#                     flag = 'npo'
                
#                 elif row["ref_po_num"] != '' or row["ref_po_num"] != None :
#                     flag = 'po'
                
#                 if row["in_status"] == "new" or row["in_status"] == "draft" or row["in_status"] == "inapproval":
#                     if flag == "npo":
#                         inprocess_npo = inprocess_npo + 1
                    
#                     elif flag == "po":
#                         inprocess_po = inprocess_po + 1
                    
#                 elif row["in_status"] == "tosap":
#                     if flag == "npo":
#                         processed_npo = processed_npo + 1
                        
#                     elif flag == "po":
#                         processed_po = processed_po + 1
                        
#                 if row["due_date"] != None and type(row["due_date"]) is not str:
#                     if today <= row["due_date"]:
#                         if flag == "npo":
#                             current_npo = current_npo + row["amount"]
                            
#                         elif flag == "po":
#                             current_po = current_po + row["amount"]
                        
#                     elif today > row["due_date"]:
#                         if flag == "npo":
#                             overdue_npo = overdue_npo + row["amount"]
                            
#                         elif flag == "po":
#                             overdue_po = overdue_po + row["amount"]
                            
#             output2 = {
#                 "inprocess_npo": inprocess_npo,
#                 "inprocess_po": inprocess_po,
#                 "inprocess_total":  inprocess_npo + inprocess_po,
                
#                 "processed_npo": processed_npo,
#                 "processed_po": processed_po,
#                 "processed_total": processed_npo + processed_po,
                
#                 "total_po": inprocess_po + processed_po,
#                 "total_npo": inprocess_npo + processed_npo,
#                 "total_all":  inprocess_npo + inprocess_po + processed_npo + processed_po
#             }
            
#             output3 = {
#                 "current_liability_po": current_po,
#                 "current_liability_npo": current_npo,
#                 "total_current_liability": current_po + current_npo,
                
#                 "overdue_po": overdue_po,
#                 "overdue_npo": overdue_npo,
#                 "total_overdue": overdue_po + overdue_npo,
                
#                 "total_po": current_po + overdue_po,
#                 "total_npo": current_npo + overdue_npo,
#                 "total_liability": current_po + current_npo + overdue_po + overdue_npo,
                
#                 "total_processed_amount": processed_amount["total"]
#             }
                
#             records = {
#                 "output1": output1,
#                 "output2": output2,
#                 "output3": output3
#             }
            
#     except:
#         return {
#             'statuscode': 500,
#             'body': json.dumps("Internal Error!")
#         }
            
#     finally:
#         mydb.close()

#     return {
#         'statuscode': 200,
#         'body': records
#     }

# #complex query
# def getLiabilityReportDetails(event, context):
#     global dbScehma 
#     dbScehma = ' DBADMIN '
    
#     # client = boto3.client(
#     # 'secretsmanager',
#     # region_name='eu-central-1',
#     # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
#     # aws_secret_access_key='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' )
#     # secret = event["stage-variables"]["secreat"]
#     # resp = client.get_secret_value(
#     #     SecretId= secret
#     # )
#     # secretDict = json.loads(resp['SecretString'])

#     mydb = hdbcliConnect()

#     records = []

#     try:
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "set schema " + dbScehma
#             mycursor.execute(defSchemaQuery)
            
#             val_list = []
#             pos = 0
#             condn = ""
    
#             if "condn" in event["body-json"]:
#                 for row in event["body-json"]["condn"]:
#                     condn = condn + " and "
                    
#                     if str(row["operator"]) == "like":
#                         val_list.append("%" + row["value"] + "%")
                        
#                     elif str(row["operator"]) == "between":
#                         val_list.append(row["value"])
#                         val_list.append(row["value2"])
                        
#                     else:
#                         val_list.append(row["value"])
                        
#                     if row["field"] == "company_code" or row["field"] == "amount":
#                         if str(row["operator"]) == "between":
#                             condn = condn + "b." + str(row["field"]) + " between %s and %s "
#                         else:
#                             condn = condn + "b." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s "
#                     else:
#                         condn = condn + "a." + str(row["field"]) + " " + str(row["operator"]) + " " + "%s "
                        
#             sqlQuery = "select a.vendor_no, a.vendor_name, b.currency " \
#             	"from vendor_master a " \
#             	"inner join invoice_header b " \
#             	"on a.vendor_no = b.supplier_id " \
#             	"where b.in_status != 'deleted' and b.document_type = 'RE' and (datediff( date(b.due_date), curdate() ) < 0) and b.in_status != 'tosap' " + condn + \
#                 "group by a.vendor_no, b.currency " \
#                 "order by a.vendor_no"
                
#             mycursor.execute(sqlQuery, tuple(val_list))
#             overdue_company = mycursor.fetchall()
            
#             sqlQuery = "select a.vendor_no, a.vendor_name, count(b.invoice_no) as total_no_of_invoice, b.invoice_date, b.due_date, b.company_code, b.amount, b.currency, " \
#             	"sum(case when ( (datediff( date(b.due_date), curdate() ) >= 0) and b.in_status != 'tosap' )then b.amount else 0 end) as due_amount, " \
#                 "sum(case when ( (datediff( date(b.due_date), curdate() ) < 0) and b.in_status != 'tosap' )then b.amount else 0 end) as overdue_amount, " \
#                 "sum(case when ( b.in_status = 'tosap' and b.payment_status = 'unpaid' )then b.amount else 0 end) as processed_amount, " \
#                 "sum(case when ( b.in_status = 'tosap' and b.payment_status = 'paid' )then b.amount else 0 end) as paid_amount, " \
#                 "sum(case when ( (datediff( date(b.due_date), curdate() ) >= 0) and b.in_status != 'tosap' )then 1 else 0 end) as due_invoice, " \
#                 "sum(case when ( (datediff( date(b.due_date), curdate() ) < 0) and b.in_status != 'tosap' )then 1 else 0 end) as overdue_invoice, " \
#                 "sum(case when ( b.in_status = 'tosap' and b.payment_status = 'unpaid' )then 1 else 0 end) as processed_invoice, " \
#                 "sum(case when ( b.in_status = 'tosap' and b.payment_status = 'paid' )then 1 else 0 end) as paid_invoice " \
#             	"from vendor_master a " \
#             	"inner join invoice_header b " \
#             	"on a.vendor_no = b.supplier_id " \
#             	"where b.in_status != 'deleted' and b.document_type = 'RE' " + condn + \
#                 "group by a.vendor_no, b.currency " \
#                 "order by due_amount desc"
                
#             mycursor.execute(sqlQuery, tuple(val_list))
            
#             for row in mycursor :
#                 overdue_flag = 'n'
#                 for data in overdue_company:
#                     if row["vendor_no"] == data["vendor_no"] and row["currency"] == data["currency"]:
#                         overdue_flag = 'y'
#                         break
                
#                 data = {
#                     "company_code": row["company_code"],
#                     "vendor_no": row["vendor_no"],
#                     "vendor_name": str(row["vendor_name"]) + " (" + row["currency"] + ")",
#                     "total_no_of_invoice": row["due_invoice"] + row["overdue_invoice"] + row["processed_invoice"] + row["paid_invoice"],
#                     "total_amount": row["due_amount"] + row["overdue_amount"] + row["processed_amount"] + row["paid_amount"],
#                     "currency": row["currency"],
#                     "total_amt_paid": row["processed_amount"],
#                     "total_no_of_invoice_paid": row["processed_invoice"],
#                     "total_due_amount":row["due_amount"] ,
#                     "total_no_of_invoice_due": row["due_invoice"],
#                     "total_over_due_amount": row["overdue_amount"],
#                     "total_no_of_invoice_due_crossed": row["overdue_invoice"],
#                     "total_paid_amount": row["paid_amount"],
#                     "total_no_of_paid_invoice": row["paid_invoice"],
#                     "overdue_flag": overdue_flag
#                 }
#                 records.append(data) 
                    
#     except:
#         return {
#             'statuscode': 500,
#             'body': json.dumps("Internal Error!")
#         }
                    
#     finally:
#         mydb.close()

#     return {
#         'statuscode': 200,
#         'body': records
#     }

# def getLiabilityGraphBasedOnAmount(event, context):
#     global dbScehma 
#     dbScehma = '"DBADMIN"'
    
#     mydb = hdbcliConnect()
    
#     records = {}
    
#     try:
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "set schema " + dbScehma
#             mycursor.execute(defSchemaQuery)
            
#             if "fiscal_year" in event["params"]["querystring"] and "fiscal_year" != "":
#                 year = event["params"]["querystring"]["fiscal_year"]
                
#             else:
#                 year = datetime.now().year
            
#             if "company_code" in event["params"]["querystring"] and "company_code" != "":
#                 company_code = event["params"]["querystring"]["company_code"]
            
#             sqlQuery = "SELECT sum(case when in_status = 'tosap' then amount else 0 end) as processed_amount, " \
#                 "sum(case when in_status != 'tosap' and curdate() > baseline_date then amount else 0 end) as op_overdue_amount, " \
#                 "sum(case when in_status != 'tosap' and curdate() <= baseline_date then amount else 0 end) as op_due_amount, " \
#                 "sum(case when curdate() > baseline_date then amount else 0 end) as overdue_amount, " \
#                 "sum(case when curdate() <= baseline_date then amount else 0 end) as due_amount " \
#                 "FROM invoice_header " \
#                 "where in_status != 'deleted' and document_type != 'RE' and year(invoice_date) = ? and company_code = ?"
            
#             values = (year, company_code)
#             mycursor.execute(sqlQuery, values)
#             data = mycursor.fetchone()
            
#             output1 = {}
#             output2 = {}
            
#             if data["processed_amount"] == None or data["processed_amount"] == "":
#                 data["processed_amount"] = 0
                
#             if data["op_overdue_amount"] == None or data["op_overdue_amount"] == "":
#                 data["op_overdue_amount"] = 0
                
#             if data["op_due_amount"] == None or data["op_due_amount"] == "":
#                 data["op_due_amount"] = 0
                
#             if data["overdue_amount"] == None or data["overdue_amount"] =="":
#                 data["overdue_amount"] = 0
            
#             if data["due_amount"] == None or data["due_amount"] == "":
#                 data["due_amount"] = 0
            
#             output1 = {
#                 "processed_amount": data["processed_amount"],
#                 "overdue_amount": data["op_overdue_amount"],
#                 "due_amount": data["op_due_amount"]
#             }
            
#             output2 = {
#                 "overdue_amount": data["op_overdue_amount"],
#                 "due_amount": data["op_due_amount"]
#             }
            
#             sqlQuery = "SELECT b.vendor_no, b.vendor_name, sum(a.amount) as total_amount, " \
#             	"sum(case when a.in_status = 'tosap' then a.amount else 0 end) as processed_amount, " \
#             	"sum(case when curdate() > a.baseline_date then a.amount else 0 end) as overdue_amount, " \
#                 "sum(case when curdate() <= a.baseline_date then a.amount else 0 end) as due_amount " \
#                 "FROM invoice_header a " \
#                 "inner join vendor_master b " \
#                 "on a.supplier_id = b.vendor_no " \
#                 "where a.in_status != 'deleted' and document_type != 'RE' and year(a.invoice_date) = ? and company_code = ? " \
#                 "group by b.vendor_no " \
#                 "order by due_amount desc, overdue_amount desc " \
#                 "limit 5"
            
#             values = (year, company_code)
#             mycursor.execute(sqlQuery, values)
#             data1 = mycursor.fetchall()
            
#             output3 = []
#             for row in data1:
#                 value = {
#                     "vendor_no": row["vendor_no"],
#                     "vendor_name": row["vendor_name"],
#                     "total_amount": row["total_amount"],
#                     "processed_amount": row["processed_amount"],
#                     "overdue_amount": row["overdue_amount"],
#                     "due_amount": row["due_amount"]
#                 }
#                 output3.append(value)
            
#             records = {
#                 "TotalAccountsPayable": output1,
#                 "LiabilityBasedOnAmount": output2,
#                 "VendorLiabilityReportforCompanyCode": output3
#             }
            
#     # except:
#     #     return {
#     #         'statuscode': 500,
#     #         'body': json.dumps("Internal Error!")
#     #     }
            
#     finally:
#         mydb.close()

#     return {
#         'statuscode': 200,
#         'body': records
#     }


#singapore region

#einvoice_ocr and  #myapppkn

def startJob(s3BucketName, objectName):
    response = None
    client = boto3.client('textract')
    response = client.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': s3BucketName,
            'Name': objectName
        }
    })

    return response["JobId"]

def isJobComplete(jobId):
    print(jobId)
    # For production use cases, use SNS based notification 
    # Details at: https://docs.aws.amazon.com/textract/latest/dg/api-async.html
    time.sleep(5)
    client = boto3.client('textract')
    # response = client.get_document_text_detection(JobId=jobId)
    response = client.get_document_analysis(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(5)
        # response = client.get_document_text_detection(JobId=jobId)
        response = client.get_document_analysis(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))

    return status

def getJobResults(jobId):

    pages = []

    client = boto3.client('textract')
    # response = client.get_document_text_detection(JobId=jobId)
    response = client.get_document_analysis(JobId=jobId) 
    
    pages.append(response)
    print("Resultset page recieved: {}".format(len(pages)))
    nextToken = None
    if('NextToken' in response):
        nextToken = response['NextToken']

    while(nextToken):

        # response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)
        response = client.get_document_analysis(JobId=jobId, NextToken=nextToken)

        pages.append(response)
        print("Resultset page recieved: {}".format(len(pages)))
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']

    return pages
    
def get_kv_map(blocks):
    
    key_map = {}
    value_map = {}
    block_map = {}
    # table_blocks = []
    
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block
        # elif block['BlockType'] == "TABLE":
        #     table_blocks.append(block)

    # return key_map, value_map, block_map, table_blocks
    return key_map, value_map, block_map
    
def get_kv_relationship(key_map, value_map, block_map):
    kvs = {}
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key] = val
    return kvs


def find_value_block(key_block, value_map):
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                value_block = value_map[value_id]
    return value_block


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '    

                                
    return text
    
def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                        
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows
    
def generate_table(table_blocks, blocks_map):
    
    text_data = ""

    for index, table in enumerate(table_blocks):
        rows = get_rows_columns_map(table, blocks_map)
        
        for row_index, cols in rows.items():
            for col_index, text in cols.items():
                print(text)
                # text_data = text_data + str(text)
                
    # return text_data

def search_kvs(kvs, searchKeys):
    
    matching_keys = []
    
    for key, value in kvs.items():
        
        print(str(key),len(key))
        
        for skey in searchKeys:
            if re.search(skey, key, re.IGNORECASE):
                key_val = {
                    'key' : key,
                    'value' : value
                }
                matching_keys.append(key_val)
        
        # if str(key) in searchKeys:
        #     key_val = {
        #         'key' : key,
        #         'value' : value
        #     }
        #     matching_keys.append(key_val)
            
    return matching_keys
    
def print_kvs(kvs,mycursor):
    
    values = []
    
    for key, value in kvs.items():
        # print(key, ":", value)
        record = (2, "key-value", key, value)
        values.append(record)
        
    # if values:  
    #     print("values ok")
    #     try:
            
    #         mycursor.executemany("INSERT INTO einvoice_db_portal.aws_textract (file_id, type, value1, value2) VALUES(%s, %s, %s, %s)", values)
    #         # mydb.commit()
           
    #     # except:
    #         # print("exception")
            
    #     finally:
    #         pass
    #         # mydb.close()

def s3_file_upload(body, s3BucketName):
    
    try:
        if body:
            
            post_data = base64.b64decode(body)
            
            if "Content-Type" in event["headers"]:
                
                content_type = event["headers"]["Content-Type"]
                ct = "Content-Type: "+content_type+"\n"
                
                
            elif "content-type" in event["headers"]:
               
                content_type = event["headers"]["content-type"]
                ct = "content-type: "+content_type+"\n"
              
                
            if ct:
                
                msg = email.message_from_bytes(ct.encode()+post_data)
                
                if msg.is_multipart():
                    
                    multipart_content = {}
                    
                    for part in msg.get_payload():
                        
                        multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)
                    
                    file_id = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["file_id"])))
                    file_name = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["file_name"]))) 
                    mime_type = " ".join(re.findall("(?<=')[^']+(?=')", str(multipart_content["mime_type"]))) 
                    print(invoice_no, file_name, mime_type)
                    
                    up_file_name = str(file_id) + file_name
                    
                    s3_upload = s3.put_object(Bucket="einvoice-attachments", Key=s3BucketName, Body=multipart_content["file"])    
                    
                    return up_file_name
    
    # except:
    #     return None
                    
    finally:
        pass

def einvoice_ocr(event, context):
    # Document
    s3BucketName = "textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db"
    documentName = "ecs_invoice.pdf"
    
    # documentName = s3_file_upload(event["body"], s3BucketName)
    
    # jobId = startJob(s3BucketName, documentName)
    # print("Started job with id: {}".format(jobId))
    # if(isJobComplete(jobId)):
    #     response = getJobResults(jobId)
    
    if documentName:
        
        client = boto3.client('textract')
        jobId = client.start_document_analysis(
            DocumentLocation={
                'S3Object': {
                    'Bucket': s3BucketName,
                    'Name': documentName,
                    # 'Version': 'string'
                }
            },
            FeatureTypes=[
                'TABLES','FORMS',
            ])
        
    # print(jobId)
    
    # response = client.
        if(isJobComplete(jobId['JobId'])):
            response = getJobResults(jobId['JobId'])
        
    # print(response)
        
    # doc = Document(response)
    
    # for page in doc.pages:
    #     # Print fields
    #     print("Fields:")
    #     for field in page.form.fields:
    #         print("Key: {}, Value: {}".format(field.key, field.value))
    
        # # Get field by key
        # print("\nGet Field by Key:")
        # key = "Phone Number:"
        # field = page.form.getFieldByKey(key)
        # if(field):
        #     print("Key: {}, Value: {}".format(field.key, field.value))
    
        # # Search fields by key
        # print("\nSearch Fields:")
        # key = "address"
        # fields = page.form.searchFieldsByKey(key)
        # for field in fields:
        #     print("Key: {}, Value: {}".format(field.key, field.value))
    
    #print(response)
    
#     # Print detected text
#     text_data = ""
    
#     for resultPage in response:
#         # print(resultPage)
#         for item in resultPage["Blocks"]:
#             if item["BlockType"] == "LINE":
#                 text_data = text_data + str(item["Text"])  
#             # print(item)
#             # print(item["BlockType"])
#             # if item["BlockType"] == "LINE":
# #                 # print ('\033[94m' +  item["Text"] + '\033[0m')
# #                 print(item["Text"])

#     print("!!!!!!!!!!text in file !!!!!!!!!!!!")
#     print(text_data)
#     comprehend = boto3.client('comprehend')
#     print("detect_entities")
#     response = comprehend.detect_entities(Text = text_data, LanguageCode = "en")
#     print(response)
#     print("detect_key_phrases")
#     response = comprehend.detect_key_phrases(Text = text_data, LanguageCode = "en")
#     print("")
    
    # print(response) 
    # blocks = response["Blocks"]   #comment ed 8/5
    
    # for item in resultPage["Blocks"]:
        
    ##commented today 8/5
    # key_map, value_map, block_map, table_blocks = get_kv_map(response["Blocks"])
    
    # print(response)
    for page in response:
        key_map, value_map, block_map = get_kv_map(page['Blocks'])
    
    kvs = get_kv_relationship(key_map, value_map, block_map)
    print("\n\n== FOUND KEY : VALUE pairs ===\n")
    
    searchKeys = ["invoice","date","PAN: ","Bill No.: ","Authorised by: ","Request Date : ","Request Date ","Amount: ","AMOUNT ","Service Accounting Code : "]
    print_kvs(kvs,searchKeys)
    
    print("matching keys")
    print(search_kvs(kvs, searchKeys))
    # print("tables")
    # generate_table(table_blocks, block_map)
    
    ##commented today 8/5 end
    
    # client = boto3.client('secretsmanager')
    
    # resp = client.get_secret_value(
    #     SecretId='test/einvoice/secret'
    # )
    
    # secretDict = json.loads(resp['SecretString'])
    
    # mydb = pymysql.connect(
    #     host=secretDict['host'],
    #     user=secretDict['username'],
    #     passwd=secretDict['password'],
    #     database=secretDict['dbname'],
    #     charset='utf8mb4',
    #     cursorclass=pymysql.cursors.DictCursor
    # )
    # mydb = pymysql.connect(
    #     host="db-dev-einvoice.cwbsvhy5n8rm.eu-central-1.rds.amazonaws.com",
    #     user="einvoice_user",
    #     passwd="peol12345",
    #     database="einvoice_db_portal",
    #     charset='utf8mb4',
    #     cursorclass=pymysql.cursors.DictCursor
    # )
    
    # try:
    #     with mydb.cursor() as mycursor:
    
    #         print("\n\n== FOUND KEY : VALUE pairs ===\n")
    #         print_kvs(kvs,mycursor)
            
    # finally:
    #     mydb.commit()
    #     mydb.close()

    
    
    
    
    

    
    
    # s3 = boto3.client('s3')
    
    # s3.get_object(Bucket="file-bucket-emp", Key="ECS Invoice.pdf")
    
    # s3BucketName = "textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db"
    # documentName = "ecs_invoice.pdf"
    
    # textract = boto3.client('textract')
    
    # response = textract.start_document_text_detection(
    # DocumentLocation={
    #             'S3Object': {
    #                 'Bucket': s3BucketName,
    #                 'Name': documentName
    #             }
    #         })
    # # Document={
    # #     'S3Object': {
    # #         'Bucket': s3BucketName,
    # #         'Name': documentName
    # #     }
    # # })

    # print(response)
    
    # Print detected text
    # for item in response["Blocks"]:
    #     if item["BlockType"] == "LINE":
    #         print ('\033[94m' +  item["Text"] + '\033[0m')
    
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

#revision

def getTextFromS3PDF(event, context):
    # patcher.patch_all()
    client = boto3.client('events',region_name='eu-central-1',
                    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
                    aws_secret_access_key='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')
    response = client.put_events(
        Entries=[
            {
                'Source': 'foo',
                'DetailType': 'foo',
                'Detail': '{\"foo\": \"foo\"}'
            },
        ]
    )
    # print('..............................')
    print(event)  
    
    # secret = os.environ.get('secret')

    secret = 'test/einvoice/secret'

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # resp = client.get_secret_value(
    #     SecretId=secret
    # )

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    if mydb:

        try:
            with mydb.cursor() as mycursor:
                # bucket = "s3-event-notify-s3bucket-11n8dhktkj0ci"
                if 's3' in event['Records'][0]:
                    bucket = event['Records'][0]['s3']['bucket']['name']
                    key = str(urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8'))
                else:
                    bucket1 = event['Records'][0]['Sns']['Message']
                    bucket2 = bucket1.split(":")[24]
                    bucket3 = bucket2.split(",")[0]
                    bucket = bucket3.replace('"',"")
                            
            
                    key1 = bucket1.split(":")[34]
                    key2 = key1.split(",")[0]
                    key3 = key2.replace('"',"")
                    key = str(urllib.parse.unquote_plus(key3))
                
              
                
                ocr_folder_name = key.split('/')
                    
                values = (ocr_folder_name[0],)
                ocr_fol = []
                mycursor.execute('select * from schemas_confg where ocr_folder = ?', values)
                ocr_folder = mycursor.fetchone()  
                ocr_fol.append(ocr_folder)
                ocr_folder = convertValuesTodict(mycursor.description,ocr_fol)
                ocr_folder = ocr_folder[0]
                    
                defSchemaQuery = "set schema DBADMIN "
                mycursor.execute(defSchemaQuery)    

                mycursor.execute("SELECT * FROM elipo_setting where key_name = 'elipo_ocr'")
                ocr_det = mycursor.fetchone()

                # print(ocr_det)

                if ocr_det and ocr_det['value1'] == "textract":

                    mycursor.execute("SELECT * FROM aws_textract")
                    aws_data = mycursor.fetchall()

                    awsdata = {}

                    for each in aws_data:
                        awsdata[each['resname']] = each['value1']

                    del aws_data

                    if awsdata:

                        # print("Triggered getTextFromS3PDF event: " + json.dumps(event, indent=2))

                        # Get the object from the event and show its content type

                        print(bucket, key)

                        snsarn = awsdata['OCR-Textract-to-lambda']
                        rolearn = awsdata['OCRFullAccessOCRRole']

                        # snsarn = "arn:aws:sns:ap-southeast-1:524145442725:einvoice-ocr-completion"

                        jobtag = ''

                        if len(key) > 58:
                            jobtag = key[0:58] + '_Job'
                        else:
                            jobtag = key + '_Job'

                        jobtag = jobtag.replace("/", "")
                        try:

                            config = Config(retries=dict(max_attempts=10))

                            textract = boto3.client('textract', config=config)
                            
                            time.sleep(1)   

                            # responce = textract.start_document_text_detection(
                            responce = textract.start_document_analysis(
                                DocumentLocation={
                                    'S3Object': {
                                        'Bucket': bucket,
                                        'Name': key
                                    }
                                },

                                FeatureTypes=[
                                    'TABLES', 'FORMS',
                                ],

                                JobTag=jobtag,

                                NotificationChannel={
                                    "RoleArn": rolearn,
                                    "SNSTopicArn": snsarn
                                })

                            # "RoleArn" : "arn:aws:iam::524145442725:role/AWSSNSFullAccessRole",

                            print(responce)
                            # return 'Triggered PDF Processing for ' + key

                        except textract.exceptions.InvalidParameterException as e:

                            values = (key,) 
                            print('error')
                            # mycursor.execute("DELETE FROM mail_message WHERE filename = %s", values)
                            mycursor.execute(
                                "UPDATE mail_message SET is_processed = 'n' WHERE filename = ?",
                                values)
                            mydb.commit()

                            raise e

                else:
                    
                
                    mycursor.execute("SELECT * FROM elipo_setting where key_name = 'paper-ai'")
                    paperai = mycursor.fetchall()

                    if paperai:

                        try:

                            endpoint = None
                            access_key = None

                            base_url = ""

                            for each in paperai:
                                if each['value1'] == "endpoint":
                                    base_url = each['value2']
                                elif each['value1'] == "access_key":
                                    access_key = each['value2']

                            endpoint = base_url + "api/v1/queue_document_s3/"

                            file_name = key

                            # getdata = requests.post(endpoint, data={
                            #     "access_key": access_key,
                            #     "file_name": file_name,
                            #     "doc_type": "ap_invoice",
                            #     "lang": "English",
                            #     # "post_processor": "no_post_processing",
                            #     "post_processor": "fifth",
                            #     "aws_access_key": "AKIAXUCMAX6S36GOUQ5E",
                            #     "aws_secret_key": "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",
                            #     "bucket_name": bucket,
                            #     "elipo_endpoint": "https://7firau5x7b.execute-api.eu-central-1.amazonaws.com/einvoice-v1/paper-entry"
                            # })
                            
                            time.sleep(1)
                            
                            ocr_folder['paper_postpro'] = "fifth"

                            getdata = requests.post(endpoint, json={
                                "access_key": access_key,
                                "file_name": file_name,  
                                "doc_type": "ap_invoice",
                                "lang": "English",   
                                # "post_processor": "fifth",
                                "post_processor": ocr_folder['paper_postpro'],  
                                "aws_access_key": "AKIAXUCMAX6S36GOUQ5E",
                                "aws_secret_key": "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",
                                # "bucket_name": "textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db",
                                "bucket_name": bucket,
                                # "bucket_name": "524145442725-elipo-ocr-bucket",
                                "elipo_endpoint": "https://elipo_backend-agile-crane-rg.cfapps.us10-001.hana.ondemand.com/dev/paper-entry"
                            })

                            print(getdata)
                            print(ocr_folder['paper_postpro'], access_key )
                            print(getdata.text)

                            if getdata.status_code == 200:

                                responce = getdata.json()

                                # print(responce)
                                s = requests.Session()

                                s.headers.update({'Connection': 'keep-alive'})
                                
                                url = "https://elipo_backend-agile-crane-rg.cfapps.us10-001.hana.ondemand.com/dev/updatesmm"
                                
                                headers = {"key": key}
                                
                                sap_responce = s.post(url, data=responce,  params=headers)

                                if responce['status'] == "OK":
                                    values = (responce['task_id'], key)
                                    mycursor.execute(
                                        "UPDATE mail_message SET is_processed = 'y', job_id = ? WHERE filename = ?",
                                        values)
                                    key1 = key.split('/')
                                    values = (responce['task_id'], key1[1])
                                    mycursor.execute(
                                        "UPDATE aws_mail_message SET is_processed = 'y', job_id = ? WHERE filename = ?",
                                        values)
                                    mydb.commit()  

                        except Exception as e:
                            
                            print(e)             
                            
                            values = (key,)
                            mycursor.execute(
                                "UPDATE mail_message SET is_processed = 'n' WHERE filename = ?", values)
                            mydb.commit()

                        finally:
                            pass


        except Exception as e:
            print(e)
            print(
                'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                    key, bucket))

        finally:
            mydb.close()
            
    return responce

# event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-southeast-1', 'eventTime': '2023-06-30T06:14:02.959Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AIDAXUCMAX6STXCLTG4FR'}, 'requestParameters': {'sourceIPAddress': '49.206.130.247'}, 'responseElements': {'x-amz-request-id': '51W6GHZRSSA3MDYH', 'x-amz-id-2': '0Qc6zxygkg8HQkhh/0SfqqSzcshNh/9jEXkYa01NCRIErOBTlm1HfGgRmDXFu+QECzUsrEpIFowHobI4tZ0BLy62t31aUYcd'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '033a4d80-1cfc-48dd-9ee3-28dc102b430a', 'bucket': {'name': 'textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db', 'ownerIdentity': {'principalId': 'A28OG3S47O6VLN'}, 'arn': 'arn:aws:s3:::textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db'}, 'object': {'key': 'old-dev/D1688105594.62483___graphichub9200110036invoice.pdf', 'size': 207542, 'eTag': '661681957e06acf2442d409733487690', 'sequencer': '00649E72AAA2320BFB'}}}]}
# event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-southeast-1', 'eventTime': '2023-07-02T06:53:38.159Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AWS:AIDAXUCMAX6STXCLTG4FR'}, 'requestParameters': {'sourceIPAddress': '34.201.208.150'}, 'responseElements': {'x-amz-request-id': '1PGM99RV3ZTCDBDQ', 'x-amz-id-2': 'S9eLUK807Msk3HsK9E3NPo615zKw5NVwOm0fIwL2xstwjcN1PhG1eCURSWwTpVnuKaDbu8OXTffxTFEzS7f9bMx5XkcOfoZP'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': '033a4d80-1cfc-48dd-9ee3-28dc102b430a', 'bucket': {'name': 'textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db', 'ownerIdentity': {'principalId': 'A28OG3S47O6VLN'}, 'arn': 'arn:aws:s3:::textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db'}, 'object': {'key': 'old-dev/D1688280815.527088___graphichub.pdf', 'size': 207423, 'eTag': 'ea98b1ea8215cc7451d9c8f0011df1f2', 'sequencer': '0064A11EF0E28CD38E'}}}]}

# print(getTextFromS3PDF(event, ' '))



    

