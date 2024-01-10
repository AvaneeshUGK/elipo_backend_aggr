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
    
    ocr_folder = event["stageVariables"]["ocr_bucket_folder"]
    
    bucket = event["stageVariables"]["company_logo"]
    secret = event["stageVariables"]["secreat"]
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
            
            s3 = boto3.client("s3")
        
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
            
            secret = event["stageVariables"]["secreat"]
            bucket = event["stageVariables"]["non_ocr_attachment"]
            stage = event["stageVariables"]["lambda_alias"]
            
            # resp = client.get_secret_value(
            #     SecretId= secret
            # )
        
            # secretDict = json.loads(resp['SecretString'])
        
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
                    mycursor.execute("TRUNCATE department_master")
                    
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
                    
                    sqlQuery = "select department_id, department_name from departmental_budget_master where department_name in (?)" % format_strings_depName
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
                        
                        touple = (departmentID, row["department_name"], row["cost_center"], row["gl_account"], memberID, row["internal_order"])
                        values.append(touple) 
                        
                    sqlQuery = "select count(*) as count from department_master where department_id = ? and department_name = ? " \
                        "and cost_center = ? and gl_account = ? and member_id = ? and internal_order = ?"
                    
                    mycursor.executemany(sqlQuery, values)
                    dup = mycursor.fetchone()
                    
                    msg = "Duplicate Entry!"
                        
                    if dup["count"] != 1:
                        sqlQuery = "insert into department_master (department_id, department_name, cost_center, gl_account, member_id, internal_order) " \
                            "values (?, ?, ?, ?, ?, ?)"
                        mycursor.executemany(sqlQuery, values)
                        msg = "Inserted Successfully!"
                    
                else:
                    for row in list_item:
                        touple = (row["department_id"], row["department_name"], row["cost_center"], row["gl_account"], row["member_id"], row["internal_order"])
                        values.append(touple)
                    
                    sqlQuery = "select count(*) as count from department_master where department_id = ? and department_name = ? " \
                        "and cost_center = ? and gl_account = ? and member_id = ? and internal_order = ?"
                    
                    mycursor.executemany(sqlQuery, values)
                    dup = mycursor.fetchone()
                    msg = "Duplicate Entry!"
                        
                    if dup["count"] != 1:
                        sqlQuery = "insert into department_master (department_id, department_name, cost_center, gl_account, member_id, internal_order) " \
                            "values (?, ?, ?, ?, ?, ?)"
                            
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
                mycursor.execute("TRUNCATE departmental_budget_master")
                
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
        
            mycursor.executemany(sqlQuery, values)
            msg = "Inserted Successfully"
            
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

            if "querystring" in event["params"]:
                if "material_no" in event["params"]["querystring"]:
                    if len(event["params"]["querystring"]["material_no"].split(',')) == 1:
                        
                        mycursor.execute("DELETE FROM material_master WHERE material_no = ? ",event["params"]["querystring"]["material_no"])
                    else:
                        
                        values = event["params"]["querystring"]["material_no"].split(',')
                        mycursor.execute("delete from material_master where material_no in {}".format(tuple(values)))
            
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
            record = {
                "material_no":"", 
                "material_name":"", 
                "gst_per":"", 
                "unit_price":"", 
                "gl_account":"", 
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
                "tds": "",
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

                touple = ( str(row["vendor_no"]).strip(), row["vendor_name"], row["gst_treatment"], str(row["gstin_uin"]).upper(), row["source_of_supply"],row["jurisdiction_code"], row["currency"], row["payment_terms"], 
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
                sqlQuery += " where (in_status = 'tosap' and payment_status = 'paid') and document_type = 'RE' " + condn + " group by supplier_id order by total_amount desc, b.currency limit 5"
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
    print(fileQuery)
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
            
            if "sr_no" in event["params"]["querystring"]:
                sqlQuery = "delete from comment_templates where sr_no = %s" 
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
                mycursor.execute("select name from group where group_id = ?", record["app"])
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
            
            client = boto3.client('events')
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
    
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error!")
        }
    
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Update Successful!")
    }
# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'key_name': 'ConfigTraceToggle', 'key_value': 'off'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImQyNjkzODhhLTg1ODQtNDI1NS1hZjYxLTM1MWJkNDZiN2Y1ZiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg2ODk1NDA4LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg2ODk5MDA4LCJpYXQiOjE2ODY4OTU0MDgsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.MyfffnMyMPsgtmSEp-lH5x-kO7iiRZ-mwpQwPdEvfHjjRbJiVI-IU0k0N8QjzjaCSaWt7LfU2ui62DAN_zqBSppDRTaMu59MAr0AqdqkxNdlLKQVyx8lkZdezR2jcKSjA1TJC9AlhbGKsoAHuLjHH7dOASrQXvKBbPH_vg3JqnvRZHU0DL7h-dNTMtyXpccOUv-xZ_wfmUAsyXnWyiN8vdU8ZRsQuKAvnqB-2a7PSOiGbAjte5GQETGLh4Z4YlcfGp9n5Gj6tkqriy4py7b5oEoJVgJ2QAsRISEJccqf2JzaOyGuLcDQcRqNpxCOVmUqAunK0-AByUIzMa2LCcjluQ', 'content-type': 'application/json', 'Host': 'd1zhvpkkf9.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-648bfb37-1312036d5ed315e731f197ed', 'X-Forwarded-For': '49.207.52.67', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'attachment_bucket': 'einvoice-dev-enquiry', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': 'd1zhvpkkf9', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'einvoice-v1', 'source-ip': '49.207.52.67', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': '858c102b-0787-49e5-9646-bfbdb1dd7fa8', 'resource-id': 'zn2sp7', 'resource-path': '/setting'}}
# print(patchSetting(event , ' '))

#event not found
def getDetailedSupplierEnquiry(event, context): 
    
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
    client = boto3.client('events')
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

    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    resp = client.get_secret_value(
        SecretId=secret
    )

    secretDict = json.loads(resp['SecretString'])

    mydb = pymysql.connect(
        host=secretDict['host'],
        user=secretDict['username'],
        passwd=secretDict['password'],
        database=secretDict['dbname'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

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
                mycursor.execute('select * from elipo_saas_seeting.schemas_confg where ocr_folder = %s', values)
                ocr_folder = mycursor.fetchone()  
                    
                defSchemaQuery = "use " + ocr_folder['schema_name']
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
                                "UPDATE mail_message SET is_processed = 'n' WHERE filename = %s",
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
                                "elipo_endpoint": ocr_folder['endpoint']
                            })

                            print(ocr_folder['paper_postpro'], access_key )
                            print(getdata.text)

                            if getdata.status_code == 200:

                                responce = getdata.json()

                                # print(responce)

                                if responce['status'] == "OK":
                                    values = (responce['task_id'], key)
                                    mycursor.execute(
                                        "UPDATE mail_message SET is_processed = 'y', job_id = %s WHERE filename = %s",
                                        values)
                                    key1 = key.split('/')
                                    values = (responce['task_id'], key1[1])
                                    mycursor.execute(
                                        "UPDATE aws_mail_message SET is_processed = 'y', job_id = %s WHERE filename = %s",
                                        values)
                                    mydb.commit()  

                        except Exception as e:
                            
                            print(e)             
                            
                            values = (key,)
                            mycursor.execute(
                                "UPDATE mail_message SET is_processed = 'n' WHERE filename = %s", values)
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




    

