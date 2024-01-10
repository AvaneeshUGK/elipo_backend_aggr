import pymysql.cursors
import boto3
import json
import base64
import os
from collections import OrderedDict 
import requests
from  aws_xray_sdk.core import recorder 
from aws_xray_sdk.core import patch_all
import jwt
import pymysql
import datetime
from requests.auth import HTTPBasicAuth
from googleapiclient.discovery import build
import httplib2
import pickle
import os.path
import email.mime.text
import urllib3
import os
from pprint import pprint
import time
import re
import email
import json
from googleapiclient.discovery import build
import logging
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from googleapiclient.discovery import build

import requests
from  aws_xray_sdk.core import recorder 
from  aws_xray_sdk.core import xray_recorder 
from aws_xray_sdk.core import patch_all
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import calendar
from hdbcli import dbapi

import base64
from googleapiclient.discovery import build

atoken = ''
flg = ''

logs = boto3.client('logs',region_name='eu-central-1')
ssm = boto3.client('ssm',region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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')

def enable_xray(event):
    if 'Authorization' in event['params']['header'] :
       atoken =  event['params']['header']['Authorization']
    
    if atoken != '':
        flg = requests.get("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/getemail", headers={"Content-Type":"application/json", "Authorization":atoken})

    return json.loads(flg.text)['body']


def updateMailMessage(event, context):

    headers = {
            "Content-Type": "application/json"
            }

    # requests.patch("https://vxx4jwamw0.execute-api.sa-east-1.amazonaws.com/dev/event" , json = event , headers = headers)

    global dbScehma 
    dbScehma = ' DBADMIN '

    mydb = hdbcliConnect()

    try:
        key = event['params']['header']['Key']

        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            

            responce = event['body-json']

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

    except:
        return {
            'statuscode': 500,
            'event':event,
            'body': json.dumps("Internal Fail")

        }            
                
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': {"status":"success"}
    }



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

# def getRuleDetails(event, context):
#     global dbScehma 
#     dbScehma = event["stage-variables"]["schema"]
    
#     client = boto3.client(
#     'secretsmanager',
#     region_name='eu-central-1',
#     aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
#     aws_secret_access_key='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' )
    
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

#     try:
#         print(event)
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "use " + dbScehma
#             mycursor.execute(defSchemaQuery)
            
#             mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
#             on = mycursor.fetchone()
#             if on['value1'] == 'on':
#                 chk = enable_xray(event)
#                 if chk['Enable'] == True:
#                     patch_all() 
#                     print(event)
            
#             if "rule_id" in event["params"]["querystring"]:
                
#                 rule_id = event["params"]["querystring"]["rule_id"]
#                 rule = {}
                
#                 mycursor.execute("SELECT a.*, b.rule_name " \
#                     "FROM rule a " \
#                     "inner join rule_snro b " \
#                     "on a.rule_id = b.rule_id " \
#                     "where a.rule_id = %s", rule_id)
#                 rule_list = mycursor.fetchall()
             
#                 criteria = []
#                 approval_type = ""
#                 ec_isgroup = ""
#                 escelator = ""
#                 ifnot_withindays = ""
#                 comments = ""
#                 due_notification = ""
#                 due_reminder = ""
#                 overdue_notification = ""
#                 overdue_reminder = ""
                
#                 for row in rule_list:
                    
#                     approval_type = row["approval_type"]
#                     ec_isgroup = row["ec_isgroup"]
#                     escelator = row["escelator"]
#                     ifnot_withindays = row["ifnot_withindays"]
#                     comments = row["comments"]
#                     rule_name = row["rule_name"]
#                     due_notification = row["due_notification"]
#                     due_reminder = row["due_reminder"]
#                     overdue_notification = row["overdue_notification"]
#                     overdue_reminder = row["overdue_reminder"]
                        
#                     if row["decider_type"] == "number":
#                         data = {
#                             "decider" : row["decider"],
#                             "operator" : row["operator"], 
#                             "d_value" : int( row["d_value"] ), 
#                             "d_value2" : int( row["d_value2"] ), 
#                             "decider_type" : row["decider_type"]
#                         }
#                         criteria.append(data)
                        
#                     else:
#                         data = {
#                             "decider" : row["decider"],
#                             "operator" : row["operator"], 
#                             "d_value" : row["d_value"], 
#                             "d_value2" : row["d_value2"],
#                             "decider_type" : row["decider_type"]
#                         }
#                         criteria.append(data)
               
#                 mycursor.execute("select * from rule_approver where rule_key = %s", rule_id)
#                 approver = mycursor.fetchall()
                
#                 approver_final = [] 
#                 groupid = []
#                 memberid = []
                
#                 for row in approver:
#                     if row["isgroup"] == 'y':
#                         groupid.append(row["approver"])
#                     elif row["isgroup"] == 'n':
#                         memberid.append(row["approver"])
                
#                 if groupid and len(groupid) > 1:
#                     mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in {}".format(tuple(groupid)))
                    
#                 elif groupid and len(groupid) == 1:
#                     group = (groupid[0])
#                     sqlQuery = "select group_id, name from " + dbScehma + ".group where group_id = %s"
#                     mycursor.execute(sqlQuery, group)
                    
#                 for row in mycursor:
#                     temp1 = {
#                         "isgroup": "y",
#                         "approver": row["group_id"],
#                         "name": row["name"],
#                         "position": ""
#                     }
#                     approver_final.append(temp1)
             
#                 if memberid and len(memberid) > 1:
#                     mycursor.execute("select member_id, fs_name, ls_name, position from member where member_id in {}".format(tuple(memberid)))
                
#                 elif memberid and len(memberid) == 1:
#                     member = (memberid[0])
#                     sqlQuery = "select member_id, fs_name, ls_name, position from member where member_id = %s"
#                     mycursor.execute(sqlQuery, member) 
                    
#                 for row in mycursor:
#                     temp1 = {
#                         "isgroup": "n",
#                         "approver": row["member_id"],
#                         "name": row["fs_name"] + " " + row["ls_name"],
#                         "position": row["position"]
#                     }
#                     approver_final.append(temp1)
           
#                 app = []
#                 for data in approver:
                    
#                     for row in approver_final:
                        
#                         if row["approver"] == data["approver"] and row["isgroup"] == data["isgroup"]:
                            
#                             temp = {
#                                 "isgroup" : row["isgroup"],
#                                 "approver" : row["approver"],
#                                 "name": row["name"],
#                                 "level" : data["level"],
#                                 "position": row["position"]
#                             }
#                             app.append(temp)
                            
#                     if str(data["approver"]) == "999999999" and data["isgroup"] == "y":
#                             temp = {
#                                 "isgroup" : data["isgroup"],
#                                 "approver" : data["approver"],
#                                 "name": "To ERP",
#                                 "level" : data["level"],
#                                 "position": ""  
#                             }
#                             app.append(temp)
                            
#                 rule_detail = {
#                     "rule_id": rule_id,
#                     "rule_name": rule_name,
#                     "approval_type" : approval_type, 
#                     "due_notification" : due_notification,
#                     "due_reminder" : due_reminder,
#                     "overdue_notification" : overdue_notification,
#                     "overdue_reminder" : overdue_reminder,
#                     "ec_isgroup" : ec_isgroup, 
#                     "escelator" : escelator, 
#                     "es_name" : "",
#                     "ifnot_withindays" : ifnot_withindays, 
#                     "comments" : comments,
#                     "criteria" : criteria,
#                     "approvers" : app
#                 }
                
#             else:
                
#                 is_approval = 'y'
                
#                 if "is_approval" in event["params"]["querystring"]:
#                     is_approval = event["params"]["querystring"]["is_approval"]
                    
#                 rule_detail = []
                
#                 mycursor.execute("SELECT a.*, b.rule_name, c.department_name " \
#                 	"FROM rule a " \
#                 	"inner join rule_snro b " \
#                 	"on a.rule_id = b.rule_id " \
#                     "left join departmental_budget_master c " \
#                     "on a.d_value = c.department_id " \
#                 	"where b.is_approval = %s " \
#                 	"order by a.rule_id", is_approval)
#                 rules = mycursor.fetchall()
                
#                 dict_rule = rules
#                 rule_keys = []
#                 escalator = []
#                 distinct_rule = []
                
#                 for row in rules:
#                     temp = {
#                         "is_on": row["is_on"],
#                         "rule_id": row["rule_id"],
#                         "rule_name": row["rule_name"],
#                         "approval_type" : row["approval_type"], 
#                         "ec_isgroup" : row["ec_isgroup"], 
#                         "escelator" : row["escelator"], 
#                         "es_name" : "",
#                         "ifnot_withindays" : row["ifnot_withindays"], 
#                         "comments" : row["comments"],
#                         "due_notification" : row["due_notification"],
#                         "due_reminder" : row["due_reminder"],
#                         "overdue_notification" : row["overdue_notification"],
#                         "overdue_reminder" : row["overdue_reminder"]
#                     }
#                     distinct_rule.append(temp)
                
                    
#                 res_list = [] 
#                 approvers_list = []
                
#                 for i in range(len(distinct_rule)): 
#                     if distinct_rule[i] not in distinct_rule[i + 1:]: 
#                         res_list.append(distinct_rule[i]) 
                
#                 for each in rules:
#                     rule_keys.append(each['rule_id'])
                
#                 if rule_keys and len(rule_keys) > 1:
#                     mycursor.execute("SELECT * FROM rule_approver where rule_key in {}".format(tuple(rule_keys)))
#                     approvers_list = mycursor.fetchall()
                    
#                 elif len(rule_keys) == 1:
#                     key = (rule_keys[0])
#                     sqlQuery = "select * from rule_approver where rule_key = %s"
#                     mycursor.execute(sqlQuery, key)
#                     approvers_list = mycursor.fetchall()
                
#                 groupid = []
#                 memberid = []
                
#                 for row in approvers_list:
#                     if row["isgroup"] == 'y':
#                         groupid.append(row["approver"])
#                     elif row["isgroup"] == 'n':
#                         memberid.append(row["approver"])
            
#                 approver_final = []  
                
#                 if groupid and len(groupid) > 1:
                
#                     mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in {}".format(tuple(groupid)))
                    
#                 elif len(groupid) == 1:
#                     group = (groupid[0])
#                     sqlQuery = "select group_id, name from " + dbScehma + ".group where group_id = %s"
#                     mycursor.execute(sqlQuery, group)
                    
#                 for row in mycursor:
#                     temp1 = {
#                         "isgroup": "y",
#                         "approver": row["group_id"],
#                         "name": row["name"],
#                         "position": ""
#                     }
#                     approver_final.append(temp1)
         
#                 if memberid and len(memberid) > 1:
#                     mycursor.execute("select member_id, fs_name, ls_name, position from member where member_id in {}".format(tuple(memberid)))
                
#                 elif len(memberid) == 1:
#                     member = (memberid[0])
#                     sqlQuery = "select member_id, fs_name, ls_name, position from member where member_id = %s"
#                     mycursor.execute(sqlQuery, member) 
                    
#                 for row in mycursor:
#                     temp1 = {
#                         "isgroup": "n",
#                         "approver": row["member_id"],
#                         "name": row["fs_name"] + " " + row["ls_name"],
#                         "position": row["position"]
#                     }
#                     approver_final.append(temp1)
         
#                 for row in res_list:
#                     approvers = []
#                     criteria = []
                    
#                     for data in approvers_list:
                        
#                         if row["rule_id"] == data["rule_key"]:
                            
#                             for temp1 in approver_final:
                                
#                                 if data["approver"] == temp1["approver"] and data["isgroup"] == temp1["isgroup"]:
#                                     temp = {
#                                         "isgroup" : temp1["isgroup"],
#                                         "approver" : data["approver"],
#                                         "name": temp1["name"],
#                                         "level" : data['level'],
#                                         "position": temp1["position"]
#                                     }
#                                     approvers.append(temp)
                                    
#                                 elif str(data["approver"]) == "999999999" and data["isgroup"] == "y":
#                                     temp = {
#                                         "isgroup" : temp1["isgroup"],
#                                         "approver" : data["approver"],
#                                         "name": "To ERP",
#                                         "level" : data['level'],
#                                         "position": ""
#                                     }
#                                     approvers.append(temp)
#                                     break
                                
#                             approvers = sorted(approvers, key = lambda i: i['level'])      
                            
#                     for value in dict_rule:
                        
#                         decider = ""
#                         if row["rule_id"] == value["rule_id"]:
                            
#                             if value["decider_type"] == "string":
                                
#                                 if value["decider"] == "discount" and value["operator"] != "between":
#                                     decider = "Discount" + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "discount" and value["operator"] == "between":
#                                     decider = "Discount between " + value["d_value"] + " and " + value["d_value2"]
                                    
#                                 elif value["decider"] == "amount" and value["operator"] != "between":
#                                     decider = "Amount " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "amount" and value["operator"] == "between":
#                                     decider = "Amount between " + value["d_value"] + " and " + value["d_value2"]
                                    
#                                 elif value["decider"] == "gl_account" and value["operator"] != "between":
#                                     decider = "G/L account " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "currency" and value["operator"] != "between":
#                                     decider = "Currency " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "cost_center":
#                                     decider = "Cost center " + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "npo":
#                                     decider = "NPO " + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "vendor_no":
#                                     decider = "Vendor No. " + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "department_id":
#                                     if value["department_name"] == None :
#                                         value["department_name"] = ''
#                                     decider = "Department " + " " + value["operator"] + " " + value["department_name"]
                                
#                                 elif value["decider"] == "item_category":
#                                     decider = "Item Category " + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "invoice_type":
#                                     decider = "Invoice Type" + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "supplier_type	":
#                                     decider = "Supplier Type" + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "jurisdiction_code": #EPDS-69
#                                     decider = "jurisdiction code" + " " + value["operator"] + " " + value["d_value"] #EPDS-69
                                    
#                                 elif value["decider"] == "document_type":
#                                     rule_value = " "
#                                     if value["d_value"] == 'RE':
#                                         rule_value = "Invoice" 
#                                     elif value["d_value"] == 'KG':
#                                         rule_value = "Credit Memo" 
#                                     elif value["d_value"] == 'SU':
#                                         rule_value = "Debit Memo"
                                        
#                                     decider = "Document Type" + " " + value["operator"] + " " + rule_value
                                    
#                                 elif value["decider"] == "default":
#                                     decider = "Default"
                                
#                                 val = {
#                                     "rule" : decider,
#                                     "decider_type" : value["decider_type"]
#                                 }
#                                 criteria.append(val)
                                
#                             else:
                                
#                                 if value["decider"] == "discount" and value["operator"] != "between":
#                                     decider = "Discount" + " " + value["operator"] + " " + str(int(value["d_value"]))
                                    
#                                 elif value["decider"] == "discount" and value["operator"] == "between":
#                                     decider = "Discount between " + " " + str(int(value["d_value"])) + " and " + str(int(value["d_value2"]))
                                    
#                                 elif value["decider"] == "amount" and value["operator"] != "between":
#                                     decider = "Amount " + " " + str(value["operator"]) + " " + str(int(value["d_value"]))
                                    
#                                 elif value["decider"] == "amount" and value["operator"] == "between":
#                                     decider = "Amount between " + str(int(value["d_value"])) + " and " + str(int(value["d_value2"]))
                                    
#                                 elif value["decider"] == "gl_account" and value["operator"] != "between":
#                                     decider = "G/L account " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "currency" and value["operator"] != "between":
#                                     decider = "Currency " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "cost_center":
#                                     decider = "Cost center " + " " + value["operator"] + " " + value["d_value"]
                                
#                                 elif value["decider"] == "npo":
#                                     decider = "NPO " + " " + value["operator"] + " " + value["d_value"]
                                
#                                 elif value["decider"] == "vendor_no":
#                                     decider = "Vendor No. " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "department_id":
#                                     decider = "Department " + " " + value["operator"] + " " + value["department_name"]
                                    
#                                 elif value["decider"] == "item_category":
#                                     decider = "Item Category " + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "invoice_type":
#                                     decider = "Invoice Type" + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "supplier_type	":
#                                     decider = "Supplier Type" + " " + value["operator"] + " " + value["d_value"]
                                    
#                                 elif value["decider"] == "Jurisdiction_code": #EPDS-69
#                                     decider = "jurisdiction code" + " " + value["operator"] + " " + value["d_value"] #EPDS-69
                                
#                                 elif value["decider"] == "default":
#                                     decider = "Default"
                                    
#                                 val = {
#                                     "rule": decider,
#                                     "decider_type" : value["decider_type"]
#                                 }
#                                 criteria.append(val)
                        
#                     record = {
#                         "is_on": row["is_on"],
#                         "rule_id": row["rule_id"],
#                         "rule_name": row["rule_name"],
#                         "approval_type" : row["approval_type"], 
#                         "ec_isgroup" : row["ec_isgroup"], 
#                         "escelator" : row["escelator"], 
#                         "es_name" : row["es_name"],
#                         "ifnot_withindays" : row["ifnot_withindays"], 
#                         "comments" : row["comments"],
#                         "due_notification" : row["due_notification"],
#                         "due_reminder" : row["due_reminder"],
#                         "overdue_notification" : row["overdue_notification"],
#                         "overdue_reminder" : row["overdue_reminder"],
#                         "criteria": criteria,
#                         "approvers" : approvers
#                     }
#                     rule_detail.append(record) 
        
#     except:
#         return {
#             'statuscode': 500,
#             'body': json.dumps("Internal Fail")
#         }            
                
#     finally:
#         mydb.close()

#     return {
#         'statuscode': 200,
#         'body': rule_detail
#     }

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
    aws_secret_access_key='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')

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

def GetUserEmails(event, context):
    
    atoken = ''
    op = ''
    enable = ''
    if 'Authorization' in event['params']['header']:
        atoken = event['params']['header']['Authorization']
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
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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')

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
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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')
            
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

#=============API demo-vendo================================================================== 
def EnableXrayLambda(lam , switch):
    print(lam,switch)
    client = boto3.client('lambda', aws_access_key_id='AKIAXUCMAX6S27NZCRFL',aws_secret_access_key='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',region_name='eu-central-1')
 
    if switch == 'on':
        tracing = 'Active'
    if switch == 'off':
        tracing = 'PassThrough' 

    response = client.update_function_configuration(
    FunctionName  = lam,
    TracingConfig = {'Mode':tracing} ) #PassThrough #Active
    
def decode_jwt_token(Authorization):
    header1 =  jwt.decode(Authorization , options={"verify_signature": False})
    if 'email' in header1:
        return header1['email']
    else:
        return ''

def EnableXrayApi(api , switch):
    print(api,switch)
    tracing = ''

    if switch == 'on':
        tracing = 'True'
    else:
        tracing = 'False'

    devstages = [ 'dev' , 'einvoice-v1' , 'einvoice-dev' ]

    client = boto3.client('apigateway', aws_access_key_id='AKIAXUCMAX6S27NZCRFL',aws_secret_access_key='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',region_name='eu-central-1')

    response1 = client.get_stages(
    restApiId=api)



    # rapiid = api['id']
    stagename = ''
    for stage in response1['item']:
        if stage['stageName'] in devstages:
            stagename = stage['stageName']
    if stagename != '':
        response = client.update_stage(
            restApiId=api,
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

#statements working fine
def EnableXRayTracesIndividually(event, context):
    
    print(event)

    api = ''
    lam = ''
    Authorization = ''
    switch = ''
    result = ''
    
    if 'switch' in event['params']['header']:
        switch = event['params']['header']['switch']

    if 'api' in event['params']['header']:
        api = event['params']['header']['api']
    
    if 'lambda' in event['params']['header']:
        lam = event['params']['header']['lambda']

    if 'Authorization' in event['params']['header']:
        Authorization =  event['params']['header']['Authorization']
        
    
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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')
    
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
            flg = mycursor.fetchone()
            if flg['value1'] == 'on':
                print('config_trace is true')
                email=decode_jwt_token(Authorization)
            if email != '':
                mycursor.execute("select flag from email where userid = ?",email)
                flag = mycursor.fetchone()
                

                if flag['flag'] == 'true' and lam != '' and api != '':
                    # result = 'true'
                    
                    if 'switch' not in event['params']['header']:
                        switch = 'on'
                        print('enabling xray for lam , api ')
                    EnableXrayLambda(lam , switch)
                    EnableXrayApi(api , switch)
                else:
                    # re
                    print('disabling xray for lam , api ')
                    switch = 'off'
                    EnableXrayLambda(lam , switch)
                    EnableXrayApi(api , switch)


    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure")   
        }  

    finally:
        mydb.close()


    return {
        'statusCode': 200,
        'body': switch
    }

#tested statements work fine 
def getmasterdetailssap(event, context ):

    pre_sync_flag = ''

    # event = {'body-json': {}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'cache-control': 'max-age=0', 'Host': '4kaosyaovj.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://eu-central-1.console.aws.amazon.com/', 'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'cross-site', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-62ff1c4d-340a121323bf725e2ea3f1b6', 'X-Forwarded-For': '49.206.129.63', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {
    #         'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '4kaosyaovj', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'GET', 'stage': 'dev', 'source-ip': '49.206.129.63', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': '1bd8f530-6976-4eb3-8521-bda154b4f5f6', 'resource-id': 'nzkebn', 'resource-path': '/getmasterdetailssap'}}

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

    s = requests.Session()
    s.headers.update({'Connection': 'keep-alive'})

    try:
        
        lv_date = ''
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema" + dbScehma
            mycursor.execute(defSchemaQuery)

            mycursor.execute("SELECT value1 FROM elipo_setting where key_name = 'master_sync' ")
            master_psync_flag = mycursor.fetchone()
            master_psync_flag = 'on'

            if(master_psync_flag == 'on'):
                 mycursor.execute("SELECT value1 FROM elipo_setting where key_name = 'master_sync_date' ")
                 master_psync_date = mycursor.fetchone()
                 print('previous sync date '+ str(master_psync_date) + '.')

                 if(master_psync_date['value1'] != str(datetime.datetime.now()).split(' ')[0].replace("-",'') ):
                    lv_date = str(datetime.datetime.now()).split(' ')[0].replace("-",'')
                    mycursor.execute("UPDATE elipo_setting SET value1 = ? WHERE (key_name = 'master_sync_date') ",lv_date)
                 pre_sync_flag =  master_psync_date['value1']
                 if lv_date != '':
                    print('current sync date '+ str(lv_date))
                    
            mycursor.execute("SELECT value1 FROM elipo_setting where key_name = 'master_sync_material' ")
            material_flag = mycursor.fetchone()
            print('material flag is '+str(material_flag))

            mycursor.execute("SELECT value1 FROM elipo_setting where key_name = 'master_sync_vendor' ")
            vendor_flag = mycursor.fetchone()
            print('vendor_flag is '+str(vendor_flag))

            data = {
                "material_flag" :material_flag['value1'] ,
                "vendor_flag"   :vendor_flag['value1'] ,
                "pre_sync_flag" : pre_sync_flag
            }


            url = "http://182.72.219.94:8000/zfetchdeails/fetchdetails?sap-client=800"
            params = {"sap-client": "800"}
            headersFetch = {"X-CSRF-TOKEN": "Fetch"}
            headers = {"X-CSRF-TOKEN": 'true',
                       "Content-type": "application/json"}
            sap_responce = s.post(url, auth=HTTPBasicAuth(
                'developer08', 'Peol@123'), headers=headers, json=data , params=params , timeout=150 )
            sap_responce = json.loads(sap_responce.text)
            print(sap_responce)

            val = []
            val1 = []

            if(len(sap_responce) == 0):
                print('no vendor and material master data was created')

            check = ['VENDOR_NO',
                         'VENDOR_NAME',
                         'USER_ID',
                         'GST_TREATMENT',
                         'GSTIN_INT_TAX_CODE',
                         'SOURCE_OF_SUPPLY',
                         'JURISDICTION_CODE',
                         'CURRENCY_KEY',
                         'PAYMENT_TERMS',
                         'TDS',
                         'GST',
                         'PAN']

            check1 = ['MATNR' , 'MAKTX' , 'GST_PER' , 'MEINS' , 'STPRS']

            for i in sap_responce:
                

                if(vendor_flag['value1'] == 'on' and i['VENDOR_NO'] != '' ):
                    for j in check:
                        val.append(i[j])
                    val.append('')

                    # values = ('1', val[0], 'Company Code', val[1])
                    # sqlQuery = "INSERT INTO master (master_id, code, master_name, description) VALUES (%s, %s, %s, %s )"
                    # mycursor.execute(sqlQuery, tuple(values))
                    
                    mycursor.execute("INSERT INTO vendor_master (vendor_no , vendor_name , member_id , gst_treatment , gstin_uin , source_of_supply ,  jurisdiction_code , currency , payment_terms ,  tds  , gst_per ,pan , international_code  ) VALUES {}".format(tuple(val)))
                    print(val)

                if(material_flag['value1']  == 'on' and i['MATNR'] != '' ):
                    for k in check1:
                        if(k == 'MATNR'):
                            i['MATNR'] = i['MATNR'].lstrip('0')
                        val1.append(i[k])

                    sqlQuery1 = "insert into material_master (material_no, material_name, gst_per, uom, unit_price)" \
                    "values {}"
                       
                    mycursor.execute(sqlQuery1.format(tuple(val1)))
                    print(val1)

                val = []
                val1 = []

            mydb.commit()
            print('executed successfully')

    # except:
    #     return {
    #         'statusCode': 500,
    #         'body': json.dumps("Internal Failure")
    #     }

    finally:
        mydb.close()

#working fine for event
def updatePoDetails(event, context):
    # TODO implement
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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')

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])
    # # print(secretDict)

    mydb = hdbcliConnect()
    # print(resp['SecretString'])
    # payload = []
    # vendor_data = {}
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            ref_po_no = ''

            if 'header' in event['body-json']:

                po_h_list = ['po_number','po_date','delivery_address','bill_to_address','buyer','currency','delivery_date','purchase_group','total_amount','taxable_amount','tax_percentage','ref_po_no','plant']

                po_h = {
                'po_number' : '',
                'po_date' : '',
                'delivery_address':'',
                'bill_to_address':'',
                'buyer':'',
                'currency':'',
                'delivery_date':'',
                'purchase_group':'',
                'total_amount':'',
                'taxable_amount':'',
                'tax_percentage':'',
                'plant':'',
                'status':'',
                'modified_date':'',
                'company_code':'',
                'ref_po_no':''
                }

                po_h['po_number'] = event['body-json']['header']['poNumber']

                po_h['po_date'] = event['body-json']['header']['poDate']
                po_h['delivery_address'] = event['body-json']['header']['deliveryAddress']
                po_h['bill_to_address'] = event['body-json']['header']['billToAddress']
                po_h['buyer'] = event['body-json']['header']['buyer']
                po_h['currency'] = event['body-json']['header']['currency']
                po_h['delivery_date'] = event['body-json']['header']['deliveryDate']
                po_h['purchase_group'] = event['body-json']['header']['purchaseGroup']
                po_h['total_amount'] = event['body-json']['header']['totalAmount']
                po_h['taxable_amount'] = event['body-json']['header']['taxableAmount']
                po_h['tax_percentage'] = event['body-json']['header']['taxPercentage']
                po_h['plant'] = event['body-json']['header']['plant']
                po_h['status'] = event['body-json']['header']['inStatus']
                po_h['modified_date'] = event['body-json']['header']['modified_date']
                
                po_h['ref_po_no'] = event['body-json']['header']['refPoNum']
                po_h['company_code'] = event['body-json']['header']['companyCode']

                ref_po_no = event['body-json']['header']['refPoNum']
                
                # mycursor.execute('SELECT * FROM material_master where material_name = ?', value)
                mycursor.execute('UPDATE po_header SET po_number = ? , po_date = ?, delivery_address = ?, bill_to_address = ? , buyer = ?,'
                                 ' currency = ? , delivery_date = ? , purchase_group = ? , total_amount = ? , taxable_amount = ?,'
                                 'tax_percentage = ? ,  plant = ? ,in_status = ? , modified_date=? , company_code = ? WHERE ref_po_no = ? ',tuple(po_h.values()))

                print(po_h)

            if 'item' in event['body-json']:

                po_i_list = ['item_no','hsn_code','material_no','material_name','quantity','unit_price','unit_of_measure','tax','taxable_amount','tax_amount','total_amount']

                po_i = {
                    'item_no':'',
                    'hsn_code':'',
                    'material_name':'',
                    'quantity':'',
                    'unit_price':'',
                    'unit_of_measure':'',
                    'tax':'',
                    'taxable_amount':'',
                    'tax_amount':'',
                    'total_amount':'',
                    
                    'ref_po_no':'',
                    'material_no':''
                }

                final_item = []

                for i in range(len(event['body-json']['item'])):
                    po_i['item_no'] = event['body-json']['item'][i]['item_no']
                    po_i['hsn_code'] = event['body-json']['item'][i]['hsnCode']
                    po_i['material_name'] = event['body-json']['item'][i]['materialName']
                    po_i['quantity'] = event['body-json']['item'][i]['quantity']
                    po_i['unit_price'] = event['body-json']['item'][i]['unitprice']
                    po_i['unit_of_measure'] = event['body-json']['item'][i]['unitOfMeasure']
                    po_i['tax'] = event['body-json']['item'][i]['taxPercentage']
                    po_i['taxable_amount'] = event['body-json']['item'][i]['taxableAmount']
                    po_i['tax_amount'] = event['body-json']['item'][i]['taxAmount']
                    po_i['total_amount'] = event['body-json']['item'][i]['totalAmount']
                    po_i['ref_po_no'] = ref_po_no
                    po_i['material_no'] = event['body-json']['item'][i]['materialNo']

                    # temp = po_i
                    final_item.append(po_i) 
                    # po_i.clear()

                    mycursor.execute('UPDATE po_item SET item_no = ? , hsn_code = ?,  material_name = ? , quantity = ?,'
                                 ' unit_price = ? , unit_of_measure = ? , tax_percentage = ? , taxable_amount = ? , tax_amount = ?,'
                                 'total_amount = ?  WHERE ref_po_no = ? and material_no = ? ',tuple(po_i.values()))

                print(final_item)


            mydb.commit()
    
    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Successful')
    }    

# event = {'body-json': {'taxAmount': 45, 'amount': 44.81, 'currency': 'KWD', 'ref_po_no': 60, 'purchase_group': ''}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'content-type': 'application/json', 'Host': '4kaosyaovj.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-64885115-28bfc06b376dd618773f4175', 'X-Forwarded-For': '49.207.51.54', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '4kaosyaovj', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'dev', 'source-ip': '49.207.51.54', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'cfe0aaa5-9d2e-464f-9097-dda345619230', 'resource-id': 'b8p5ip', 'resource-path': '/getpo'}}
# print(updatePoDetails(event, ' '))
#working fine
def fetchPoDetails(event, context):

    ref_po_no = ''
    data = []
    files = []
    final = {
                'po_number':'',
                'po_date':'',
                'delivery_address':'',
                'bill_to_address':'',
                'buyer':'',
                'currency':'',
                'delivery_date':'',
                'purchase_group':'',
                'total_amount':'',
                'taxable_amount':'',
                'tax_percentage':'',
                'ref_po_no':'',
                'in_status':'',
                'files':[],
                'item': []
            }

    # TODO implement
    dbScehma = ' DBADMIN '
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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')

    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])
    # print(secretDict)

    mydb = hdbcliConnect()

    # print(resp['SecretString'])
    # payload = []
    # vendor_data = {}
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            if 'po_no' in event['params']['querystring']:
                ref_po_no = event['params']['querystring']['po_no']

            if ref_po_no != '':
                data1 =[]
                data2 = []
                data3 = []
                mycursor.execute("select *  from po_header where ref_po_no = ?" , ref_po_no )
                data1.append(mycursor.fetchone())
                data1 = convertValuesTodict(mycursor.description, data1)
                data.append(data1[0])
                mycursor.execute("select *  from po_item where ref_po_no = ?" , ref_po_no )
                data2 = mycursor.fetchall()
                data2 = convertValuesTodict(mycursor.description, data2)
                data.append(data2)
                mycursor.execute(" SELECT * FROM file_storage where file_id = ? and attach_id > 7000 " ,ref_po_no)
                data3.append(mycursor.fetchone())
                data3 = convertValuesTodict(mycursor.description, data3)
                data.append(data3[0])

            
            final_labels = ['po_number','po_date','delivery_address','bill_to_address','buyer','currency','delivery_date','purchase_group','total_amount','taxable_amount','tax_percentage','ref_po_no','in_status','plant','company_code']
            for val in final_labels:
                final[val] = data[0][val]
            final['item'] = data[1]
            final['files'] = data[2]
            mydb.commit()
    
    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': final
    }

def send_message(service, user, message):
    try:     
        # sqlQurey = ("select user_id from mail_message where invoice_no = ?")
        # values = (invoice_no)
        # user = mycursor.execute(sqlQurey,values)
        message = (service.users().messages().send(userId=user, body=message).execute())
        return message
    except Exception as error:
        print("An error occurred: ", error)

def create_message(sender, to, subject, message_text,cc):
    message = email.mime.text.MIMEText(message_text, 'html')

    if isinstance(to, list):
        for index, eto in enumerate(to):
            if index == 0:
                tomails = str(eto['email'])
                continue

            tomails += "," + str(eto['email'])
    else:
        tomails = to

    message['to'] = tomails
    message['from'] = sender
    message['subject'] = subject
    message['cc']=cc
    encoded = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {'raw': encoded.decode("utf-8")}

def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)

def get_stored_credentials(user_id):
    
    global ocr_bucket_folder
    
    try:
        s3 = boto3.client("s3")
        encoded_file = s3.get_object(Bucket=elipo_bucket, Key=ocr_bucket_folder+user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
    except Exception as excep:
        creds = None
  
# event working fine      
def rejectInvoice(event, context):
    # global dbScehma 
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    # secret = event["stage-variables"]["secreat"]

    # global elipo_email
    # elipo_email = event["stage-variables"]["notification_email"]

    global elipo_bucket
    elipo_bucket = event["stage-variables"]["cred_bucket"]
    
    global ocr_bucket_folder
    ocr_bucket_folder = event["stage-variables"]["ocr_bucket_folder"]
    
    # global login_url
    
    # curr_window_url=event["params"]["querystring"]["windowlogin"]
    
    # login_url=curr_window_url.split('#')[0]
    
    # resp = client.get_secret_value(
    #     SecretId=secret
    # )

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            dbScehma = ' DBADMIN '
            
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 	
            
            mail_cc = ''
            mycursor.execute("select * from elipo_setting where key_name = 'notification-mail'")
            email_data = mycursor.fetchone()
            user_id = email_data["value1"]
            credentials = get_stored_credentials(user_id)
            invoice_no = event["params"]["querystring"]["invoice_no"]
            body = event["params"]["querystring"]["body"]
            rejected_by = event["params"]["querystring"]["email"]
            # vendor_name = event["params"]["querystring"]["vendor_name"]
            sqlQuery = ("select * from invoice_header where invoice_no = ?")
            mycursor.execute(sqlQuery,invoice_no)
            value = mycursor.fetchone()
            user_invoice_id = value["user_invoice_id"]
            sqlQurey1=("select recieved_from from mail_message where invoice_no = ? ")
            mycursor.execute(sqlQurey1,invoice_no)
            vendor_name = mycursor.fetchone()
            vendor_name = vendor_name["recieved_from"]
            # vendor_name="harshithaprabhu14@gmail.com"
            mail_subject = 'Rejected for Correction' + ' ' + user_invoice_id
            if credentials and credentials.refresh_token is not None:
                service = build_service(credentials=credentials)
                message_body = '''<html>
                    <body  >
                <div style="  max-width: 500px; margin: auto; padding: 10px; ">
                        <div style=" width:100%; align-content: center;text-align: center;">
                            <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/ELIPO+logo.png" alt="Italian Trulli" style="vertical-align:middle; width: 140px;height:50px;text-align: center;"  >
                        </div>
                    <div style=" width:100%; align-content:left;text-align:left;">
                            <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                        </div>
                    <b> 
    
                    <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Dear User,
                    </span> 
                    <br><br>
                    

                    <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Invoice No: <span style="font: 500  15px/22px ;">{},</span>
                    </span> 
    
                    <br>
                    <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Rejected By : <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;"> {},</span> 
                    </span> 
                    </b> 
                    <br>
                    <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">{} </span>
                    <br>
                    <br>
                    
                    <div style="width:100%;">
                    <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Regards,</span>
                    <br>
                    <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Team ELIPO</span>
                    </div>
                <div style=" width:100%; align-content:left;text-align:left;">
                            <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                        </div>
    
    
                    <div style="width:100%;align-content: center;text-align: center;">
                        <span style=" text-align: center;font: 600 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 0.7;">This message was sent to you by ELIPO</span>
                    </div>
                    <div style="width:100%;align-content: center;text-align: center;">
                        <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/elipo+logo_2.png" alt="Italian Trulli" style="text-align: center;width: 80px;height: 30px;" >
                    </div>
    
                    <br>
                </div>
                    </body></html>'''.format(user_invoice_id,rejected_by,body)
                    
                message = create_message(sender="elipotest@gmail.com", to=vendor_name, subject=mail_subject, message_text=str(message_body),cc=mail_cc)
                send_message(service=service, user="me", message=message)
                sqlQuery = "update invoice_header set in_status = 'invoice_resent' where invoice_no = ?"
                mycursor.execute(sqlQuery,invoice_no)
                
                mydb.commit()
                
    except Exception as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
    # TODO implement
    return {
        'statuscode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'body': 'test', 'email': 'abhishek194194@gmail.com', 'invoice_no': '7430'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJlMzM4NjkyYi0wMjkzLTRhNWQtOWQ3My01ZjE5MzQzZDBkMzIiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LWNlbnRyYWwtMS5hbWF6b25hd3MuY29tXC9ldS1jZW50cmFsLTFfUDlybm5xaUx1IiwiY29nbml0bzp1c2VybmFtZSI6ImUzMzg2OTJiLTAyOTMtNGE1ZC05ZDczLTVmMTkzNDNkMGQzMiIsImF1ZCI6IjI0YmplNGp1ZDhoM2Y4cnNua2toZzBibHYxIiwiZXZlbnRfaWQiOiIyYzBjYmNjNC1kZjQ3LTQ0MTMtOGQwOS0zMjg4NzgwZmY2NzUiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTY0MzcxNjY0NSwibmFtZSI6IlRlc3QiLCJleHAiOjE2NDM3MjAyNDUsImlhdCI6MTY0MzcxNjY0NSwiZmFtaWx5X25hbWUiOiJFTElQTyIsImVtYWlsIjoiYWJoaXNoZWsxOTQxOTRAZ21haWwuY29tIn0.B1Ph9xXTeL_3EzW6pVspQTBe-iQEXVVtxevr_H1qr7hC-xbsJoFW0nFXYOc7jtunLNMihtI6YbRGj38CT352m0n0UE7g_WfDCHbk8CAOYTIAMGEC1KO80Kz6pZEWrGgZKtMEZSpZgPlI1T6oLmRkc3Q1m3Kxdgozx0bAKrpfAcrf-bLqkgqMqtHE4BSQVMJF-459UUfSxWo--jT6CXA8TGsi-XthDZ7LOWo2IcLWK_lknIs4k8z0FYoAfGS0S2mjRFr7qOea6LHRXIzKXVEBMx_YvPrKdeCKn2H8SygCUOt2_y_tZw9MhTnlqm11eDW_sz6s3mrpk5Hdx_I4I5CwsA', 'content-type': 'application/json', 'Host': '4kaosyaovj.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-61f92153-77d3a0ba45545c8d4c799043', 'X-Forwarded-For': '49.207.210.163', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '4kaosyaovj', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'dev', 'source-ip': '49.207.210.163', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36', 'user-arn': '', 'request-id': '5d4b4d08-512b-4d07-81a3-b4610eff8e79', 'resource-id': 'rcfkwk', 'resource-path': '/reject'}}

# print(rejectInvoice(event , ' '))

# no sql statement present
def s3logs(event, context):
    print(event)
    extra_args = {}
    log_groups = []
    log_groups_to_export = []
    
    if 'S3_BUCKET' not in os.environ:
        print("Error: S3_BUCKET not defined")
        return
    
    print("--> S3_BUCKET=%s" % os.environ["S3_BUCKET"])
    
    while True:
        response = logs.describe_log_groups(**extra_args)
        log_groups = log_groups + response['logGroups']
        
        if not 'nextToken' in response:
            break
        extra_args['nextToken'] = response['nextToken']
    
    for log_group in log_groups:
        response = logs.list_tags_log_group(logGroupName=log_group['logGroupName'])
        log_group_tags = response['tags']
        if 'ExportToS3' in log_group_tags and log_group_tags['ExportToS3'] == 'true':
            log_groups_to_export.append(log_group['logGroupName'])
    
    for log_group_name in log_groups_to_export:
        ssm_parameter_name = ("/log-exporter-last-export/%s" % log_group_name).replace("//", "/")
        try:
            ssm_response = ssm.get_parameter(Name=ssm_parameter_name)
            ssm_value = ssm_response['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            ssm_value = "0"
        
        export_to_time = int(round(time.time() * 1000))
        
        print("--> Exporting %s to %s" % (log_group_name, os.environ['S3_BUCKET']))
        
        if export_to_time - int(ssm_value) < (24 * 60 * 60 * 1000):
            # Haven't been 24hrs from the last export of this log group
            print("    Skipped until 24hrs from last export is completed")
            continue
        
        try:
            response = logs.create_export_task(
                logGroupName=log_group_name,
                fromTime=int(ssm_value),
                to=export_to_time,
                destination=os.environ['S3_BUCKET'],
                destinationPrefix=log_group_name.strip("/")
            )
            print("    Task created: %s" % response['taskId'])
            time.sleep(5)
            
        except logs.exceptions.LimitExceededException:
            print("    Need to wait until all tasks are finished (LimitExceededException). Continuing later...")
            return
        
        except Exception as e:
            print("    Error exporting %s: %s" % (log_group_name, getattr(e, 'message', repr(e))))
            continue
        
        ssm_response = ssm.put_parameter(
            Name=ssm_parameter_name,
            Type="String",
            Value=str(export_to_time),
            Overwrite=True)

class SapPostException(Exception):
    pass

class ErpPostException(Exception):
    pass

#worked fine for event but invoice_no not declared anywhere
def postSalesOrder(event, context):
    
    # TODO implement

    Sresponce = ''

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
    # print(resp['SecretString'])
    # payload = []
    vendor_data = {}
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema  " + dbScehma
            mycursor.execute(defSchemaQuery)

            header = ''
            item = ''
            if 'header' in event['body-json']:
                header = event['body-json']['header']

            if 'item' in event['body-json']:
                item = event['body-json']['item']

            item_list = ['item_no','materialNo','quantity','unitOfMeasure','unitOfMeasure','itemno','quantity','itemno','KSCHA','unitprice','currency']
            header_list = ['poDate','poNumber','plant','deliveryDate','deliveryAddress','billToAddress']
            
            item = {
                "POSEX":'',
                "MATNR":'',
                "DZMENG":'',
                "ISO_ZIEME":'',
                "VRKME":'',
                "POSNR_VA":'10',
                "WMENG":'',
                "KPOSN":'',
                "KSCHA":'',
                "BAPIKBETR1":'',
                "WAERS":''
            }

            records = {
                "AUART":'OR',
                "VKORG":'1000',
                "VTWEG":'10',
                "SPART":'00',
                "BSTDK":event['body-json']['header'][header_list[0]],
                "BSTKD":event['body-json']['header'][header_list[1]],
                "PARVW":'SP',
                "KUNNR":'1000',
                "WERKS_D":event['body-json']['header'][header_list[2]],
                "EDATU":event['body-json']['header'][header_list[3]],
                "WERKS_E":event['body-json']['header'][header_list[2]],
                "WERKS_F":event['body-json']['header'][header_list[2]],
                'items' : [],
                'attachments':[]
            }

            item['KSCHA'] = 'PB00'
            if event['body-json']['header']['currency'] == 'KD/ ' :
                event['body-json']['header']['currency'] = 'KWD'
            item['WAERS'] = event['body-json']['header']['currency']
            
            POSNR_va_count = 1

            for i in event['body-json']['item']:
                
                item["POSNR_VA"] = int( item["POSNR_VA"] ) * POSNR_va_count
                POSNR_va_count = POSNR_va_count + 1
                
                for j in i:

                    if j == 'item_no':
                        item['KPOSN'] = i[j]
                        item['POSEX'] = i[j]
                    if j == 'materialNo':
                        item['MATNR'] = i[j]
                    if j == 'quantity':
                        item['DZMENG'] = i[j]
                        item['WMENG'] = i[j]
                    if j == 'unitOfMeasure':
                        item['ISO_ZIEME'] = 'ST'
                        item['VRKME'] = i[j]
                    if  j == 'unitPrice':
                        item['BAPIKBETR1'] = i[j]
                    # if j == 'currency':

                # temp_items = set(item)
                # item.clear()    
                records['items'].append(item.copy())
                # item.clear()  

            s3 = boto3.client("s3")

            if 'files' in event['body-json']['header']:

                file = []
                file.append(event['body-json']['header']['files'])
                upload_attach = []
                data = ''

                if file:
                    try:
                        for row in file:
                            file_obj = s3.get_object(Bucket=row["file_path"], Key=row["name"])
                            file_content = file_obj["Body"].read()
                            file_content = str(base64.b64encode(file_content))
                            length = len(file_content)
                            file_content = file_content[2:length - 1]

                            if row["mime_type"] == '' and row['name'].split('.')[-1] == 'jpg' :
                                row["mime_type"] ='image/'+row['name'].split('.')[-1]

                            data = {
                                "file_content": file_content,
                                "mime_type": row["mime_type"]
                            }
                            

                            upload_attach.append(data)

                            records['attachments'].append(data)
            
                        # indicator = True
            
                    except Exception as e:
                        print("process didn't stopped", e)

            s = requests.Session()
            s.headers.update({'Connection': 'keep-alive'})
    
            try:
            
                url = "http://182.72.219.94:8000/zpostingso/postso?sap-client=800"
                params = {"sap-client": "800"}
                headersFetch = {"X-CSRF-TOKEN": "Fetch"}

                y = s.get(url, auth=HTTPBasicAuth('developer08', 'Peol@123'), headers=headersFetch, params=params, timeout=8)

                token = y.headers["X-CSRF-TOKEN"]
                headers = {"X-CSRF-TOKEN": token, "Content-type": "application/json"}   
                
                sap_responce = s.post(url, json=records, auth=HTTPBasicAuth('developer08', 'Peol@123'), headers=headers, params=params , timeout=8)

                if 'TYPE' in  sap_responce.json()[0] :
                    
                    responce = sap_responce.json()
                    error_list = []
                    sap_errors = []
                    error_flag = False

                    for count, each in enumerate(responce, 1):
                        if each['TYPE'] == 'E':
                            error_flag = True
                
                        if each['TYPE'] == 'W':
                            mycursor.execute("select is_warning_set from invoice_header where invoice_no = ?", invoice_no)
                            warning_flag = mycursor.fetchall()
                            if warning_flag["is_warning_set"] == 'n':
                                mycursor.execute("update invoice_header set is_warning_set = 'y' where invoice_no = ?", invoice_no)
                                error_flag = True
                
                        err_dict = {
                            'type': each['TYPE'],
                            'msg': each['MESSAGE']
                        }
                        sap_errors.append(err_dict)
                        # error_dict = (str(invoice_no), str(count), each["TYPE"], each["MESSAGE"])
                        # error_list.append(error_dict)
                
                    if error_flag == True:
                        msg = "While posting error was generated please check the error log!"
                        err_responce = {
                            "sap_errors": sap_errors,
                            "msg": msg
                        }
                        raise SapPostException(err_responce)
                    
                else:
                    responce = sap_responce.json()
                    msg = "Sales order created Successfully"
                    Sresponce = {
                        "salesOrderNumber": responce,
                        "msg": msg + ' ' + responce
                    }
                    
                    mycursor.execute("UPDATE po_header SET in_status = 'submitted' , so_number = ?  WHERE ref_po_no = ? ", (responce,header['ref_po_num']))
                    
    
            
            except requests.exceptions.Timeout as msg:

                mydb.rollback()

                erp_errors = {
                    'statuscode': 300,
                    'body': json.dumps("Resource temporarily unavailable!")
                }

                raise ErpPostException(erp_errors)
               

            except requests.exceptions.TooManyRedirects as msg:
                mydb.rollback()
                return {
                    'statuscode': 500,
                    'body': json.dumps("Too Many Redirects!")
                }

            except requests.exceptions.RequestException as msg:
                # mydb.rollback()
                return {
                    'statuscode': 500,
                    'body': json.dumps("Resource temporarily unavailable!")
                }

            except requests.exceptions.ConnectionError as msg:
                mydb.rollback()
                return {
                    'statuscode': 500,
                    'body': json.dumps("Resource temporarily unavailable!")
                }
            
            
            except SapPostException as er:
                # mydb.rollback()
                return {
                    'statuscode': 300,
                    'body': er.args[0]
        }
            
            finally:
                pass

            mydb.commit()

    except ErpPostException as er:
        mydb.rollback()
        return {
            # 'statuscode': 300,
            'body': {'msg' : er.args[0]}
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
            'body': Sresponce
        }
# event = {'body-json': {'header': {'plant': '1000', 'inStatus': 'new', 'poNumber': 'LPO/119008 ', 'poDate': '06-02-22 ', 'deliveryAddress': 'P.O. BOX: 72, SAFAT 13001, KUWAIT.KUWAIT CITY', 'billToAddress': 'GRAND HYPER SOUQ AL ', 'buyer': 'GRAND HYPER SOUQ AL ', 'currency': 'KWD', 'deliveryDate': '06-02-22 ', 'baselinedate_due': '', 'purchaseGroup': '100', 'taxableAmount': 45, 'totalAmount': 44.81, 'taxPercentage': 0, 'ref_po_num': 60, 'company_code': '1000', 'amount': 0, 'files': {'attach_id': 8182, 'file_id': '60', 'name': 'old-dev/D1684481807.030913___po1.pdf', 'mime_type': 'application/pdf', 'file_path': 'textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db', 'file_link': 'https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/dev/attachment?file_name=old-dev/D1684481807.030913___po1.pdf&bucket=textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db'}}, 'item': [{'item_no': 1, 'itemno': '', 'materialName': 'COLGATE HERBAL TOOTHPASTE 125ML', 'materialNo': '10522', 'quantity': 1, 'unitprice': 18.41, 'unitPrice': 18.41, 'cgst_per': None, 'cgst_amount': None, 'refPoNo': 60, 'sgst_per': None, 'sgst_amount': None, 'igst_per': '', 'igst_amount': '', 'hsnCode': '42411', 'unitOfMeasure': 'UN', 'taxPercentage': 0, 'taxableAmount': 0, 'taxAmount': 0, 'temptotal': None, 'totalAmount': 18.41}, {'item_no': 2, 'itemno': '', 'materialName': 'BEESLINE LIP CARE SOOTHING JOURI ROSE 4S*4GM', 'materialNo': '20522', 'quantity': 1, 'unitprice': 26.4, 'unitPrice': 26.4, 'cgst_per': None, 'cgst_amount': None, 'refPoNo': 60, 'sgst_per': None, 'sgst_amount': None, 'igst_per': '', 'igst_amount': '', 'hsnCode': '415242', 'unitOfMeasure': 'UN', 'taxPercentage': 0, 'taxableAmount': 0, 'taxAmount': 0, 'temptotal': None, 'totalAmount': 26.4}]}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-GB,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImM4YTc1OTFmLWNmNGEtNGNlOS1iNzVhLWFkNDMwMWJiMTViMiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg0NzQ3MzkzLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg0NzUwOTkzLCJpYXQiOjE2ODQ3NDczOTMsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.fR3yIpXN4FleF8TV19b8MADP82YEXABMNuz8p-7CYOP45L13KVLraKcJb_WthjO3KdUwmeopu9GWSVfAUA0UMNxHspv393ZsSlBauX6-rtetMn1Q9nF16pQ4IT12a9hhv071rLhV_FoyVn1kBrsjyoX6vErdEgGmhZqrErc924s6jlLIneSBV6eUKQZVwyrTW4SKD0fqRg7I1gKHLAOsNEbpKEaGEiPNCHc6kB0Zxm8dNfy3ER1junyHez3b2vI-eCvwlvmXjwh-MQ402WVJel0N4OlBv7R4ydxzDaXcKNx0e40ruUODg41MaHE4M8GYEdLhVUFbcgiaRDHwBCiC3Q', 'content-type': 'application/json', 'Host': '4kaosyaovj.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-646b3c21-1c461e222b91afdf353d3b22', 'X-Forwarded-For': '157.50.15.235', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '4kaosyaovj', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'dev', 'source-ip': '157.50.15.235', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'ff2841e1-f598-4f71-ba78-c011b5ecc115', 'resource-id': 'lh304s', 'resource-path': '/salesorder'}}

# print(postSalesOrder(event , ' '))

#working fine for event passed
def patchUserId(event, context):
    
    print(event)
    global dbScehma 
    dbScehma = ' DBADMIN '

    Email = event['body-json']
    # size = len(Email)


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

            for mails in Email:
                if mails['flag'] == 'true' or mails['flag'] == True :
                    values = mails['userid']
                    mycursor.execute(" UPDATE email SET flag = 'true' WHERE userid = ? " , values)
                elif mails['flag'] == 'false' or mails['flag'] == False:
                    value = mails['userid']
                    mycursor.execute(" UPDATE email SET flag = 'false' WHERE userid = ? " , value)
                    
            mydb.commit() 
            
            # Flag = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
        
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure")   
        }  
        
    finally:
        mydb.close()
         
    return {
        'statuscode': 200,
        'body': json.dumps("Update Successful!")
    }
# event = {'body-json': [{'userid': 'abhishek194194@gmail.com', 'flag': True}, {'userid': 'einvoiceportal@gmail.com', 'flag': False}], 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6ImE2ZjNhODZhLWI2OGYtNGU4Ni04NTZiLTk2OTBkNjk2YjRiZiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjQ5NjU0ODIxLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjQ5NjU4NDIxLCJpYXQiOjE2NDk2NTQ4MjEsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.lM0eSfRo74oTmB0nuqN6qOhiYoZ7ALY38maDVSCQzblTSsLDtxc2VPKkiPpJfDl_tgxX4TAwuPsrAT2s3lCZvfRANxRMWOtqzaHAPbKeKy1wFHgeqPBGRrL0_MHU0GSkhAiGpyzJekyntzn73RJT8vbDQpnbxmXi-hVX0eYuvHFdKH4ce8p1V6FribDQwpZnV2Yn8kFMzhclSJ_yS4-c4YE9C8fJLYBevdG0rKVmmA5dtrecIuYSHURMnvJBe3pfcExByvW90Jp_pKOEcP8nqYlBjB9Wol47cHQQ-V5wAnURjiJ55Y0-X7sh7yPij0cxuvALdEJ3Ei8KIFPTw6rDhw', 'content-type': 'application/json', 'Host': '4kaosyaovj.execute-api.eu-central-1.amazonaws.com', 'origin': 'http://localhost:4200', 'referer': 'http://localhost:4200/', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-6253bc55-42e2985a314b7674604e3296', 'X-Forwarded-For': '49.207.202.73', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '4kaosyaovj', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'dev', 'source-ip': '49.207.202.73', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36', 'user-arn': '', 'request-id': 'b21024ea-0140-4838-9457-1eb7055f7541', 'resource-id': 'mjxny4', 'resource-path': '/tracing'}}
# print(patchUserId(event , ' '))

#working fine for event i changed limit query
def getTrackSalesOrders(event, context):
    # TODO implement
    records_list = []
    po_header = ''
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
    # print(secretDict)

    mydb = hdbcliConnect()
    # print(resp['SecretString'])
    # payload = []
    vendor_data = {}
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)

            if "pageno" in event["params"]["querystring"]:
                start_idx = int(event["params"]["querystring"]['pageno'])
                
            if "nooflines" in event["params"]["querystring"]:
                end_idx = int(event["params"]["querystring"]['nooflines'])
                        
                start_idx = (start_idx -1 ) * end_idx


            # SELECT *  FROM einvoice_db_portal.po_header where in_status = 'new' or in_status = 'approved' order by ref_po_no desc  limit 0 , 6 ; 
            if "pageno" in event["params"]["querystring"] and "nooflines" in event["params"]["querystring"]:

                records = {
                    "po_number":'',
                    "ref_po_no":'',
                    "supplier_name":'',
                    "po_date":'',
                    "modified_by":'',
                    "status":'',
                    "error_log":''
                }
                
                mycursor.execute(" SELECT *  FROM po_header where in_status = 'new' or in_status = 'submitted' order by ref_po_no desc  limit ? offset ? ",(end_idx,start_idx))
              
                rec = mycursor.fetchall()
                
                for i in rec:
                    records["po_number"] = i["po_number"]
                    records["ref_po_no"] = i["ref_po_no"]
                    records["supplier_name"] = i["buyer"]
                    records["po_date"] = i["po_date"]
                    records["modified_by"] = ''
                    records["status"] = i["in_status"]
                    records["error_log"] = ''

                    records_list.append(records.copy())

            if "ref_po_no" in event["params"]["querystring"]:
                
                ref_po_no = int(event["params"]["querystring"]['ref_po_no'])
                
                mycursor.execute('SELECT * FROM einvoice_db_portal.file_storage where file_id = ? and attach_id > 5000' , ref_po_no )
                files = mycursor.fetchone()
                mycursor.execute(" SELECT *  FROM einvoice_db_portal.po_header where ref_po_no = ? ",(ref_po_no))
                po_h = mycursor.fetchone()
                mycursor.execute(" SELECT *  FROM einvoice_db_portal.po_item where ref_po_no = ? ",(ref_po_no))
                po_i = mycursor.fetchall()

                lis_po_h = ['po_number','po_date','delivery_address','bill_to_address','buyer','currency','delivery_date','purchase_group','total_amount','taxable_amount','tax_percentage']

                po_header = {
                    'po_number' : '',
                    'po_date' : '',
                    'delivery_address':'',
                    'bill_to_address':'',
                    'buyer':'',
                    'currency':'',
                    'delivery_date':'',
                    'purchase_group':'',
                    'total_amount':'',
                    'taxable_amount':'',
                    'tax_percentage':'',
                    'ref_po_no':ref_po_no,
                    'in_status':po_h['in_status'],
                    'plant':po_h['plant'],
                    'company_code':po_h['company_code'],
                    'items':[],
                    'files':[],
                    'so_number':po_h['so_number'],
                    'audit_trails':[
         {
            "member_id":39,
            "date":"2023-04-20 12:08:52",
            "msg":"Scanned from a Xerox Multifunction Printer-8 (1).pdf attachment uploaded by Admin 001"
         },
         {
            "member_id":39,
            "date":"2023-04-20 12:01:18",
            "msg":"Scanned from a Xerox Multifunction Printer-8 (1).pdf attachment uploaded by Admin 001"
         },
         {
            "member_id":39,
            "date":"2023-04-13 11:08:32",
            "msg":"Techpass-9200109783_INVOICE.pdf attachment uploaded by Admin 001"
         }
 ]
                }

                for i in lis_po_h:
                    po_header[i] = po_h[i]
                
                print(po_header)

                lis_po_i = ['item_no','hsn_code','material_no','material_name','quantity','unit_price','unit_of_measure','tax_percentage','taxable_amount','tax_amount','total_amount','ref_po_no']

                po_item = {
                    'item_no':'',
                    'hsn_code':'',
                    'material_no':'',
                    'material_name':'',
                    'quantity':'',
                    'unit_price':'',
                    'unit_of_measure':'',
                    'tax_percentage':'',
                    'taxable_amount':'',
                    'tax_amount':'',
                    'total_amount':''
                }

                items = []
                for j in po_i:  
                    for i in lis_po_i:
                        po_item[i] = j[i]
                    items.append(po_item.copy())

                po_header['items'] = items
                po_header['files'] = [files]

            mydb.commit()
    
    except :
        return {  
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()

    if records_list != []:
        return {
        'statusCode': 200,
        'body': records_list
    }
    elif po_header != '':
        return {
        'statusCode': 200,
        'body': po_header
    }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Successful')
        }
# event = {'body-json': {'condn': []}, 'params': {'path': {}, 'querystring': {'nooflines': '10', 'pageno': '1', 'userid': 'einvoiceportal@gmail.com'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjYyZTlkYThmLTc2NmQtNDdlOC1hMTIzLTg1M2RiY2Q4N2FmOSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg2NjU0OTIzLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg2NjU4NTIzLCJpYXQiOjE2ODY2NTQ5MjMsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.Jm5fa9O5Cier519bkwdmvMg6utxa9WLEYZB-nmhemE0J5PIleYk5HKEyCOmZkv4-w-vHxRM9ARRaTGqmynB0OkA_KGt11TjrGudZqcTX7JNbD9NjEzCI5n3rmFROrAoTUoeayop6iVMf2M2pC9i-i_WmP_mfxaj-8LR8EWWKOW9h2iPTQ1UPXW_rVpUqQsyQLKjlHgkLeSIwXQBlsKa8TYYcCLyY-Vl3mjlUPr5EkyiIRg48FDUTYjOfV8PKfMMuqtphHKFaTpegzdnvR7MAcHQhuPvg4_EZIOtrfKBMp65aJYhOYaK8vIepiR_keGgGeeZuLrq6vHtLe4yCUijk7A', 'content-type': 'application/json', 'Host': '4kaosyaovj.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-64884fee-6e660cb251796f167c157b97', 'X-Forwarded-For': '49.207.51.54', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '4kaosyaovj', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'dev', 'source-ip': '49.207.51.54', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': '5b1443db-f0fd-4b73-a9ac-1856fd4a5ca3', 'resource-id': 'vvlhxg', 'resource-path': '/trackso'}}

# print(getTrackSalesOrders(event, ' '))

#working fine for event  
def fetchlogintime(event, context):
    date = datetime.datetime.now()
    email = str(event['params']['querystring']['email'])
    date = str(date)
    result = ''
    # TODO implement
    print(event)
    
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
    # # secretDict = {'username': 'admin', 'password': 'U2r3MmmffmtZMSJMrG2u', 'engine': 'mysql', 'host': 'newclientdb.cuoh0am6dz76.ap-northeast-1.rds.amazonaws.com', 'port': '3306', 'dbname': 'einvoice_db_portal', 'dbInstanceIdentifier': 'db-dev-einvoice'}


    mydb = hdbcliConnect()
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")

            if 'email' in event['params']['querystring'] and 'login_date_time' not in event['params']['querystring']  :
                # email = event['params']['querystring']['email']
                asd = email 
                result = mycursor.execute(" SELECT date FROM user_logintime where email = ? ", asd)
                result = mycursor.fetchone()
                if result != None :
                    date = result['date']
                else :                    
                    mycursor.execute("INSERT INTO user_logintime (email,date) values (? , ?) ", (email, date))

            elif 'email' in event['params']['querystring']  and 'login_date_time' in event['params']['querystring']  :
                date = str(event['params']['querystring']['login_date_time'])
                values = (date,email)
                
                time.sleep(1)
                mycursor.execute("UPDATE user_logintime SET date = ? WHERE email = ?",values)            
            mydb.commit()

    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
    return {
        'statusCode': 200,
        'body': {'date':"Last Login Date & Time "+date}
    }
 
# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'email': 'einvoiceportal@gmail.com', 'login_date_time': '15/06/2023 10:59:51'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjEwOTIwNDUyLTZhYzAtNGNmZC04OWQ3LTIwNTFkODRmNmU3MyIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjg2ODA2OTkwLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjg2ODEwNTg5LCJpYXQiOjE2ODY4MDY5OTAsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.lZSNWrOF-QgaJt-1PTRkdagvmASZikbd7klWEaQiBapb2wnZCRvLV6PTibHmBi8LykVCmQgzvwrrPp4QqTaFwfK7zxKrIT5RyrWxXhosKQtQ5VRyMKCDiHI0PXIYUeleYghePZLhclgPvFT1lSUhq8n0cr26LQwmWP6NT75rRCeEzo-hr3FXQQqnpMkC7erVaMe94cUcL9w1APXr3mMYJxHTG3Al9n-0gML1TMGqNzdc0Npz9OZEIkoatUPJdAKOGbye3F5AvtQMKMLCJHDZsTd5JuySLZ9OREajizjwxYvpeAzTNkRCvkzOVSN-K9wMMQ7X1teeUmfcxv_TWF7rLA', 'Host': '4kaosyaovj.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-648aa1ce-78f03e5b627cedf912c49cdf', 'X-Forwarded-For': '49.207.51.244', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '4kaosyaovj', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'dev', 'source-ip': '49.207.51.244', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'f131b6f9-98c8-47cf-a108-20785bd905e3', 'resource-id': 'x54kty', 'resource-path': '/user_logintime'}}
# print(fetchlogintime(event , ' '))

#event not found
def deleteVendordemo(event, context):
    # TODO implement
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
    # print(secretDict)

    mydb = hdbcliConnect()
    # print(resp['SecretString'])
    # payload = []
    vendor_data = {}
    
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
            
            code = event["params"]["querystring"]["code"]
            sqlQuery = "delete from master where code = ?"
            mycursor.execute(sqlQuery,code)
            mydb.commit()
    
    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Deleted Successfully')
    }

#working fine for event 
def getVendordemo(event, context):
    # TODO implement
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
    # print(resp['SecretString'])
    # payload = []
    vendor_data = {}
    
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
                    
            sqlQuery="select * from Vendor_master"
            mycursor.execute(sqlQuery)   
            vendor_data = mycursor.fetchall()
            vendor_data = convertValuesTodict(mycursor.description, vendor_data)

    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
    
    return {
        'statusCode': 200,
        'body': vendor_data
    }

#working fine for event 
def patchVendordemo(event, context):
    # TODO implement
    
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
    # print(resp['SecretString'])
    # payload = []
    vendor_data = {}
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = " set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            master_name = event["params"]["querystring"]["master_name"]
            code = event["params"]["querystring"]["code"]
            sqlQuery = "update master set master_name = ? where code = ?"
            values = (master_name,code)
            mycursor.execute(sqlQuery,values)
            mydb.commit()
        
        
    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': json.dumps('Updated Successfull!')
    }

# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'code': '100', 'master_name': 'DEF'}, 'header': {'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Host': '4kaosyaovj.execute-api.eu-central-1.amazonaws.com', 'Postman-Token': 'e9f0ce10-26d7-49a5-81ab-21a6ff54eaf3', 'User-Agent': 'PostmanRuntime/7.28.4', 'X-Amzn-Trace-Id': 'Root=1-61db27bf-4def408257d171bf593fba58', 'X-Forwarded-For': '115.99.98.61', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'elipo_trainee', 'lambda_alias': 'dev', 'secreat': 'demo/elipo/secret'}, 'context': {'account-id': '', 'api-id': '4kaosyaovj', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'PATCH', 'stage': 'dev', 'source-ip': '115.99.98.61', 'user': '', 'user-agent': 'PostmanRuntime/7.28.4', 'user-arn': '', 'request-id': 'e6be0583-f521-4de4-a5f6-ba3160625977', 'resource-id': '3e3qrv', 'resource-path': '/vendor'}}
# print(patchVendordemo(event , ' '))

#working fine
def postVendordemo(event, context):
    # TODO implement
    
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
    # print(resp['SecretString'])
    # payload = []
    
    
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
            
            master_id = event["params"]["querystring"]["master_id"]
            code = event["params"]["querystring"]["code"]
            master_name = event["params"]["querystring"]["master_name"]
            description = event["params"]["querystring"]["description"]
            sqlQuery="insert into master(master_id,code,master_name,description) values {}"
            values = (master_id,code,master_name,description)
            mycursor.execute(sqlQuery.format(tuple(values))) 
            mydb.commit()

    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
    return {
        'statusCode': 200,
        'body': json.dumps('Inserted Successfully')
    }

def deleteAprroverDetails(event, context):
    global dbScehma 
    
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
    
    # print(event)

    try:
        with mydb.cursor() as mycursor:
            dbScehma = event["stage-variables"]["schema"]
            
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            # sqlQuery = "DELETE FROM approver WHERE approver_id = ?"
            # values = (event["params"]["querystring"]["approver_id"])
            # mycursor.execute(sqlQuery, values)
            # # affected_row = mycursor.lastrowid
            
            # msg = "Approver ID " + event["params"]["querystring"]["approver_id"] + " deleted"   
            
            
            if len(event["params"]["querystring"]["approver_id"].split(',')) == 1:
                values = (event["params"]["querystring"]["approver_id"],)
                mycursor.execute("DELETE FROM approver WHERE approver_id = %s",values)
            else:
                mycursor.execute("DELETE FROM approver WHERE approver_id in {}".format(tuple(event["params"]["querystring"]["approver_id"].split(','))))
            
            mydb.commit()
            
            # msg = "Code" + event["params"]["querystring"]["codes"] + " deleted" 
            
            # mydb.commit()
            
    except:
        
        return {
            'statuscode': 500,
            'body': json.dumps("unable to delete")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("deleted successfully")
    }

def getApproverDetails(event, context):
    print('event')
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

    records = {}
    
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



            # approver = []
            
            # sqlQuery = "select a.approver_id, a.member_id, a.approval_type, a.approval_level," \
            #     " a.is_valid, m.fs_name, m.ls_name, m.email, m.position " \
            #     "from approver a inner join member m on a.member_id = m.member_id where a.rule = %s"
            
            # ==========================
            # sqlQuery = "SELECT r.rule, r.decider, r.operator, r.d_value, r.d_value2, r.rule_id, ra.approver, ra.level, ra.isgroup, m.fs_name, m.ls_name, m.email, m.position " \
            #             "FROM einvoice_db_portal.rule r " \
            #             "inner join einvoice_db_portal.rule_approver ra " \
            #             "on r.rule_id = ra.rule_key " \
            #             "inner join einvoice_db_portal.member m " \
            #             "on ra.approver = m.member_id " \
            #             "where r.rule = %s and ra.isgroup = 'n' order by r.rule"
                        
            # values = (event["params"]["querystring"]["rule"],)

            # mycursor.execute(sqlQuery, values)
            # print(mycursor)
            # for row in mycursor:
                
            #     if row["decider"] == "cost_center":
            #         decider = "Cost center"
                
            #     elif row["decider"] == "amount":
            #         decider = "Amount"
                    
            #     elif row["decider"] == "discount":
            #         decider = "Discount"
                
            #     if row["operator"] == "between":
            #         approval_type = decider + " in between " + row["d_value"] + " and " + row["d_value2"]
            #     else:
            #         approval_type = decider + " " + row["operator"] + " " + row["d_value"]
                
            #     record = {
            #         'rule_id' : row["rule_id"],
            #         'level' : row["level"],
            #         'member_id': row["approver"],
            #         'member_name': row["fs_name"] + " " + row["ls_name"],
            #         'approval_type': approval_type,
            #         'approval_level': row["level"],
            #         'isgroup': row["isgroup"],
            #         'email': row["email"]
            #     }
            #     approver.append(record)
                
            # records["approver"] = sorted(approver, key = lambda i: (i['rule_id'], i['level'])) 
            
            # =====================
                
            # sqlQuery = "SELECT r.rule, r.decider, r.operator, r.d_value, r.d_value2, r.rule_id, ra.approver, ra.level, ra.isgroup, g.group_id, g.name " \
            #             "FROM einvoice_db_portal.rule r " \
            #             "inner join einvoice_db_portal.rule_approver ra " \
            #             "on r.rule_id = ra.rule_key  " \
            #             "inner join einvoice_db_portal.group g " \
            #             "on ra.approver = g.group_id " \
            #             "where r.rule = %s and ra.isgroup = 'y'"
                        
            # values = (event["params"]["querystring"]["rule"],)

            # mycursor.execute(sqlQuery, values)
            
            # for row in mycursor:
                
            #     if row["decider"] == "cost_center":
            #         decider = "Cost center"
                
            #     elif row["decider"] == "amount":
            #         decider = "Amount"
                    
            #     elif row["decider"] == "discount":
            #         decider = "Discount"
                
            #     if row["operator"] == "between":
            #         approval_type = decider + " in between " + row["d_value"] + " and " + row["d_value2"]
            #     else:
            #         approval_type = decider + " " + row["operator"] + " " + row["d_value"]
                
            #     record = {
            #         'rule_id' : row["rule_id"],
            #         'level' : row["level"],
            #         'member_id': row["approver"],
            #         'member_name': row["name"],
            #         'approval_type': approval_type,
            #         'approval_level': row["level"],
            #         'isgroup': row["isgroup"]
            #     }
            #     approver.append(record)

            # records["approver"] = sorted(approver, key = lambda i: (i['rule_id'], i['level'])) 
            
            
            
            rule_detail = []
                
            mycursor.execute("SELECT a.* FROM rule a left join rule_snro b on a.rule_id = b.rule_id where b.is_approval = 'y' order by rule_id ")
            rules = mycursor.fetchall()
                
            dict_rule = rules
            rule_keys = []
            escalator = []
            distinct_rule = []
                
            for row in rules:
                temp = {
                    "rule_id": row["rule_id"],
                    "approval_type" : row["approval_type"]
                }
                distinct_rule.append(temp)
                
            # print(distinct_rule)
                    
            res_list = [] 
            for i in range(len(distinct_rule)): 
                if distinct_rule[i] not in distinct_rule[i + 1:]: 
                    res_list.append(distinct_rule[i]) 
            # print(res_list)
            
            if rules:
                for each in rules:
                    rule_keys.append(each['rule_id'])
            
            if rule_keys and len(rule_keys) > 1:
                mycursor.execute("SELECT * FROM rule_approver where isgroup = 'n' and rule_key in {}".format(tuple(rule_keys)))
                approvers_list = mycursor.fetchall()
                
            elif len(rule_keys) == 1:
                key = (rule_keys[0])
                sqlQuery = "select * from rule_approver where isgroup = 'n' and rule_key = %s"
                mycursor.execute(sqlQuery, key)
                approvers_list = mycursor.fetchall()
                
            memberid = []
            
            if approvers_list:
                for row in approvers_list:
                    memberid.append(row["approver"])
            
            approver_final = []  
            
            if memberid and len(memberid) > 1:
                mycursor.execute("select member_id, fs_name, ls_name, position from member where member_id in {}".format(tuple(memberid)))
            
            elif len(memberid) == 1:
                member = (memberid[0])
                sqlQuery = "select member_id, fs_name, ls_name, position from member where member_id = %s"
                mycursor.execute(sqlQuery, member) 
                    
            for row in mycursor:
                temp1 = {
                    "approver": row["member_id"],
                    "name": row["fs_name"] + " " + row["ls_name"]
                }
                approver_final.append(temp1)
         
            for row in res_list:
                approvers = []
                criteria = []
                
                for data in approvers_list:
                        
                    if row["rule_id"] == data["rule_key"]:
                        
                        for temp1 in approver_final:
                                
                            if data["approver"] == temp1["approver"]:
                            
                                temp = {
                                    "approver" : data["approver"],
                                    "name": temp1["name"],
                                    "level" : data['level']
                                }
                                approvers.append(temp)
                                    
                for value in dict_rule:
                    
                    decider = ""
                    if row["rule_id"] == value["rule_id"]:
                        
                        if value["decider_type"] == "string":
                            
                            if value["decider"] == "discount" and value["operator"] != "between":
                                decider = "Discount" + " " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "discount" and value["operator"] == "between":
                                decider = "Discount between" + value["d_value"] + " and " + value["d_value2"]
                                    
                            elif value["decider"] == "amount" and value["operator"] != "between":
                                decider = "Amount" + " " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "amount" and value["operator"] == "between":
                                decider = "Amount between " + value["d_value"] + " and " + value["d_value2"]
                                    
                            elif value["decider"] == "gl_account":
                                decider = "G/L account " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "currency":
                                decider = "Currency " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "cost_center":
                                decider = "Cost center" + " " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "npo":
                                decider = "NPO " + " " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "vendor_no":
                                decider = "Vendor No. " + " " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "department_id":
                                decider = "Department ID " + " " + value["operator"] + " " + value["d_value"]
                                
                            elif value["decider"] == "item_category":
                                decider = "Item Category " + " " + value["operator"] + " " + value["d_value"]
                            
                            elif value["decider"] == "default":
                                decider = "Default"
                                
                            criteria.append(decider)
                                
                        else:
                            
                            if value["decider"] == "discount" and value["operator"] != "between":
                                decider = "Discount" + " " + value["operator"] + " " + str(int(value["d_value"]))
                                
                            elif value["decider"] == "discount" and value["operator"] == "between":
                                decider = "Discount between" + " " + str(int(value["d_value"])) + " and " + str(int(value["d_value2"]))
                                
                            elif value["decider"] == "amount" and value["operator"] != "between":
                                    decider = "Amount" + " " + value["operator"] + " " + str(int(value["d_value"]))
                                
                            elif value["decider"] == "amount" and value["operator"] == "between":
                                decider = "Amount between " + str(int(value["d_value"])) + " and " + str(int(value["d_value2"]))
                                    
                            elif value["decider"] == "gl_account" and value["operator"] != "between":
                                decider = "G/L account " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "currency" and value["operator"] != "between":
                                decider = "Currency " + value["operator"] + " " + value["d_value"]
                                
                            elif value["decider"] == "cost_center":
                                decider = "Cost center between " + " " + value["operator"] + " " + value["d_value"]
                                
                            elif value["decider"] == "npo":
                                decider = "NPO " + " " + value["operator"] + " " + value["d_value"]
                                
                            elif value["decider"] == "vendor_no":
                                decider = "Vendor No. " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "department_id":
                                decider = "Department ID " + " " + value["operator"] + " " + value["d_value"]
                                    
                            elif value["decider"] == "item_category":
                                decider = "Item Category " + " " + value["operator"] + " " + value["d_value"]
                                
                            elif value["decider"] == "default":
                                decider = "Default"
                                    
                            criteria.append(decider)
                        
                record = {
                    "rule_id": row["rule_id"],
                    "approval_type" : row["approval_type"], 
                    "criteria": criteria,
                    "approvers" : approvers
                }
                rule_detail.append(record)
        
    except :   
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure"),
        }
        
    finally:
        mydb.close()
    
    return {
        'statuscode': 200,
        'body': rule_detail
    }

def patchApproverDetails(event, context):
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
    
    # print(event)

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "approval_type" in event["body-json"] and "approval_level" in event["body-json"]:
                sqlQuery = "update approver set approval_type = %s, approval_level = %s where approver_id = %s"
                values = (event["body-json"]["approval_type"], event["body-json"]["approval_level"], event["params"]["querystring"]["approver_id"])
                mycursor.execute(sqlQuery, values)
                # affected_row = mycursor.lastrowid
                
            elif "group_id" in event["body-json"] and "approval_level" in event["body-json"]:
                sqlQuery = "update approver set group_id = %s, approval_level = %s where approver_id = %s"
                values = (event["body-json"]["group_id"], event["body-json"]["approval_level"], event["params"]["querystring"]["approver_id"])
                mycursor.execute(sqlQuery, values)
                # affected_row = mycursor.lastrowid
                
            elif "approval_type" in event["body-json"]:
                sqlQuery = "update approver set approval_type = %s where approver_id = %s"
                values = (event["body-json"]["approval_type"],  event["params"]["querystring"]["approver_id"])
                mycursor.execute(sqlQuery, values)
                # affected_row = mycursor.lastrowid
                
            elif "approval_level" in event["body-json"]:
                sqlQuery = "update approver set approval_level = %s where approver_id = %s"
                values = (event["body-json"]["approval_level"], event["params"]["querystring"]["approver_id"])
                mycursor.execute(sqlQuery, values)
                # affected_row = mycursor.lastrowid
            
            elif "group_id" in event["body-json"]:
                sqlQuery = "update approver set group_id = %s where approver_id = %s"
                values = (event["body-json"]["group_id"], event["params"]["querystring"]["approver_id"])
                mycursor.execute(sqlQuery, values)
                # affected_row = mycursor.lastrowid
            
            msg = "Approver ID " + event["params"]["querystring"]["approver_id"] + " updated"   
            
            mydb.commit()
            
    except:
        
        return {
            'statuscode': 500,
            'body': json.dumps("unable to modify")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps(msg)
    }

def postApproverDetails(event, context):
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
        "rule" :"",
        "member_id" : "",
        "approval_type" : "",
        "approval_level" : "",
        "is_valid":"y",
        "group_id":""
    }

    try:
        
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
            
            sqlQuery = "INSERT INTO approver (rule, member_id, approval_type, approval_level, is_valid, group_id)" \
                       " VALUES (%s, %s, %s, %s, %s, %s)"
            values = (record["rule"], record["member_id"], record["approval_type"], record["approval_level"], record["is_valid"], record["group_id"])
            
            # print(sqlQuery)
            # print(values)
            mycursor.execute(sqlQuery, values)
    
            approver_id = mycursor.lastrowid
    
            del sqlQuery
            del values
    
            sqlQuery = "select fs_name, ls_name, email, position, group_id from member where member_id = '%s'"
            values = (int(record["member_id"]),)
    
            mycursor.execute(sqlQuery, values)
            member_details = mycursor.fetchone()
    
            del sqlQuery
            del values
    
            sqlQuery = "INSERT INTO dropdown (drop_key, value1, value2, value3) VALUES (%s, %s, %s, %s)"
    
            values = ('approver', approver_id, member_details["position"], member_details["email"])
    
            mycursor.execute(sqlQuery, values)
            
            mydb.commit()
            
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Approver insertion failed!")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Record inserted!")
    }

def getMemberNGroupDetails(event, context):
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
   
    records = []
    
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

            
            if "search_string" in event["params"]["querystring"] and "assign_details" in event["params"]["querystring"]:
                temp = event["params"]["querystring"]["search_string"] + "%%"
                 
                mycursor.execute("SELECT distinct(group_id), name " \
                	"FROM " + dbScehma + ".group " \
                    "where role in ('app', 'ssu', 'superadmin') and name like %s " \
                    "order by name", temp)
                    
                for row in mycursor:
                    record = { 
                        'id'  : row['group_id'], 
                        'name' : row['name'],
                        'is_group': 'y',
                        'position': ""
                    }
                    records.append(record)
                    
                values = ( temp , temp )
                mycursor.execute("SELECT m.member_id, concat(m.fs_name, ' ', m.ls_name) as member_name, d.value2 " \
                	"FROM member m " \
                	"left join dropdown d " \
                	"on m.user_type = d.value1 " \
                    "inner join " + dbScehma + ".group g " \
                    "on m.group_id = g.group_id " \
                    "where g.role in ('app', 'ssu', 'superadmin') and (m.fs_name like %s or m.ls_name like %s) " \
                    "order by m.fs_name", values)
                    
                for row in mycursor:
                    record = {
                        'id': row['member_id'],
                        'name': row['member_name'],
                        'is_group': 'n',
                        'position': row["value2"]
                    }
                    records.append(record)
                
            elif "search_string" in event["params"]["querystring"]:
                sqlQuery = "SELECT m.member_id, concat(m.fs_name, ' ', m.ls_name) as member_name, d.value2 " \
                    "FROM member m " \
                	"left join dropdown d " \
                	"on m.user_type = d.value1 " \
                    "where fs_name like %s or ls_name like %s order by fs_name"
                temp = event["params"]["querystring"]["search_string"] + "%%"
                values = ( temp , temp )
                mycursor.execute(sqlQuery, values)
                
                for row in mycursor:
                    record = {
                        'id': row['member_id'],
                        'name': row['member_name'],
                        'is_group': 'n',
                        'position': row["value2"]
                    }
                    records.append(record)
                    
                sqlQuery = "SELECT group_id, name FROM " + dbScehma + ".group where name like %s order by name"
                temp = event["params"]["querystring"]["search_string"] + "%%"
                values = ( temp, )
                mycursor.execute(sqlQuery, values)
                
                for row in mycursor:
                    record = { 
                        'id'  : row['group_id'], 
                        'name' : row['name'],
                        'is_group': 'y'
                    }
                    records.append(record)
            
            elif "assign_details" in event["params"]["querystring"]:
                mycursor.execute("SELECT distinct(group_id), name " \
                	"FROM " + dbScehma + ".group " \
                    "where role in ('app', 'ssu', 'superadmin') " \
                    "order by name")
                    
                for row in mycursor:
                    record = { 
                        'id'  : row['group_id'], 
                        'name' : row['name'],
                        'is_group': 'y'
                    }
                    records.append(record)
                    
                mycursor.execute("SELECT m.member_id, concat(m.fs_name, ' ', m.ls_name) as member_name, value2 " \
                	"FROM member m " \
                	"left join dropdown d " \
                	"on m.user_type = d.value1 " \
                    "inner join " + dbScehma + ".group g " \
                    "on m.group_id = g.group_id " \
                    "where g.role in ('app', 'ssu', 'superadmin')" \
                    "order by m.fs_name")
                    
                for row in mycursor:
                    record = {
                        'id': row['member_id'],
                        'name': row['member_name'],
                        'is_group': 'n',
                        'position': row["value2"]
                    }
                    records.append(record)
                
            else:   
                mycursor.execute("select group_id, name from " + dbScehma + ".group order by name")
                
                for row in mycursor:
                    record = { 
                        'id'  : row['group_id'], 
                        'name' : row['name'],
                        'is_group': 'y'
                    }
                    records.append(record)
                    
                mycursor.execute("SELECT member_id, concat(fs_name, ' ', ls_name) as member_name, value2 " \
                    "FROM member " \
                	"left join dropdown " \
                	"on user_type = value1 " \
                	"order by fs_name")
                	
                for row in mycursor:
                    record = {
                        'id': row['member_id'],
                        'name': row['member_name'],
                        'is_group': 'n',
                        'position': row["value2"]
                    }
                    records.append(record)
    except:
        return{
            'statusCode': 500,
            'body': json.dumps("Internal Error")
        }
                
    finally:
        mydb.close()
        
    return{
        'statusCode': 200,
        'body':records
    }  

# secretsmanager NOT DONE
def downloadAttachments(event, context):
    print(event)
    global dbScehma 
    dbScehma = event["stageVariables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )
            
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
    # return base64.b64encode(file_content)

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
                        
                        mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
                        on = mycursor.fetchone()
                        if on['value1'] == 'on':
                            chk = enable_xray(event)
                            if chk['Enable'] == True:
                                patch_all() 
                                print(event)
                        
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

def postChangPassword(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    secreat = event["stage-variables"]["secreat"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    resp = client.get_secret_value(
        SecretId=secreat
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
        "previouspassword": "",
        "proposedpassword": "",
        "accesstoken": "",
        "email": ""
    }

    try: 
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

            
            cognito = boto3.client('cognito-idp')
            response = cognito.change_password(
                PreviousPassword = record["previouspassword"],
                ProposedPassword = record["proposedpassword"],
                AccessToken = record["accesstoken"]
            )
            
            if response:
                # print(response)
                pass
                
            #     sqlQuery = "update einvoice_db_portal.member set password = %s where email = %s"
            #     values = ( record["proposedpassword"], record["email"] )
            #     mycursor.execute( sqlQuery, values )
            
            # mydb.commit()

    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Password Not Changed!")
        }
          
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Password Changed!")
    }

# einvoice-fetch-dropdown
def einvoice_fetch_dropdown(event, context):
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
    
    headers_res = {
                    "Access-Control-Allow-Origin":"*",
                    "Access-Control-Allow-Headers":"Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods":"GET,POST,OPTIONS",
                    "Access-Control-Expose-Headers":"*"
                    
                }
    
    # records = {}
    drop_values = []
    
    
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
                    # print(event)
            
            if "drop_key" in event["params"]["querystring"]:
                
                drop_name =  event["params"]["querystring"]['drop_key']
                
                if drop_name == "approver":
                    
                    mycursor.execute("select group_id, name from " + dbScehma + ".group")
                    for row in mycursor:
                        record = { 
                        'drop_key': "approver",
                        'table_key'  : row['group_id'], 
                        'value2' : row['name'], 
                        'value3' : "y",
                        'value4' : ""
                        }
                        drop_values.append(record)
                        
                    mycursor.execute("select a.approver_id, a.member_id, b.fs_name, b.ls_name, b.email from approver a inner join member b on a.member_id = b.member_id")
                    for row in mycursor:
                        record = { 
                        'drop_key': "Approver",
                        'table_key'  : row['approver_id'], 
                        'value2' : row['fs_name'] + " " + row["ls_name"], 
                        'value3' : "n",
                        'value4' : row["email"]
                        }
                        drop_values.append(record)
                        
                elif drop_name == "comp_tax":
                    mycursor.execute("SELECT value1 FROM elipo_setting where key_name = 'country';")
                    con = mycursor.fetchone()
                    mycursor.execute("SELECT company_code FROM default_master where country = %s " , con['value1'] )
                    com_code = mycursor.fetchone()
                    mycursor.execute("SELECT tax_code , description , tax_per FROM tax_code where company_code = %s;" , com_code['company_code'] )
                    for row in mycursor:
                        tax_dec = str(row['tax_per']) + '--' + row['description']
                        record = { 
                        'drop_key': "comp_tax",
                        'table_key'  : row['tax_code'], 
                        'value2' : tax_dec , 
                        'value3' : row['description'],
                        'value4' : row['tax_per']
                        }
                        drop_values.append(record)   
                        tax_dec = ''

                        
                else:
                    query ="select * from dropdown where drop_key = %s order by value2"
                        
                    values = (str(drop_name),)
                    
                    mycursor.execute(query, values)
                    
                    for row in mycursor:
                        record = { 
                        'drop_key': row['drop_key'],
                        'table_key'  : row['value1'], 
                        'value2' : row['value2'], 
                        'value3' : row['value3'],
                        'value4' : row['value4'] 
                        }
                        drop_values.append(record)
                        
                
            elif "drop_keys" in event["params"]["querystring"]:  
                # print(list(event["params"]["querystring"]["drop_keys"]))
                l_ist = ['approver','group']
                mycursor.execute("select * from dropdown where drop_key in {}".format(tuple(l_ist)))
                
                for row in mycursor:
                    record = { 
                    'drop_key': row['drop_key'],
                    'table_key'  : row['value1'], 
                    'value2' : row['value2'], 
                    'value3' : row['value3'],
                    'value4' : row['value4'] 
                    }
                    drop_values.append(record)
                    
    
    except:
        return{
            'statusCode': 500,
            'headers': headers_res,
            'body': json.dumps("Key not found")
        }
                
    finally:
        mydb.close()
        
        
    return{
        'statusCode': 200,
        'headers': headers_res,
        'body':drop_values
    }    

def getSearchedInvoice(event, context):
    global dbScehma 

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
    
    records = {}
    user_settings = {}
    print('-------------------')
    print(event)
    try:
        with mydb.cursor() as mycursor:
            dbScehma = event["stage-variables"]["schema"]
            
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute("SELECT * FROM elipo_setting")
            settings = mycursor.fetchall()

            if settings:
                for each in settings:
                    user_settings[each['key_name']] = each['value1']
                del settings
            
            email = None
            edit = None
            
            values_pag = []
            
            if "tabname" in event["params"]["querystring"]:
                tabname = event["params"]["querystring"]['tabname']
                start_idx = int(event["params"]["querystring"]['pageno'])
                end_idx = int(event["params"]["querystring"]['nooflines'])
                    
                start_idx = (start_idx -1 ) * end_idx
                    
            
            if "userid" in event["params"]["querystring"]:
                email = event["params"]["querystring"]["userid"]
                
            if "edit" in event["params"]["querystring"]:
                edit  = event["params"]["querystring"]["edit"]
                
            if "invoice_no" in event["params"]["querystring"]:
                    
                invoiceNo = event["params"]["querystring"]["invoice_no"] 
                
                if edit:
                
                    values = (invoiceNo,)
                    mycursor.execute("select * from invoice_log where invoice_no = %s", values)
                    invoice_log = mycursor.fetchone()
                    
                    if invoice_log:
                        values = (invoice_log["member_id"],)
                        mycursor.execute("select fs_name, ls_name, email from member where member_id = %s", invoice_log["member_id"])
                        member = mycursor.fetchone()
                        
                        if email != member["email"]:
                            msg = "Invoice is locked by " + str(member["fs_name"]) + " " + str(member["ls_name"])
                            
                            return {
                                'statuscode': 204,
                                'body': json.dumps(msg)
                            }
                    else:
                        if email:
                            values = (email,)
                            mycursor.execute("select member_id from member where email = %s", values)
                            member = mycursor.fetchone()
                            
                            if member:
                                values = ( invoiceNo, member["member_id"] )
                                mycursor.execute("insert into invoice_log (invoice_no, member_id) values (%s, %s)", values)
                                mydb.commit()
                    
                items = []
                invoice_files = []
                error_log = []
                record = []
                approvers = []
                
                sqlQuery = "select country from default_master where company_code = (Select company_code from invoice_header where invoice_no = %s)"
                values = (invoiceNo)
                mycursor.execute(sqlQuery,values)
                country = mycursor.fetchone()
                    
                mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id = %s order by attach_id", event["params"]["querystring"]["invoice_no"])
                for row in mycursor:
                    record = {
                        'attach_id': row['attach_id'],  
                        "invoice_id" : row["file_id"],
                        "file_name" : row["name"],
                        "mime_type" : row["mime_type"],
                        "file_link" : row["file_link"]
                    }
                    invoice_files.append(record)
                    
                mycursor.execute("select a.member_id, a.approved_date, concat(b.fs_name, ' ', b.ls_name) as app_name " \
                	"from approval_history a " \
                    "join member b " \
                    "on a.member_id = b.member_id " \
                    "where invoice_no = %s ",  event["params"]["querystring"]["invoice_no"] )
                        
                for row in mycursor:
                    record = {
                        "member_id": row["member_id"],
                        "approved_date": str(row["approved_date"]),
                        "member_name": row["app_name"]
                    }
                    approvers.append(record)
                    
                mycursor.execute("select * from sap_error_log where invoice_no = %s", event["params"]["querystring"]["invoice_no"])
                for row in mycursor:
                    err = {
                        "type": row["error_type"],
                        "msg": row["error_msg"]
                    }
                    error_log.append(err)
                        
                values = (event["params"]["querystring"]["invoice_no"],)
                mycursor.execute("select a.*, b.vendor_name, c.value2 from invoice_header a left join vendor_master b " \
                    "on a.supplier_id = b.vendor_no left join dropdown c on a.document_type = c.value1 where invoice_no = %s", values)
                invoice_header = mycursor.fetchone()
                    
                if invoice_header:
                    mycursor.execute("select department_name from departmental_budget_master where department_id = %s", (invoice_header["department_id"],))
                    department = mycursor.fetchone()
                    
                if department:
                    department_name = department["department_name"]
                    
                else:
                    department_name = None
                    
                tax_percentage = None
                
                if invoice_header["tax_per"]:
                    tax_percentage = int(invoice_header["tax_per"])
                    
                records = {
                    "user_invoice_id": invoice_header["user_invoice_id"],
                    "invoice_no" :invoice_header["invoice_no"],
                    "in_status" : invoice_header["in_status"],
                    "from_supplier" : invoice_header["from_supplier"],
                    "sap_invoice_no" : invoice_header['sap_invoice_no'],
                    "ref_po_num" : invoice_header["ref_po_num"],
                    "company_code" : invoice_header["company_code"],
                    "invoice_date" : str(invoice_header["invoice_date"]),
                    "posting_date" : str(invoice_header["posting_date"]),
                    "baseline_date": str(invoice_header["baseline_date"]),
                    "amount" : invoice_header["amount"],
                    "currency" : invoice_header["currency"],
                    "jurisdiction_code":invoice_header["jurisdiction_code"],
                    "payment_method" : invoice_header["payment_method"],
                    "gl_account" : invoice_header["gl_account"],
                    "business_area" : invoice_header["business_area"],
                    "supplier_id" : invoice_header["supplier_id"],
                    "supplier_name" : invoice_header["supplier_name"],
                    "approver_id" : invoice_header["approver_id"],
                    "approver_comments" : invoice_header["approver_comments"],
                    "modified_date" : str(invoice_header["modified_date"]),
                    "cost_center" : invoice_header["cost_center"],
                    "taxable_amount" : invoice_header["taxable_amount"],
                    "discount_per" : invoice_header["discount_per"],
                    "total_discount_amount" : invoice_header["total_discount_amount"],
                    "is_igst" : invoice_header["is_igst"],
                    "tax_per" : tax_percentage, 
                    "cgst_tot_amt": invoice_header["cgst_tot_amt"],
                    "sgst_tot_amt": invoice_header["sgst_tot_amt"],
    	            "igst_tot_amt": invoice_header["igst_tot_amt"],
                    "tds_per": invoice_header["tds_per"],
                    "tds_tot_amt": invoice_header["tds_tot_amt"],
                    "payment_terms" : invoice_header["payment_terms"],
                    "adjustment" : invoice_header["adjustment"],
                    "supplier_comments": invoice_header['supplier_comments'],
                    "tcs": invoice_header["tcs"],
                    "internal_order": invoice_header["internal_order"],
                    "department_id": invoice_header["department_id"],
                    "department_name": department_name,
                    "npo": invoice_header["npo"],
                    "app_comment": invoice_header["app_comment"],
                    "document_type" : invoice_header["document_type"],
                    "gstin": invoice_header["gstin"],
                    "irn": invoice_header["irn"],
                    "doc_type_desc": invoice_header["value2"],
                    "head_accuracy": invoice_header["head_accuracy"],
                    "item_accuracy": invoice_header["item_accuracy"],
                    "ocr_accuracy": invoice_header["ocr_accuracy"],
                    "items" : items,
                    "files" : invoice_files,
                    "error_log": error_log,
                    "approvers": approvers,
                    "country" : country['country']
                }
                    
                mycursor.execute("select * from invoice_item where invoice_no = %s", values)
                for row in mycursor:
                    record = {
                      "item_no":row["item_no"],
                      "ebelp": row["ebelp"],
                      "hsn_code": row["hsn_code"],
                      "material":row["material"],
                      "material_desc":row["material_desc"],
                      "quantity":row["quantity"],
                      "unit":row["unit"],
                      "amount":row["amount"],
                      "currency": row["currency"],
                      "amt_per_unit" : row["amt_per_unit"],
                      "cgst_per": row["cgst_per"],
                      "cgst_amount":row["cgst_amount"],
                      "tax_code":row["tax_code"],
                      "ref_po_no":row["ref_po_no"],
                      "plant":row["plant"],
                      "discount":row["discount"],
                      "discount_amount" : row["discount_amount"],
                      "gross_amount" : row["gross_amount"],
                      "sgst_per": row["sgst_per"],
                      "sgst_amount": row["sgst_amount"],
                      "igst_per": row["igst_per"],
                      "igst_amount": row["igst_amount"],
                      "taxable_amount": row["taxable_amount"],
                      "tax_value_amount": row["tax_value_amount"],
                      "gl_account": row["gl_account"],
                      "gst_per": row["gst_per"],
                      "ocr_matched" : row["ocr_matched"],
                      "cost_center": row["cost_center"],
                      "qc_check": row["qc_check"]
                      }
                    items.append(record) 
                        
                records["items"] = items
                
            elif "condn" in event["body-json"]:
                
                if "userid" in event["params"]["querystring"]:
                    email = event["params"]["querystring"]["userid"]
                    mycursor.execute("select user_type, member_id, group_id from member where email = %s", email)
                    role = mycursor.fetchone()
                
                val_list = []
                member_detail = []
                pos = 0
                condn = ""
                records = {}
                
                val_list.append(tabname)
    
                for row in event["body-json"]["condn"]:
                    if pos != 0:
                        condn = condn + " and "
                    elif pos == 0:
                        pos = pos + 1
    
                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                        condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                    elif str(row["operator"]) == "between":
                        val_list.append(row["value"])
                        val_list.append(row["value2"])
                        condn = condn + " " + str(row["field"]) + " between %s and %s "
                    else:
                        val_list.append(row["value"])
                        condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                    
                if role["user_type"] == 'npoapp':
                    condn = condn + " and a.npo = 'y' "
                
                if user_settings["app_assignment"] == 'on':
                    sqlQuery = "SELECT a.invoice_no as invoice_no, a.ref_po_num, a.in_status, a.user_invoice_id, a.sap_invoice_no, a.invoice_date, a.posting_date, a.amount, " \
                        "a.currency,a.jurisdiction_code, a.supplier_name, a.approver_id, a.approver_comments, convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date , a.supplier_comments, " \
                        "a.faulty_invoice, a.gstin, c.fs_name, c.ls_name, d.vendor_name, e.value2 as document_type " \
                        "FROM invoice_header a " \
                        "left outer join member c on a.working_person = c.member_id " \
                        "left outer join dropdown e on a.document_type = e.value1 " \
                        "left join vendor_master d " \
                        "on a.supplier_id = d.vendor_no " \
                        "where (sup_status is null or sup_status <> 'draft') and invoice_no in ( " \
                        	"select invoice_no " \
                        		"from assignment " \
                                "where ( isgroup = 'y' and app = %s ) or ( isgroup = 'n' and app = %s ) ) and in_status = %s "
                
                elif user_settings["app_assignment"] == 'off':
                    sqlQuery = "SELECT a.invoice_no as invoice_no, a.ref_po_num, a.in_status, a.user_invoice_id, a.sap_invoice_no, a.invoice_date, a.posting_date, a.amount, " \
                        "a.currency,a.jurisdiction_code, a.supplier_name, a.approver_id, a.approver_comments, convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date , a.supplier_comments, " \
                        "a.faulty_invoice, a.gstin, c.fs_name, c.ls_name, d.vendor_name, e.value2 as document_type " \
                        "FROM invoice_header a " \
                        "left outer join member c on a.working_person = c.member_id " \
                        "left outer join dropdown e on a.document_type = e.value1 " \
                        "left join vendor_master d " \
                        "on a.supplier_id = d.vendor_no " \
                        "where (sup_status is null or sup_status <> 'draft') and in_status = %s "
                                
                if condn:
                    sqlQuery = sqlQuery + " and " + condn 
                    
                if user_settings["app_assignment"] == 'on':
                    member_detail.append(role["group_id"])
                    member_detail.append(role["member_id"])
                val_list.append(start_idx)
                val_list.append(end_idx)
                    
                sqlQuery = sqlQuery + " order by a.invoice_no desc limit %s,%s "
                
                values = member_detail + val_list
                mycursor.execute(sqlQuery, values)
                    
                invoice_obj = mycursor.fetchall()
                
                val_list.pop()
                val_list.pop()
                
                if user_settings["app_assignment"] == 'on':     
                    sqlQuery = "select count(in_status) as invoice_count, in_status from invoice_header " \
                        "where (sup_status is null or sup_status <> 'draft')  and invoice_no in ( " \
                    	"select invoice_no " \
                    		"from assignment " \
                            "where ( isgroup = 'y' and app = %s ) or ( isgroup = 'n' and app = %s ) ) "
                
                elif user_settings["app_assignment"] == 'off':
                    sqlQuery = "select count(in_status) as invoice_count, in_status from invoice_header where (sup_status is null or sup_status <> 'draft')"
                    
                if condn:
                    sqlQuery = sqlQuery + "  and " + condn + " group by in_status"  
                else:
                    sqlQuery = sqlQuery + " group by in_status"
                    
                del val_list[0]
    
                values = member_detail + val_list
                # print(sqlQuery, values)
                mycursor.execute(sqlQuery,values)
        
                countrec = {}
                total_count = 0
                
                for each in mycursor:
                    
                    total_count = total_count + int(each["invoice_count"])
                    countrec[each['in_status']] = each['invoice_count']
                    
                if "" in countrec:
                    del countrec['']
                
                if None in countrec:
                    del countrec[None]
                    
                if "new" not in countrec:
                    countrec["new"] = 0
                        
                if "draft" not in countrec:
                    countrec["draft"] = 0
                    
                if "inapproval" not in countrec:
                    countrec["inapproval"] = 0
                        
                if "tosap" not in countrec: 
                    countrec["tosap"] = 0
                        
                if "rejected" not in countrec:
                    countrec["rejected"] = 0
                    
                countrec['total_count'] = total_count
                        
                invoices = []
                invoice_files = []
                groupid = []
                memberid = []
                    
                res = [sub['invoice_no'] for sub in invoice_obj]
                
                if res :
                    if len(res) == 1:
                        values = (res[0], )
                        mycursor.execute("select * from approval where invoice_no = %s and referred_approver = 'n' order by invoice_no desc, approval_level", values)
                        approvers_list = mycursor.fetchall()
                            
                    elif len(res) > 1:
                        mycursor.execute("select * from approval where referred_approver = 'n' and invoice_no in {} order by invoice_no desc, approval_level".format(tuple(res)))
                        approvers_list = mycursor.fetchall()
                
                    for row in approvers_list: 
                    
                        if row["isgroup"] == 'y':
                            groupid.append(row["approver"])
                        elif row["isgroup"] == 'n':
                            memberid.append(row["approver"])
                        
                    format_strings_mem = ','.join(['%s'] * len(memberid))
                        
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
                            "approval_type": ""
                        }
                        approver_final.append(temp1)
                        
                    if memberid:
                        sqlQuery = "select distinct a.approver, b.member_id, b.fs_name, b.ls_name from rule_approver a " \
                            "inner join member b on a.approver = b.member_id where a.approver in (%s)" % format_strings_mem
                        mycursor.execute(sqlQuery, tuple(memberid)) 
                        
                        for row in mycursor:
                            
                            if row["fs_name"] == None and row["ls_name"] == None:
                                name = None
                            
                            elif row["fs_name"] == None and row["ls_name"] != None:
                                name = row["ls_name"]
                                
                            elif row["fs_name"] != None and row["ls_name"] == None:
                                name = row["fs_name"]
                            
                            else:
                                name = str(row["fs_name"]) + " " + str(row["ls_name"])
                                
                            temp1 = {
                                "isgroup": "n",
                                "approver": row["approver"],
                                "name": str(name),
                                "approval_type": ""
                            }
                            approver_final.append(temp1)
                    
                if res and len(res) > 1:
                    mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id in {}".format(tuple(res)))
                            
                elif res and len(res) == 1:
                    values = (res[0],)
                    mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id = %s", values)
                        
                for row in mycursor:
                    record = {
                        'attach_id': row['attach_id'],
                        "invoice_id" : row["file_id"],
                        "file_name" : row["name"],
                        "mime_type" : row["mime_type"],
                        "file_link" : row["file_link"]
                    }   
                    invoice_files.append(record)
                    
                if len(res) == 1:
                    mycursor.execute("select m.member_id, concat(m.fs_name, ' ', m.ls_name) as approver_name, a.invoice_no, a.approval_level, a.approval_type " \
                        "from member m " \
                        "inner join approval_history a " \
                    	"on m.member_id = a.member_id " \
                        "where a.invoice_no = %s " \
                        "order by a.invoice_no desc, a.approval_level desc ", res[0])
                    sap_approved = mycursor.fetchall()
                            
                elif len(res) > 1:
                    mycursor.execute("select m.member_id, concat(m.fs_name, ' ', m.ls_name) as approver_name, a.invoice_no , a.approval_level, a.approval_type " \
                        "from member m " \
                        "inner join approval_history a " \
                        "on m.member_id = a.member_id " \
                        "where a.invoice_no in {} " \
                        "order by a.invoice_no desc, a.approval_level desc".format(tuple(res)))
                    sap_approved = mycursor.fetchall()  
                    
                approval_type = []
                error_op = []
                sap_app_name = ""
                sap_app_list = []
                
                for row in invoice_obj:
                    approvers = []
                    files = []
                    
                    for data in invoice_files:
                        
                        if str(row["invoice_no"]) == str(data["invoice_id"]):
                            temp = {
                                "file_name" : data["file_name"],
                                "mime_type" : data["mime_type"],
                                "file_link" : data["file_link"]
                            }
                            files.append(temp)
                            
                    for app in sap_approved:
                        if int(row["invoice_no"]) == int(app["invoice_no"]):    
                            sap_app_name = app["approver_name"]
                            temp2 = {
                                "isgroup" : 'n',
                                "approver" : app["member_id"],
                                "name": app["approver_name"],
                                "level" : app['approval_level'],
                                "approval_type": app["approval_type"],
                                "isapproved" : 'To ERP'
                            }
                            sap_app_list.append(temp2)
                        
                    if row["fs_name"] == None and row["ls_name"] == None:
                        name = None
                            
                    elif row["fs_name"] == None and row["ls_name"] != None:
                        name = row["ls_name"]
                        
                    elif row["fs_name"] != None and row["ls_name"] == None:
                        name = row["fs_name"]
                            
                    else:
                        name = str(row["fs_name"]) + " " + str(row["ls_name"])   
                        
                    for temp in approvers_list:
                        approval_type = None
                        
                        if row["invoice_no"] == temp["invoice_no"]:
                                
                            for temp1 in approver_final:
                                if temp["approver"] == temp1["approver"] and temp["isgroup"] == temp1["isgroup"]:
                                        
                                    if temp["isapproved"] == "y":
                                        status = "accepted"
                                    elif temp["isapproved"] == 'n':
                                        status = "inapproval" 
                                            
                                    status_ap = {
                                        "isgroup" : temp1["isgroup"],
                                        "approver" : temp1["approver"],
                                        "name": temp1["name"],
                                        "level" : temp['approval_level'],
                                        "approval_type": temp1["approval_type"],
                                        "isapproved" : status
                                    }
                                    approvers.append(status_ap)
                        
                    record = {
                      "invoice_no":row["invoice_no"],
                      "document_type": row["document_type"],
                      "gstin": row["gstin"],
                      "in_status":row["in_status"],
                      "ref_po_no": row["ref_po_num"],
                      "user_invoice_id" : row['user_invoice_id'],
                      "working_person" : str(name),
                      "sap_invoice_no" : row['sap_invoice_no'],
                      "invoice_date":str(row["invoice_date"]),
                      "posting_date":str(row["posting_date"]),
                      "amount":row["amount"],
                      "currency": row["currency"],
                      "jurisdiction_code":row["jurisdiction_code"],
                      "supplier_name":row["vendor_name"], 
                      "approver_id":row["approver_id"],
                      "approver_comments" : row["approver_comments"],
                      "modified_date" : str(row["modified_date"]),
                      "supplier_comments": row['supplier_comments'],
                      "approver_name":sap_app_name,
                      "approvers": approvers,
                      "approval_type": approval_type,
                      "error_log": error_op,
                      "invoice_files" : files,
                      'faulty_invoice': row['faulty_invoice'],
                      'sap_approver': sap_app_list
                    }
                    invoices.append(record)
                        
                records["invoices"] = invoices
                records["count"] = countrec
                
            else:
                
                records = {}
                condn = " " 
                
                if "userid" in event["params"]["querystring"]:
                    email = event["params"]["querystring"]["userid"]
                    mycursor.execute("select user_type, member_id, group_id from member where email = %s", email)
                    role = mycursor.fetchone()
                
                values_pag.append(tabname)
                if user_settings["app_assignment"] == 'on':
                    values_pag.append(role["group_id"])
                    values_pag.append(role["member_id"])
                values_pag.append(start_idx)
                values_pag.append(end_idx)
                
                if role["user_type"] == 'npoapp':
                    condn = " and a.npo = 'y' "

                invoices_obj = []
                result_list = []
                sqlQuery = "select d_value from rule where decider='vendor_no' and is_on = 'y' and rule_id in (select rule_key from rule_approver where approver = %s )" 
                values = (tuple(values_pag))[2]
                mycursor.execute(sqlQuery,values)
                supplier_id = mycursor.fetchall()
                for each in supplier_id:
                    result = eval(each['d_value']) 
                    result_list.append(result)
                    result_tuple = tuple(result_list)
                    list = [tuple([value]) for value in result_tuple]
                    cond = (', '.join("'{}'".format(t[0]) for t in list))
                               
                if user_settings["app_assignment"] == 'on' and len(supplier_id) != 0:

                    sqlQuery = "select a.invoice_no, a.in_status,a.sap_invoice_no, a.user_invoice_id, a.from_supplier, a.ref_po_num, a.company_code, a.invoice_date, a.posting_date, " \
                        "a.amount, a.currency,a.jurisdiction_code, a.gl_account, a.business_area, a.supplier_id, a.npo, a.approver_id, a.supplier_name, a.approver_comments, " \
                        "convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date, a.working_person,a.supplier_comments, a.faulty_invoice, a.gstin, c.fs_name, " \
                        "c.ls_name, d.vendor_name, e.value2 as document_type " \
                        "FROM invoice_header a " \
                        "left outer join member c " \
                        "on a.working_person = c.member_id " \
                        "left join vendor_master d " \
                        "on a.supplier_id = d.vendor_no " \
                        "left outer join dropdown e " \
                        "on a.document_type = e.value1 " \
                        "where a.supplier_id IN ({}) and in_status = %s " \
                        " order by a.invoice_no desc limit %s, %s " .format(cond)
                    
                    mycursor.execute(sqlQuery,(values_pag[0],values_pag[3],values_pag[4]))
                    invoices_obj= mycursor.fetchall()
                                 
                elif user_settings["app_assignment"] == 'on':
                    sqlQuery = "select d_value from rule where decider='vendor_no' and is_on = 'y'"
                    result_list = []
                    mycursor.execute(sqlQuery)
                    values = mycursor.fetchall()
                    values1 = values
                    for each in values:
                        values = eval(each['d_value'])
                        result_list.append(values)
                        result_tuple = tuple(result_list)
                        list = [tuple([value]) for value in result_tuple]
                        cond = (', '.join("'{}'".format(t[0]) for t in list))
                    if len(values1) != 0:  
                        sqlQuery = "select a.invoice_no, a.in_status,a.sap_invoice_no, a.user_invoice_id, a.from_supplier, a.ref_po_num, a.company_code, a.invoice_date, a.posting_date, " \
                            "a.amount, a.currency,a.jurisdiction_code, a.gl_account, a.business_area, a.supplier_id, a.npo, a.approver_id, a.supplier_name, a.approver_comments, " \
                            "convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date, a.working_person,a.supplier_comments, a.faulty_invoice, a.gstin, c.fs_name, " \
                            "c.ls_name, d.vendor_name, e.value2 as document_type " \
                            "FROM invoice_header a " \
                            "left outer join member c " \
                            "on a.working_person = c.member_id " \
                            "left join vendor_master d " \
                            "on a.supplier_id = d.vendor_no " \
                            "left outer join dropdown e " \
                            "on a.document_type = e.value1 " \
                            "where a.supplier_id Not IN ({}) and in_status = %s and (sup_status is null or sup_status <> 'draft') and invoice_no in ( " \
                                "select invoice_no " \
                                "from assignment " \
                                "where ( isgroup = 'y' and app = %s ) or ( isgroup = 'n' and app = %s ) " \
                            ")  order by a.invoice_no desc limit %s, %s" .format(cond)
                    else:
                        sqlQuery = "select a.invoice_no, a.in_status,a.sap_invoice_no, a.user_invoice_id, a.from_supplier, a.ref_po_num, a.company_code, a.invoice_date, a.posting_date, " \
                        "a.amount, a.currency,a.jurisdiction_code, a.gl_account, a.business_area, a.supplier_id, a.npo, a.approver_id, a.supplier_name, a.approver_comments, " \
                        "convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date, a.working_person,a.supplier_comments, a.faulty_invoice, a.gstin, c.fs_name, " \
                        "c.ls_name, d.vendor_name, e.value2 as document_type " \
                        "FROM invoice_header a " \
                        "left outer join member c " \
                        "on a.working_person = c.member_id " \
                        "left join vendor_master d " \
                        "on a.supplier_id = d.vendor_no " \
                        "left outer join dropdown e " \
                        "on a.document_type = e.value1 " \
                        "where in_status = %s and (sup_status is null or sup_status <> 'draft') and invoice_no in ( " \
                    		"select invoice_no " \
                    			"from assignment " \
                                "where ( isgroup = 'y' and app = %s ) or ( isgroup = 'n' and app = %s ) " \
                        ") order by a.invoice_no desc limit %s, %s "

                    mycursor.execute(sqlQuery,(tuple(values_pag)))
                    invoices_obj = mycursor.fetchall() 
                        

                elif user_settings["app_assignment"] == 'off':
                    sqlQuery = "select a.invoice_no, a.in_status,a.sap_invoice_no, a.user_invoice_id, a.from_supplier, a.ref_po_num, a.company_code, a.invoice_date, a.posting_date, " \
                        "a.amount, a.currency, a.jurisdiction_code, a.gl_account, a.business_area, a.supplier_id, a.npo, a.approver_id, a.supplier_name, a.approver_comments, " \
                        "convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date, a.working_person,a.supplier_comments, a.faulty_invoice, a.gstin, c.fs_name, " \
                        "c.ls_name, d.vendor_name, e.value2 as document_type " \
                        "FROM invoice_header a " \
                        "left outer join member c " \
                        "on a.working_person = c.member_id " \
                        "left join vendor_master d " \
                        "on a.supplier_id = d.vendor_no " \
                        "left outer join dropdown e " \
                        "on a.document_type = e.value1 " \
                        "where in_status = %s and (sup_status is null or sup_status <> 'draft') " \
                        "order by a.invoice_no desc limit %s, %s "
                
                # sqlQuery = "select a.invoice_no, a.in_status,a.sap_invoice_no, a.user_invoice_id, a.from_supplier, a.ref_po_num, a.company_code, a.invoice_date, a.posting_date, " \
                #     "a.amount, a.currency, a.gl_account, a.business_area, a.supplier_id, a.npo, a.approver_id, a.supplier_name, a.approver_comments, " \
                #     "convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date, a.working_person,a.supplier_comments, a.faulty_invoice, a.gstin, c.fs_name, " \
                #     "c.ls_name, d.vendor_name, e.value2 as document_type " \
                #     "FROM invoice_header a " \
                #     "left outer join member c " \
                #     "on a.working_person = c.member_id " \
                #     "left join vendor_master d " \
                #     "on a.supplier_id = d.vendor_no " \
                #     "left outer join dropdown e " \
                #     "on a.document_type = e.value1 " \
                #     "where in_status = %s and (sup_status is null or sup_status <> 'draft') and invoice_no in ( " \
                #     	"select invoice_no " \
                #     		"from assignment " \
                #             "where ( isgroup = 'y' and app = %s ) or ( isgroup = 'n' and app = %s ) " \
                #     ") order by a.invoice_no desc limit %s, %s "
                    
                    mycursor.execute(sqlQuery, tuple(values_pag))
                    invoices_obj = mycursor.fetchall()
                
                invoices = []
                invoice_files = []
                    
                res = [sub['invoice_no'] for sub in invoices_obj]
                    
                groupid = []
                memberid = []
                error_log = []
                    
                if res:  
                    if len(res) == 1:
                        values = (res[0], )
                        mycursor.execute("select * from sap_error_log where invoice_no = %s order by invoice_no desc", values)
                        error_log = mycursor.fetchall()
                        
                    elif len(res) > 1:
                        mycursor.execute("select * from sap_error_log where invoice_no in {} order by invoice_no desc".format(tuple(res)))
                        error_log = mycursor.fetchall()
                    
                    if len(res) == 1:
                        values = (res[0], )
                        mycursor.execute("select * from approval where invoice_no = %s and referred_approver = 'n' order by invoice_no desc, approval_level", values)
                        approvers_list = mycursor.fetchall()
                            
                    elif len(res) > 1:
                        mycursor.execute("select * from approval where referred_approver = 'n' and invoice_no in {} order by invoice_no desc, approval_level".format(tuple(res)))
                        approvers_list = mycursor.fetchall()
                
                    for row in approvers_list: 
                    
                        if row["isgroup"] == 'y':
                            groupid.append(row["approver"])
                        elif row["isgroup"] == 'n':
                            memberid.append(row["approver"])
                        
                    format_strings_mem = ','.join(['%s'] * len(memberid))
                        
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
                            "approval_type": ""
                        }
                        approver_final.append(temp1)
                        
                    if memberid:
                        sqlQuery = "select distinct a.approver, b.member_id, b.fs_name, b.ls_name from rule_approver a " \
                            "inner join member b on a.approver = b.member_id where a.approver in (%s)" % format_strings_mem
                        mycursor.execute(sqlQuery, tuple(memberid)) 
                        
                        for row in mycursor:
                            
                            if row["fs_name"] == None and row["ls_name"] == None:
                                name = None
                            
                            elif row["fs_name"] == None and row["ls_name"] != None:
                                name = row["ls_name"]
                                
                            elif row["fs_name"] != None and row["ls_name"] == None:
                                name = row["fs_name"]
                            
                            else:
                                name = str(row["fs_name"]) + " " + str(row["ls_name"])
                                
                            temp1 = {
                                "isgroup": "n",
                                "approver": row["approver"],
                                "name": str(name),
                                "approval_type": ""
                            }
                            approver_final.append(temp1)
                        
                    if len(res) == 1:
                        mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id = %s", res[0])
                        file = mycursor.fetchall()
                        
                    elif len(res) > 1:
                        mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id in {}".format(tuple(res))) 
                        file = mycursor.fetchall()
                    
                    if len(res) == 1:
                        mycursor.execute("select DISTINCT(concat(m.fs_name, ' ', m.ls_name)) as approver_name, a.invoice_no, a.approval_level, a.approval_type, a.member_id " \
                            "from member m " \
                            "inner join approval_history a " \
                        	"on m.member_id = a.member_id " \
                            "where a.invoice_no = %s " \
                            "order by a.invoice_no desc, a.approval_level desc ", res[0])
                        sap_approved = mycursor.fetchall()
                            
                    elif len(res) > 1:
                        mycursor.execute("select DISTINCT(concat(m.fs_name, ' ', m.ls_name)) as approver_name, a.invoice_no, a.approval_level, a.approval_type, a.member_id " \
                            "from member m " \
                            "inner join approval_history a " \
                            "on m.member_id = a.member_id " \
                            "where a.invoice_no in {} " \
                            "order by a.invoice_no desc, a.approval_level ".format(tuple(res)))
                        sap_approved = mycursor.fetchall()
                    
                sap_app_name = "" 
                
                for row in invoices_obj:
                    approvers = []
                    files = []
                    error_op = []
                    sap_app_list = []
                    
                    for errors in error_log:
                        if str(row["invoice_no"]) == str(errors["invoice_no"]):
                            err = {
                                "invoice_no" : errors["invoice_no"],
                                "type" : errors["error_type"],
                                "msg" : errors["error_msg"]
                            }
                            error_op.append(err)
                        
                    for data in file: 
                            if str(row["invoice_no"]) == str(data["file_id"]):
                                temp = {
                                    'attach_id': data['attach_id'],
                                    "file_name" : data["name"],
                                    "mime_type" : data["mime_type"],
                                    "file_link" : data["file_link"]
                                }
                                files.append(temp)
                        
                    for temp in approvers_list:
                        approval_type = None
                        
                        if row["invoice_no"] == temp["invoice_no"]:
                                
                            for temp1 in approver_final:
                                if temp["approver"] == temp1["approver"] and temp["isgroup"] == temp1["isgroup"]:
                                        
                                    if temp["isapproved"] == "y":
                                        status = "accepted"
                                    elif temp["isapproved"] == 'n':
                                        status = "inapproval" 
                                            
                                    status_ap = {
                                        "isgroup" : temp1["isgroup"],
                                        "approver" : temp1["approver"],
                                        "name": temp1["name"],
                                        "level" : temp['approval_level'],
                                        "approval_type": temp1["approval_type"],
                                        "isapproved" : status
                                    }
                                    approvers.append(status_ap)
                                    
                    for app in sap_approved:
                        if int(row["invoice_no"]) == int(app["invoice_no"]):
                            temp2 = {
                                "isgroup" : 'n',
                                "approver" : app["member_id"],
                                "name": app["approver_name"],
                                "level" : app['approval_level'],
                                "approval_type": app["approval_type"],
                                "isapproved" : 'To ERP'
                            }
                            sap_app_list.append(temp2)
                             
                    if row["fs_name"] == None and row["ls_name"] == None:
                        name = None
                            
                    elif row["fs_name"] == None and row["ls_name"] != None:
                        name = row["ls_name"]
                        
                    elif row["fs_name"] != None and row["ls_name"] == None:
                        name = row["fs_name"]
                            
                    else:
                        name = str(row["fs_name"]) + " " + str(row["ls_name"])
                        
                    approval_type = None
                    
                    if tabname == "tosap":
                        for each in sap_approved:
                            if each["invoice_no"] == row["invoice_no"]:
                                approval_type = each["approval_type"]
                                break
                            
                    else:
                        for each in approvers_list:
                            if each["invoice_no"] == row["invoice_no"]:
                                approval_type = each["approval_type"]
                                break
                        
                    if row["npo"] == 'y':
                        invoice_type = 'NPO'
                        
                    elif row["npo"] == None and row["ref_po_num"] == None:
                        invoice_type = 'None'
                        
                    elif row["ref_po_num"] != None:
                        invoice_type = 'PO'
                        
                    record = {
                        "invoice_no" :row["invoice_no"],
                        "document_type": row["document_type"],
                        "gstin": row["gstin"],
                        "ref_po_no": row["ref_po_num"],
                        "in_status" : row["in_status"],
                        "invoice_type": invoice_type,
                        "user_invoice_id" : row['user_invoice_id'],
                        "sap_invoice_no" : row['sap_invoice_no'],
                        "invoice_date" : str(row["invoice_date"]),
                        "posting_date" : str(row["posting_date"]),
                        "amount" : row["amount"],
                        "currency": row["currency"],
                        "jurisdiction_code" : row["jurisdiction_code"],
                        "supplier_id" : row["supplier_id"],
                        "supplier_name" : row["vendor_name"],
                        "approver_name": sap_app_name,
                        "modified_date": str(row["modified_date"]),
                        "working_person": str(name),
                        "supplier_comments":row["supplier_comments"],
                        "approval_type": approval_type,
                        "invoice_files":files,
                        "approvers":approvers,
                        "sap_approver": sap_app_list,
                        "error_log": error_op,
                        'faulty_invoice': row['faulty_invoice']  
                    }
                    invoices.append(record)
                records["invoices"] = invoices

    except: 
        return {
        'statuscode': 500,
        'body': json.dumps("Internal Failure")   
    }
            
    finally:
        mydb.close()
        
    # if records['supplier_name'] == 'PricewaterhouseCoopers Ltd':
    #     for i in records['items'] :
    #         i['material'] = ' '
        
    return {
        'statuscode': 200,
        'body': records
    }
# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'nooflines': '50', 'pageno': '1', 'tabname': 'new', 'userid': 'einvoiceportal@gmail.com'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjA4NWMyODRjLTM1NmItNGM0Ni04OWIwLTZmNzFiYWI5YWFiNSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjQ1NTEyMzUxLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjQ1NTE1OTUxLCJpYXQiOjE2NDU1MTIzNTEsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.LAB1waI9IKObN5mSSAzi1ri-QQO_N6JWr_Wny-TQJ-ayeH88ZOxhUwZXFTD0Bl4UBMGufuxyP4vEGym1hmOb1x5yg1Z-JsuPTAV2eQbDP7jTNH02W0WQT754vg1SALIwCGk2ObwV11tIKIjQIvI4gGKKspowtp-fKNvv-8Qli-8UQ-WbPfKK8DqFd4D9nloKpRJS9g24rTjb00BJ85FljSutUe6BO_duYuDDFGY0C9Oe3UWomSYq8IErT_aQfjccHjyghs1uYTzCe6_lZRbBWNDOGQwMYGRsiB39m5L8KcmMOCxs7Corxf57alj77laXPIKLsV9Cz7fyp57Vio5Smg', 'content-type': 'application/json', 'Host': '5ud4f0kv53.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-62148d36-5630f7f2033a54f50c4d0655', 'X-Forwarded-For': '171.61.97.214', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '5ud4f0kv53', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'einvoice-v1', 'source-ip': '171.61.97.214', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36', 'user-arn': '', 'request-id': '63fd3122-ba20-4a99-b04e-1c0f0a44a47c', 'resource-id': 'jrt2lh', 'resource-path': '/fetch-invoice'}}
# print(lambda_handler(event,context=""))

def getSapPoDetail(event, context):
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
    
    s3 = boto3.client("s3")
    
    output = {}
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            print(event)
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            mycursor.execute("select value1 from elipo_setting where key_name = 'po_validation'")
            on1 = mycursor.fetchone()
            if on1['value1'] == 'on':
                
                if "ref_po_num" in event["params"]["querystring"]:
                    po_number = event["params"]["querystring"]["ref_po_num"]
                    
                    mycursor.execute("select * from elipo_setting where key_name in ('sap_po_fetch_url', 'sap_password', 'sap_userid')")
                    settings = mycursor.fetchall()
    
                    user_settings = {}
        
                    if settings:
                        for each in settings:
                            user_settings[each['key_name']] = each['value1']
        
                        del settings
                    
                        # url = "http://182.72.219.94:8000/zgetpo/GetPo"
                    
                    s = requests.Session()
                    s.headers.update({'Connection': 'keep-alive'})
                    # url = user_settings["sap_po_fetch_url"]
                    url = "http://182.72.219.94:8000/zinvoicepo/GetPo"
                    params = { 'sap-client': '800' }
        
                    headersFetch = { 'X-CSRF-TOKEN': 'Fetch' }
                    # y = s.get(url, auth=HTTPBasicAuth(user_settings["sap_userid"], user_settings["sap_password"]), headers=headersFetch, params=params, timeout=10)
                    y = s.get(url, auth=HTTPBasicAuth('developer08', 'Peol@123'), headers=headersFetch, params=params, timeout=10)

                    token = y.headers["X-CSRF-TOKEN"]
                    # token = True
    
                    
                    if token:
                        headers = {"X-CSRF-TOKEN": token, 'Content-type': 'application/json'}
                        records = {
                            "ID": po_number
                        }
                        
                        x = s.post(url, json=records, headers = headers, auth=HTTPBasicAuth('developer08', 'Peol@123'),  params=params, timeout=10)
            
                        payload = x.json()
                        print(payload)
                        sap_errors = []
                        items = []
                        error_flag = False
                        
                        if payload:
                            # print(payload)
                            if payload[0]["PORETURN"]:
                                for each in payload[0]["PORETURN"]:
                                    if each["TYPE"] == "E":
                                        error_flag = True
                                    
                                    err_dict = {
                                        'type' : each["TYPE"],                                    
                                        'msg' : each["MESSAGE"]
                                    }
                                    sap_errors.append(err_dict)
                                    
                                output = sap_errors
                                
                                return{
                                    'statuscode': 201,
                                    'body': output
                                }
                            
                            values = []   
                            if payload[0]["POITEM"]:
                                res = [sub['PLANT'] for sub in payload[0]["POITEM"]]
                                if res:
                                    format_strings = ','.join(['%s'] * len(res))
                                    
                                    sqlQuery = "select code, description " \
                                        "from master " \
                                        "where master_id = '7' and code in (%s)" % format_strings
                                    mycursor.execute(sqlQuery, tuple(res))
                                    plants = mycursor.fetchall()
                                
                                for each in payload[0]["POITEM"]:
                                    temp = ( po_number, each["MATERIAL"], each["SHORT_TEXT"], each["PO_ITEM"] )
                                    values.append(temp)
                                    
                                    plant_desc = None
                                    mat_no = None
                                    
                                    for row in plants:
                                        if row["code"] == each["PLANT"]:
                                            plant_desc = row["description"]
                                            
                                    if str(each["ITEM_CAT"]) == str(9) and each["ACCTASSCAT"] == 'K':
                                        mycursor.execute("select material_no from material_master where material_name = %s", each["SHORT_TEXT"])
                                        material_det = mycursor.fetchone()
                                        
                                        if material_det:
                                            mat_no = material_det["material_no"]
                                            
                                    if mat_no == None:
                                        mat_no = each["MATERIAL"]
                                            
                                    row_item = {
                                        "po_item": each["PO_ITEM"],
                                        "material": mat_no,
                                        "materialdesc": each["SHORT_TEXT"],     
                                        "quantity": each["QUANTITY"],
                                        "unit": each["PO_UNIT"],
                                        "tax_code": each["TAX_CODE"],
                                        "plant": each["PLANT"],
                                        "plant_desc": plant_desc,
                                        "item_category": each["ITEM_CAT"],
                                        "net_price": each["NET_PRICE"],                            #each["ITEM_CAT"]    each["PSTYP"]
                                        "account_assign": each["ACCTASSCAT"]
                                    }
                                    items.append(row_item)
                                    
                                header = {
                                    "company_code": payload[0]["COMP_CODE"],
                                    "currency": payload[0]["CURRENCY"],
                                    "supplier_id": payload[0]["VENDOR"],
                                    "total_amount": int(payload[0]["LV_NETVAL"]),
                                    "sheet_no": (payload[0]["LV_SHEET_NO"]),     
                                    "items": items
                                }
                                output = header
                            
                            mycursor.execute("select count(*) as count from po_detail where po_number = %s", po_number)
                            count = mycursor.fetchone()
                            
                            if count["count"] != 0: 
                                mycursor.execute("delete from po_detail where po_number = %s", po_number)
                            
                            sqlQuery = "insert into po_detail (po_number, material, material_desc, item_no) values (%s, %s, %s, %s)"
                            mycursor.executemany(sqlQuery, values)
                            
                            mydb.commit()
            
    except requests.exceptions.Timeout as msg:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Resource temporarily unavailable!")
        }
        
    except requests.exceptions.TooManyRedirects as msg:
        mydb.rollback()
        return {
            'statuscode': 500, 
            'body': json.dumps("Too Many Redirects!")
        }
        
    except requests.exceptions.RequestException as msg:
        mydb.rollback()
        return {
            'statuscode': 500, 
            'body': json.dumps("Resource temporarily unavailable!")
        }
        
    except requests.exceptions.ConnectionError as msg:
        mydb.rollback()
        return {
            'statuscode': 500, 
            'body': json.dumps("Resource temporarily unavailable!")
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
        'body': output
    }

# event = {'body-json': {}, 'params': {'path': {}, 'querystring': {'ref_po_num': '4500020423'}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6Ijc2ZjU5ZTE3LTk4ODQtNDIxNy05YzExLWYwZmZkYzgxMWNmZiIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjU1OTYwNzc3LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjU1OTY0Mzc3LCJpYXQiOjE2NTU5NjA3NzcsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.JRq9APX4PCe38tCbZXU1hb3Bkdw0wBq3j3PhHYmHr4eOXkz37AvZFXukO6rrhM4RjW9ISlL8N6d60jDrsmCxHHc1zoqFx6YRM4-ZMyvBgivKAiQWY2FD1nvZ-Q7ZrckqSbgmDVDCDU3yq9GRrou_mDK0HYWdq_v-XjRQUhg4Q_w7jq6fYOM2PsLGRkDX4Sxrlcz58GwCQoerJGDb7zq9ycGeXK1pHUUi6WihlydMAglbGW2GEWxj2iEivNZfcn9ZAFspqtDsjUyoyAGfFiJOHziJXJeajuwsws-jbBwH7F4ONB1QHXX7SPUTt0zRYFtzyToIUExC6hZdGJTLhdUEhQ', 'Host': 'overview.peoltechnologies.net', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-62b3f57d-4e2f4ed82f1622026ec56d8a', 'X-Forwarded-For': '49.206.129.228', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret', 'notification_email': 'elipotest@gmail.com', 'ocr_bucket_folder': 'old-dev/', 'cred_bucket': 'file-bucket-emp'}, 'context': {'account-id': '', 'api-id': '5ud4f0kv53', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'GET', 'stage': 'einvoice-v1', 'source-ip': '49.206.129.228', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36', 'user-arn': '', 'request-id': 'ee98a859-9256-49bf-b559-0a0e96f29739', 'resource-id': 'hsx45i', 'resource-path': '/get-sap-po'}}

# lambda_handler(event , '')

def deleteGroup(event, context):
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
            
            sqlQuery = "DELETE FROM " + dbScehma + ".group WHERE group_id = %s"
            values = (event["params"]["querystring"]["group_id"])
            mycursor.execute(sqlQuery, values)
            
            sqlQuery = "DELETE FROM dropdown WHERE value1 = %s"
            values = (event["params"]["querystring"]["group_id"])
            mycursor.execute(sqlQuery, values)
            
            msg = "Group ID " + event["params"]["querystring"]["group_id"] + " deleted"   
            
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
        'body': json.dumps(msg)
    }

def getGroupDetails(event, context):
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

    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            group = []
            final_group = []
            member = []
            
            sqlQuery = "select * from " + dbScehma + ".group order by name"
            mycursor.execute(sqlQuery)
            
            for row in mycursor:
                rawRecord = {
                    "group_id": row["group_id"],
                    "name": row['name'],
                    'description': row['description'],
                    'member_count': row['member_count'],
                    'is_valid': row['is_valid'],
                    'role': row["role"],
                    'members' : member
                }
                final_group.append(rawRecord)
            
            sqlQuery = 'SELECT g.group_id, m.member_id, m.fs_name, m.ls_name, m.profile_photo, m.email, m.position FROM ' + dbScehma + '.group as g inner join member m on g.group_id = m.group_id'

            mycursor.execute(sqlQuery)
            
            group_list = list()
         
            for row in mycursor:
                
                rawRecord_t = {
                    "group_id": row["group_id"],
                    "member_id":row['member_id'],
                    'member_name':row["fs_name"] + " " + row["ls_name"],
                    "profile_photo":row["profile_photo"],
                    'email':row["email"],
                    'position':row["position"]
                }
                group.append(rawRecord_t)
                
            group.sort(key=lambda i: i['group_id'])
            
            for row in final_group:
                temp1 = list()
                for row_t in group:
                    no1 = row_t["group_id"]
                    no2 = row["group_id"]
                    if row_t["group_id"] == row["group_id"]:
                    # if no1 == no2:
                        # print(row["group_id"],row_t["group_id"])
                        temp = {
                            'group_id': row['group_id'],
                            'member_id':row_t['member_id'],
                            "member_name":row_t['member_name'],
                            "profile_photo":row_t['profile_photo'],
                            'email':row_t["email"],
                            "position":row_t['position'],
                            'role': row["role"]
                        }
                        temp1.append(temp)
                        
                row["members"] = temp1
       
            records['Group'] = final_group   
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Failed to load groups"),
        }  
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records,
    }
        
def get_stored_credentials(user_id):

    global bucket_folder

    try:
        s3 = boto3.client("s3")
        encoded_file = s3.get_object(Bucket=elipo_bucket, Key=bucket_folder+user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
    except Exception as excep:
        creds = None
        # print(str(excep))
        # raise NoUserIdException(excep)

def create_message(sender, to, cc, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """

    message = email.mime.text.MIMEText(message_text, 'html')
    message['to'] = to
    message['cc'] = cc
    message['from'] = sender
    message['subject'] = subject
    encoded = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {'raw': encoded.decode("utf-8")}


def send_message(service, user_id, message):
    try:  
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return message
    # except errors.HttpError as error:
    except Exception as error:
        print("An error occurred: ", error)

def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)  

def sendMailNotifications(email, group, mycursor):
    # user_id = elipo_cred
    mycursor.execute("select * from elipo_setting where key_name = 'notification-mail' ")
    email_data = mycursor.fetchone()
    user_id = email_data["value1"]
    
    mail_cc = ''
    mail_subject = 'ELIPO Notification'
    mail_body = ''
    
    mail_body = '''<html>
            <body  >
        <div style=" max-width: 500px; margin: auto; padding: 10px; ">
                <div style=" width:100%; align-content: center;text-align: center;">
                    <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/ELIPO+logo.png" alt="Italian Trulli" style="vertical-align:middle; width: 140px;height:50px;text-align: center;"  >
                </div>
            <div style=" width:100%; align-content:left;text-align:left;">
                    <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                </div>
                <b>
                    <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Hello User,
                    </span> 
                <div style=" width:100%; align-content: center;text-align: center;margin-top: 10px;">   
                    <span style="vertical-align: middle; align-content: center; font: 500 16px/23px Open Sans;letter-spacing: 0px;color:#000000;white-space: nowrap;opacity: 1;" >
                         Welcome to ELIPO
                    </span>
                    
                </div>
        
            <br>
            <div style=" max-width:800px; min-width: 100px;  text-align: center ; margin-top: 10px; font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;opacity: 1;">
                You have been assigned to {} group . You can login to ELIPO by clicking on the below link.
            </div>
            <br>
            <div style=" width:100%;align-content: center;text-align: center;">
                <a href="https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/production/login" target="_blank">
                    <button style="border: none;box-shadow: 1px 1px 5px 1px #5a9e9b; background:rgb(80, 219, 212) 0% 0% no-repeat padding-box; border-radius: 7px;opacity: 1;width:180px; height: 35px;outline: none;border: none;" > 
                        <span style="vertical-align: middle; text-align: left;font: 600 bold 16px/23px Open Sans;letter-spacing: 0px;color: whitesmoke;white-space: nowrap;opacity: 1;">Login to ELIPO</span>
                    </button>
                </a>
            </div>
        
            <br><br>
            <div style="width:100%;">
                <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Happy Invoicing!</span>
            <br>
            <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Regards,</span>
            <br>
            <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Team ELIPO</span>
            </div>
        <div style=" width:100%; align-content:left;text-align:left;">
                    <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                </div>
        
            
            <div style="width:100%;align-content: center;text-align: center;">
                <span style=" text-align: center;font: 600 bold 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 0.7;">This message was sent to you by ELIPO</span>
            </div>
            <div style="width:100%;align-content: center;text-align: center;">
                <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/elipo+logo_2.png" alt="Italian Trulli" style="text-align: center;width: 80px;height: 30px;" >
            </div>
            
            <br>
        </div>
            </body></html>'''.format(group)

    credentials = get_stored_credentials(user_id)

    if credentials and credentials.refresh_token is not None:
        service = build_service(credentials=credentials)
        message = create_message(sender=user_id, to=str(email), cc=mail_cc, subject=mail_subject, message_text=mail_body)
        send_message(service=service, user_id="me", message=message) 

def patchGroup(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    global bucket_folder
    bucket_folder = event["stage-variables"]["ocr_bucket_folder"]

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
    
    global elipo_bucket
    elipo_bucket = event["stage-variables"]["cred_bucket"]

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
            
            if "description" in event["body-json"] and "name" in event["body-json"]:
                if "role" in event["body-json"]:
                    groupRole = event["body-json"]["role"]
                
                else:
                    mycursor.execute("select role from " + dbScehma + ".group where group_id = %s", event["params"]["querystring"]["group_id"])
                    roleData = mycursor.fetchone()
                    groupRole = roleData["role"]
                    
                sqlQuery = "update " + dbScehma + ".group set description = %s, name = %s, role = %s where group_id = %s"
                values = (event["body-json"]["description"], event["body-json"]["name"], groupRole, event["params"]["querystring"]["group_id"]) 
                print(sqlQuery, values)
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = "update dropdown set value2 = %s where value1 = %s and drop_key = 'group' "
                values = (event["body-json"]["name"], event["params"]["querystring"]["group_id"])
                mycursor.execute(sqlQuery, values)
                
            elif "description" in event["body-json"]:
                sqlQuery = "update " + dbScehma + ".group set description = %s where group_id = %s"
                values = (event["body-json"]["description"],  event["params"]["querystring"]["group_id"])
                mycursor.execute(sqlQuery, values)
                
            elif "role" in event["body-json"]:
                sqlQuery = "update " + dbScehma + ".group set role = %s where group_id = %s"
                values = (event["body-json"]["role"],  event["params"]["querystring"]["group_id"])
                mycursor.execute(sqlQuery, values)
                
            elif "name" in event["body-json"]:
                sqlQuery = "update " + dbScehma + ".group set name = %s where group_id = %s"
                values = (event["body-json"]["name"], event["params"]["querystring"]["group_id"])
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = "update dropdown set value2 = %s where value1 = %s and drop_key = 'group' "
                values = (event["body-json"]["name"], event["params"]["querystring"]["group_id"])
                mycursor.execute(sqlQuery, values)
            
            if "member_ids" in event["body-json"]:
                
                if len(event["body-json"]["member_ids"]) == 1:
                    
                    member_id = event["body-json"]["member_ids"][0]
                    
                    mycursor.execute("select concat(fs_name, ' ', ls_name) as mem_name, group_id, email from member where member_id = %s", member_id)
                    member_detail = mycursor.fetchone()
                    
                    values = (event["params"]["querystring"]["group_id"],member_id)
                    sqlQuery = "update member set group_id = %s where member_id = %s"
                    mycursor.execute(sqlQuery,values)
                    
                    values = (event["params"]["querystring"]["group_id"], member_id)
                    sqlQuery = "update member set group_id = '' where group_id = %s and member_id != %s"
                    mycursor.execute(sqlQuery, values)
                    
                    if member_detail["group_id"] != event["params"]["querystring"]["group_id"]:
                        sendMailNotifications(email=member_detail["email"] ,group=event["body-json"]["name"], mycursor=mycursor)
                    
                elif len(event["body-json"]["member_ids"]) > 1:
                    email = ""
                    
                    mycursor.execute("select member_id, group_id, email from member where member_id in {}".format(tuple(event["body-json"]["member_ids"])))
                    members_detail = mycursor.fetchall()
                    
                    for row in members_detail:
                        if int(row["group_id"]) != int(event["params"]["querystring"]["group_id"]):
                            email = email + str(row["email"]) + ", "
                            print(email)
                    
                    if email != "":
                        leng = len(email) - 2
                        email = email[0: leng]
                    
                    mycursor.execute("update member set group_id = '' where group_id = %s and member_id Not IN {}".format(tuple(event["body-json"]["member_ids"])),(event["params"]["querystring"]["group_id"]))
                    mycursor.execute("update member set group_id = %s where member_id IN {}".format(tuple(event["body-json"]["member_ids"])),(event["params"]["querystring"]["group_id"]))
                    
                    if email != "":
                        sendMailNotifications(email=email ,group=event["body-json"]["name"], mycursor=mycursor)
            
                elif len(event["body-json"]["member_ids"]) == 0:
                    
                    values = (event["params"]["querystring"]["group_id"],)
                    sqlQuery = "update member set group_id = '' where group_id = %s"
                    mycursor.execute(sqlQuery, values)
                    
            mydb.commit()
            
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Update Unsuccessful")  
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Update Successful")
    }

# postGroupDetails
def postGroupDetails(event, context):
                 
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
        "name" : "",
        "description" : "",
        "member_count":"",
        "is_valid":"y",
        "role": ""
    }
    
    try:
        
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
        
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "group_id" not in event["body-json"] and ( record["name"] != ' ' or record["name"] != None ):
            
                sqlQuery = "INSERT INTO " + dbScehma + ".group (name, description, member_count, is_valid, role) VALUES ( %s, %s, %s, %s, %s)"
                values = ( record["name"], record["description"],  record["member_count"], record["is_valid"], record["role"] )
                mycursor.execute(sqlQuery, values)
    
                group_id = mycursor.lastrowid
                
                del sqlQuery
                del values
        
                sqlQuery = "INSERT INTO dropdown (drop_key, value1, value2) VALUES (%s, %s, %s)"
                values = ( 'group', group_id, record["name"] )
                mycursor.execute(sqlQuery, values)
                
                
            # else:
            elif "group_id" in event["body-json"]:
                group_id = event["body-json"]["group_id"]
            
            touple = tuple(event["body-json"]["member_ids"])
            

            if "member_ids" in event["body-json"]:
                
                if len(event["body-json"]["member_ids"]) == 1:
                    
                    member_id = event["body-json"]["member_ids"][0]
                    values = (group_id, member_id)
                    sqlQuery = "update member set group_id = %s where member_id = %s"
                    mycursor.execute(sqlQuery,values)
                    
                elif len(event["body-json"]["member_ids"]) > 1:
                    mycursor.execute("update member set group_id = %s where member_id IN {}".format(tuple(event["body-json"]["member_ids"])),(group_id))

                mydb.commit()
            
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Group name already exists, please provide a different group name")
        }
            
    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Group insertion failed!")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Record inserted!")
    }

# getInboxApprovals
def getInboxApprovals(event, context):
    trace_off = ''
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

    records = {}

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
                    # print(event)
            
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
            
            email = None
            edit = None
            
            if "userid" in event["params"]["querystring"]:
                email = event["params"]["querystring"]["userid"]
                
            if "invoice_no" in event["params"]["querystring"]:
                
                invoiceNo = event["params"]["querystring"]["invoice_no"] 
                
                values = (email,)
                mycursor.execute("select member_id, concat(fs_name, ' ', ls_name) as mem_name from   member where email = %s", values)
                member = mycursor.fetchone()
                        
                items = []
                invoice_files = []
                record = []
                approvers = []
                delegate_info = []
                refered_reply = []
                
                mycursor.execute("select file_id, name, mime_type, file_link from   file_storage where file_id = %s", event["params"]["querystring"]["invoice_no"])
                
                for row in mycursor:
                    record = {
                        "invoice_id" : row["file_id"],
                        "file_name" : row["name"],
                        "mime_type" : row["mime_type"],
                        "file_link" : row["file_link"]
                    }
                    invoice_files.append(record)
                    
                values = (member["member_id"], invoiceNo)
                mycursor.execute("select m.member_id, concat(m.fs_name, ' ', m.ls_name) as member_name, refer_comment, accepted_comment, sr_no " \
                	"from   member m " \
                    "inner join   delegate d " \
                    "on m.member_id = d.delegated_to " \
                    "where d.delegated_from = %s and d.is_refered = 'y' and d.invoice_id = %s order by entry_time", values)
                refered = mycursor.fetchall()
                
                if refered:
                    for row in refered:
                        temp = {
                            "sr_no": row["sr_no"],
                            "refered_from_id": member["member_id"],
                            "refered_from_name": member["mem_name"],
                            "refered_to_id": row["member_id"],
                            "refered_to_name": row["member_name"] ,
                            "refer_comment": row["refer_comment"],
                            "reply_comment": row["accepted_comment"]
                        }
                        refered_reply.append(temp)
                
                values = (member["member_id"], invoiceNo)
                mycursor.execute("select m.member_id, concat(m.fs_name, ' ', m.ls_name) as member_name, refer_comment, accepted_comment, sr_no " \
                	"from   member m " \
                    "inner join   delegate d " \
                    "on m.member_id = d.delegated_from " \
                    "where d.delegated_to = %s and d.is_refered = 'y' and d.invoice_id = %s order by entry_time", values)
                delegate_member = mycursor.fetchall()
                
                if delegate_member:
                    for row in delegate_member:
                        temp = {
                            "sr_no": row["sr_no"],
                            "refered_from_id": row["member_id"],
                            "refered_from_name": row["member_name"],
                            "refered_to_id": member["member_id"],
                            "refered_to_name": member["mem_name"],
                            "refer_comment": row["refer_comment"],
                            "status": "Refered",
                            "reply_comment": row["accepted_comment"]
                        }
                        delegate_info.append(temp)
                
                values = (event["params"]["querystring"]["invoice_no"],)
                mycursor.execute("select a.*, b.value2 from   invoice_header a " \
                    "inner join   dropdown b on a.document_type = b.value1 where a.invoice_no = %s", values)
                invoice_header = mycursor.fetchone()
                
                if invoice_header:
                    mycursor.execute("select department_name from   departmental_budget_master where department_id = %s", (invoice_header["department_id"],))
                    department = mycursor.fetchone()
                    
                if department:
                    department_name = department["department_name"]
                    
                else:
                    department_name = None
                    
                sqlQuery = "select country from default_master where company_code = (Select company_code from invoice_header where invoice_no = %s)"
                values = (invoiceNo)
                mycursor.execute(sqlQuery,values)
                country = mycursor.fetchone()
                
                records = {
                    "user_invoice_id": invoice_header["user_invoice_id"],
                    "invoice_no": invoice_header["invoice_no"],
                    "document_type" : invoice_header["value2"],
                    "gstin": invoice_header["gstin"],
                    "in_status": invoice_header["in_status"],
                    "from_supplier": invoice_header["from_supplier"],
                    "ref_po_num": invoice_header["ref_po_num"],
                    "company_code": invoice_header["company_code"],
                    "invoice_date": str(invoice_header["invoice_date"]),
                    "posting_date": str(invoice_header["posting_date"]),
                    "baseline_date": str(invoice_header["baseline_date"]),
                    "amount": invoice_header["amount"],
                    "currency": invoice_header["currency"],
                    "payment_method": invoice_header["payment_method"],
                    "gl_account": invoice_header["gl_account"],
                    "business_area" : invoice_header["business_area"],
                    "supplier_id" : invoice_header["supplier_id"],
                    "supplier_name" : invoice_header["supplier_name"],
                    "approver_id" : invoice_header["approver_id"],
                    "approver_comments" : invoice_header["approver_comments"],
                    "modified_date" : str(invoice_header["modified_date"]),
                    "cost_center" : invoice_header["cost_center"],
                    "taxable_amount" : invoice_header["taxable_amount"],
                    "discount_per" : invoice_header["discount_per"],
                    "total_discount_amount" : invoice_header["total_discount_amount"],
                    "is_igst" : invoice_header["is_igst"],
                    "tax_per" : invoice_header["tax_per"],
                    "cgst_tot_amt": invoice_header["cgst_tot_amt"],
                    "sgst_tot_amt": invoice_header["sgst_tot_amt"],
	                "igst_tot_amt": invoice_header["igst_tot_amt"],
                    "tds_per": invoice_header["tds_per"],
                    "tds_tot_amt": invoice_header["tds_tot_amt"],
                    "payment_terms" : invoice_header["payment_terms"],
                    "adjustment" : invoice_header["adjustment"],
                    "supplier_comments" : invoice_header['supplier_comments'],
                    "department_id": invoice_header["department_id"],
                    "department_name": department_name,
                    "app_comment": invoice_header["app_comment"],
                    "tcs": invoice_header["tcs"],
                    "internal_order": invoice_header["internal_order"],
                    "irn": invoice_header["irn"],
                    "items" : items,
                    "files" : invoice_files,
                    "refer_details": delegate_info,
                    "refer_comment": refered_reply,
                    "country" : country['country'],
                    "jurisdiction_code":invoice_header["jurisdiction_code"]
                }
                
                mycursor.execute("select * from   invoice_item where invoice_no = %s", values)
                
                for row in mycursor:
                    record = {
                      "item_no":row["item_no"],
                      "material":row["material"],
                      "material_desc":row["material_desc"],
                      "quantity":row["quantity"],
                      "unit":row["unit"],
                      "amount":row["amount"],
                      "currency": row["currency"],
                      "amt_per_unit" : row["amt_per_unit"],
                      "cgst_per": row["cgst_per"],
                      "cgst_amount":row["cgst_amount"],
                      "tax_code":row["tax_code"],
                      "ref_po_no":row["ref_po_no"],
                      "plant":row["plant"],
                      "discount":row["discount"],
                      "discount_amount" : row["discount_amount"],
                      "gross_amount" : row["gross_amount"],
                      "sgst_per": row["sgst_per"],
                      "sgst_amount": row["sgst_amount"],
                      "igst_per": row["igst_per"],
                      "igst_amount": row["igst_amount"],
                      "taxable_amount": row["taxable_amount"],
                      "tax_value_amount": row["tax_value_amount"],
                      "gl_account": row["gl_account"],
                      "gst_per": row["gst_per"],
                      "hsn_code": row["hsn_code"]
                      }
                    items.append(record)
                    
                mycursor.execute("select member_id, group_id from   member where email = %s", event["params"]["querystring"]["userid"])
                member = mycursor.fetchone()
                
                sqlQuery = "update   approval set working_person = %s where ((isgroup = 'y' and approver = %s) or (isgroup = 'n' and approver = %s)) and invoice_no = %s"
                values = (member['member_id'], member['group_id'], member['member_id'], event["params"]["querystring"]["invoice_no"])
                mycursor.execute(sqlQuery, values)
                
                mydb.commit()
                    
                records["items"] = items

            elif "condn" in event["body-json"]:
                
                val_list = []
                pos = 0
                condn = ""
                records = {}
                
                refered_inv = []
                member_ids = []
                reply_list = []
                delegate_list = []

                for row in event["body-json"]["condn"]:

                    condn = condn + " and "

                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                        condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                    elif str(row["operator"]) == "between":
                        val_list.append(row["value"])
                        val_list.append(row["value2"])
                        condn = condn + " " + str(row["field"]) + " between %s and %s "
                    else:
                        val_list.append(row["value"])
                        condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"

                mycursor.execute("select member_id, delegate_to, until from   member where email = %s", event["params"]["querystring"]["userid"])
                member = mycursor.fetchone()

                mycursor.execute("select d.*, concat(m.fs_name, ' ', m.ls_name) as member_name " \
                	"from   delegate d " \
                	"left join   member m " \
                    "on d.delegated_from = m.member_id " \
                	"where d.delegated_to = %s and (d.delegate_until >= CURDATE() or d.is_refered = 'y')", member['member_id'])
                delegated = mycursor.fetchall()
                
                if delegated:
                    values = []
                    for row in delegated:
                        if row["is_accepted"] == 'n':
                            if row["is_refered"] == 'n':
                                member_ids.append(row["delegated_from"])
                                
                            else:
                                values.append(row["delegated_from"])
                                refered_inv.append(row["invoice_id"])
                                
                            if row["is_refered"] == 'y':
                                delegate_list.append( {
                                    "refered_from_id":row["delegated_from"],
                                    "invoice_no": row["invoice_id"],
                                    "refered_from_name": row["member_name"],
                                    "refered_to_id": member["member_id"]
                                } )
                                
                        elif row["is_accepted"] == 'y':
                            reply_list.append( {
                                    "refered_from_id":row["delegated_from"],
                                    "invoice_no": row["invoice_id"],
                                    "refered_from_name": row["member_name"],
                                    "refered_to_id": member["member_id"],
                                    "accepted_comment": row["accepted_comment"],
                                    "request_comment": row["refer_comment"]
                                } )

                member_ids.append(member['member_id'])
                format_strings_mem = ','.join(['%s'] * len(member_ids))

                sqlQuery = "select group_id FROM   member where member_id in (%s)" % format_strings_mem
                mycursor.execute(sqlQuery, tuple(member_ids))
                grp_details = mycursor.fetchall()
                groups = [sub['group_id'] for sub in grp_details]

                format_strings_grp = ','.join(['%s'] * len(groups))

                if member_ids and groups:

                    sqlQuery = "select invoice_no from   approval where " \
                               "(( isgroup = 'y' and approver in ({}) ) or ( isgroup = 'n' and approver in ({}) )) " \
                               "and ((pre_approval = 'y' or approval_level = 1 ) or approval_type = 'parallel') " \
                               "and isapproved = 'n'"
                    sqlQuery = sqlQuery.format(format_strings_grp, format_strings_mem)

                    values = tuple(groups + member_ids)
                    mycursor.execute(sqlQuery, values)
                    invoice_tup = mycursor.fetchall()
                    res = [sub['invoice_no'] for sub in invoice_tup]

                elif groups:

                    sqlQuery = "select invoice_no from   approval where isgroup = 'y' " \
                               "and approver in (%s) and ((pre_approval = 'y' or approval_level = 1 ) or approval_type = 'parallel') " \
                               "and isapproved = 'n'" % format_strings_grp

                    mycursor.execute(sqlQuery, tuple(groups))
                    invoice_tup = mycursor.fetchall()
                    res = [sub['invoice_no'] for sub in invoice_tup]

                elif member_ids:

                    sqlQuery = "select invoice_no from   approval where isgroup = 'n' " \
                               "and approver in (%s) and ((pre_approval = 'y' or approval_level = 1 ) or approval_type = 'parallel') " \
                               "and isapproved = 'n'" + condn % format_strings_mem

                    mycursor.execute(sqlQuery, tuple(member_ids))
                    invoice_tup = mycursor.fetchall()
                    res = [sub['invoice_no'] for sub in invoice_tup]

                if res:
                    res = res + refered_inv
                    format_strings = ','.join(['%s'] * len(res))
                    
                    if len(res) == 1:
                        mycursor.execute("select attach_id, file_id, name, mime_type, file_link from   file_storage where file_id = %s", res[0])
                        file = mycursor.fetchall()
                    elif len(res) > 1:
                        mycursor.execute("select attach_id, file_id, name, mime_type, file_link from   file_storage where file_id in {}".format(tuple(res))) 
                        file = mycursor.fetchall()

                    sqlQuery = "select invoice_no, invoice_date, user_invoice_id, amount, convert_tz(modified_date, '+00:00','+05:30' ) as modified_date, supplier_id, " \
                    	"concat(m.fs_name, ' ', m.ls_name ) as modified_by, vm.vendor_name " \
                    	"FROM   invoice_header " \
                        "left join   vendor_master vm " \
                        "on supplier_id = vm.vendor_no " \
                        "inner join   member m " \
                        "on working_person = m.member_id " \
                    	"where in_status = 'inapproval' and invoice_no in (%s)" % format_strings 
                    sqlQuery = sqlQuery + condn
                    
                    res = res + val_list
                    mycursor.execute(sqlQuery, tuple(res))

                    invoices = []

                    for row in mycursor:
                        
                        refer_details = []
                        if row["invoice_no"] in refered_inv:
                            for each in delegate_list:
                                if row["invoice_no"] == each["invoice_no"]:
                                    refer_details.append(each)
                                    
                        refered_reply = []
                        for sub in reply_list:
                            if row["invoice_no"] == sub["invoice_no"]:
                                refered_reply.append(sub)
                                
                        files = []
                        for data in file:
                            if str(row["invoice_no"]) == str(data["file_id"]):
                                temp = {
                                    "file_name" : data["name"],
                                    "mime_type" : data["mime_type"],
                                    "file_link" : data["file_link"]
                                }
                                files.append(temp)
                        
                        record = {
                            "invoice_no": row["invoice_no"],
                            "invoice_date": str(row["invoice_date"]),
                            "user_invoice_id": row["user_invoice_id"],
                            "amount": row["amount"],
                            "modified_date": str(row["modified_date"]),
                            "modified_by": row["modified_by"],
                            "supplier_id": row["supplier_id"],
                            "supplier_name": row["vendor_name"],
                            "invoice_files": files,
                            "refer_details": refer_details,
                            "refered_reply": refered_reply
                        }
                        invoices.append(record)
                    records["invoices"] = sorted(invoices, key = lambda i: i['invoice_no'],reverse=True)

                else:
                    invoices = []
                    records["invoices"] = invoices
                  
            else:
                
                invoice_files = []
                member_ids = []
                refered_inv = []
                delegate_list = []
                reply_list = []

                mycursor.execute("select member_id, delegate_to, until from   member where email = %s", event["params"]["querystring"]["userid"])
                member = mycursor.fetchone()
                
                mycursor.execute("select d.*, concat(m.fs_name, ' ', m.ls_name) as member_name " \
                	"from   delegate d " \
                	"left join   member m " \
                    "on d.delegated_from = m.member_id " \
                	"where d.delegated_to = %s and (d.delegate_until >= CURDATE() or d.is_refered = 'y')", member['member_id'])
                delegated = mycursor.fetchall()
                
                if delegated:
                    values = []
                    for row in delegated:
                        if row["is_accepted"] == 'n':
                            if row["is_refered"] == 'n':
                                member_ids.append(row["delegated_from"])
                                
                            else:
                                values.append(row["delegated_from"])
                                refered_inv.append(row["invoice_id"])
                                
                            if row["is_refered"] == 'y':
                                delegate_list.append( {
                                    "refered_from_id":row["delegated_from"],
                                    "invoice_no": row["invoice_id"],
                                    "refered_from_name": row["member_name"],
                                    "refered_to_id": member["member_id"]
                                } )
                                
                        elif row["is_accepted"] == 'y':
                            reply_list.append( {
                                    "refered_from_id":row["delegated_from"],
                                    "invoice_no": row["invoice_id"],
                                    "refered_from_name": row["member_name"],
                                    "refered_to_id": member["member_id"],
                                    "accepted_comment": row["accepted_comment"],
                                    "request_comment": row["refer_comment"]
                                } )

                member_ids.append(member['member_id'])

                format_strings_mem = ','.join(['%s'] * len(member_ids))

                sqlQuery = "select group_id FROM   member where member_id in (%s)" % format_strings_mem
                mycursor.execute(sqlQuery, tuple(member_ids))
                grp_details = mycursor.fetchall()
                groups = [sub['group_id'] for sub in grp_details]

                format_strings_grp = ','.join(['%s'] * len(groups))
                
                invoice_tup = None
                
                if member_ids and groups:

                    sqlQuery = "select invoice_no, refer_completed from   approval where (( isgroup = 'y' and approver in ({}) ) or ( isgroup = 'n' and approver in ({}) )) " \
                        "and ((pre_approval = 'y' or approval_level = 1 ) or approval_type = 'parallel' or approval_type = 'single'  or  " \
		                "(approval_type = 'series' and referred_approver = 'y')) and isapproved = 'n' and refer_lock = 'n'"
                    sqlQuery = sqlQuery.format(format_strings_grp, format_strings_mem)

                    values = tuple(groups + member_ids)
                    mycursor.execute(sqlQuery, values)
                    invoice_tup = mycursor.fetchall()

                elif groups:

                    sqlQuery = "select invoice_no, refer_completed from   approval where isgroup = 'y' " \
                               "and approver in (%s) and ((pre_approval = 'y' or approval_level = 1 ) or approval_type = 'parallel' or approval_type = 'single') " \
                               "and isapproved = 'n' and refer_lock = 'n'" % format_strings_grp

                    mycursor.execute(sqlQuery, tuple(groups))
                    invoice_tup = mycursor.fetchall()

                elif member_ids:

                    sqlQuery = "select invoice_no, refer_completed from   approval where isgroup = 'n' " \
                               "and approver in (%s) and ((pre_approval = 'y' or approval_level = 1 ) or approval_type = 'parallel') " \
                               "and isapproved = 'n' and refer_lock = 'n'" % format_strings_mem

                    mycursor.execute(sqlQuery, tuple(member_ids))
                    invoice_tup = mycursor.fetchall()
                    
                res = []
                refered_invoice_rply = []
                if invoice_tup:
                    for sub in invoice_tup:
                        res.append(sub["invoice_no"])
                        
                        if sub["refer_completed"] == 'y':
                            refered_invoice_rply.append(sub["invoice_no"])
                
                if delegate_list:
                    for each in delegate_list:
                        res.append(each['invoice_no'])
                        
                if res:
                    res = res + refered_inv
                    format_strings = ','.join(['%s'] * len(res))
                    
                    sqlQuery = "select file_id, name, mime_type, file_link " \
                        "from   file_storage " \
                        "where file_id in (%s) order by file_id desc" % format_strings
                    mycursor.execute(sqlQuery, tuple(res))
                    file = mycursor.fetchall()
                    
                    for row in file:
                        record = {
                            "invoice_id" : row["file_id"], 
                            "file_name" : row["name"],
                            "mime_type" : row["mime_type"],
                            "file_link" : row["file_link"]
                        }
                        invoice_files.append(record)
                    
                    sqlQuery = "select a.invoice_no, a.user_invoice_id, a.invoice_date, a.amount, a.currency, convert_tz(a.modified_date, '+00:00','+05:30' ) as modified_date, " \
                        "b.fs_name, b.ls_name, c.vendor_name " \
                    	"FROM   invoice_header a " \
                        "left join   member b " \
                        "on a.working_person = b.member_id " \
                        "left join   vendor_master c " \
                        "on a.supplier_id = c.vendor_no " \
                    	"where in_status = 'inapproval' and invoice_no in (%s) order by a.invoice_no desc" % format_strings
                    mycursor.execute(sqlQuery, tuple(res))

                    invoices = []

                    for row in mycursor:
                        refer_details = []
                        if row["invoice_no"] in refered_inv:
                            for each in delegate_list:
                                if row["invoice_no"] == each["invoice_no"]:
                                    refer_details.append(each)
                                    
                        refered_reply = []
                        for sub in reply_list:
                            if row["invoice_no"] == sub["invoice_no"]:
                                refered_reply.append(sub)
                        
                        files = []
                        for data in invoice_files:
                            
                            if str(row["invoice_no"]) == str(data["invoice_id"]):
                                temp = {
                                    "file_name" : data["file_name"],
                                    "mime_type" : data["mime_type"],
                                    "file_link" : data["file_link"]
                                }
                                files.append(temp)
                                
                        record = {
                            "invoice_no": row["invoice_no"],
                            "user_invoice_id": row["user_invoice_id"],
                            "invoice_date": str(row["invoice_date"]),
                            "amount": row["amount"],
                            "currency": row["currency"],
                            "supplier_name": row["vendor_name"],
                            "modified_date": str(row["modified_date"]),
                            "modified_by": str(row["fs_name"]) + " " + str(row["ls_name"]),
                            "invoice_files": files,
                            "refer_details": refer_details,
                            "refered_reply": refered_reply
                        }
                        invoices.append(record)
                    records["invoices"] = invoices

                else:
                    invoices = []
                    records["invoices"] = invoices 
        
        # xray_recorder.begin_subsegment(name="Test")
        # # patch_all()
        # # patch_all()
        # # time.sleep(1)
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , "switch":'off'})
        # xray_recorder.end_subsegment()            

    except:
        mydb.rollback()   
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
        # time.sleep(1)
        

    return {
        'statuscode': 200,
        'body': records
    }

# deleteInvoiceLog
def deleteInvoiceLog(event, context):
    print(event)
    
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
            
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
            #     atoken =  event['params']['header']['Authorization']
            #     print(atoken)
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
            #     patch_all()
            #     print(event)
            
            mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            on = mycursor.fetchone()
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)
            
            if "invoice_no" in event["params"]["querystring"]:
                sqlQuery = "DELETE FROM invoice_log WHERE invoice_no = %s"
                values = (event["params"]["querystring"]["invoice_no"])
                mycursor.execute(sqlQuery, values)  
                
            elif "userid" in event["params"]["querystring"]:
                sqlQuery = "select member_id from member where email = %s"
                values = (event["params"]["querystring"]["userid"],)
                mycursor.execute(sqlQuery, values)
                member = mycursor.fetchone()
                
                values = (member["member_id"],)
                mycursor.execute("delete FROM invoice_log WHERE member_id = %s ", values)
                
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
        'body': json.dumps("Delete Successful!")
    }

# getErrorLog
def getErrorLog(event, context):
    
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
    
    records = []
                
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
            
            if "invoice_no" not in event["params"]["querystring"]:
                mycursor.execute("SELECT a.*, concat(b.fs_name, ' ', b.ls_name) as member_name FROM  invoice_log a left join   member b on a.member_id = b.member_id")
                
                for row in mycursor:
                    data = {
                        "invoice_no": row["invoice_no"],
                        "entry_timestamp": str(row["entry_timestamp"]),
                        "member_id": row["member_id"],
                        "member_name": row["member_name"]
                    }
                    records.append(data)
                    
            else:
                
                invoice_no = event["params"]["querystring"]["invoice_no"]
                mycursor.execute("select * from   invoice_log where invoice_no = %s", invoice_no)
                invoice = mycursor.fetchone()
                
                if invoice:
                    msg = "This invoice is currently edited by Member ID " + str(invoice["member_id"])
                    records = {
                        "flag": "y",
                        "msg": msg
                    }
                    
                else:
                    records = {
                        "flag": "n"
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
        'body': records
    }

def getMasterDetails(event, context):
    global dbScehma 
    print(event)
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

    print(event)
    
    master = []

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


            if "querystring" in event["params"]:
                
                if "master_id" in event["params"]["querystring"]:
                    
                    if event["params"]["querystring"]["master_id"] == "4":
                        
                        mycursor.execute("select * from vendor_master")
                        
                        for row in mycursor:
                            record = {
                                "master_id" : event["params"]["querystring"]["master_id"],
                                "vendor_no" : row["vendor_no"], 
                                "vendor_name" : row["vendor_name"], 
                                "gst_treatment" : row["gst_treatment"], 
                                "gstin_uin" : row["gstin_uin"], 
                                "source_of_supply" : row["source_of_supply"], 
                                "currency" : row["currency"], 
                                "payment_terms" : row["payment_terms"], 
                                "tds" : row["tds"], 
                                "gst_per" : row["gst_per"], 
                                "pan" : row["pan"]
                            }
                            master.append(record)
                            
                    elif event["params"]["querystring"]["master_id"] == "8":
                        
                        mycursor.execute("select * from material_master")
                        
                        for row in mycursor:
                            record = {
                                "master_id" : event["params"]["querystring"]["master_id"],
                                "material_no" : row["material_no"], 
                                "material_name" : row["material_name"], 
                                "gst_per" : row["gst_per"], 
                                "unit_price" : row["unit_price"], 
                                "gl_account" : row["gl_account"]
                            }
                            master.append(record)
                            
                    elif "vendor_no" in event["params"]["querystring"]:
                        value = event["params"]["querystring"]["vendor_no"]
                        mycursor.execute("SELECT jurisdiction_code from vendor_master where vendor_no = %s", value)
                        jurisdiction_code = mycursor.fetchone()
                        master.append(jurisdiction_code)
                        
                    else:
                    
                        sqlQuery = "select * from master where master_id = %s"
                        values = (event["params"]["querystring"]["master_id"],)
                        mycursor.execute(sqlQuery, values)
    
                        for row in mycursor:
                            record = {
                                'master_id' : row["master_id"],
                                'master_name': row["master_name"],
                                'code': row["code"],
                                'description': row["description"],
                                'tax_treatement':row["tax_treatement"]
                            }
                            master.append(record)
    
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Unknown Error while fetching")
        }
        
    finally:
        mydb.close()
    
    return {
        'statuscode': 200,
        'body': master
    }

def patchMasterDetails(event, context):
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
        "code": "",
        "description": "",
        "tax_treatement":"",
        "vendor_no": "",
        "vendor_name": "",
        "gst_treatment": "",
        "gstin_uin": "",
        "source_of_supply": "",
        "currency": "",
        "payment_terms": "",
        "tds": "",
        "gst_per": "",
        "pan": "",
        "material_no": "", 
        "material_name": "", 
        "gst_per": "", 
        "unit_price": "", 
        "gl_account": ""
    }
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

            if event["params"]["querystring"]["master_id"] == "8":
                sqlQuery = "update material_master set material_name = %s, gst_per = %s, unit_price = %s, gl_account = %s where material_no = %s"
                values = (record["material_name"], record["gst_per"], record["unit_price"], record["gl_account"], record["material_no"])
                mycursor.execute(sqlQuery, values)
                
            elif event["params"]["querystring"]["master_id"] == "4":
                sqlQuery = "update vendor_master set vendor_name = %s, gst_treatment = %s, gstin_uin = %s, source_of_supply = %s, currency = %s, " \
                        "payment_terms = %s, tds = %s, gst_per = %s, pan = %s where vendor_no = %s"
                values = ( record["vendor_name"], record["gst_treatment"], record["gstin_uin"], record["source_of_supply"], record["currency"],
                            record["payment_terms"], record["tds"], record["gst_per"], record["pan"], record["vendor_no"] )
                mycursor.execute(sqlQuery, values)
            
            if "description" in event["body-json"] and "code" in event["body-json"]:
                
                sqlQuery = "update master set code = %s, description = %s , tax_treatement = %s where master_id = %s and code = %s"
                
                values = (record["code"], record["description"], record["tax_treatement"],  event["params"]["querystring"]["master_id"], event["params"]["querystring"]["code"])
                
                mycursor.execute(sqlQuery, values)
                
                msg = "Code " + event["params"]["querystring"]["code"] + " updated to " + str(event["body-json"]["code"]) + " " + event["body-json"]["description"]
                
            elif "code" in event["body-json"]:
                
                sqlQuery = "update master set code = %s where master_id = %s and code = %s"
                
                values = (record["code"],  event["params"]["querystring"]["master_id"], event["params"]["querystring"]["code"])
                
                mycursor.execute(sqlQuery, values)
                
                msg = "Code " + event["params"]["querystring"]["code"] + " updated to " + event["body-json"]["code"]
                
            elif "description" in event["body-json"]:
                
                sqlQuery = "update master set description = %s where master_id = %s and code = %s"
                
                values = (record["description"],  event["params"]["querystring"]["master_id"], event["params"]["querystring"]["code"])
                
                mycursor.execute(sqlQuery, values)
                
                msg = "Code " + event["params"]["querystring"]["code"] + " updated Description " + event["body-json"]["description"]
                
            elif "tax_treatement" in event["body-json"]:
                
                sqlQuery = "update master set tax_treatement = %s where master_id = %s and code = %s"
                
                values = (record["tax_treatement"], event["params"]["querystring"]["master_id"], event["params"]["querystring"]["code"])
                
                mycursor.execute(sqlQuery, values)
                
                msg = "Code " + event["params"]["querystring"]["code"] + " updated Tax Treatement " + event["body-json"]["tax_treatement"]
            
            # msg = "Code " + event["params"]["querystring"]["code"] + " updated"  
            
            mydb.commit()
            
    # except:
        
    #     return {
    #         'statuscode': 500,
    #         'body': json.dumps("Internal Failure")
    #     }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Successfully updated")
    }

#  postMasterDetails
def postMasterDetails(event, context):
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
            
            msg = "Inserted Successfully!"
            if "master_id" not in event["body-json"]:
                
                if "codes" in event["body-json"] and "master_name" in event["body-json"]:
                    
                    sqlQuery = "select * from master where master_name = %s"
                    values = (event["body-json"]["master_name"],)
                      
                    mycursor.execute(sqlQuery, values)
                      
                    if mycursor.rowcount > 0:
                        return {
                            'statuscode': 500,
                            'body': json.dumps("Master already Available")
                        }
                        
                    mycursor.execute("SELECT max(master_id) as cnt FROM master")
                    
                    distinct_masters = mycursor.fetchone() 
                    
                    new_master = distinct_masters["cnt"] + 1
            
                    values = []
                
                    for row in event["body-json"]["codes"]:
                        touple = (new_master, row["code"], event["body-json"]["master_name"], row["description"])
                        values.append(touple)
                    
                    
                    sqlQuery = "INSERT INTO master (master_id, code, master_name, description) VALUES (%s, %s, %s, %s )"
                    
                    mycursor.executemany(sqlQuery, values)
                    
                    values = ('master', new_master, event["body-json"]["master_name"])
                    
                    sqlQuery = "INSERT INTO dropdown (drop_key, value1, value2) VALUES (%s, %s, %s)"
            
                    mycursor.execute(sqlQuery, values)
                
                    # master_id = mycursor.lastrowid
                    
            elif "codes" in event["body-json"]:
                
                if "import_entries" in event["params"]["querystring"] and event["body-json"]["master_id"] == "4":
                    mycursor.execute("delete from vendor_master")
                    
                elif "import_entries" in event["params"]["querystring"] and event["body-json"]["master_id"] == "8":
                    mycursor.execute("delete from material_master")
                    
                elif "import_entries" in event["params"]["querystring"]:
                    sqlQuery = "delete from master where master_id = %s"
                    masterid = (event["body-json"]["master_id"],)
                    mycursor.execute(sqlQuery, masterid)
                    
                sqlQuery = "select value2 from dropdown where drop_key = 'master' and value1 = %s"
                masterid = (event["body-json"]["master_id"],)
                
                mycursor.execute(sqlQuery, masterid)
                mast = mycursor.fetchone()
                
                master_name = mast["value2"]
                
                values = []
                values1 = []
                if event["body-json"]["master_id"] == "4":
                    for row in event["body-json"]["codes"]:
                        touple = (row["vendor_no"], row["vendor_name"], row["gst_treatment"], row["gstin_uin"], row["source_of_supply"], row["currency"],
                                    row["payment_terms"], row["tds"], row["gst_per"], row["pan"])
                        values.append(touple)
                    sqlQuery = "insert into vendor_master (vendor_no, vendor_name, gst_treatment, gstin_uin, source_of_supply, currency, " \
                        "payment_terms, tds, gst_per, pan) values (%s, %s, %s, %s, %s, %s, %s, %s , %s, %s)"
                        
                elif event["body-json"]["master_id"] == "8":
                    
                    for row in event["body-json"]["codes"]:
                        touple = (row["material_no"], row["material_name"], row["gst_per"], row["unit_price"], row["gl_account"])
                        values.append(touple)
                    sqlQuery = "insert into material_master (material_no, material_name, gst_per, unit_price, gl_account)" \
                        "values (%s, %s, %s, %s, %s)"
                    
                elif event["body-json"]["codes"]:
                    for row in event["body-json"]["codes"]:
                        if "tax_treatement" in row:
                            touple = (event["body-json"]["master_id"], row["code"], master_name, row["description"], row["tax_treatement"])
                            values.append(touple)
                        else:
                            touple = (event["body-json"]["master_id"], row["code"], master_name, row["description"])
                            values1.append(touple)
                    if len(values1) != 0:
                        sqlQuery = "INSERT INTO master (master_id, code, master_name, description) VALUES (%s, %s, %s, %s )"
                        mycursor.executemany(sqlQuery, values1)
                    else:
                        sqlQuery = "INSERT INTO master (master_id, code, master_name, description,tax_treatement) VALUES (%s, %s, %s, %s, %s )"
                    
              
                mycursor.executemany(sqlQuery, values)
                
              
            mydb.commit()
            
    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        msg = "Duplicate entry code"
        return {
            'statuscode': 500,
            'body': json.dumps(msg)
        }
            
    except:
        mydb.rollback()
        msg = "Group insertion failed!"
        return {
            'statuscode': 500,
            'body': json.dumps(msg)
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps(msg)
    }

# 
def deleteMemberDetail(event, context):
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
            
            # cognito = boto3.client('cognito-idp') 
            
            # response = cognito.admin_delete_user(
            #     UserPoolId='eu-central-1_P9rnnqiLu',
            #     Username='bb7eecc4-3ad5-4f68-936c-dc4ae1ce9a25'
            # )

            if "member_id" in event["params"]["querystring"]:
                mycursor.execute("delete from member where member_id = %s", event["params"]["querystring"]["member_id"])
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
        'body': json.dumps("Delete Successful!"),
    }

def decode_jwt_token(Authorization):
    header1 =  jwt.decode(Authorization , options={"verify_signature": False})
    if 'email' in header1:
        return header1['email']
    else:
        return ''
def getMemberDetails(event, context):
    
    trace_off = ''
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

    records = {}
    row2 = None
    
    try:
        # xray_recorder.begin_subsegment(name="Test")
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
            
            

            # values = event["params"]["querystring"]["userid"]
            # mycursor.execute('select flag from email where userid = %s', values )
            # flag = mycursor.fetchone()
            
            print(context.function_name)
            print(event['context']['api-id'])
            
            
           
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
            #     atoken =  event['params']['header']['Authorization']
            #     print(atoken)
                
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     trace_off = 'off'
            #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
            #     # if json.loads(a.text)['body'] == 'on':
            #     patch_all()
            #         # print(event)  
            #     print("me")

            # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            # if on == 1:
            #     chk = enable_xray(event)
            #     if chk['Enable'] == True:
            #         patch_all()
            
            member = []
            
            if "vendor_member" in event["params"]["querystring"]:
                
                sqlQuery = "SELECT vendor_name FROM vendor_master where member_id = %s"
                mycursor.execute(sqlQuery, event["params"]["querystring"]["vendor_member"])
                vendor_mem = mycursor.fetchone()
                
                if vendor_mem:
                    retMsg = {
                        "flag": "n",   
                        "msg": "Member already exists in Vendor " + vendor_mem["vendor_name"]
                    }
                    
                    return {
                        'statuscode': 201,
                        'body': retMsg
                    }
                    
                else:
                    retMsg = {
                        "flag": "y",
                        "msg": "Member is avaliable!"
                    }
                    
                    return {
                        'statuscode': 201,
                        'body': retMsg
                    }
            elif "search_string" in event["params"]["querystring"] and "role" in event["params"]["querystring"]:
                
                sqlQuery = "SELECT *, value2 FROM member inner join dropdown on user_type = value1 where (fs_name like %s or ls_name like %s) and user_type = %s"
                temp = event["params"]["querystring"]["search_string"] + "%%"
                userRole = event["params"]["querystring"]["role"]
                values = ( temp , temp, userRole )
                mycursor.execute(sqlQuery, values)
                
                for row in mycursor:
                    record = {
                        'member_id': row['member_id'],
                        'department_id': row['department_id'],
                        'fs_name': row['fs_name'],
                        'ls_name': row['ls_name'],
                        'profile_photo' : row['profile_photo'],
                        'email': row['email'], 
                        'group_id': row['group_id'],
                        'position': row['value2']
                    }
                    member.append(record)
                records['Member'] = member  
                
            elif "search_string" in event["params"]["querystring"]:
                
                sqlQuery = "SELECT *, value2 FROM member inner join dropdown on user_type = value1 where fs_name like %s or ls_name like %s"
                temp = event["params"]["querystring"]["search_string"] + "%%"
                values = ( temp , temp )
                mycursor.execute(sqlQuery, values)
                
                for row in mycursor:
                    record = {
                        'member_id': row['member_id'],
                        'department_id': row['department_id'],
                        'fs_name': row['fs_name'],
                        'ls_name': row['ls_name'],
                        'profile_photo' : row['profile_photo'],
                        'email': row['email'], 
                        'group_id': row['group_id'],
                        'position': row['value2']
                    }
                    member.append(record)
                records['Member'] = member  
            
            elif "member_id" in event["params"]["querystring"]:
                
                sqlQuery = "select m.member_id, concat(fs_name, ' ', ls_name) as member_name, m.group_id, g.name " \
                	"from member m " \
                    "left join " + dbScehma + ".group g " \
                    "on m.group_id = g.group_id " \
                    "where m.member_id = %s"
                values = event["params"]["querystring"]["member_id"]
                mycursor.execute(sqlQuery, values)
                records = mycursor.fetchone()
                
            elif "refer_list" in event["params"]["querystring"]:
                userid = ""
                if "userid" in event["params"]["querystring"]:
                    userid = event["params"]["querystring"]["userid"]
                    
                mycursor.execute("SELECT m.member_id, m.department_id, m.fs_name, m.ls_name, m.profile_photo, m.email, m.user_type, m.group_id, d.value2 " \
                    "from member m " \
                    "left OUTER join dropdown d " \
                    "on m.user_type = d.value1 " \
                    "where m.user_type in ('fh', 'cfo', 'fc') and m.email != %s " \
                    "order by m.fs_name", userid)
                
                for row in mycursor:
                    record = {
                        'member_id': row['member_id'],
                        'department_id': row['department_id'],
                        'name': row['fs_name'] + " " + row['ls_name'],
                        'profile_photo' : row['profile_photo'],
                        'user_type': row["user_type"],
                        'group_id': row["group_id"],
                        'user_type_description': row["value2"]
                    }
                    member.append(record)
                records['Member'] = member 
                
            elif "userid" in event["params"]["querystring"]:
                
                sqlQuery = "select *, value2 from member inner join dropdown on user_type = value1 where email = %s"
                values = event["params"]["querystring"]["userid"]
                mycursor.execute(sqlQuery, values)
                row = mycursor.fetchone()
                
                if row:
                    if str(row["delegate_to"]) != "" or str(row["delegate_to"]) != "0":
                        
                        sqlQuery = "select fs_name, ls_name, email, value2 from member inner join dropdown on user_type = value1 where member_id = %s"
                        values = (row["delegate_to"],)
                        mycursor.execute(sqlQuery, values)
                        row1 = mycursor.fetchone()
                    
                    if row["user_type"] == "admin":
                        mycursor.execute("select value2 from dropdown where drop_key = 'my-company-details' and value1 = 'gstin' ")
                        row2 = mycursor.fetchone()
                    
                    records = {
                        'member_id': row['member_id'],
                        'department_id': row["department_id"],
                        'fs_name': row['fs_name'],
                        'ls_name': row['ls_name'],
                        'profile_photo' : row['profile_photo'],
                        'email': row['email'], 
                        'position': row['value2'],
                        'password':row["password"],
                        'until':str(row["until"]),
                        'delegate_to':row["delegate_to"],
                        'delegate_email':"",
                        'delegate_name':"",
                        'gstin': ""
                    }
                    
                    if row1 != None:
                        records["delegate_email"] = row1["email"]
                        records["delegate_name"] = row1["fs_name"] + " " + row1["ls_name"]
                    
                    if row2 != None:
                        records["gstin"] = row2["value2"]
                
            else:
                mycursor.execute("SELECT m.member_id, m.department_id, m.fs_name, m.ls_name, m.profile_photo, m.user_type, m.group_id, d.value2 from member m left OUTER join dropdown d on m.user_type = d.value1")
                
                for row in mycursor:
                    record = {
                        'member_id': row['member_id'],
                        'department_id': row['department_id'],
                        'name': row['fs_name'] + " " + row['ls_name'],
                        'profile_photo' : row['profile_photo'],
                        'user_type': row["user_type"],
                        'group_id': row["group_id"],
                        'user_type_description': row["value2"]
                    }
                    member.append(record)
                records['Member'] = member    
        
        # xray_recorder.end_subsegment()     
    except :
        return{
          'statuscode': 500,
          'body': "Internal Failure",  
        }
        
    finally:
        mydb.close()
        # xray_recorder.begin_subsegment(name="Test")
       
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , "switch":'off'})
        # xray_recorder.end_subsegment()
        
        
    return {
        'statuscode': 200,
        'body': records,
    }

# patchMemberDetails
def patchMemberDetails(event, context):
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
        'fs_name' : "",
        'ls_name' : "",
        'user_id' : "",
        'email' : "",
        'password' : "",
        'delegate_to' :"",
        'until' :"",
        'gstin' : ""
    }
    
    for value in event["body-json"]:
        if value in record:
            record[value] = event["body-json"][value]
                
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
            
            member_id = event["params"]["querystring"]["member_id"]
            
            values = (member_id, )
            mycursor.execute("select member_id, user_type, email from member where member_id = %s", values)
            usertype = mycursor.fetchone()
            
            if usertype and usertype['user_type'] == "admin":
                values = (record['gstin'], )
                mycursor.execute("update dropdown set value2 = %s where drop_key = 'my-company-details' and value1 = 'gstin'", values)

            sqlQuery = "update member set fs_name = %s, ls_name = %s, user_id = %s, password = %s, " \
                " delegate_to = %s, until = %s where member_id = %s"
            
            values = (record["fs_name"], record["ls_name"], record["user_id"], 
                        record["password"], record["delegate_to"], record["until"],
                        member_id)
                        
            mycursor.execute(sqlQuery, values)
            
            if record["until"] != None:
                until = datetime.datetime.strptime("2020-10-15", '%Y-%m-%d')
                
            else:
                until = datetime.datetime.strptime(record["until"], '%Y-%m-%d')
            
            now = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
            
            if until >= now:
            
                values = (record["delegate_to"], member_id)  
                
                mycursor.execute("delete from delegate where delegated_to = %s and delegated_from = %s", values)
                
                values = (record["delegate_to"], member_id, record["until"])
                
                mycursor.execute("INSERT INTO delegate ( delegated_to, delegated_from, delegate_until) VALUES( %s, %s, %s )", values)
             
            else:
                values = (record["delegate_to"], member_id)  
                
                mycursor.execute("delete from delegate where delegated_to = %s and delegated_from = %s", values)
                
            msg = "Member ID" + event["params"]["querystring"]["member_id"] + " updated"
              
            mydb.commit()
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("unable to modify")
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': msg,
    }

# getNpoRuleDetail
def getNpoRuleDetail(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    print(event)
    
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
    
    decider = {
        'discount' : 0,
        'amount' : 0,
        'cost_center' : "",
        'currency' : "",
        'gl_account' : "",
        'npo' : "",
        'vendor_no': "",
        'department_id': "",
        'item_category': [],
        'document_type': ""
    }
    
    try:
        for value in event["body-json"]["decider"]:
            if value in decider:
                decider[value] = event["body-json"]["decider"][value]
                
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

            
            mycursor.execute("SELECT * FROM elipo_setting")
            settings = mycursor.fetchall()
            
            user_settings = {}

            if settings:
                for each in settings:
                    user_settings[each['key_name']] = each['value1']

                del settings
            
            if user_settings["approval_rules"] == 'on' and (user_settings["invoice_posting"] == 'on' or user_settings["invoice_posting"] == 'off'):
                flag = None
                records = {}
                rule_ids = []
                
                mycursor.execute("SELECT a.* FROM rule a inner join rule_snro b on a.rule_id = b.rule_id where b.is_approval = 'y' and a.is_on = 'y'")
                all_rules = mycursor.fetchall()
    
                for row in all_rules:
                    if row["decider"] == "npo":
                        rule_ids.append(row["rule_id"])
                
                rule_ids = set(rule_ids)
                rule_ids = list(rule_ids)
                
                rule = []
                default = []
    
                for ruleID in rule_ids:
                    rules = [] 
                    noOfRules = 0
                    countMatches = 0
    
                    for row in all_rules:
                        if row["rule_id"] == ruleID:
                            noOfRules += 1
                            if row['decider_type'] == "number":
    
                                if row['decider'] == "amount" or row["decider"] == "discount":
                                    d_value = float(decider[row['decider']])
                                    
                                else:
                                    d_value = int(decider[row['decider']])
    
                                if row['operator'] == "=" and d_value == int(row['d_value']):
                                    countMatches += 1
                                    
                                elif row['operator'] == ">" and d_value > int(row['d_value']):
                                    countMatches += 1
                                    
                                elif row['operator'] == "<" and d_value < int(row['d_value']):
                                    countMatches += 1
                                    
                                elif row['operator'] == "between" and int(row['d_value']) <= d_value <= int(row['d_value2']):
                                    countMatches += 1
    
                            elif row['decider_type'] == "string":
                                if row["decider"] == "item_category":
                                    for each in decider["item_category"]:
                                        if each == str(row['d_value']):
                                            countMatches += 1
                                            break
    
                                elif decider[row['decider']] == str(row['d_value']):
                                    countMatches += 1
                    
                    if noOfRules == countMatches and noOfRules != 0:
                        flag = True
                        rule.append(ruleID)
    
                if rule:
                    format_strings = ','.join(['%s'] * len(rule))
                    sqlQuery = "select distinct * from rule_approver where rule_key in (%s) " % format_strings
                    mycursor.execute(sqlQuery, tuple(rule))
                    approvers = mycursor.fetchall()
    
                    for row in approvers:
                        if row["approver"] == 999999999:
                            if user_settings["invoice_posting"] == 'on':
                                records = {
                                    "flag": 'y',
                                    "msg": "Send to ERP"
                                }
                            elif user_settings["invoice_posting"] == 'off':
                                records = {
                                    "flag": 'y',
                                    "msg": "Submit"
                                }
                            break
    
                if not records:
                    records = {
                        "flag": 'n',
                        "msg": "Send for Approval"
                    }
            
            elif user_settings["approval_rules"] == 'off' and user_settings["invoice_posting"] == 'on':
                records = {
                    "flag": 'y',
                    "msg": "Send to ERP"
                }
                
            elif user_settings["approval_rules"] == 'off' and user_settings["invoice_posting"] == 'off':
                records = {
                    "flag": 'y',
                    "msg": "Submit"
                }
                
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

# def getOverviewDetails(event, context):
#     trace_off = ''
#     global dbScehma 
#     dbScehma = event["stage-variables"]["schema"]
    
#     client = boto3.client(
#     'secretsmanager',
#     region_name='eu-central-1',
#     aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
#     aws_secret_access_key='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' )

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

#     try:
#         print(event)
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "use " + dbScehma
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
# 	           # atoken =  event['params']['header']['Authorization']
# 	           # print(atoken)
#             # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
#             # flg = mycursor.fetchone()
#             # if flg['value1'] == 'on':
#             #     trace_off = 'off'
#             #     print('enabling patch all')
#             #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
#             #     if json.loads(a.text)['body'] == 'on':
# 	           #     patch_all()
# 	           #     print('patch all worked')
# 	           #     print(event)  
	                
#             # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
#             # if on == 1:
#             #     chk = enable_xray(event)
#             #     if chk['Enable'] == True:
#             #         patch_all()
    
#             sqlQuery = "SELECT invoice_no, in_status, amount, due_date " \
#                 "FROM invoice_header " \
#                 "where in_status != 'tosap' or in_status != 'deleted'"
            
#             mycursor.execute(sqlQuery)
#             raw_data = mycursor.fetchall() 

#             due_amount = 0
#             over_due_amount = 0
#             payable_amount_today = 0
#             payable_within_7days = 0

#             if raw_data:

#                 for row in raw_data:
#                     today = date.today()

#                     if row["due_date"] != None and type(row["due_date"]) is not str:
                        
#                         noOfDueDays = (row["due_date"] - today).days
#                         if today <= row["due_date"]:
#                             due_amount = due_amount + row["amount"]

#                         elif today > row["due_date"]:
#                             over_due_amount = over_due_amount + row["amount"]
                        
#                         if today == row["due_date"]:
#                             payable_amount_today = payable_amount_today + row["amount"]
                        
#                         if noOfDueDays <= 7 and noOfDueDays >= 0:
#                             payable_within_7days = payable_within_7days + row["amount"]

#             overview = {
#                 "total_payable": due_amount + over_due_amount,
#                 "current_payable": due_amount,
#                 "over_due_amount": over_due_amount,
#                 "payable_by_today": payable_amount_today,
#                 "payable_within_7days": payable_within_7days
#             }
            
#     except :
#         return {
#             'statuscode': 500,
#             'body': json.dumps("Internal Error")
#         }

#     finally:
#         mydb.close()
#         # if trace_off == 'off':
#         #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , 'switch':'off'})
#         #     print('disabling patch all')

#     return {
#         'statuscode': 200,
#         'body': overview
#     }

# patchInvoiceStatus
class FailedToCreateApprocalsException(Exception):
    """"""  

def notify_approvers(members, body):
    pass

class ApprovalException(Exception):
    pass

class SapPostException(Exception):
    pass

class ErpPostException(Exception):
    pass

def get_stored_credentials(user_id):
    
    global ocr_bucket_folder
    
    try:
        s3 = boto3.client("s3")
        encoded_file = s3.get_object(Bucket=elipo_bucket, Key=ocr_bucket_folder+user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
    except Exception as excep:
        creds = None
        # print(str(excep))
        # raise NoUserIdException(excep)

def create_message(sender, to, cc, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """

    message = email.mime.text.MIMEText(message_text, 'html')
    # message = email.mime.message.MIMEMessage(message_text)
    message['to'] = to
    message['cc'] = cc
    message['from'] = sender
    message['subject'] = subject
    # return {'raw': base64.urlsafe_b64encode(message.as_string())}
    encoded = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {'raw': encoded.decode("utf-8")}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        # print("Message Id: ", message['id'])
        return message
    # except errors.HttpError as error:
    except Exception as error:
        print("An error occurred: ", error)

def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)

def sendMailNotifications(invoice_id, mycursor, status, email, by=None):
    # user_id = elipo_email
    mycursor.execute("select * from elipo_setting where key_name = 'notification-mail' ")
    email_data = mycursor.fetchone()
    user_id = email_data["value1"]

    mail_cc = ''
    mail_subject = 'ELIPO Notification'
    mailbody_text = ''

    if not by:
        by = ''

    values = (status,)
    mycursor.execute("select * from rule_notification where invoice_status = %s", values)
    notification = mycursor.fetchone()

    text1 = 'Approved'

    if status == 'approval-reject':
        text1 = 'Rejected '
        
    if status == 'referred':
        text1 = 'Referred '

    if notification:
        mail_cc = notification['mail_cc']
        mail_subject = notification["subject"]
        mailbody_text = notification["body"]
                
    mail_body = '''<html>
            <body  >
        <div style="  max-width: 500px; margin: auto; padding: 10px; ">
                <div style=" width:100%; align-content: center;text-align: center;">
                    <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/ELIPO+logo.png" alt="Italian Trulli" style="vertical-align:middle; width: 140px;height:50px;text-align: center;"  >
                </div>
        	<div style=" width:100%; align-content:left;text-align:left;">
                    <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                </div>
            <b>
                
            <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                Dear User,
            </span> 
            <br><br>
            <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                Invoice No: <span style="font: 500  15px/22px ;">{},</span>
            </span> 
        
            <br>
            <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                {} By : <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;"> {},</span> 
            </span> 
            </b> 
            <br>
            <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;"> {} </span>
            <br>
            <br>
            <div style=" width:100%;align-content: center;text-align: center; ">
                <a href="https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/production/login" target="_blank">
                    <button style="border: none;box-shadow: 1px 1px 5px 1px #5a9e9b; background:rgb(80, 219, 212) 0% 0% no-repeat padding-box; border-radius: 7px;opacity: 1;width:180px; height: 35px;outline: none;border: none;" > 
                        <span style="vertical-align: middle; text-align: left;font: 600 16px/23px Open Sans;letter-spacing: 0px;color: whitesmoke;white-space: nowrap;opacity: 1;">Login to ELIPO</span>
                    </button>
                </a>
            </div>
        
            <br><br>
            <div style="width:100%;">
            <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Regards,</span>
            <br>
            <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Team ELIPO</span>
            </div>
        <div style=" width:100%; align-content:left;text-align:left;">
                    <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                </div>
        
            
            <div style="width:100%;align-content: center;text-align: center;">
                <span style=" text-align: center;font: 600 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 0.7;">This message was sent to you by ELIPO</span>
            </div>
            <div style="width:100%;align-content: center;text-align: center;">
                <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/elipo+logo_2.png" alt="Italian Trulli" style="text-align: center;width: 80px;height: 30px;" >
            </div>
            
            <br>
        </div>
            </body></html>'''.format(invoice_id, text1, by, mailbody_text)   


    credentials = get_stored_credentials(user_id)

    if credentials and credentials.refresh_token is not None:

        service = build_service(credentials=credentials)
        message = create_message(sender="raj.gupta@peolsolutions.com", to=email, cc=mail_cc, subject=mail_subject, message_text=mail_body)
        send_message(service=service, user_id="me", message=message)


def erp_operations(user_settings, invoice_no, mycursor, working_person, is_mannually):

    erp_responce = None
    responce = None


    if user_settings['invoice_posting'] == "on":
        if user_settings['user_erp'] == "sap":
            erp_responce = sap_post_invoice(invoice_no=invoice_no, mycursor=mycursor, simulation="")
            responce = erp_responce[0]["INVOICE_NO"]
            after_erppost_audit(mycursor=mycursor,
                                invoice_no=invoice_no,
                                erp_invoiceno=erp_responce[0]["INVOICE_NO"],
                                working_person=working_person,
                                is_mannually=is_mannually)

        elif user_settings['user_erp'] == "zoho":
            zoho_invoice_post(invoice_no=invoice_no, mycursor=mycursor)
            responce = "ZOHO123"

    else:
        responce = "erpPostingOff"     

    return responce


def sap_post_invoice(invoice_no, mycursor):
    
    s3 = boto3.client("s3")
    items = []
    records = []
    values = invoice_no

    time = datetime.datetime.now()
    current_time = time.strftime("%H:%M:%S")
    
    mycursor.execute("select value1 from elipo_setting where key_name = 'attach_to_erp' ")
    post_attach = mycursor.fetchone()

    mycursor.execute("select * from invoice_header where invoice_no = %s", values)
    invoice_header = mycursor.fetchone()
    
    mycursor.execute("select name, file_path, mime_type from file_storage where file_id = %s", values)
    file = mycursor.fetchall()
    
    if post_attach["value1"] == 'on':
        upload_attach = []
        indicator = None
    
        if file:
            try:
                for row in file:
                    file_obj = s3.get_object(Bucket=row["file_path"], Key=row["name"])
                    file_content = file_obj["Body"].read()
                    file_content = str(base64.b64encode(file_content))
                    length = len(file_content)
                    file_content = file_content[2:length - 1]
                    data = {
                        "file_content": file_content,
                        "mime_type": row["mime_type"]
                    }
                    
                    if(data['mime_type'] == ''):
                        fname = file[0]['name'].split('.')[len(file[0]['name'].split('.')) - 1]
                        if fname == "pdf":
                            data['mime_type'] = "application/pdf"
                        elif fname == "png":
                            data['mime_type'] = "image/png"
                        elif fname == "jpg":
                            data['mime_type'] = "image/jpg"
                        elif fname == "jpeg":
                            data['mime_type'] = "image/jpg"
                    
                    upload_attach.append(data)
    
                indicator = True
    
            except Exception as e:
                print("process didn't stopped", e)
    
        if not indicator:
            file_content = None
            upload_attach.append({
                "file_content": "None",
                "mime_type": "None"
            })
            
    elif post_attach["value1"] == 'off':
        upload_attach = []
        file_content = None
        upload_attach.append({
            "file_content": "None",
            "mime_type": "None"
        })

    values1 = (invoice_header["company_code"],invoice_header["tax_per"])
    mycursor.execute("select tax_code from tax_code where company_code = %s and tax_per = %s",values1)
    # tax_code = mycursor.fetchone()  #new invoices
    
    if values[1] != '0':
        tax_code = mycursor.fetchone()
    else:
        tax_code = mycursor.fetchall()
        tax_code = tax_code[len(tax_code)-1]
        
        if tax_code['tax_code'] == '5':
            tax_code['tax_code'] = '05'
        
    tax_per_h = tax_code['tax_code']

    mycursor.execute("select a.*, mm.material_no " \
		"from invoice_item a " \
        "left join material_master mm " \
        "on a.material = mm.material_no or a.material_desc = mm.material_name " \
		"where invoice_no = %s order by a.item_no", values)
    
    creditDebitInd = ""
    if invoice_header:
        if invoice_header["npo"] == "y":
            creditDebitInd = "S"
        else:
            if invoice_header["document_type"] == "RE" or invoice_header["document_type"] == "KG":
                creditDebitInd = ""
            else:
                creditDebitInd = "X"
        
    for index, row in enumerate(mycursor):
        
        if row["material_no"] == None:
            materialName = row["material"].upper()
        else:
            materialName = row["material_no"].upper()
            
        if row["ebelp"] == None or row["ebelp"] == "":
            ebelp_data = (index + 1) * 10
        else:
            ebelp_data = row["ebelp"]
            
        # if row["gst_per"] == 0 or row["gst_per"] == '0':  #new invoices
        #     tax_per_h = '00'
        # else:
        #     if  tax_per_h == '':
        #         tax_per_h = row["gst_per"]
        # tax_code = ""
        
        # mycursor.execute("select company_code from default_master where company_code = (select company_code from invoice_header where invoice_no = %s)",invoice_no)
        # c_code = mycursor.fetchone()
        # if invoice_header['company_code'] == 3000:

        # values = (invoice_header["company_code"],invoice_header["tax_per"])
        # mycursor.execute("select tax_code from tax_code where company_code = %s and tax_per = %s",values)
        # tax_code = mycursor.fetchone()
        # tax_per_h = tax_code['tax_code']

        record = {
            "Belnr": " ",
            "Gjahr": " ",
            "Buzei": row["item_no"],
            "Ebeln": invoice_header["ref_po_num"],
            "Ebelp": ebelp_data,
            "Matnr": materialName,
            "Wrbtr": str(row["gross_amount"]),
            "BWKEY": row["plant"],
            "Shkzg": creditDebitInd,
            "Mwskz": str(tax_per_h),
            "TXJCD": invoice_header["jurisdiction_code"],
            "Menge": str(row["quantity"]),
            "Bstme": row["unit"],
            "WRF_CHARSTC1": row["gl_account"],
        }
        items.append(record)

    if invoice_header:
        baseline_date = str(invoice_header["baseline_date"]) + "T" + current_time
        posting_date = str(invoice_header["posting_date"]) + "T" + current_time
        invoice_date = str(invoice_header["invoice_date"]) + "T" + current_time
        
        if invoice_header["document_type"] == "RE" or invoice_header["document_type"] == "SU":
            invoice_ind = "X"
        else:
            invoice_ind = ""
            
        mycursor.execute("select value1 from elipo_setting where key_name = 'npo_tcode' ")
        npoTcode = mycursor.fetchone()
        
        
        postingFlag = None
        if npoTcode:
            if npoTcode["value1"] == "FB60":
                postingFlag = "X"
            else:
                postingFlag = ""
                
        if invoice_header["tax_per"] == 0 or invoice_header["tax_per"] == '0':
            tax_per_i = '00'
        else:
            tax_per_i = invoice_header["tax_per"]
        
        if tax_code != "":
            tax_per_i = tax_code
            
        # mycursor.execute(" SELECT value1 FROM elipo_setting where key_name = 'country' ")
        # country = mycursor.fetchone()
        # country = country['value1']
        # if country == 'india':
        #     tax_per_h = '0I'

        records = {
            "Belnr": " ",
            "Gjahr": " ",
            "Blart": "RE",
            "Xrech": invoice_ind,
            "Bldat": invoice_date,
            "Budat": posting_date,
            "Bukrs": invoice_header["company_code"],
            "Lifnr": invoice_header["supplier_id"],
            "Waers": invoice_header["currency"],
            "Xmwst": "",
            "Rmwwr": str(invoice_header["amount"]),
            "Mwskz_bnk": tax_per_h,
            # "Mwskz_bnk": tax_per_i['tax_code'],
            "Zfbdt": baseline_date,
            "InvoicehToitem": items,
            "Simu": "",
            "NpoPosting": postingFlag,
            "Attachment": upload_attach
        }
        print(records)
        
    mycursor.execute("select * from elipo_setting where key_name in ('sap_posting_url', 'sap_password', 'sap_userid')")
    sap_settings = mycursor.fetchall()

    sap_post_setting = {}
    
    if sap_settings:
        for each in sap_settings:
            sap_post_setting[each['key_name']] = each['value1']
    
        del sap_settings

    try: 
        s = requests.Session()
        s.headers.update({'Connection': 'keep-alive'})
    
        # url = "http://182.72.219.94:8000/zinvoiceno1/InvoicePost"
        # url = sap_post_setting["sap_posting_url"]
        url = 'http://182.72.219.94:8000/zinvoicebp/invoicebp'
        params = {'sap-client': '800'}
    
        headersFetch = {'X-CSRF-TOKEN': 'Fetch'}
        y = s.get(url, auth=HTTPBasicAuth('developer08', 'Peol@123'), headers=headersFetch, params=params)
        token = y.headers["X-CSRF-TOKEN"]
        # token = 'abc'
    
        headers = {"X-CSRF-TOKEN": token, 'Content-type': 'application/json'}
        records['Bldat'] = records['Bldat'].replace("-", "")
        records['Zfbdt'] = records['Zfbdt'].replace("-", "")
        records['Budat'] = records['Budat'].replace("-", "")
        records['TXJCD_BNK'] = records['InvoicehToitem'][0]['TXJCD']
        sap_responce = s.post(url, json=records, auth=HTTPBasicAuth('developer08', 'Peol@123'), headers=headers, params=params)
        responce = sap_responce.json()
        
        print(responce)
        error_list = []
        sap_errors = []
        error_flag = False
    
        for count, each in enumerate(responce[0]["RET"], 1):
            if each['TYPE'] == 'E':
                error_flag = True
    
            if each['TYPE'] == 'W':
                mycursor.execute("select is_warning_set from invoice_header where invoice_no = %s", invoice_no)
                warning_flag = mycursor.fetchall()
                if warning_flag["is_warning_set"] == 'n':
                    mycursor.execute("update invoice_header set is_warning_set = 'y' where invoice_no = %s", invoice_no)
                    error_flag = True
    
            err_dict = {
                'type': each['TYPE'],
                'msg': each['MESSAGE']
            }
            sap_errors.append(err_dict)
            error_dict = (str(invoice_no), str(count), each["TYPE"], each["MESSAGE"])
            error_list.append(error_dict)
    
        if error_flag == True:
            msg = "While posting error was generated please check the error log!"
            err_responce = {
                "sap_errors": sap_errors,
                "msg": msg
            }
            raise SapPostException(err_responce)
    
        else:
            return responce[0]["INVOICE_NO"]
            
    # except requests.exceptions.Timeout as msg:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Resource temporarily unavailable!")
    #     }
    
    # except requests.exceptions.HTTPError as msg:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Resource temporarily unavailable!")
    #     }
        
    # except requests.exceptions.TooManyRedirects as msg:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Too Many Redirects!")
    #     }
        
    # except requests.exceptions.RequestException as msg:
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Resource temporarily unavailable!")
    #     }
        
    # except requests.exceptions.ConnectionError as msg:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Resource temporarily unavailable!")
    #     }
    
    finally:
        pass
        

def zoho_invoice_post(mycursor, invoice_no):
    zoho_invoice = {'line_items': []}

    # s3 = boto3.client("s3")

    values = (invoice_no,)

    mycursor.execute("select * from invoice_header where invoice_no = %s", values)
    invoice_header = mycursor.fetchone()

    if invoice_header:

        mycursor.execute("select a.*, mm.material_no " \
                         "from invoice_item a " \
                         "left join material_master mm " \
                         "on a.material = mm.material_no or a.material_desc = mm.material_name " \
                         "where invoice_no = %s order by a.item_no", values)
        items = mycursor.fetchall

        if items:
            for index, row in enumerate(mycursor):
                item_id = ''

                if row["material_no"] == None:
                    item_id = row["material"].upper()

                else:
                    item_id = row["material_no"].upper()

                zoho_item = {}
                zoho_item['item_id'] = item_id
                zoho_item['quantity'] = row["quantity"]
                zoho_item['rate'] = float(row['amt_per_unit'])
                zoho_item['unit'] = row['unit']

                zoho_invoice['line_items'].append(zoho_item)

        zoho_invoice['invoice_number'] = invoice_header['user_invoice_id']
        zoho_invoice['customer_id'] = invoice_header['supplier_id']
        zoho_invoice["contact_persons"]= ["1597715000000303029"]
        zoho_invoice['date'] = str(invoice_header["invoice_date"])
        zoho_invoice['due_date'] = str(invoice_header["baseline_date"])
        zoho_invoice['currency_id'] = invoice_header["currency"]
        # zoho_invoice['currency_code'] = invoice_header["currency"]
        # zoho_invoice['gst_no'] = 788

        req = requests.Session()

        url = "https://accounts.zoho.com/oauth/v2/token"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded"
        }

        params = {
            'redirect_uri': "http://example.com/yourcallback",
            'client_id': "1000.M9VQW4HBX0KMZILVA2QO1GJXF0HCFX",
            'client_secret': "00ebd763b7e68be7ee65d89d641e93130f1ea44201",
            'refresh_token': "1000.0f0c53563239b7e47e760c8dc270c288.a1f05395858255b0b339aa168806f6ec",
            'grant_type': "refresh_token"
        }

        access_token = req.post(url=url, headers=headers, params=params)

        if access_token.status_code == 200:
            access_token = access_token.json()

            url = "https://invoice.zoho.com/api/v3/invoices"

            headers = {
                # 'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8",
                'Authorization': "Zoho-oauthtoken " + str(access_token['access_token'])
            }

            params = {
            }
            # "customer_id": "1597715000000303001",
            # "contact_persons": ["1597715000000303029"],

            body = {
                "JSONString": json.dumps(zoho_invoice),
            }

            responce = requests.post(url=url, params=params, headers=headers, data=body)

            # print(responce.json())
            dbdh = responce.json()
            print(responce.status_code)

            if responce.status_code != 200:

                erp_errors = []

                if responce.status_code == 400:
                    error = json.loads(responce.text)

                    erp_errors.append({
                        'type': error['code'],
                        'msg': error['message']
                    })
                    msg = "While posting error was generated please check the error log!"
                    err_responce = {
                        "sap_errors": erp_errors,
                        "msg": msg
                    }
                    raise ErpPostException(erp_errors)

            # zoho_invoice_post(mycursor=mycursor, invoice_no=3122)


def getUsrEmails(mycursor, groups=None, members=None):

    emails = None
    emails_str = ""

    if groups:
        format_strings_grp = ','.join(['%s'] * len(groups))
    if members:
        format_strings_mem = ','.join(['%s'] * len(members))

    if members and groups:
        mix = members + groups
        mycursor.execute("select email from member where member_id in ({}) or group_id in ({})".format(format_strings_mem, format_strings_grp), tuple(mix))
        emails = mycursor.fetchall()

    elif groups:
        mycursor.execute("select email from member where group_id in ({})".format(format_strings_grp), tuple(groups))
        emails = mycursor.fetchall()

    else:
        mycursor.execute("select email from member where member_id in ({})".format(format_strings_mem), tuple(members))
        emails = mycursor.fetchall()

    if emails:
        for index, each in enumerate(emails):
            if index == 0:
                emails_str = str(each['email'])
                continue

            emails_str += "," + str(each['email'])

    return  emails_str

def patchInvoiceStatus(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    secret = event["stage-variables"]["secreat"]
    
    # global elipo_email
    # elipo_email = event["stage-variables"]["notification_email"]
    
    global elipo_bucket
    elipo_bucket = event["stage-variables"]["cred_bucket"]
    
    global ocr_bucket_folder
    ocr_bucket_folder = event["stage-variables"]["ocr_bucket_folder"]

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
        cursorclass=pymysql.cursors.DictCursor
    )

    msg = "Action not performed!"
    records = {}
    print(event)
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

            mycursor.execute("SELECT * FROM elipo_setting")
            settings = mycursor.fetchall()

            user_settings = {}

            if settings:
                for each in settings:
                    user_settings[each['key_name']] = each['value1']

                del settings

            invoice_no = event["params"]["querystring"]["invoice_no"]
            status = event["params"]["querystring"]["in_status"]
            email = event["params"]["querystring"]["userid"]
            time_taken = event["params"]["querystring"]["time_taken"]

            if (status == "tosap" or (status == "rejected" and "approver_comments" in event["body-json"]) or (status == "refer" and "refer_id" in event["params"]["querystring"] 
                and "refer_comment" in event["body-json"])):


                if "approver_comments" in event["body-json"]:
                    comments = event["body-json"]["approver_comments"]
                else:
                    comments = ""

                mycursor.execute("select member_id, group_id, concat(fs_name , ' ', ls_name) as member_name from member where email = %s", email)
                member = mycursor.fetchone()

                sqlQuery = "select approver_id FROM approver where member_id = %s"
                values = (member["member_id"],)
                mycursor.execute(sqlQuery, values)
                approver = mycursor.fetchone()

                approval = None

                if member['member_id'] and member['group_id']:
                    sqlQuery = "select * from approval where (( isgroup = 'y' and approver = %s ) or ( isgroup = 'n' and approver = %s )) " \
                        "and (isapproved = 'n' or approval_type = 'parallel') and invoice_no = %s"
                    values = (member['group_id'], member['member_id'], invoice_no)
                    mycursor.execute(sqlQuery, values)
                    approval = mycursor.fetchone()

                elif member['member_id']:
                    sqlQuery = "select * from approval where isgroup = 'n' and approver = %s and (isapproved = 'n' or approval_type = 'parallel') and invoice_no = %s"
                    values = (member['member_id'], invoice_no)
                    mycursor.execute(sqlQuery, values)
                    approval = mycursor.fetchone()

                elif member['group_id']:
                    sqlQuery = "select * from approval where isgroup = 'y' and approver = %s and (isapproved = 'n' or approval_type = 'parallel') and invoice_no = %s"
                    values = (member['group_id'], invoice_no)
                    mycursor.execute(sqlQuery, values)
                    approval = mycursor.fetchone()

                if approval is not None:

                    if approval["isapproved"] == "n" and (approval['approval_type'] == 'parallel' or approval["pre_approval"] == 'y' or int(approval["approval_level"]) == 1):

                        sqlQuery = "select * from invoice_header where invoice_no = %s"
                        values = (invoice_no,)
                        mycursor.execute(sqlQuery, values)
                        invoiceheader = mycursor.fetchone()
                        
                        if invoiceheader and invoiceheader["document_type"] == 'RE':
                            documentType = "Invoice "
                            
                        elif invoiceheader and invoiceheader["document_type"] == 'KG':
                            documentType = "Credit Memo "
                            
                        elif invoiceheader and invoiceheader["document_type"] == 'SU':
                            documentType = "Debit Memo "

                        if status == "tosap":

                            sqlQuery = "update approval set isapproved = 'y', time_taken = %s, accept_comment = %s where invoice_no = %s and approval_level = %s"
                            values = (time_taken, comments, approval['invoice_no'], approval['approval_level'])
                            mycursor.execute(sqlQuery, values)

                            sqlQuery = "select * from approval where isapproved = 'n' and invoice_no = %s and approval_level != %s"
                            values = (invoice_no, approval['approval_level'])
                            mycursor.execute(sqlQuery, values)
                            remaining = mycursor.fetchone()

                            if not remaining:

                                if invoiceheader and invoiceheader['from_supplier'] == 'y':
                                    sup_status = "approved"
                                else:
                                    sup_status = ""
                                    
                                sqlQuery = "update invoice_header set in_status = %s, sup_status = %s, end_date = current_timestamp() where invoice_no = %s"
                                values = (status, sup_status, invoice_no)
                                mycursor.execute(sqlQuery, values)

                                if user_settings['invoice_posting'] == "on":
                                    if user_settings['user_erp'] == "sap":
                                        erp_responce = sap_post_invoice(invoice_no=invoice_no, mycursor=mycursor)
                                        responce = erp_responce  
                                        print("responce", responce)
                                        
                                        if "statuscode" in responce:
                                            mydb.rollback()
                                            return {
                                                'statuscode': 500,
                                                'body': json.dumps(responce["body"])
                                            }
                                        
                                    elif user_settings['user_erp'] == "zoho":
                                        responce = "ZOHO123"
                                    
                                    if comments == "" or comments == None:
                                        msg_cmnt = str(documentType) + str(invoice_no) + " Approved and Submitted to ERP with " + str(documentType) + str(responce) + " by " + str(member["member_name"])
                                    else:
                                        msg_cmnt = str(documentType) + str(invoice_no) + " Approved with comment '" + comments + "' and Submitted to ERP with " + str(documentType) + str(responce) + " by " + str(member["member_name"])
                                    
                                    
                                    msg = str(documentType) + str(responce) + " created in ERP for " + str(documentType) + str(invoice_no)
                                    
                                else:
                                    responce = None
                                    if comments == "" or comments == None:
                                        msg_cmnt = str(documentType) + "Approved and Accepted by " + str(member["member_name"])
                                    else:
                                        msg_cmnt = str(documentType) + "Approved with comment '" + comments + "' and Accepted by " + str(member["member_name"])
                                        
                                    msg = str(documentType) + str(invoice_no) + " Submitted." 

                                sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                                values = (invoice_no, "inapproval", "tosap", member['member_id'], msg_cmnt)
                                mycursor.execute(sqlQuery, values)
                                
                                sqlQuery = "INSERT INTO approval_history (isgroup,approver_id,invoice_no,member_id,approval_level,approval_type,entry_date, " \
                                    "in_status, time_taken, accept_comment) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                values = ( approval['isgroup'], approval['approver'], approval['invoice_no'], member['member_id'], approval['approval_level'], 
                                approval['approval_type'], approval['entry_date'], "approved", approval['time_taken'], comments)
                                mycursor.execute(sqlQuery, values)

                                sqlQuery = "delete from approval where invoice_no = %s"
                                values = (invoice_no,)
                                mycursor.execute(sqlQuery, values)

                                sqlQuery = "update invoice_header set sap_invoice_no = %s, end_date = CURRENT_TIMESTAMP() where invoice_no = %s "
                                values = (responce, invoice_no)
                                print(sqlQuery, values)
                                mycursor.execute(sqlQuery, values) 

                                email_adres = None
                                if invoiceheader['working_person']:
                                    templist = []
                                    templist.append(invoiceheader['working_person'])
                                    email_adres = getUsrEmails(mycursor=mycursor, members=templist)

                                if email_adres:
                                    sendMailNotifications(invoice_id=invoice_no, mycursor=mycursor, status='approval-tosap', email= email_adres, by=member['member_name'])
                                
                                
                                
                            else:

                                sqlQuery = "INSERT INTO approval_history (isgroup,approver_id, invoice_no,member_id,approval_level,approval_type,entry_date, " \
                                    "in_status, time_taken, accept_comment) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                values = (approval['isgroup'], approval['approver'], approval['invoice_no'], member['member_id'], approval['approval_level'], approval['approval_type'], 
                                    approval['entry_date'], "approved", time_taken, comments)
                                mycursor.execute(sqlQuery, values)

                                sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                                
                                if comments == None or comments == "":
                                    msg_cmnt = str(documentType) + "approved by " + str(member["member_name"])
                                else:
                                    msg_cmnt = str(documentType) + "approved with comment '" + comments + "' by " + str(member["member_name"])
                                    
                                values = (invoice_no, "inapproval", "inapproval", member['member_id'], msg_cmnt)
                                mycursor.execute(sqlQuery, values)

                                level = int(approval["approval_level"]) + 1
                                values = (invoice_no, level)
                                mycursor.execute("update approval set pre_approval = 'y' where invoice_no = %s and approval_level = %s", values)

                                if approval['approval_type'] != 'parallel':
                                    values = (invoice_no, level)
                                    mycursor.execute("select isgroup, approver from approval where invoice_no = %s and approval_level = %s",values)
                                    multiple_app = mycursor.fetchall()

                                    groups = []
                                    members = []

                                    for row in multiple_app:
                                        if row['isgroup'] == 'y': 
                                            groups.append(row['approver'])

                                        else:
                                            members.append(row['approver'])

                                    email_adres = getUsrEmails(mycursor=mycursor, groups=groups, members=members)

                                    if email_adres:
                                        sendMailNotifications(invoice_id=invoice_no, mycursor=mycursor, status="next_approval", email=email_adres, by=member['member_name'])

                                msg = str(documentType) + str(invoice_no) + " is approved and sent for next approval"

                        elif status == "rejected":

                            if invoiceheader and invoiceheader['from_supplier'] == 'y':
                                sup_status = "rejected"
                            else:
                                sup_status = ""

                            sqlQuery = "update invoice_header set in_status = %s, sup_status = %s, approver_comments = %s where invoice_no = %s"
                            values = (status, sup_status, comments, invoice_no)
                            mycursor.execute(sqlQuery, values) 

                            # sqlQuery = "INSERT INTO approval_history (isgroup,approver_id,invoice_no, member_id,approval_level,approval_type,entry_date, in_status, " \
                            #     " time_taken) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                            # values = (approval['isgroup'], approval['approver'], approval['invoice_no'], member['member_id'], approval['approval_level'], approval['approval_type'],
                            #     approval['entry_date'], "rejected", time_taken)
                            # mycursor.execute(sqlQuery, values)

                            sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                            msg_cmnt = str(documentType) + "rejected by " + str(member["member_name"])
                            values = (invoice_no, "inapproval", "rejected", member['member_id'], msg_cmnt)
                            mycursor.execute(sqlQuery, values)

                            sqlQuery = "delete from approval where invoice_no = %s"
                            values = (invoice_no,)
                            mycursor.execute(sqlQuery, values)

                            sqlQuery = "delete from approval_history where invoice_no = %s"
                            values = (invoice_no,)
                            mycursor.execute(sqlQuery, values)

                            sqlQuery = "delete from delegate where invoice_id = %s"
                            values = (invoice_no,)
                            mycursor.execute(sqlQuery, values)
                            
                            email_adres = None
                            if invoiceheader['working_person']:
                                templist = []
                                templist.append(invoiceheader['working_person'])
                                email_adres = getUsrEmails(mycursor=mycursor, members=templist)

                            msg = str(documentType) + str(invoice_no) + " rejected"

                            if email_adres:
                                # sendMailNotifications(invoice_id=invoice_no, mycursor=mycursor, status="rejected")
                                sendMailNotifications(invoice_id=invoice_no, mycursor=mycursor, status='approval-reject', email=email_adres, by=member['member_name'])

                        elif status == "delegate":
                            pass
                            # if email:
                            #     # pass
                            #     values = (email,)
                            #     mycursor.execute(
                            #         "SELECT member_id, delegate_to FROM member where email = %s",
                            #         values)
                            #     delegator = mycursor.fetchone()
                            #
                            #     if delegator is not None:
                            #
                            #         until_date = datetime.date.today() + datetime.timedelta(days=2)
                            #         values = (delegator["delegate_to"], delegator["member_id"], invoice_no, until_date)
                            #         mycursor.execute(
                            #             "INSERT INTO delegate (delegated_to, delegated_from, invoice_id, delegate_until) VALUES (%s, %s, %s, %s)",
                            #             values)
                            #
                            #         sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                            #         msg_cmnt = "Invoice delegated to Member ID " + str(delegator["member_id"])
                            #         values = (invoice_no, "inapproval", "inapproval", delegator['member_id'], msg_cmnt)
                            #         mycursor.execute(sqlQuery, values)
                            #
                            #         msg = "Invoice delegated successfully"
                            #
                            #     else:
                            #         msg = "Provide User id"

                        elif status == 'refer': 

                            refer_member_id = event["params"]["querystring"]["refer_id"]
                            refer_comment = event["body-json"]["refer_comment"]

                            sqlQuery = "update approval set refer_lock = 'y' where approval_level = %s and invoice_no = %s " \
                                "and ( isgroup = 'y' or ( isgroup = 'n' and approver != %s)) "
                            values = (approval["approval_level"], approval['invoice_no'], member["member_id"])
                            mycursor.execute(sqlQuery, values)

                            # this select statement is to check if the invoice was refered by same member to others
                            values = (member["member_id"], invoice_no)
                            mycursor.execute("select * from delegate where delegated_from = %s and invoice_id = %s and is_refered = 'y'", values)
                            if_delegated = mycursor.fetchone()

                            if not if_delegated:
                                if approval["isgroup"] == 'y':
                                    sqlQuery = "INSERT INTO approval (isgroup, approver, invoice_no, isapproved, approval_level, approval_type, escalate_date, " \
                                       " rule_id, refer_lock, referred_approver) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                    values = ('n', member["member_id"], approval["invoice_no"], approval["isapproved"], approval["approval_level"], approval["approval_type"],
                                        approval["escalate_date"], approval["rule_id"], 'n', 'y')
                                    mycursor.execute(sqlQuery, values)
                            else:

                                if approval["isgroup"] == 'y':
                                    values = (member['member_id'], invoice_no)
                                    mycursor.execute("select * from approval where isgroup = 'n' and approver = %s and invoice_no = %s", values)
                                    entrycheck = mycursor.fetchone()  

                                    if not entrycheck:
                                        sqlQuery = "INSERT INTO approval (isgroup, approver, invoice_no, isapproved, approval_level, approval_type, escalate_date, " \
                                                    " rule_id, refer_lock, referred_approver) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                        values = ('n', member["member_id"], approval["invoice_no"], approval["isapproved"], approval["approval_level"], approval["approval_type"],
                                                    approval["escalate_date"], approval["rule_id"], 'n', 'y')
                                        mycursor.execute(sqlQuery, values)            

                            values = (refer_member_id, member["member_id"], invoice_no, 'y', refer_comment)
                            mycursor.execute("INSERT INTO delegate (delegated_to, delegated_from, invoice_id, is_refered, " \
                                "refer_comment) VALUES (%s, %s, %s, %s, %s)", values)

                            values = (refer_member_id, )
                            mycursor.execute("select member_id, group_id, concat(fs_name , ' ', ls_name) as member_name, email from member where member_id = %s", values)
                            refer_mem = mycursor.fetchone()

                            if refer_mem:
                                email_adres = refer_mem["email"]

                            sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                            msg_cmnt = str(documentType) + "referred by " + str(member["member_name"]) + " to " + str(refer_mem["member_name"]) 
                            values = (invoice_no, "inapproval", "inapproval", member['member_id'], msg_cmnt)
                            mycursor.execute(sqlQuery, values)

                            msg = str(documentType) + str(invoice_no) + " Refered Successfully!"

                            if email_adres:
                                sendMailNotifications(invoice_id=invoice_no, mycursor=mycursor, status='referred', email=email_adres, by=member['member_name'])

                        mydb.commit()
  
                    else:
                        if approval["pre_approval"] != 'y':
                            msg = "Previous approval is pending" 
                            
                        else:
                            msg = "Already Approved"

                else:
                    msg = "No approval created for this invoice"

            else:
                msg = "Provide all mandotory fields"

    # except SapPostException as er:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 300,
    #         # 'body': sap_errors
    #         'body': er.args[0]
    #     }
        
    # except requests.exceptions.Timeout as msg:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Resource temporarily unavailable!")
    #     }
        
    # except requests.exceptions.TooManyRedirects as msg:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Too Many Redirects!")
    #     }
        
    # except requests.exceptions.RequestException as msg:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Resource temporarily unavailable!")
    #     }
        
    # except requests.exceptions.ConnectionError as msg:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Resource temporarily unavailable!")
    #     }
    
    # except Exception as e:
    #     mydb.rollback()
    #     return {
    #         'statuscode': 500, 
    #         'body': json.dumps("Internal Error!")   
    #     } 

    finally: 
        mydb.close()

    if not msg:
        msg = ""

    return {
        'statuscode': 200,
        'body': json.dumps(msg)
    }

# patchReferInvoice
def get_stored_credentials(user_id):
    
    global ocr_bucket_folder
    
    try:
        s3 = boto3.client("s3")
        encoded_file = s3.get_object(Bucket=elipo_bucket, Key=ocr_bucket_folder+user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
        
    except Exception as excep:
        creds = None

def create_message(sender, to, cc, subject, message_text):
    
    message = email.mime.text.MIMEText(message_text, 'html')
    message['to'] = to
    message['cc'] = cc
    message['from'] = sender
    message['subject'] = subject
    encoded = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {'raw': encoded.decode("utf-8")}

def send_message(service, user_id, message):
    try:  
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return message
        
    except Exception as error:
        print("An error occurred: ", error)

def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)  

def sendMailNotifications(invoice_id, mycursor, email, by=None):
    
    # user_id = elipo_email
    mycursor.execute("select * from elipo_setting where key_name = 'notification-mail' ")
    email_data = mycursor.fetchone()
    user_id = email_data["value1"]
    
    mail_cc = ''
    mail_subject = 'ELIPO Notification'
    mailbody_text = 'Reply to the referred invoice has been received.'

    if not by:
        by = ''

    text1 = 'Replied '
    
    mail_body = '''<html>
            <body  >
        <div style="  max-width: 500px; margin: auto; padding: 10px; ">
                <div style=" width:100%; align-content: center;text-align: center;">
                    <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/ELIPO+logo.png" alt="Italian Trulli" style="vertical-align:middle; width: 140px;height:50px;text-align: center;"  >
                </div>
        	<div style=" width:100%; align-content:left;text-align:left;">
                    <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                </div>
            <b>
                
            <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                Dear User,
            </span> 
            <br><br>
            <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                Invoice No: <span style="font: 500  15px/22px ;">{},</span>
            </span> 
        
            <br>
            <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                {} By : <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;"> {},</span> 
            </span> 
            </b> 
            <br>
            <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;"> {} </span>
            <br>
            <br>
            <div style=" width:100%;align-content: center;text-align: center; ">
                <a href="https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/production/login" target="_blank">
                    <button style="border: none;box-shadow: 1px 1px 5px 1px #5a9e9b; background:rgb(80, 219, 212) 0% 0% no-repeat padding-box; border-radius: 7px;opacity: 1;width:180px; height: 35px;outline: none;border: none;" > 
                        <span style="vertical-align: middle; text-align: left;font: 600 16px/23px Open Sans;letter-spacing: 0px;color: whitesmoke;white-space: nowrap;opacity: 1;">Login to ELIPO</span>
                    </button>
                </a>
            </div>
        
            <br><br>
            <div style="width:100%;">
            <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Regards,</span>
            <br>
            <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Team ELIPO</span>
            </div>
        <div style=" width:100%; align-content:left;text-align:left;">
                    <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                </div>
        
            
            <div style="width:100%;align-content: center;text-align: center;">
                <span style=" text-align: center;font: 600 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 0.7;">This message was sent to you by ELIPO</span>
            </div>
            <div style="width:100%;align-content: center;text-align: center;">
                <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/elipo+logo_2.png" alt="Italian Trulli" style="text-align: center;width: 80px;height: 30px;" >
            </div>
            
            <br>
        </div>
            </body></html>'''.format(invoice_id, text1, by, mailbody_text)   

    credentials = get_stored_credentials(user_id)

    if credentials and credentials.refresh_token is not None: 
        service = build_service(credentials=credentials)
        message = create_message(sender=user_id, to=str(email), cc=mail_cc, subject=mail_subject, message_text=mail_body)
        send_message(service=service, user_id="me", message=message) 

def patchReferInvoice(event, context):
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
    
    # global elipo_email
    # elipo_email = event["stage-variables"]["notification_email"]
    
    global elipo_bucket
    elipo_bucket = event["stage-variables"]["cred_bucket"]
    
    global ocr_bucket_folder
    ocr_bucket_folder = event["stage-variables"]["ocr_bucket_folder"]

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
            
            if "comment" in event["body-json"]:
                
                delegated_from = event["params"]["querystring"]["delegated_from"]
                delegated_to = event["params"]["querystring"]["delegated_to"]
                invoice_no = event["params"]["querystring"]["invoice_no"]
                sr_no = event["params"]["querystring"]["sr_no"]
                comment = event["body-json"]["comment"]
                
                sqlQuery = "select member_id, concat(fs_name, ' ', ls_name) as member_name, email from member where member_id = %s or member_id = %s"
                values = ( delegated_from, delegated_to )
                mycursor.execute(sqlQuery, values)
                data = mycursor.fetchall()
                print(data) 
                
                for row in data:
                    if str(row["member_id"]) == str(delegated_from):
                        dele_from = {
                            "member_id": row["member_id"],
                            "member_name": row["member_name"]
                        }
                        email_adres = row["email"]
                        
                    if str(row["member_id"]) == str(delegated_to):
                        dele_to = {
                            "member_id": row["member_id"],
                            "member_name": row["member_name"]
                        }
                        mailMemberName = row["member_name"]
                
                sqlQuery = "update delegate set accepted_comment = %s, is_accepted = 'y' where invoice_id = %s and delegated_to = %s and delegated_from = %s and sr_no = %s"
                values = ( comment, invoice_no, delegated_to, delegated_from, sr_no )
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = "update approval set refer_completed = 'y' where isgroup = 'n' and approver = %s and invoice_no = %s"
                values = ( delegated_from, invoice_no)
                mycursor.execute(sqlQuery, values)
                
                if dele_to:
                    sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                    msg_cmnt = str(dele_to["member_name"]) + " Replied to Invoice Referred by " + str(dele_from["member_name"])
                    values = (invoice_no, "inapproval", "inapproval", dele_to['member_id'], msg_cmnt) 
                    mycursor.execute(sqlQuery, values)
                
                sendMailNotifications(invoice_id=invoice_no, mycursor=mycursor, email= email_adres, by=mailMemberName)
                
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
        'body': json.dumps("Replied Successfully!")
    }

def getRuleNotification(event, context):
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

    records = []

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

            mycursor.execute("select r.*,d.value2 as description from rule_notification r "
                             "left join dropdown d on r.invoice_status = d.value1 "
                             "where d.drop_key = 'rule_statuses'")
            notifications = mycursor.fetchall()

            allmails = []

            for each in notifications:
                if each['mail_cc']:
                    mails = each['mail_cc'].split(',')
                    allmails += mails

            allmails = set(allmails)
            allmails = list(allmails)
            
            if allmails:
                format_String = ','.join(['%s'] * len(allmails))
                mycursor.execute("select member_id, fs_name, ls_name, email "
                                 "from member "
                                 "where email in ({})".format(format_String), tuple(allmails))
                members = mycursor.fetchall()

            for row in notifications:

                if row['mail_cc'] and row['mail_cc'] != "":
                    mails = row['mail_cc'].split(',')
                else:
                    mails = []
                reclist = []

                for mail in mails:
                    for mem in members:
                        if mail == mem['email']:
                            rec = {
                                'name': mem['fs_name'] + " " + mem['ls_name'],
                                'member_id': mem['member_id']
                            }
                            reclist.append(rec)
                            break

                record = {
                    "invoice_status": row["invoice_status"],
                    "status_desc": row['description'],
                    # "mail_to": row["mail_to"],
                    "mail_cc": reclist,
                    "subject": row["subject"],
                    "body": row["body"]
                }
                records.append(record)

    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure!"),
        }

    finally:
        mydb.close()
    
    return {
        'statuscode': 200,
        'body': records
    }

# patchRuleNotification
def patchRuleNotification(event, context):
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
        # "mail_to": "",
        "mail_cc": [],
        "subject": "",
        "body": ""
    }

    for value in event["body-json"]:
        if value in record:
            record[value] = event["body-json"][value]

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

            if "invoice_status" in event["params"]["querystring"]:

                tomails = None

                if record['mail_cc']:

                    format_strings = ','.join(['%s'] * len(record['mail_cc']))

                    mycursor.execute("select email from member "
                                     "where member_id in ({})".format(format_strings), tuple(record['mail_cc']))
                    emails = mycursor.fetchall()

                    if emails:
                        for index, each in enumerate(emails):
                            if index == 0:
                                tomails = str(each['email'])
                                continue

                            tomails += "," + str(each['email'])

                status = event["params"]["querystring"]["invoice_status"]

                sqlQuery = "update rule_notification set mail_cc = %s, subject = %s, body = %s where invoice_status = %s"
                values = (tomails, record["subject"], record["body"], status)
                mycursor.execute(sqlQuery, values)

                mydb.commit()

    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure"),
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Updated Successfully!")
    }

# postRuleNotification
def postRuleNotification(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    # print(event) 
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
        "invoice_status": "",
        # "mail_to" : [],
        "mail_cc": [],
        "subject": "",
        "body": ""
    }

    for value in event["body-json"]:
        if value in record:
            record[value] = event["body-json"][value]
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
            
            tomails = None

            if record['mail_cc']:

                format_strings = ','.join(['%s'] * len(record['mail_cc']))

                mycursor.execute("select email from member "
                                 "where member_id in ({})".format(format_strings), tuple(record['mail_cc']))
                emails = mycursor.fetchall()
                
                if emails:
                    for index, each in enumerate(emails):
                        if index == 0:
                            tomails = str(each['email'])
                            continue

                        tomails += "," + str(each['email'])

            sqlQuery = "INSERT INTO rule_notification ( invoice_status, mail_cc, subject, body) values (%s, %s, %s, %s )"
            values = (record["invoice_status"], tomails, record["subject"], record["body"])

            mycursor.execute(sqlQuery, values)
            mydb.commit()

    except pymysql.err.IntegrityError as e:

        mydb.rollback()

        return {
            'statuscode': 500,
            'body': json.dumps("Notification Status already exists")
        }

    except:
        mydb.rollback()

        return {
            'statuscode': 500,
            'body': json.dumps("Invoice insertion failed!"),
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': record,
    }

# patchRuleStatus
def patchRuleStatus(event, context):
    print(event)
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
            
            if "rule_id" in event["params"]["querystring"] and "is_on" in event["params"]["querystring"]:
                rule_id = event["params"]["querystring"]["rule_id"]
                status = event["params"]["querystring"]["is_on"]
                
                sqlQuery = "update rule set is_on = %s where rule_id = %s"
                values = ( status, rule_id )
                mycursor.execute(sqlQuery, values)
                
                mydb.commit()

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
        'body': json.dumps("Successfully Updated!")
    }

# deleteRuleDetails
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

# getRuleDetails
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

# patchRuleDetails
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

# postRuleDetails
def postRuleDetails(event, context):
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

# getSearchDetails
def getSearchDetails(event, context):
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

    records = {}
    print(event)
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

            srch_field = []
            
            sqlQuery = "select s.operator, s.ui_element, s.search_id, s.is_multivalued, " \
            " s.help_required, d.value2 from serach_options s inner join" \
            " dropdown d on s.operator = d.value1 where s.search_field = %s and d.drop_key = 'operators'"
                
            values = (event["params"]["querystring"]["search_field"],)

            mycursor.execute(sqlQuery, values)
            data = mycursor.fetchall()
            
            for row in data:
                record = {
                    # 'search_field': row["search_field"],
                    'operator': row["operator"],
                    'operator_name' : row["value2"],
                    'ui_element': row["ui_element"],
                    'search_id': row["search_id"],
                    'is_multivalued': row["is_multivalued"],
                    'help_required': row["help_required"]
                }
                srch_field.append(record)

            records["srch_field"] = srch_field
            
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

# getTrackInvoices
def getTrackInvoices(event, context):
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
    
    records = {}
    print(event)
    try:
        # print(event)
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
            
            email = None
            edit = None
            
            values_pag = []
            
            if "pageno" in event["params"]["querystring"]:
                start_idx = int(event["params"]["querystring"]['pageno'])
                
            if "nooflines" in event["params"]["querystring"]:
                end_idx = int(event["params"]["querystring"]['nooflines'])
                        
                start_idx = (start_idx -1 ) * end_idx
                    
            email = event["params"]["querystring"]["userid"]
                
            if "edit" in event["params"]["querystring"]:
                edit  = event["params"]["querystring"]["edit"]
                
            if "invoice_no" in event["params"]["querystring"]:
                    
                invoiceNo = event["params"]["querystring"]["invoice_no"] 
                
                items = []
                invoice_files = []
                error_log = []
                record = []
                approvers = []
                audit_trails = []
                delegate_info = []
                
                values = (email,)
                mycursor.execute("select member_id, concat(fs_name, ' ', ls_name) as mem_name from member where email = %s", values)
                member = mycursor.fetchone()
                
                mycursor.execute("select file_id, name, mime_type, file_link from file_storage where file_id = %s", event["params"]["querystring"]["invoice_no"])
                for row in mycursor:
                    record = {
                        "invoice_id" : row["file_id"],
                        "file_name" : row["name"],
                        "mime_type" : row["mime_type"],
                        "file_link" : row["file_link"]
                    }
                    invoice_files.append(record)
                    
                mycursor.execute("select a.member_id, a.approved_date, concat(b.fs_name, ' ', b.ls_name) as app_name " \
                	"from approval_history a " \
                    "join member b " \
                    "on a.member_id = b.member_id " \
                    "where invoice_no = %s ",  event["params"]["querystring"]["invoice_no"] )
                        
                for row in mycursor:
                    record = {
                        "member_id": row["member_id"],
                        "approved_date": str(row["approved_date"]),
                        "member_name": row["app_name"]
                    }
                    approvers.append(record)
                
                mycursor.execute("select sr_no, invoice_no, convert_tz(entry_timestamp, '+00:00','+05:30' ) as entry_timestamp, prev_status, new_status, working_person, msg " \
                    "from invoice_audit where invoice_no = %s order by entry_timestamp desc, invoice_no", invoiceNo)
                invoice_audit = mycursor.fetchall()
                
                for row in invoice_audit:
                    record = {
                        "member_id": row["working_person"],
                        "date": str(row["entry_timestamp"]),
                        "msg": row["msg"]
                    }
                    audit_trails.append(record)
                    
                mycursor.execute("select * from sap_error_log where invoice_no = %s", event["params"]["querystring"]["invoice_no"])
                for row in mycursor:
                    err = {
                        "type": row["error_type"],
                        "msg": row["error_msg"]
                    }
                    error_log.append(err)
                
                values = (invoiceNo, )
                mycursor.execute("select m.member_id, concat(m.fs_name, ' ', m.ls_name) as member_name, d.refer_comment, d.accepted_comment, d.sr_no, d.delegated_to " \
                	"from member m " \
                    "inner join delegate d " \
                    "on m.member_id = d.delegated_from " \
                    "where d.is_refered = 'y' and d.invoice_id = %s order by entry_time", values)
                delegate_member = mycursor.fetchall()
                
                if delegate_member:
                    values = (invoiceNo, )
                    sqlQuery = "select member_id, concat(m.fs_name, ' ', m.ls_name) as mem_name from member m " \
                        "inner join delegate d on m.member_id = d.delegated_to where d.is_refered = 'y' and d.invoice_id = %s order by entry_time"
                    mycursor.execute(sqlQuery, values)
                    referred_member = mycursor.fetchall()
                    
                    for row in delegate_member:
                        for each in referred_member:
                            if str(row["delegated_to"] ) == str(each["member_id"]):
                                temp = {
                                    "sr_no": row["sr_no"],
                                    "refered_from_id": row["member_id"],
                                    "refered_from_name": row["member_name"],
                                    "refered_to_id": each["member_id"],
                                    "refered_to_name": each["mem_name"],
                                    "refer_comment": row["refer_comment"],
                                    "reply_comment": row["accepted_comment"]
                                }
                                delegate_info.append(temp)
                                break
                        
                values = (event["params"]["querystring"]["invoice_no"],)
                mycursor.execute("select a.*, b.vendor_name, c.value2 from invoice_header a left join vendor_master b " \
                    "on a.supplier_id = b.vendor_no left join dropdown c on a.document_type = c.value1 where invoice_no = %s", values)
                invoice_header = mycursor.fetchone()
                    
                if invoice_header:
                    
                    mycursor.execute("select department_name from departmental_budget_master where department_id = %s", (invoice_header["department_id"],))
                    department = mycursor.fetchone()
                    
                if department:
                    department_name = department["department_name"]
                else:
                    department_name = None
                    
                sqlQuery = "select country from default_master where company_code = (Select company_code from invoice_header where invoice_no = %s)"
                values = (invoiceNo)
                mycursor.execute(sqlQuery,values)
                country = mycursor.fetchone()
                
                sqlQuery = "Select jurisdiction_code from invoice_header where invoice_no = %s" #changed
                values = (invoiceNo)
                mycursor.execute(sqlQuery,values)
                jc = mycursor.fetchone()
                    
                records = {
                    "user_invoice_id": invoice_header["user_invoice_id"],
                    "invoice_no" :invoice_header["invoice_no"],
                    "in_status" : invoice_header["in_status"],
                    "from_supplier" : invoice_header["from_supplier"],
                    "sap_invoice_no" : invoice_header['sap_invoice_no'],
                    "ref_po_num" : invoice_header["ref_po_num"],
                    "company_code" : invoice_header["company_code"],
                    "invoice_date" : str(invoice_header["invoice_date"]),
                    "posting_date" : str(invoice_header["posting_date"]),
                    "baseline_date": str(invoice_header["baseline_date"]),
                    "amount" : invoice_header["amount"],
                    "currency" : invoice_header["currency"],
                    "payment_method" : invoice_header["payment_method"],
                    "payment_status" : invoice_header["payment_status"],
                    "transaction_no" : invoice_header["transaction_no"],
                    "gl_account" : invoice_header["gl_account"],
                    "business_area" : invoice_header["business_area"],
                    "supplier_id" : invoice_header["supplier_id"],
                    "supplier_name" : invoice_header["supplier_name"],
                    "approver_id" : invoice_header["approver_id"],
                    "approver_comments" : invoice_header["approver_comments"],
                    "modified_date" : str(invoice_header["modified_date"]),
                    "cost_center" : invoice_header["cost_center"],
                    "taxable_amount" : invoice_header["taxable_amount"],
                    "discount_per" : invoice_header["discount_per"],
                    "total_discount_amount" : invoice_header["total_discount_amount"],
                    "is_igst" : invoice_header["is_igst"],
                    "tax_per" : invoice_header["tax_per"],
                    "cgst_tot_amt": invoice_header["cgst_tot_amt"],
                    "sgst_tot_amt": invoice_header["sgst_tot_amt"],
    	            "igst_tot_amt": invoice_header["igst_tot_amt"],
                    "tds_per": invoice_header["tds_per"],
                    "tds_tot_amt": invoice_header["tds_tot_amt"],
                    "payment_terms" : invoice_header["payment_terms"],
                    "adjustment" : invoice_header["adjustment"],
                    "supplier_comments": invoice_header['supplier_comments'],
                    "tcs": invoice_header["tcs"],
                    "internal_order": invoice_header["internal_order"],
                    "department_id": invoice_header["department_id"],
                    "department_name": department_name,
                    "npo": invoice_header["npo"],
                    "document_type": invoice_header["value2"],
                    "gstin": invoice_header["gstin"],
                    "irn": invoice_header["irn"],
                    "items" : items,
                    "files" : invoice_files,
                    "error_log": error_log,
                    "approvers": approvers,
                    "audit_trails": audit_trails,
                    "refer_details": delegate_info,
                    "country" : country['country'],
                    "jurisdiction_code" : jc['jurisdiction_code'] #changed
                }
                    
                mycursor.execute("select * from invoice_item where invoice_no = %s", values)
                for row in mycursor:
                    record = {
                      "item_no":row["item_no"],
                      "material":row["material"],
                      "hsn_code": row["hsn_code"],
                      "material_desc":row["material_desc"],
                      "quantity":row["quantity"],
                      "unit":row["unit"],
                      "amount":row["amount"],
                      "currency": row["currency"],
                      "amt_per_unit" : row["amt_per_unit"],
                      "cgst_per": row["cgst_per"],
                      "cgst_amount":row["cgst_amount"],
                      "tax_code":row["tax_code"],
                      "ref_po_no":row["ref_po_no"],
                      "plant":row["plant"],
                      "discount":row["discount"],
                      "discount_amount" : row["discount_amount"],
                      "gross_amount" : row["gross_amount"],
                      "sgst_per": row["sgst_per"],
                      "sgst_amount": row["sgst_amount"],
                      "igst_per": row["igst_per"],
                      "igst_amount": row["igst_amount"],
                      "taxable_amount": row["taxable_amount"],
                      "tax_value_amount": row["tax_value_amount"],
                      "gl_account": row["gl_account"],
                      "gst_per": row["gst_per"],
                      "ocr_matched" : row["ocr_matched"],
                      "cost_center": row["cost_center"],
                      "qc_check": row["qc_check"]
                      }
                    items.append(record)
                        
                records["items"] = items
                
            elif "condn" in event["body-json"]:
                
                if "userid" in event["params"]["querystring"]:
                    email = event["params"]["querystring"]["userid"]
                    mycursor.execute("select user_type from member where email = %s", email)
                    role = mycursor.fetchone()
                
                val_list = []
                pos = 0
                condn = ""
                records = {}
                
                for row in event["body-json"]["condn"]:
                    if row["value"] == '':  #ch
                        row["value"] = row['searchField']
                    if pos != 0:
                        condn = condn + " and "
                    elif pos == 0:
                        pos = pos + 1
    
                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                        condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                    elif str(row["operator"]) == "between":
                        val_list.append(row["value"])
                        val_list.append(row["value2"])
                        condn = condn + " " + str(row["field"]) + " between %s and %s "
                    else:
                        val_list.append(row["value"])
                        condn = condn + str(row["field"]) + " " + str(row["operator"]) + " " + "%s"
                    
                if role["user_type"] == 'npoapp':
                    condn = condn + " and a.npo = 'y' "
                
                sqlQuery = "SELECT a.invoice_no, a.in_status, a.user_invoice_id, a.sap_invoice_no, a.invoice_date, a.posting_date, a.amount, a.supplier_name, a.approver_id, " \
                	"a.approver_comments, a.modified_date, a.supplier_comments, a.payment_status, a.gstin, c.fs_name, c.ls_name, d.vendor_name, e.value2 as document_type " \
                    "FROM invoice_header a " \
                    "left outer join member c on a.working_person = c.member_id " \
                    "left join vendor_master d " \
                    "on a.supplier_id = d.vendor_no " \
                    "left join dropdown e " \
                    "on a.document_type = e.value1 " \
                    "where (sup_status is null or sup_status <> 'draft')"
                               
                temp = condn #jurisdiction 
                if condn[:17] == 'jurisdiction_code' : #jurisdiction
                    condn = 'a.' + condn #jurisdiction
                               
                if condn:
                    sqlQuery = sqlQuery + " and " + condn 
                
                val_list.append(start_idx)
                val_list.append(end_idx)
                    
                sqlQuery = sqlQuery + " order by a.invoice_no desc limit %s,%s "
                
                values = tuple(val_list,)
                mycursor.execute(sqlQuery, values)
                    
                condn = temp #jurisdiction
                
                invoice_obj = mycursor.fetchall()
                
                val_list.pop()
                val_list.pop()
                
                sqlQuery = "select count(in_status) as invoice_count, in_status from invoice_header where (sup_status is null or sup_status <> 'draft') "
                if condn:
                    sqlQuery = sqlQuery + "  and " + condn + " group by in_status"
                else:
                    sqlQuery = sqlQuery + " group by in_status"
                    
                mycursor.execute(sqlQuery, tuple(val_list))
        
                countrec = {}
                total_count = 0
                
                for each in mycursor:
                    total_count = total_count + int(each["invoice_count"])
                    countrec[each['in_status']] = each['invoice_count']
                    
                if "" in countrec:
                    del countrec['']
                
                if None in countrec:
                    del countrec[None]
                    
                if "new" not in countrec:
                    countrec["new"] = 0
                        
                if "draft" not in countrec:
                    countrec["draft"] = 0
                    
                if "inapproval" not in countrec:
                    countrec["inapproval"] = 0
                        
                if "tosap" not in countrec:
                    countrec["tosap"] = 0
                        
                if "rejected" not in countrec:
                    countrec["rejected"] = 0
                    
                countrec['total_count'] = total_count
                        
                invoices = []
                invoice_files = []
                    
                res = [sub['invoice_no'] for sub in invoice_obj]
                    
                if res and len(res) > 1:
                    mycursor.execute("select file_id, name, mime_type, file_link from file_storage where " \
                        "file_id in {}".format(tuple(res))) 
                            
                elif res and len(res) == 1:
                    values = (res[0],)
                    mycursor.execute("select file_id, name, mime_type, file_link from file_storage where file_id = %s", values)
                        
                for row in mycursor:
                    record = {
                        "invoice_id" : row["file_id"],
                        "file_name" : row["name"],
                        "mime_type" : row["mime_type"],
                        "file_link" : row["file_link"]
                    }   
                    invoice_files.append(record)
                    
                approvers_list = []
                approver_final = []
                
                if res:
                    format_strings_in = ','.join(['%s'] * len(res))
    
                    sqlQuery = "select * from approval where referred_approver = 'n'and invoice_no in ({}) " \
                               "order by invoice_no desc, approval_level".format(format_strings_in)
                    mycursor.execute(sqlQuery, tuple(res))
                    approvers_list = mycursor.fetchall()
            
                    groupid = []
                    memberid = []
            
                    for row in approvers_list:
            
                        if row["isgroup"] == 'y':
                            groupid.append(row["approver"])
                        elif row["isgroup"] == 'n':
                            memberid.append(row["approver"])
            
                    format_strings_mem = ','.join(['%s'] * len(memberid))
            
                    approver_final = []
            
                    if groupid:
                        groupid = set(groupid)
                        groupid = list(groupid)
                        format_strings_grp = ','.join(['%s'] * len(groupid))
                        mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in ({})".format(format_strings_grp), tuple(groupid))
                        grp_det = mycursor.fetchall()
            
                        if grp_det:
                            for row in grp_det:
                                temp1 = {
                                    "isgroup": "y",
                                    "approver": row["group_id"],
                                    "name": row["name"],
                                    "approval_type": ""
                                }
                                approver_final.append(temp1)
            
                    if memberid:
            
                        memberid = set(memberid)
                        memberid = list(memberid)
            
                        format_strings_mem = ','.join(['%s'] * len(memberid))
            
                        sqlQuery = "select member_id, fs_name, ls_name from member " \
                                   "where member_id in (%s)" % format_strings_mem
                        mycursor.execute(sqlQuery, tuple(memberid))
            
                        mem_det = mycursor.fetchall()
            
                        if mem_det:
            
                            for row in mem_det:
            
                                if row["fs_name"] == None and row["ls_name"] == None:
                                    name = None
            
                                elif row["fs_name"] == None and row["ls_name"] != None:
                                    name = row["ls_name"]
            
                                elif row["fs_name"] != None and row["ls_name"] == None:
                                    name = row["fs_name"]
            
                                else:
                                    name = str(row["fs_name"]) + " " + str(row["ls_name"])
            
                                temp1 = {
                                    "isgroup": "n",
                                    "approver": row["member_id"],
                                    "name": str(name),
                                    "approval_type": ""
                                }
                                approver_final.append(temp1)
                    
                approval_type = []
                error_op = []
                
                for row in invoice_obj:
                    files = []
                    approvers = []
                    
                    for temp in approvers_list:
                        if temp['invoice_no'] == row["invoice_no"]:
                            for temp1 in approver_final:
                                if str(temp["approver"]) == str(temp1["approver"]) and str(temp["isgroup"]) == str(temp1["isgroup"]):
                                        
                                    if temp["isapproved"] == "y":
                                        status = "accepted"
                                    elif temp["isapproved"] == 'n':
                                        status = "inapproval" 
                                            
                                    status_ap = {
                                        "isgroup" : temp1["isgroup"],
                                        "approver" : temp1["approver"],
                                        "name": temp1["name"],
                                        "level" : temp['approval_level'],
                                        "approval_type": temp1["approval_type"],
                                        # "isapproved" : temp["isapproved"]
                                        "isapproved" : status
                                    }
                                    approvers.append(status_ap) 
                                    
                    for data in invoice_files:
                           
                        if row["invoice_no"] == data["invoice_id"]:
                            temp = {
                                "file_name" : data["file_name"],
                                "mime_type" : data["mime_type"],
                                "file_link" : data["file_link"]
                            }
                            files.append(temp)
                            # break
                            
                    approval_type = None
                    for each in approvers_list:
                        if each["invoice_no"] == row["invoice_no"]:
                            approval_type = each["approval_type"]
                            break
                        
                    if row["fs_name"] == None and row["ls_name"] == None:
                        name = None
                            
                    elif row["fs_name"] == None and row["ls_name"] != None:
                        name = row["ls_name"]
                        
                    elif row["fs_name"] != None and row["ls_name"] == None:
                        name = row["fs_name"]
                            
                    else:
                        name = str(row["fs_name"]) + " " + str(row["ls_name"])
                        
                    record = {
                      "invoice_no":row["invoice_no"],
                      "document_type": row["document_type"],
                      "gstin": row["gstin"],
                      "in_status":row["in_status"],
                      "user_invoice_id" : row['user_invoice_id'],
                    #   "working_person" : str(row["fs_name"]) + " " + str(row["ls_name"]),
                      "working_person" : str(name),
                      "sap_invoice_no" : row['sap_invoice_no'],
                      "invoice_date":str(row["invoice_date"]),
                      "posting_date":str(row["posting_date"]),
                      "amount":row["amount"],
                      "supplier_name":row["vendor_name"], 
                      "approver_id":row["approver_id"],
                      "approver_comments" : row["approver_comments"],
                      "modified_date" : str(row["modified_date"]),
                      "supplier_comments": row['supplier_comments'],
                      "payment_status" : str(row["payment_status"]),
                    #   "approver_name":str(row["fs_name"]) + " " + str(row["ls_name"]),
                      "approver_name":"",
                      "approvers": approvers,
                      "approval_type": approval_type,
                      "error_log": error_op,
                      "invoice_files" : files,
                      
                    }
                    invoices.append(record)
                        
                records["invoices"] = invoices
                records["count"] = countrec
            
            else:
                
                records = {}
                condn = " " 
                
                values_pag.append(start_idx)
                values_pag.append(end_idx)
                    
                
                if "userid" in event["params"]["querystring"]:
                    email = event["params"]["querystring"]["userid"]
                    mycursor.execute("select user_type from member where email = %s", email)
                    role = mycursor.fetchone()
                    
                    
                    if role["user_type"] == 'npoapp':
                        condn = " and a.npo = 'y' "
                    
                sqlQuery = "select a.invoice_no, a.in_status,a.sap_invoice_no, a.user_invoice_id," \
                    " a.from_supplier, a.ref_po_num, a.company_code, a.invoice_date, a.posting_date," \
                    " a.amount, a.currency, a.gl_account, a.business_area, a.supplier_id, a.npo," \
                    " a.approver_id, a.supplier_name, a.approver_comments, a.modified_date," \
                    " a.working_person,a.supplier_comments, a.payment_status, a.gstin, c.fs_name, c.ls_name, d.vendor_name, e.value2 as document_type" \
                    " FROM invoice_header a left outer join member c" \
                    " on a.working_person = c.member_id " \
                    " left join vendor_master d" \
                    " on a.supplier_id = d.vendor_no" \
                    " left join dropdown e " \
                    " on a.document_type = e.value1 " \
                    " where (sup_status is null or sup_status <> 'draft') " \
                    " " + condn + " order by a.invoice_no desc limit %s,%s"  
                    # " and date(a.entry_date) > date(now() - interval 60 day)" + condn + " order by a.invoice_no desc limit %s,%s"
                    
                mycursor.execute(sqlQuery, tuple(values_pag))
                # print(sqlQuery, values_pag)
                invoices_obj = mycursor.fetchall()
                
                invoices = []
                invoice_files = []
                    
                res = [sub['invoice_no'] for sub in invoices_obj]
                    
                groupid = []
                memberid = []
                error_log = []
                    
                if res:  
                    if len(res) == 1:
                        values = (res[0], )
                        mycursor.execute("select * from sap_error_log where invoice_no = %s order by invoice_no desc", values)
                        error_log = mycursor.fetchall()
                        
                    elif len(res) > 1:
                        mycursor.execute("select * from sap_error_log where invoice_no in {} order by invoice_no desc".format(tuple(res)))
                        error_log = mycursor.fetchall()
                    
                    if res:
                        format_strings = ','.join(['%s'] * len(res))
                        
                        sqlQuery = "select file_id, name, mime_type, file_link " \
                            "from file_storage " \
                            "where file_id in (%s) order by file_id desc" % format_strings
                        mycursor.execute(sqlQuery, tuple(res))
                        invoice_files = mycursor.fetchall()
                        
                    if len(res) == 1:
                        mycursor.execute("select concat(m.fs_name, ' ', m.ls_name) as approver_name, a.invoice_no " \
                          "from member m " \
                        	"inner join approval_history a " \
                        	"on m.member_id = a.member_id " \
                          "where a.invoice_no = %s " \
                          "order by a.invoice_no desc, a.approval_level desc ", res[0])
                        sap_approved = mycursor.fetchall()
                            
                    else:
                        mycursor.execute("select concat(m.fs_name, ' ', m.ls_name) as approver_name, a.invoice_no " \
                            "from member m " \
                            "inner join approval_history a " \
                            "on m.member_id = a.member_id " \
                            "where a.invoice_no in {} " \
                            "order by a.invoice_no desc, a.approval_level desc".format(tuple(res)))
                        sap_approved = mycursor.fetchall()
                
                approvers_list = []
                approver_final = []
                
                if res:
                    format_strings_in = ','.join(['%s'] * len(res))
    
                    sqlQuery = "select * from approval where referred_approver = 'n' and invoice_no in ({}) " \
                               "order by invoice_no desc, approval_level ".format(format_strings_in)
                    mycursor.execute(sqlQuery, tuple(res))
                    approvers_list = mycursor.fetchall()
            
                    groupid = []
                    memberid = []
            
                    for row in approvers_list:
                        if row["isgroup"] == 'y':
                            groupid.append(row["approver"])
                        elif row["isgroup"] == 'n':
                            memberid.append(row["approver"])
            
                    format_strings_mem = ','.join(['%s'] * len(memberid))
            
                    approver_final = []
            
                    if groupid:
                        groupid = set(groupid)
                        groupid = list(groupid)
                        format_strings_grp = ','.join(['%s'] * len(groupid))
                        
                        mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in ({})".format(format_strings_grp), tuple(groupid))
                        grp_det = mycursor.fetchall()
            
                        if grp_det:
                            for row in grp_det:
                                temp1 = {
                                    "isgroup": "y",
                                    "approver": row["group_id"],
                                    "name": row["name"],
                                    "approval_type": ""
                                }
                                approver_final.append(temp1)
            
                    if memberid:
            
                        memberid = set(memberid)
                        memberid = list(memberid)
            
                        format_strings_mem = ','.join(['%s'] * len(memberid))
            
                        sqlQuery = "select member_id, fs_name, ls_name from member where member_id in (%s)" % format_strings_mem
                        mycursor.execute(sqlQuery, tuple(memberid))
            
                        mem_det = mycursor.fetchall()
            
                        if mem_det:
            
                            for row in mem_det:
            
                                if row["fs_name"] == None and row["ls_name"] == None:
                                    name = None
            
                                elif row["fs_name"] == None and row["ls_name"] != None:
                                    name = row["ls_name"]
            
                                elif row["fs_name"] != None and row["ls_name"] == None:
                                    name = row["fs_name"]
            
                                else:
                                    name = str(row["fs_name"]) + " " + str(row["ls_name"])
            
                                temp1 = {
                                    "isgroup": "n",
                                    "approver": row["member_id"],
                                    "name": str(name),
                                    "approval_type": ""
                                }
                                approver_final.append(temp1)
                
                sap_app_name = "" 
                for row in invoices_obj:
                    approvers = []
                    files = []
                    error_op = []
                    
                    for errors in error_log:
                        if str(row["invoice_no"]) == str(errors["invoice_no"]):
                            err = {
                                "invoice_no" : errors["invoice_no"],
                                "type" : errors["error_type"],
                                "msg" : errors["error_msg"]
                            }
                            error_op.append(err)
                        
                    for data in invoice_files:
                        if str(row["invoice_no"]) == str(data["file_id"]):
                            temp = {
                                "file_name" : data["name"],
                                "mime_type" : data["mime_type"],
                                "file_link" : data["file_link"]
                            }
                            files.append(temp)
                        
                    for temp in approvers_list:
                        approval_type = None
                        
                        if row["invoice_no"] == temp["invoice_no"]: 
                            for temp1 in approver_final:
                                if str(temp["approver"]) == str(temp1["approver"]) and str(temp["isgroup"]) == str(temp1["isgroup"]):
                                        
                                    if temp["isapproved"] == "y":
                                        status = "accepted"
                                        
                                    elif temp["isapproved"] == 'n':
                                        status = "inapproval" 
                                            
                                    status_ap = {
                                        "isgroup" : temp1["isgroup"],
                                        "approver" : temp1["approver"],
                                        "name": temp1["name"],
                                        "level" : temp['approval_level'],
                                        "approval_type": temp1["approval_type"],
                                        "isapproved" : status
                                    }
                                    approvers.append(status_ap)
                                    
                    for app in sap_approved:
                         if row["invoice_no"] == app["invoice_no"]:
                             sap_app_name = app["approver_name"]
                             
                    if row["fs_name"] == None and row["ls_name"] == None:
                        name = None
                            
                    elif row["fs_name"] == None and row["ls_name"] != None:
                        name = row["ls_name"]
                        
                    elif row["fs_name"] != None and row["ls_name"] == None:
                        name = row["fs_name"]
                            
                    else:
                        name = str(row["fs_name"]) + " " + str(row["ls_name"])
                        
                    approval_type = None
                        
                    for each in approvers_list:
                        if each["invoice_no"] == row["invoice_no"]:
                            approval_type = each["approval_type"]
                            break
                        
                    if row["npo"] == 'y':
                        invoice_type = 'NPO'
                        
                    elif row["npo"] == None and row["ref_po_num"] == None:
                        invoice_type = 'None'
                        
                    elif row["ref_po_num"] != None:
                        invoice_type = 'PO'
                        
                    record = {
                        "invoice_no" :row["invoice_no"],
                        "document_type": row["document_type"],
                        "gstin": row["gstin"],
                        "in_status" : row["in_status"],
                        "invoice_type": invoice_type,
                        "user_invoice_id" : row['user_invoice_id'],
                        "sap_invoice_no" : row['sap_invoice_no'],
                        "invoice_date" : str(row["invoice_date"]),
                        "posting_date" : str(row["posting_date"]),
                        "amount" : row["amount"],
                        "supplier_id" : row["supplier_id"],
                        "supplier_name" : row["vendor_name"],
                        "approver_name": "",
                        "approver_name": sap_app_name,
                        "modified_date": str(row["modified_date"]),
                        "working_person": str(name),
                        "supplier_comments":row["supplier_comments"],
                        "payment_status": str(row["payment_status"]),
                        "approval_type": approval_type,
                        "invoice_files":files,
                        "approvers":approvers,
                        "error_log": error_op
                        }
                    invoices.append(record)
                    sap_app_name = "" 
                records["invoices"] = invoices
            
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

# getEinvoiceInitialData
def decode_jwt_token(Authorization):
    header1 =  jwt.decode(Authorization , options={"verify_signature": False})
    if 'email' in header1:
        return header1['email']
    else:
        return ''
def getEinvoiceInitialData(event, context):
    print(event)
    trace_off = ''
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

    record = {}

    try:
        
        # print(event)
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
            
            # atoken = ''
            # if 'Authorization' in event['params']['header'] :
            #     atoken =  event['params']['header']['Authorization']
            #     print(atoken)
                # em = decode_jwt_token(atoken)
                # mycursor.execute(" SELECT * FROM einvoice_db_portal.email where userid = %s" , em)
                # em1 = mycursor.fetchone()
                # if em1['flag'] != 'false':
                #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytraces", headers={"Content-Type":"application/json", "opetion":'off'}) 
  
            # mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ") 
            # flg = mycursor.fetchone()
            # if flg['value1'] == 'on':
            #     trace_off = 'off'
            #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken}) 
            #     if json.loads(a.text)['body'] == 'on':
            #         patch_all()
            #         print(event)
            #         print("me")
                    
            # on = mycursor.execute(" select value1 from elipo_setting where key_name = 'config_trace' ")
            # if on == 1:
            #     chk = enable_xray(event)
            #     if chk['Enable'] == True:
            #         patch_all()
            
            
            sqlQuery = "select a.user_type, b.name from " + dbScehma + ".member a left join " + dbScehma + ".group b on a.group_id = b.group_id where email = %s"
                
            mycursor.execute(sqlQuery,event["params"]["querystring"]["userid"])
            member = mycursor.fetchone()
                
            if member:
                if member["user_type"]:
                    mycursor.execute("select value2 from dropdown where drop_key = 'user_type' and value1 = %s", member["user_type"])
                    dropdown = mycursor.fetchone()
                        
                    mycursor.execute("select * from user_access_header where user_type = %s order by access_id", member["user_type"])
                    headertabs = mycursor.fetchall()
                        
                    mycursor.execute("select a.* " \
                        	"from user_access_item a " \
                            "inner join user_access_header b " \
                            "on a.access_id = b.access_id " \
                            "where b.user_type = %s " \
                            "order by a.access_id, sub_tab_id", member["user_type"])
                    itemTabs = mycursor.fetchall()
                        
                    tabAccess = []
                        
                    if headertabs:
                        for row in headertabs:
                            itemTabsList = []
                            
                            if itemTabs:
                                for each in itemTabs:
                                    if row["access_id"] == each["access_id"]:
                                        tempItem = {
                                            "access_id": each["access_id"],
                                            "sub_tab_id": each["sub_tab_id"],
                                            "subtab_name": each["subtab_name"],
                                            "subtab_desc": each["subtab_desc"]
                                        }
                                        itemTabsList.append(tempItem) 
                                        
                            temp = {
                                "access_id": row["access_id"],
                                "tab_name": row["tab_name"],
                                "tab_desc": row["tab_desc"],
                                "itemTabs": itemTabsList
                            }
                            
                            tabAccess.append(temp) 
                                
                        record = {
                            "user_type" : member["user_type"],
                            "user_description" : dropdown["value2"],
                            "group_name": member["name"],
                            "tab_access": tabAccess
                        }
                            
                else:
                    return {
                        'statuscode': 502,
                        'body': json.dumps("No Tabs Assigned"),
                    }
                    
            else:
                return {
                    'statuscode': 501,
                     'body': json.dumps("No Role Assigned"),
                }
        # xray_recorder.begin_subsegment(name="Test")
        # patch_all()
        # if trace_off == 'off':
        #     a = requests.post("https://4kaosyaovj.execute-api.eu-central-1.amazonaws.com/dev/enablexraytracesindividually", headers={"Content-Type":"application/json", "lambda":context.function_name , "api":event['context']['api-id'] ,"Authorization":atoken , "switch":'off'})
        # xray_recorder.end_subsegment()
        
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure"),
        }
            
    finally:
        mydb.close()
        
    return {
        'statuscode': 200,
        'body': record
    }

# getUserRoleTabs
def getUserRoleTabs(event, context):
    print(event)
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    secret = event["stage-variables"]["secreat"]
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
            
            if "user_type" in event["params"]["querystring"]:
                userType = event["params"]["querystring"]["user_type"]
                
                mycursor.execute("select * from user_access_header where user_type = %s order by access_id", userType)
                headertabs = mycursor.fetchall()
                    
                mycursor.execute("select a.* " \
                	"from user_access_item a " \
                    "inner join user_access_header b " \
                    "on a.access_id = b.access_id " \
                    "where b.user_type = %s " \
                    "order by a.access_id, sub_tab_id", userType)
                itemTabs = mycursor.fetchall()
                    
                tabAccess = []
                
                if headertabs:
                    for row in headertabs:
                        itemTabsList = []
                        
                        if itemTabs:
                            for each in itemTabs:
                                if row["access_id"] == each["access_id"]:
                                    tempItem = {
                                        "access_id": each["access_id"],
                                        "sub_tab_id": each["sub_tab_id"],
                                        "subtab_name": each["subtab_name"],
                                        "subtab_desc": each["subtab_desc"]
                                    }
                                    itemTabsList.append(tempItem) 
                                
                        temp = {
                            "access_id": row["access_id"],
                            "tab_name": row["tab_name"],
                            "tab_desc": row["tab_desc"],
                            "itemTabs": itemTabsList
                        }
                        
                        tabAccess.append(temp) 
                    
            mydb.commit()      

    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Interal Error!")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': tabAccess
    }

# userAuthentication
def userAuthentication(event, context):
    print(event)
    
    atoken = ''
    enable = False
    if 'Authorization' in event['params']['header']:
        atoken = event['params']['header']['Authorization']
   
    try:
            
        if event["params"]["querystring"]["userid"] == decode_jwt_token(atoken) :
            enable= True

    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Failure123")   
        }  
            
    return {
        'statusCode': 200,
       'body': {'Enable' : enable}
    }

# patchMemberRole
def get_stored_credentials(user_id):
    
    global ocr_bucket_folder  
    
    try:
        s3 = boto3.client("s3")
        encoded_file = s3.get_object(Bucket=elipo_bucket, Key=ocr_bucket_folder+user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
        
    except Exception as excep:
        creds = None
        
def create_message(sender, to, cc, subject, message_text):
 
    message = email.mime.text.MIMEText(message_text, 'html')
    message['to'] = to
    message['cc'] = cc
    message['from'] = sender
    message['subject'] = subject
    encoded = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {'raw': encoded.decode("utf-8")}

def send_message(service, user_id, message):
    try:  
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return message
    except Exception as error:
        print("An error occurred: ", error)

def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)  

def sendMailNotifications(user, role, mycursor):
    
    # user_id = elipo_cred
    mycursor.execute("select * from elipo_setting where key_name = 'notification-mail' ")
    email_data = mycursor.fetchone()
    user_id = email_data["value1"]
    
    mail_cc = ''
    mail_subject = 'ELIPO Notification'
    mail_body = ''
    
    mail_body = '''<html>
            <body  >
        <div style=" max-width: 500px; margin: auto; padding: 10px; ">
                <div style=" width:100%; align-content: center;text-align: center;">
                    <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/ELIPO+logo.png" alt="Italian Trulli" style="vertical-align:middle; width: 140px;height:50px;text-align: center;"  >
                </div>
        	<div style=" width:100%; align-content:left;text-align:left;">
                    <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                </div>
                <b>
                    <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Hello {},
                    </span> 
                <div style=" width:100%; align-content: center;text-align: center;margin-top: 10px;">   
                    <span style="vertical-align: middle; align-content: center; font: 500 16px/23px Open Sans;letter-spacing: 0px;color:#000000;white-space: nowrap;opacity: 1;" >
                         Welcome to ELIPO
                    </span>
                    
                </div>
        
            <br>
            <div style=" max-width:800px; min-width: 100px;  text-align: center ; margin-top: 10px; font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;opacity: 1;">
                You have successfully assigned the role of {} to ELIPO. You can login to ELIPO by clicking on the below link.
            </div>
            <br>
            <div style=" width:100%;align-content: center;text-align: center;">
                <a href="https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/production/login" target="_blank">
                    <button style="border: none;box-shadow: 1px 1px 5px 1px #5a9e9b; background:rgb(80, 219, 212) 0% 0% no-repeat padding-box; border-radius: 7px;opacity: 1;width:180px; height: 35px;outline: none;border: none;" > 
                        <span style="vertical-align: middle; text-align: left;font: 600 bold 16px/23px Open Sans;letter-spacing: 0px;color: whitesmoke;white-space: nowrap;opacity: 1;">Login to ELIPO</span>
                    </button>
                </a>
            </div>
        
            <br><br>
            <div style="width:100%;">
                <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Happy Invoicing!</span>
            <br>
            <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Regards,</span>
            <br>
            <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Team ELIPO</span>
            </div>
        <div style=" width:100%; align-content:left;text-align:left;">
                    <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                </div>
        
            
            <div style="width:100%;align-content: center;text-align: center;">
                <span style=" text-align: center;font: 600 bold 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 0.7;">This message was sent to you by ELIPO</span>
            </div>
            <div style="width:100%;align-content: center;text-align: center;">
                <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/elipo+logo_2.png" alt="Italian Trulli" style="text-align: center;width: 80px;height: 30px;" >
            </div>
            
            <br>
        </div>
            </body></html>'''.format(user['mem_name'], role['value2'])

    credentials = get_stored_credentials(user_id)

    if credentials and credentials.refresh_token is not None:
        service = build_service(credentials=credentials)  
        message = create_message(sender=user_id, to=str(user['email']), cc=mail_cc, subject=mail_subject, message_text=mail_body)
        send_message(service=service, user_id="me", message=message)  


def patchMemberRole(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    # global elipo_cred
    # elipo_cred = event["stage-variables"]["notification_email"] 
    
    global elipo_bucket
    elipo_bucket = event["stage-variables"]["cred_bucket"]
    
    global ocr_bucket_folder
    ocr_bucket_folder = event["stage-variables"]["ocr_bucket_folder"]
    
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

            member_id = event["params"]["querystring"]["userid"]
            role = event["params"]["querystring"]["role"]
            
            if "vendor_no" in event["params"]["querystring"]:
                vendor_no = event["params"]["querystring"]["vendor_no"]
                
                mycursor.execute("select * from vendor_master where member_id = %s", member_id)
                vendorDetail = mycursor.fetchone()
                
                if vendorDetail:
                    msg = "Member already exists for Vendor " + str(vendorDetail["vendor_name"])
                    return {
                        'statuscode': 201,
                        'body': json.dumps(msg)
                    }
                    
                else:
                    values = (member_id, vendor_no)
                    mycursor.execute("UPDATE vendor_master SET member_id = %s WHERE vendor_no = %s", values)
            
            if "department_id" in event["params"]["querystring"]:
                department_id = event["params"]["querystring"]["department_id"]
                
            else:
                department_id = ""  
                
            values = (role, department_id, member_id)
            mycursor.execute("UPDATE member SET group_id = '', user_type = %s, department_id = %s WHERE member_id = %s", values)
            
            values = (member_id,)
            mycursor.execute("select concat(fs_name , ' ', ls_name) as mem_name, email from member where member_id = %s", values)
            member = mycursor.fetchone()
            
            values = (role,)
            mycursor.execute("select * from dropdown where drop_key = 'user_type' and value1 = %s", values)
            newrole = mycursor.fetchone()
            
            mydb.commit()
   
            if member:
                sendMailNotifications(user=member, role=newrole, mycursor=mycursor )
            
    except:  
        return {
            'statuscode': 500,
            'body': json.dumps("Internal Error")
        }
        
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Role Updated")
    }

# getGSTinVerification not tested
def getGSTinVerification(event=None, context=None):
    global dbScehma 
    dbScehma = ' DBADMIN '

    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    
    # secret = event["stage-variables"]["secreat"]
    
    vendor_gst = event["params"]["querystring"]['gstin']

    # resp = client.get_secret_value(
    #     SecretId=secret
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
            on = convertValuesTodict(mycursor.description, on)
            on = on[0]
            if on['value1'] == 'on':
                chk = enable_xray(event)
                if chk['Enable'] == True:
                    patch_all() 
                    print(event)

            mycursor.execute("SELECT * FROM   elipo_setting where key_name = 'master_gst_details'")
            mastergst = mycursor.fetchall()

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

                responce = requests.get(url=base_url+'/einvoice/authenticate',
                                        params=params,
                                        headers=headers)

                if responce:
                    responce = responce.json()

                    if responce['status_cd'] == 'Sucess':

                        auth_token = responce['data']['AuthToken']

                        params = {
                            'email': mastergst['email'],
                            # 'param1': '29AAAFW9177C1ZU'
                            'param1': vendor_gst
                        }
                        headers = {
                            'username': mastergst['username'],
                            'auth-token': auth_token,
                            'ip_address': mastergst['ip_address'],
                            'client_id': mastergst['client_id'],
                            'client_secret': mastergst['client_secret'],
                            'gstin': mastergst['gstin']
                        }

                        responce = requests.get(url=base_url + '/einvoice/type/GSTNDETAILS/version/V1_03',
                                                params=params,
                                                headers=headers)

                        if responce:

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
                                        'body': json.dumps('Requested data is not available')
                                    }

                            elif responce.status_code == 404:
                                return {
                                    'statuscode': 404,
                                    'body': json.dumps("Not Found.")
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
            'body': json.dumps('Internal server error')
        }

    finally:
        mydb.close()

# ================================= MUMBAI REGION =====================================
# getDepartmentBudget
def getDepartmentBudget(event, context):
    print(event)
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

    records = {}

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

            
            if "department_id" in event["params"]["querystring"]:
                department_id = event["params"]["querystring"]["department_id"]
                
                if "budget" in event["params"]["querystring"] and event["params"]["querystring"]["budget"] == 'X':
                    sqlQuery = "select sum(a.amount) as total_amount, b.budget, " \
                        "sum(case when in_status = 'tosap' then amount else 0 end) as consumed_amount, " \
                        "sum(case when in_status = 'inapproval' then amount else 0 end) as committed_amount " \
                    	"from invoice_header a " \
                        "join departmental_budget_master b " \
                        "on a.department_id = b.department_id " \
                    	"where a.npo = 'y' and ( a.in_status = 'inapproval' or a.in_status = 'tosap' ) and a.department_id = %s"
                    values = (department_id,)
                    mycursor.execute(sqlQuery, values)
                    data = mycursor.fetchone()
                    
                    if data: 
                        if data["consumed_amount"] == None:
                            data["consumed_amount"] = 0
                        
                        if data["committed_amount"] == None:
                            data["committed_amount"] = 0
                            
                        if data["consumed_amount"] == None:
                            data["consumed_amount"] = 0
                            
                        records = {
                            "available": data["budget"] - data["consumed_amount"],
                            "committed": data["committed_amount"],
                            "consumed": data["consumed_amount"]
                        }
                    
                else:
                    now = datetime.date.today()
                    limit_flag = None
                    warning_flag = None
                    condn = ""
                    msg = None
                    
                    mycursor.execute("select * from departmental_budget_master where department_id = %s", department_id)
                    departmental_budget = mycursor.fetchone()
                    
                    if departmental_budget:
                        if departmental_budget["valid_from"] != None and departmental_budget["valid_to"] != None:
                            sqlQuery = "select sum(amount) as total_amount from invoice_header " \
                                "where npo = 'y' and ( in_status = 'inapproval' or in_status = 'tosap' ) and department_id = %s and date(entry_date) between %s and %s "
                            values = ( department_id, departmental_budget["valid_from"], departmental_budget["valid_to"] )
                        
                        else: 
                            msg = "Budget not defined for current date."
                            
                            sqlQuery = "select sum(amount) as total_amount from invoice_header " \
                                "where npo = 'y' and ( in_status = 'inapproval' or in_status = 'tosap' ) and department_id = %s "
                            values = ( department_id, )
                            
                        mycursor.execute(sqlQuery, values)
                        invoice = mycursor.fetchone()
                        
                        usable_amount_warning = ( departmental_budget["warning_per"] * departmental_budget["budget"] ) / 100
                        
                        usable_amount_limit = ( departmental_budget["limit_per"] * departmental_budget["budget"] ) / 100
                        
                        if invoice["total_amount"] != None:
                            
                            if invoice["total_amount"] >= usable_amount_limit and departmental_budget["limit_per"] != 999:
                                if msg == None:
                                    msg = "Budget value limit crossed!"
                                limit_flag = 'y'
                            
                            else:
                                limit_flag = 'n'
                        
                            if invoice["total_amount"] >= usable_amount_warning :  #or departmental_budget["limit_per"] == 999
                                warning_flag = 'y'
                                
                                if msg == None:
                                    msg = "Budget value warning crossed!"
                                
                            else:
                                warning_flag = 'n'
                                
                        else:
                            if departmental_budget["budget"] != 0:
                                limit_flag = 'n'
                                warning_flag = 'n'
                                
                            else:
                                limit_flag = 'y'
                                warning_flag = 'y'
                                msg = "No budget defined for the Department"
                                
                    records = {
                        "limit_flag": limit_flag,
                        "warning_flag": warning_flag,
                        "msg": msg
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
        'body': records
    }

# getDuplicatePO
def getDuplicatePO(event, context):
    
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
            po_number = event['params']['querystring']['ref_po_num']
            invoice_no = None

            if 'invoice_no' in event['params']['querystring']:
                invoice_no = event['params']['querystring']['invoice_no']

            if invoice_no:
                values = (po_number,)
                mycursor.execute("SELECT * FROM einvoice_db_portal.invoice_header where ref_po_num = %s", values)
                duplicate = mycursor.fetchone()
                
                if duplicate:
                    
                    if duplicate['invoice_no'] == int(invoice_no):
                        pass
                    else:
                        return {
                            'statuscode': 200,
                            'body': json.dumps('Duplicate Reference PO')
                        }
            else:
                values = (po_number,)
                mycursor.execute("SELECT * FROM einvoice_db_portal.invoice_header where ref_po_num = %s", values)
                duplicate = mycursor.fetchone()

                if duplicate:
                    return {
                        'statuscode': 200,
                        'body': json.dumps('Duplicate Reference PO')
                    }
    except:
        return {
            'statuscode': 500,
            'body': json.dumps('Internal Failure')
        }

    finally:
        mydb.close()

    return {
        'statuscode': 201,
        'body': json.dumps('Ucan use PO')
    }

# deleteInvoice
def deleteInvoice(event, context):
    
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
    
    msg = "Delete unsuccessful!"
    
    try:
        with mydb.cursor() as mycursor:
            invoice_no = event["params"]["querystring"]['invoice_no']
            userid = event["params"]["querystring"]['userid']
            
            if "invoice_no" in event["params"]["querystring"] and "userid" in event["params"]["querystring"] and "sup_invoice" in event["params"]["querystring"]:
                values = (invoice_no, )
                
                sqlQuery = "DELETE FROM einvoice_db_portal.invoice_header WHERE invoice_no = %s"
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = "DELETE FROM einvoice_db_portal.invoice_item WHERE invoice_no = %s"
                mycursor.execute(sqlQuery, values)
            
            elif "invoice_no" in event["params"]["querystring"] and "userid" in event["params"]["querystring"]:
                
                values = ( userid, )
                sqlQuery = "select concat(fs_name, ' ', ls_name) as member_name, member_id FROM einvoice_db_portal.member WHERE email = %s"
                mycursor.execute(sqlQuery, values)
                working_person = mycursor.fetchone()
                
                values = (invoice_no, )
                sqlQuery = "DELETE FROM einvoice_db_portal.assignment WHERE invoice_no = %s"
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = "update einvoice_db_portal.invoice_header set in_status = 'deleted' where invoice_no = %s"
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = "insert into einvoice_db_portal.invoice_audit (invoice_no, prev_status, new_status, working_person, msg) values (%s, %s, %s, %s, %s)"
                msg_cmnt = "Invoice No " + str(invoice_no) + " deleted by " + working_person["member_name"] 
                values = (invoice_no, "", "deleted", working_person['member_id'], msg_cmnt)
                mycursor.execute(sqlQuery, values)
                        
            msg = "Invoice no. " + event["params"]["querystring"]["invoice_no"] + " deleted"   
            mydb.commit()
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps('Internal Error')
        }
            
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps(msg)
    }

#  checkInvoiceAndVendor
def checkInvoiceAndVendor(event, context):
    
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

    body = ""

    try:
        with mydb.cursor() as mycursor:
            
            invoice_no = None
            record = None
            
            if "invoice_no" in event["params"]["querystring"]:
                invoice_no = event["params"]["querystring"]["invoice_no"]
                
            user_invoice_no = event["params"]["querystring"]["invoice_id"]
            vendor_no = event["params"]["querystring"]["vendor_no"]
               
            sqlQuery = "select invoice_no from einvoice_db_portal.invoice_header where user_invoice_id = %s and supplier_id = %s"
            values = ( user_invoice_no, vendor_no )
            mycursor.execute(sqlQuery, values)
            record = mycursor.fetchone()
            
            if record: 
                if "invoice_no" in event["params"]["querystring"]:
                    if int(record["invoice_no"]) == int(invoice_no):
                        body = 'n'
                    else:
                        body = 'y'
                else:
                    body = 'y'
            else: 
                body = 'n'
                
                            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': body
    }

# getSearchedInvoiceSup
def getSearchedInvoiceSup(event, context):
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
    
    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            email = None
            edit = None
            values_pag = []
            
            if "pageno" in event["params"]["querystring"]:
                start_idx = int(event["params"]["querystring"]['pageno'])
            
            if "nooflines" in event["params"]["querystring"]:
                end_idx = int(event["params"]["querystring"]['nooflines'])
            
                start_idx = (start_idx -1 ) * end_idx
            
            if "tabname" in event["params"]["querystring"]:
                tabname = event["params"]["querystring"]['tabname']
            
            if "userid" in event["params"]["querystring"]:
                email = event["params"]["querystring"]["userid"]
                
            if "edit" in event["params"]["querystring"]:
                edit  = event["params"]["querystring"]["edit"]
            
            if "invoice_no" in event["params"]["querystring"]:
                invoiceNo = event["params"]["querystring"]["invoice_no"] 
                
                if edit:
                    values = (invoiceNo,)
                    mycursor.execute("select * from invoice_log where invoice_no = %s", values)
                    invoice_log = mycursor.fetchone()
                    
                    if invoice_log:
                        values = (invoice_log["member_id"],)
                        mycursor.execute("select fs_name, ls_name, email from member where member_id = %s", invoice_log["member_id"])
                        member = mycursor.fetchone()
                        
                        if member['email'] != email:
                            msg = "Invoice is locked by " + str(member["fs_name"]) + " " + str(member["ls_name"])
                            
                            return {
                                'statuscode': 204,
                                'body': json.dumps(msg)
                            }
                    else:
                        if email:
                            values = (email,)
                            mycursor.execute("select member_id from member where email = %s", values)
                            member = mycursor.fetchone()
                            
                            if member:
                                values = ( invoiceNo, member["member_id"] )
                                mycursor.execute("insert into invoice_log (invoice_no, member_id) values (%s, %s)", values)
                                mydb.commit()
                
                items = []
                invoice_files = []
                
                mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id = %s", invoiceNo)
                for row in mycursor:
                    record = {
                        'attach_id': row['attach_id'],    
                        "invoice_id" : row["file_id"],
                        "file_name" : row["name"],
                        "mime_type" : row["mime_type"],
                        "file_link" : row["file_link"]
                    }
                    invoice_files.append(record)
                
                values = (event["params"]["querystring"]["invoice_no"],)
                mycursor.execute("select a.*, b.value2 from invoice_header a inner join dropdown b on a.document_type = b.value1 " \
                    "where invoice_no = %s and from_supplier = 'y'", values)
                invoice_header = mycursor.fetchone()
                
                if invoice_header:
                    records = {
                        "user_invoice_id": invoice_header["user_invoice_id"],
                        "invoice_no" :invoice_header["invoice_no"],
                        "in_status" : invoice_header["sup_status"],
                        "ref_po_num" : invoice_header["ref_po_num"],
                        "company_code" : invoice_header["company_code"],
                        "payment_method" : invoice_header["payment_method"],
                        "invoice_date" : str(invoice_header["invoice_date"]),
                        "baseline_date" : str(invoice_header["baseline_date"]),
                        "amount" : invoice_header["amount"],
                        "currency" : invoice_header["currency"],
                        "gl_account" : invoice_header["gl_account"],
                        "business_area" : invoice_header["business_area"],
                        "supplier_id" : invoice_header["supplier_id"],
                        "supplier_name" : invoice_header["supplier_name"],
                        "supplier_comments": invoice_header['supplier_comments'],
                        "taxable_amount" : invoice_header["taxable_amount"],
                        "discount_per" : invoice_header["discount_per"],
                        "total_discount_amount" : invoice_header["total_discount_amount"],
                        "is_igst" : invoice_header["is_igst"],
                        "tax_per" : invoice_header["tax_per"],
                        "cgst_tot_amt": invoice_header["cgst_tot_amt"],
                        "sgst_tot_amt": invoice_header["sgst_tot_amt"],
	                    "igst_tot_amt": invoice_header["igst_tot_amt"],
                        "tds_per": invoice_header["tds_per"],
                        "tds_tot_amt": invoice_header["tds_tot_amt"],
                        "payment_terms" :invoice_header["payment_terms"],
                        "adjustment" : invoice_header["adjustment"],
                        "tcs" : invoice_header["tcs"],
                        "npo": invoice_header["npo"],
                        "document_type": invoice_header["document_type"],
                        "doc_type_desc": invoice_header["value2"],
                        "gstin": invoice_header["gstin"],
                        "irn": invoice_header["irn"],
                        'invoice_files' : invoice_files,
                        "items" : items
                    }
                
                    mycursor.execute("select * from invoice_item where invoice_no = %s", values)
                    
                    for row in mycursor:
                        record = {
                            "item_no":row["item_no"],
                            "hsn_code": row["hsn_code"],
                            "material":row["material"],
                            "material_desc":row["material_desc"],
                            "quantity":row["quantity"],
                            "unit":row["unit"],
                            "amount":row["amount"],
                            "currency": row["currency"],
                            "amt_per_unit" : row["amt_per_unit"],
                            "cgst_per": row["cgst_per"],
                            "cgst_amount":row["cgst_amount"],
                            "tax_code":row["tax_code"],
                            "ref_po_no":row["ref_po_no"],
                            "plant":row["plant"],
                            "discount":row["discount"],
                            "discount_amount" : row["discount_amount"],
                            "gross_amount" : row["gross_amount"],
                            "sgst_per": row["sgst_per"],
                            "sgst_amount": row["sgst_amount"],
                            "igst_per": row["igst_per"],
                            "igst_amount": row["igst_amount"],
                            "taxable_amount": row["taxable_amount"],
                            "tax_value_amount": row["tax_value_amount"],
                            "gst_per": row["gst_per"]
                        }
                        items.append(record)
                        
                    records["items"] = items
            
            elif "condn" in event["body-json"]:
            
                val_list = []
                pos = 0
                condn = ""
                records = {}
                
                val_list.append(tabname)
    
                for row in event["body-json"]["condn"]:
                    if pos != 0:
                        condn = condn + " and "
                    elif pos == 0:
                        pos = pos + 1
    
                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                        condn = condn + row["field"] + " " + str(row["operator"]) + " " + "%s"
                    elif str(row["operator"]) == "between":
                        val_list.append(row["value"])
                        val_list.append(row["value2"])
                        condn = condn + " " + str(row["field"]) + " between %s and %s"
                    else:
                        val_list.append(row["value"])
                        condn = condn + row["field"] + " " + str(row["operator"]) + " " + "%s"
    
                sqlQuery = "SELECT a.invoice_no, a.sup_status, a.user_invoice_id, a.invoice_date, a.approver_comments, a.amount, a.document_type, a.gstin, b.value2 " \
                           "FROM invoice_header a inner join dropdown b on a.document_type = b.value1 where sup_status = %s and from_supplier = 'y' "
                           
                if condn:
                    sqlQuery = sqlQuery + " and " + condn + " order by invoice_no desc limit %s, %s"
                else:
                    sqlQuery = sqlQuery + " order by invoice_no desc limit %s, %s"
                    
                val_list.append(start_idx)
                val_list.append(end_idx)
    
                values = tuple(val_list,)
    
                mycursor.execute(sqlQuery, values)
                invoice_obj = mycursor.fetchall()
                
                del val_list[0]
                val_list.pop()
                val_list.pop()
                
                sqlQuery = "select count(sup_status) as invoice_count, sup_status from invoice_header where from_supplier = 'y' "
                if condn:
                    sqlQuery = sqlQuery + " and " + condn + " group by sup_status"
                else:
                    sqlQuery = sqlQuery + " group by sup_status"
                
                mycursor.execute(sqlQuery, tuple(val_list))
        
                countrec = {}
                total_count = 0
                
                for each in mycursor:
                    total_count = total_count + int(each["invoice_count"])
                    countrec[each['sup_status']] = each['invoice_count']
                    
                if "" in countrec:
                    del countrec['']
                
                if None in countrec:
                    del countrec[None]
                        
                if "draft" not in countrec:
                    countrec["draft"] = 0
                        
                if "inapproval" not in countrec:
                    countrec["inapproval"] = 0
                        
                if "approved" not in countrec:
                    countrec["approved"] = 0
                        
                if "rejected" not in countrec:
                    countrec["rejected"] = 0
                        
                countrec["total_count"] = total_count
                invoices = []
                invoice_files = []
                
                res = [sub['invoice_no'] for sub in invoice_obj]
                
                if res and len(res) > 1:
                    mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id in {}".format(tuple(res))) 
                            
                elif res and len(res) == 1:
                    values = (res[0],)
                    mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id = %s", values)
                        
                for row in mycursor:
                    record = {
                        'attach_id': row['attach_id'],
                        "invoice_id" : row["file_id"],
                        "file_name" : row["name"],
                        "mime_type" : row["mime_type"],
                        "file_link" : row["file_link"]
                    }
                    invoice_files.append(record)
                
                for row in invoice_obj:
                    files = []
                    
                    for data in invoice_files:
                        if str(row["invoice_no"]) == str(data["invoice_id"]):
                            temp = {
                                "file_name" : data["file_name"],
                                "mime_type" : data["mime_type"],
                                "file_link" : data["file_link"]
                            }
                            files.append(temp)
                            
                    record = {
                      "invoice_no":row["invoice_no"],
                      "in_status": row["sup_status"],
                      "user_invoice_id": row["user_invoice_id"],   
                      "invoice_date":str(row["invoice_date"]),
                      "approver_comments" : row["approver_comments"],
                      "total_amount": row["amount"],
                      "document_type": row["document_type"],
                      "doc_type_desc": row["value2"],
                      "gstin": row["gstin"],
                      'invoice_files' : files
                    }
                    invoices.append(record)
                    
                records["invoices"] = invoices
                records["count"] = countrec
                
            else:
                records = {}
                invoices = []
                invoice_files = []
                
                if "tabname" in event["params"]["querystring"]:
                    values_pag.append(tabname)
                    values_pag.append(start_idx)
                    values_pag.append(end_idx)
                    
                    sqlQuery = "SELECT a.invoice_no, a.user_invoice_id, a.amount, a.sup_status, a.user_invoice_id, a.invoice_date, a.approver_comments, a.document_type, a.gstin, b.value2 " \
                        "FROM invoice_header a inner join dropdown b on a.document_type = b.value1 " \
                        "where sup_status = %s and from_supplier = 'y' order by invoice_no desc limit %s, %s"
                    mycursor.execute(sqlQuery, tuple(values_pag))
                    invoices_obj = mycursor.fetchall()   
                    
                else:
                    values_pag.append(start_idx)
                    values_pag.append(end_idx)
                
                    mycursor.execute("SELECT invoice_no, user_invoice_id, amount, sup_status, user_invoice_id, invoice_date, approver_comments " \
                        "FROM invoice_header where from_supplier = 'y' order by invoice_no desc limit %s,%s", tuple(values_pag))
                    invoices_obj = mycursor.fetchall()
                
                res = [sub['invoice_no'] for sub in invoices_obj]
                
                if res and len(res) == 1:
                    mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id = %s order by file_id", res[0])
                    file = mycursor.fetchall()
                    for row in file:
                        record = {
                            'attach_id': row['attach_id'], 
                            "invoice_id" : row["file_id"], 
                            "file_name" : row["name"],
                            "mime_type" : row["mime_type"],
                            "file_link" : row["file_link"]
                        }
                        invoice_files.append(record)
                    
                elif res and len(res) > 1:
                    mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id in {} order by file_id".format(tuple(res))) 
                    file = mycursor.fetchall()
                    for row in file:
                        record = {
                            'attach_id': row['attach_id'], 
                            "invoice_id" : row["file_id"], 
                            "file_name" : row["name"],
                            "mime_type" : row["mime_type"],
                            "file_link" : row["file_link"]
                        }
                        invoice_files.append(record)
                
                if invoices_obj:
                    for row in invoices_obj:
                        files = []
                        
                        for data in invoice_files:
                            if str(row["invoice_no"]) == str(data["invoice_id"]):
                                temp = {
                                    "file_name" : data["file_name"],
                                    "mime_type" : data["mime_type"],
                                    "file_link" : data["file_link"]
                                }
                                files.append(temp)
                        
                        record = {
                          "invoice_no":row["invoice_no"],
                          "user_invoice_id": row["user_invoice_id"],
                          "in_status": row["sup_status"],
                          "total_amount": row["amount"],
                          "user_invoice_id": row["user_invoice_id"],
                          "invoice_date":str(row["invoice_date"]),
                          "approver_comments" : row["approver_comments"],
                          "document_type": row["document_type"],
                          "doc_type_desc": row["value2"],
                          "gstin": row["gstin"],
                          'invoice_files' : files
                        }
                        invoices.append(record)
                records["invoices"] = invoices
                
    except:
        return {
        'statuscode': 500,
        'body': json.dumps("Internal Error")
    }
            
    finally:
        mydb.close()
        
    return {
        'statuscode': 200,
        'body': records
    }

# einvoice_fetch_mail_attachments
class FailedToUpload(Exception):
    pass

def get_stored_credentials(user_id):
    
    s3 = boto3.client("s3")
    # bucket_name = "file-bucket-emp"
    # bucket_name = event["stage-variables"]["bucket_gmail_credential"]
    
    try:
        encoded_file = s3.get_object(Bucket=cred_bucket_name, Key=user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
        
    except Exception as excep:
        creds = None
        # print(excep)
        return creds
      
      
def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)
    

def fetch_attachments(service, user_id, msg_id, mail, attachmentIds = None, filename = None , mydb = None):
    
    s3 = boto3.client("s3")  
    
    try:
        try :
            with mydb.cursor() as mycursor: 
        
                if attachmentIds:
                    
                    att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id, id=attachmentIds).execute()
                    data = att['data']  
                
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    
                    fileKey = msg_id + "@" + filename
                
                    s3.put_object(Bucket=non_ocr_bucket, Key=fileKey, Body=file_data)
                                                  
                    # urls = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/dev/attachment?file_name=" + fileKey
                    urls = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + str(stage_name) + "/attachment?file_name=" + fileKey
                                                  
                    values = (msg_id, filename, urls) 
                                    
                    mycursor.execute("INSERT INTO einvoice_db_portal.file_storage (file_id, name, file_link) VALUES (%s, %s, %s)", values)
                            
                    mydb.commit()
                    
                    return urls
                
                else:
                    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
            
                    files = []
                    urls = []
                    if message:
                        for part in message['payload']['parts']:
                
                            if part['filename']:
                
                                if 'data' in part['body']:
                                    data = part['body']['data']
                                else:
                                    att_id = part['body']['attachmentId']
                                    att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id,
                                                                                       id=att_id).execute()
                                    data = att['data']
                
                                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                                # file_data = '"'+file_data+'"'
                
                                if file_data:
                                    # curDateTime = datetime.now()
                                    # print(now)
                
                                    # timestamp = str(datetime.timestamp(curDateTime))
                                    # print("timestamp =", timestamp)
                                    
                
                                    fileKey = msg_id + "@" + str(part["filename"])
                
                                    # s3.put_object(Bucket="einvoice-attachments", Key=fileKey,
                                    #               Body=file_data)
                                                  
                                    s3.put_object(Bucket=non_ocr_bucket, Key=fileKey,
                                                  Body=file_data)
                                                  
                                
                                                  
                                    url = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/" + str(stage_name) + "/attachment?file_name=" + fileKey
                                                  
                                    # print(url)
                                    values = (msg_id, str(part["filename"]), url)
                                    
                                    mycursor.execute(
                                        "INSERT INTO einvoice_db_portal.file_storage (file_id, name, file_link) VALUES (%s, %s, %s)", values)
                                    
                                    mydb.commit()
                                    
                                    urls.append(url)    
                                
        finally:
            mydb.close()

    finally:
        pass
    
    # except Exception as error:
    #     print('An error occurred: ', error)
    #     # raise FailedToUpload(error)
        
        
def einvoice_fetch_mail_attachments(event, context):
            
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    secret = event["stage-variables"]["secreat"]
    
    global non_ocr_bucket
    non_ocr_bucket = event["stage-variables"]["non_ocr_attachment"]
    
    global stage_name
    stage_name = event["stage-variables"]['attach_stage']  
    
    global cred_bucket_name
    cred_bucket_name = event["stage-variables"]["bucket_gmail_credential"]

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
        
        user_id = event["params"]["querystring"]["user_id"]
        msg_id = event["params"]["querystring"]["msg_id"]
        
        if "attachments" in event["params"]["querystring"]:
            ath_ids = event["params"]["querystring"]["attachments"]
            filename = event["params"]["querystring"]["filename"]
            
            with mydb.cursor() as mycursor:
                values = (msg_id, filename)
                mycursor.execute("select * from einvoice_db_portal.file_storage where file_id = %s and name = %s", values) 
                file_storage = mycursor.fetchone()
                
                if file_storage:
                    return {
                        'statusCode': 200,
                        'body': file_storage["file_link"]
                    }
        
        creds = get_stored_credentials(user_id)
        # print(creds)
        
        if creds:
            service = build_service(credentials=creds)
            
            if ath_ids:
                urls = fetch_attachments(service, "me", msg_id, user_id, ath_ids, filename, mydb)
            else:
                urls = fetch_attachments(service, "me", msg_id, user_id)
            
            # att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
    except FailedToUpload as ex:
        return {
            'statusCode': 500,
            'body': json.dumps('fAILED to upload')
        }
        
        
    return {
        'statusCode': 200,
        'body': urls
    }

# einvoice_gmail_attachments_tos3
s3 = boto3.client("s3")
creds = None

file_name = "token.pickle"

# bucket_name = event["stage-variables"]["bucket_gmail_credential"]
bucket_name = None
# bucket_name = "file-bucket-emp"

state = ""
CLIENTSECRETS_LOCATION = 'client_secret.json'
REDIRECT_URI = 'https://7firau5x7b.execute-api.eu-central-1.amazonaws.com/einvoice-v1/gmail-s3'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
    # 'https://www.googleapis.com/auth/gmail.send',
    # 'https://www.googleapis.com/auth/gmail.modify',
    # 'https://www.googleapis.com/auth/gmail.compose',
    # 'https://www.googleapis.com/auth/gmail.addons.current.action.compose'
    # Add other requested scopes.
]


class GetCredentialsException(Exception):
    """Error raised when an error occurred while retrieving credentials.

    Attributes:
      authorization_url: Authorization URL to redirect the user to in order to
                         request offline access.
    """

    def __init__(self, authorization_url ):
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
        encoded_file = s3.get_object(Bucket=bucket_name, Key=ocr_bucket_folder+user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
    except Exception as excep:
        creds = None
        raise NoUserIdException(excep)


def store_credentials(user_id, credentials, mycursor=None, mydb=None, state=None):
    try:
        fileBody = pickle.dumps(credentials)     
        s3.put_object(Bucket=bucket_name, Key=ocr_bucket_folder+user_id, Body=fileBody)

        values = (user_id, "login")
        mycursor.execute("INSERT INTO loggedin_users (userid, login_status) VALUES (%s, %s)", values)
        
        # print(state)
        # print("state")  
        if state:
            if state == "hole_access_check": 
                values = (user_id, )  
                mycursor.execute("UPDATE elipo_setting SET value1 = %s WHERE key_name = 'notification-mail'", values)
                    
        mydb.commit()

    except Exception as e:
        raise NotImplementedError(e)


def exchange_code(authorization_code):
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
    flow.redirect_uri = REDIRECT_URI

    try:
        credentials = flow.step2_exchange(authorization_code)
        return credentials
    except FlowExchangeError as error:
        logging.error('An error occurred: %s', error)
        raise CodeExchangeException(None)


def get_user_info(credentials):
    user_info_service = build(
        serviceName='oauth2', version='v2',
        http=credentials.authorize(httplib2.Http())
    )
    # print("Service is ok")

    user_info = None

    try:
        user_info = user_info_service.userinfo().get().execute()
        # print(user_info)
    except Exception as e:
        logging.error('An error occurred: %s', e)
    if user_info and user_info.get('id'):
        return user_info
    else:
        raise NoUserIdException()


def get_authorization_url(email_address=None, state=None):
    # print("ok")
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
    # print("ok")
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    if email_address:
        flow.params['user_id'] = email_address
    if state:
        flow.params['state'] = state
    return flow.step1_get_authorize_url(redirect_uri=REDIRECT_URI)


def get_credentials(authorization_code=None, state=None, user_id=None, mycursor=None, mydb=None):
    email_address = ''
    try:
        if authorization_code:
            credentials = exchange_code(authorization_code)
            user_info = get_user_info(credentials)
            user_id = user_info["email"]
            # user_id = user_info.get('id')
            if credentials.refresh_token is not None:
                store_credentials(user_id, credentials, mycursor=mycursor, mydb=mydb, state=state)
                    
                return credentials

        elif user_id:
            credentials = get_stored_credentials(user_id)
            if credentials and credentials.refresh_token is not None:
                return credentials
            else:
                False

    except CodeExchangeException as error:
        logging.error('An error occurred during code exchange.')
        # Drive apps should try to retrieve the user and credentials for the current
        # session.
        # If none is available, redirect the user to the authorization URL.
        authorization_url = get_authorization_url(email_address, state)
        # print("aok")
        raise CodeExchangeException(authorization_url)

    except NoUserIdException:
        
        values = (gmail_user,)
        mycursor.execute("DELETE FROM loggedin_users WHERE userid = %s", values)  
        mydb.commit()
        
        logging.error('No user ID could be retrieved.')
        # No refresh token has been retrieved.
        authorization_url = get_authorization_url(email_address, state)
        raise NoRefreshTokenException(authorization_url)


def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)

import pprint


def search_messages(service, user_id, search_query):
    try:

        emials = []
        nextToken = None

        search_id = service.users().messages().list(userId=user_id, q=search_query).execute()

        if search_id:

            if search_id['resultSizeEstimate'] > 0:
                emials += search_id['messages']

            if 'nextPageToken' in search_id:
                nextToken = search_id['nextPageToken']
            else:
                nextToken = None

        while nextToken:
            search_id = service.users().messages().list(userId=user_id, q=search_query,
                                                        pageToken=nextToken).execute()

            if search_id and search_id['resultSizeEstimate'] > 0:
                emials += search_id['messages']

                if 'nextPageToken' in search_id:
                    nextToken = search_id['nextPageToken']
                else:
                    nextToken = None
            else:
                if 'nextPageToken' in search_id:
                    nextToken = search_id['nextPageToken']
                else:
                    nextToken = None

        return emials

    except Exception as error:
        print("An error occurred: ", error)


def fetch_attachments(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        # print("fetch attchments encoded",message)

        if message:
            attachments = []
            mail = {}

            mail['snippet'] = message["snippet"]
            mail['msg_id'] = msg_id

            for header in message["payload"]["headers"]:
                if header["name"] == "From":
                    mail["sender"] = header["value"]

                elif header["name"] == "Date":
                    mail["date"] = header["value"]
                    mail['dateobj'] = datetime.strptime(header["value"], '%a, %d %b %Y %X %z')
                    # print(type(header["value"]))

                elif header["name"] == "Subject":
                    mail["subject"] = header["value"]

                # elif header["name"] == "Delivered-To":
                #     delevered_to = header["value"]

            for part in message['payload']['parts']:

                if part['filename']:
                    file = {
                        'filename': part['filename'],
                        'msg_id': msg_id,
                        'attachmentId': part['body']['attachmentId']
                    }

                    attachments.append(file)

            mail["attachments"] = attachments

            mail['isReaded'] = ""

            mail['invoice_no'] = None

            mail['timetaken'] = None

            return mail

        else:
            return None  


    except Exception as error:
        print('An error occurred: ', error)


def einvoice_gmail_attachments_tos3(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    # print(event)

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    secret = event["stage-variables"]["secreat"]

    global bucket_name
    bucket_name = event["stage-variables"]["bucket_gmail_credential"]
    
    global ocr_bucket_folder
    ocr_bucket_folder = event["stage-variables"]["ocr_bucket_folder"]

    global REDIRECT_URI
    REDIRECT_URI = event["stage-variables"]["oauth_ret"]

    global CLIENTSECRETS_LOCATION
    CLIENTSECRETS_LOCATION = event["stage-variables"]["clientsec_location"]
    
    global gmail_user
    
    if "user_id" in event["params"]["querystring"]:
        gmail_user = event["params"]["querystring"]["user_id"]
    
 
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
        cursorclass=pymysql.cursors.DictCursor
    )

    user = "admin"

    if "state" in event["params"]["querystring"]:
        state = event["params"]["querystring"]["state"]
        # print(state)
    else:
        state = ""
         
    # print(event)

    try:       
        with mydb.cursor() as mycursor:
            
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            final_emails = []
            if "code" in event["params"]["querystring"]:
                cred = get_credentials(authorization_code=event["params"]["querystring"]["code"],
                                       state=state, mycursor=mycursor, mydb=mydb)
                return {
                    'statuscode': 200,
                    'body': json.dumps("Auth successfully")
                }

            elif "user_id" in event["params"]["querystring"]:
                cred = get_credentials(user_id=event["params"]["querystring"]["user_id"],
                                       state=state, mycursor=mycursor, mydb=mydb)  

                user = event["params"]["querystring"]["user_id"]

            userNtextToken = ''

            start = 0
            end = 10

            if 'pageno' in event["params"]["querystring"]:
                pageno = int(event["params"]["querystring"]['pageno'])

                start = (pageno - 1) * 10
                end = pageno * 10

            condn = ' AND '
            if 'condn' in event["params"]["querystring"]:
                
                condn += str(event["params"]["querystring"]['condn'])
                # print(condn)

            noOfMails = 0    

            if cred:
                service = build_service(credentials=cred)
                # email_msges = search_messages(service, 'me', 'newer_than:10d')
                email_data = search_messages(service=service, user_id='me',
                                             search_query='has:attachment' + condn)

                email_msges = []
                noOfMails = 0

                if email_data:
                    email_msges = []
                    noOfMails = len(email_data)
                    email_data = email_data[start:end]

                    for ids in email_data:
                        email_msges.append(ids['id'])

                    processed_mails = None

                    values = (event["params"]["querystring"]["user_id"],)
                    mycursor.execute("SELECT * FROM mail_message where user_id = %s", values)
                    processed_mails = mycursor.fetchall()

                    processed_mailsD = {}

                    for each in processed_mails:
                        if not each['message_id'] in processed_mailsD:
                            processed_mailsD[each['message_id']] = []

                        processed_mailsD[each['message_id']].append(each)

                    processed_list = []

                    emails = []

                    if email_msges:
                        email_msges = set(email_msges)
                        email_msges = list(email_msges)

                        for em_msg in email_msges:

                            flag = False

                            mail_f = fetch_attachments(service, "me", em_msg)

                            if mail_f:

                                invoices = []

                                if processed_mailsD:

                                    time_taken = 0.00
                                    total = 0
                                    invoices = []

                                    if em_msg in processed_mailsD:

                                        mail_f['isReaded'] = "yes"

                                        for mail in processed_mailsD[em_msg]:

                                            if mail['invoice_no']:
                                                invoices.append(mail['invoice_no'])

                                            if mail['is_processed'] != 'y':
                                                mail_f['invoice_no'] = "Failed"

                                            if mail['is_processed'] == 'y' and mail['invoice_no'] and mail[
                                                'invoice_no'] != '' and mail['ocr_start'] and mail['ocr_end']:
                                                diff = mail['ocr_end'] - mail['ocr_start']
                                                time_taken += diff.total_seconds()
                                                total += 1
                                                    # pass
                                            flag = True

                                        invoices.sort()
                                        mail_f['invoice_no'] = invoices

                                        if time_taken > 0:
                                            time_taken = time_taken / total
                                            time_taken = format(time_taken, '.2f')

                                        mail_f['timetaken'] = time_taken

                                    if flag == True:
                                        emails.append(mail_f)
    

                                if flag == False:
                                    mail_f['isReaded'] = "no"
                                    mail_f['invoice_no'] = invoices
                                    emails.append(mail_f)

                        emails = sorted(emails, key=lambda i: i['dateobj'], reverse=True)

                        for each in emails:
                            del each['dateobj']
                            if each['attachments']:
                                final_emails.append(each)

                return {
                   'statuscode': 200,
                    'body': final_emails,
                    'noOfMails': noOfMails
                }

            else:
                mycursor.execute("delete from loggedin_users where userid = %s", user)
                mydb.commit()

    except NoRefreshTokenException as ex:
        
        print("NoRefreshTokenException")
        return {  
            'statuscode': 201,
            'body': ex.authorization_url
        }

    except CodeExchangeException as ex:
        print("CodeExchangeException")
        return {
            'statuscode': 201,
            'body': ex.authorization_url
        }

    finally:
        mydb.close()

# einvoice_prosess_gmail_msg
class FailedToUpload(Exception):
    pass

      
def einvoice_prosess_gmail_msg(event, context):
    
    def get_stored_credentials(user_id):
        
        s3 = boto3.client("s3",region_name='eu-central-1',
            aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
            aws_secret_access_key='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')
        # bucket_name = "file-bucket-emp"
        
        try:
            encoded_file = s3.get_object(Bucket=bucket_name, Key=ocr_bucket_folder+user_id)     
            creds = pickle.loads(encoded_file["Body"].read())
            return creds
            
        except Exception as excep:
            creds = None
            # print(excep)
            return creds
        
        
    def build_service(credentials):
        http = httplib2.Http()
        http = credentials.authorize(http)
        return build('gmail', 'v1', http=http)
        

    def fetch_attachments(service, user_id, msg_id, mail, mycursor):
        try:
            message = service.users().messages().get(userId=user_id, id=msg_id).execute()

            s3 = boto3.client("s3",region_name='eu-central-1',
                    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
                    aws_secret_access_key='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')
            
            files = []
                
            for part in message['payload']['parts']:
            
                if part['filename']:
                    if 'data' in part['body']:
                        data = part['body']['data']
                    else:
                        att_id = part['body']['attachmentId']
                        # print(user_id,msg_id,att_id)
                        att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id, id=att_id).execute()
                        data = att['data']
                        
                        email_from = None
                        for header in message["payload"]["headers"]:
                            if header["name"] == "From":
                                email_from = ((header["value"].split("<"))[1].split(">")[0])
            
                        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        # file_data = '"'+file_data+'"'
            
                        if file_data:
                            curDateTime = datetime.datetime.now()
                                # print(now)
            
                            timestamp = "D" + str(datetime.datetime.timestamp(curDateTime))
                            # print("timestamp =", timestamp)
                            
                            unwanted = [' ', '-', '(', ')', ','] 
                
                            fileKey = timestamp + "___" 
                            # + str(part["filename"]) 
                            temp = ""
                            
                            for c in str(part["filename"]):
                                if c == '.':
                                    temp += c
                                if c.isalnum():
                                    temp += c
                            
                            temp = temp.lower()
                            fileKey = fileKey + temp 
                
                            fileKey = ocr_bucket_folder+fileKey   
                            s3.put_object(Bucket=ocr_bucket_name, Key=fileKey, Body=file_data)
                                                
                            files.append(fileKey)  
                            
                            # name = msg_id + str(part["filename"])
                                    
                            values = (mail, msg_id, email_from, 'y', fileKey)
                            
                            # print(values)
                                    
                            mycursor.execute("INSERT INTO mail_message (user_id, message_id, recieved_from, is_processed, filename) VALUES (?, ?, ?, ?, ?)", values)

                            del fileKey, values
                            
        except Exception as error:
            print('An error occurred: ', error)
            raise FailedToUpload(error)
            

    global dbScehma 
    dbScehma = ' DBADMIN '
    
    try:
    #     client = boto3.client(
    # 'secretsmanager',
    # region_name='ap-south-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    #     secret = event["stage-variables"]["secreat"]
        global bucket_name
        bucket_name = event["stage-variables"]["cred_bucket"]
        
        global ocr_bucket_name
        # ocr_bucket_name = event["stage-variables"]["ocr_bucket"]
        ocr_bucket_name = 'textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db'
        
        global ocr_bucket_folder
        ocr_bucket_folder = event["stage-variables"]["ocr_bucket_folder"]
        

        # resp = client.get_secret_value(
        #     SecretId= secret
        # ) 
    
        # secretDict = json.loads(resp['SecretString'])
    
        mydb = hdbcliConnect()
        # print(event)
        
        user_id = event["params"]["querystring"]["user_id"]
        msg_id = event["params"]["querystring"]["msg_id"]
        
        if "attachments" in event["params"]["querystring"]:
            ath_ids = event["params"]["querystring"]["attachments"]
            
        try :
            with mydb.cursor() as mycursor:
                defSchemaQuery = "set schema " + dbScehma
                mycursor.execute(defSchemaQuery)
                
                values = (user_id, msg_id)
                mycursor.execute("select * from mail_message where user_id = ? and message_id= ?", values)
                processed = mycursor.fetchone()
                
                if processed:
                    return {
                    'statusCode': 400,
                    'body': json.dumps('Already Processed')
                }
        
                creds = get_stored_credentials(user_id)
                # print(creds)
                
                if creds:
                    service = build_service(credentials=creds)
                    
                    fetch_attachments(service, "me", msg_id, user_id, mycursor) 
                    
                    mydb.commit()
                    
        finally:
            mydb.close()
            
            # att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
    except FailedToUpload as ex:
        return {
            'statusCode': 500,
            'body': json.dumps('fAILED to upload')
        }
        
    finally:
        pass
    
    return {
        'statusCode': 200,
        'body': json.dumps('OCR initiated it may take a moment')  
    }
    
#getGstinDetails
def getGstinDetails(event, context):
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

    body = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "gstin" in event["params"]["querystring"] and "gst_treatment" in event["params"]["querystring"]:
            
                gstin = event["params"]["querystring"]["gstin"]
                gst_treatment = event["params"]["querystring"]["gst_treatment"]
                
                values = (gstin[0:2],)
                mycursor.execute("SELECT * FROM  state_code WHERE gstcode = %s", values)
                detail = mycursor.fetchone()
                
                if detail:
                    body = {
                        "state" : detail['state'],
                        "state_code" : detail['state_code'],
                        "gst_treatment": "",
                        "gst_per": ""
                    }
                    
                gst = gstin[0:2]
                
                if gst_treatment == "registered_business":
                    
                    mycursor.execute("SELECT value2 FROM  dropdown WHERE drop_key = 'my-company-details' and value1 = 'gstin'")
                    gstin = mycursor.fetchone()
                    
                    if gst == gstin["value2"][0:2] or gst == '35' or gst == '04' or gst == '26' or gst == '28' or gst == '97':
                        body["gst_treatment"] = gst_treatment
                        body["gst_per"] = "gst"
                    
                    else:
                        body["gst_treatment"] = gst_treatment
                        body["gst_per"] = "igst"
                
                elif gst_treatment == "Special-Economic-Zone":
                    body["gst_treatment"] = gst_treatment
                    body["gst_per"] = "igst"
            
            elif "vendor_no" in event["params"]["querystring"]:
                vendor_no = event["params"]["querystring"]["vendor_no"]
                
                mycursor.execute("select gstin_uin from  vendor_master where vendor_no = %s", vendor_no)
                gstin_uin = mycursor.fetchone()
                
                state_code = gstin_uin["gstin_uin"][0:2]
                
                if state_code == '35' or state_code == '4' or state_code == '26' or state_code == '38' or state_code == '97':
                    body = 'y'
                    
                else:
                    body = 'n'
                
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }
        
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': body
    }

# #getInvoiceCount
# def getInvoiceCount(event, context):
#     global dbScehma 
#     dbScehma = event["stage-variables"]["schema"]
    
#     client = boto3.client(
#     'secretsmanager',
#     region_name='eu-central-1',
#     aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
#     aws_secret_access_key='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' )

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
    

#     user_settings = {}
    
#     try:
#         with mydb.cursor() as mycursor:
#             defSchemaQuery = "use " + dbScehma
#             mycursor.execute(defSchemaQuery)
            
#             mycursor.execute("SELECT * FROM elipo_setting")
#             settings = mycursor.fetchall()

#             if settings:
#                 for each in settings:
#                     user_settings[each['key_name']] = each['value1']
#                 del settings
            
#             if "userid" in event["params"]["querystring"]:
#                 email = event["params"]["querystring"]["userid"]
            
#             if "from_cockpit" in event["params"]["querystring"]:
#                 flag = event["params"]["querystring"]["from_cockpit"]
                
#                 userBased = 'y'
#                 if "userBased" in event["params"]["querystring"]:
#                     userBased = event["params"]["querystring"]["userBased"]
                    
#                 total_count = 0
#                 countrec = {}
                
#                 mycursor.execute("select member_id, group_id, concat(fs_name, ' ', ls_name) as member_name from member where email = %s", email)
#                 member = mycursor.fetchone()
                
#                 if flag == 'y':
#                     if user_settings["app_assignment"] == 'on' and userBased == 'y':
#                         sqlQuery = "select count(in_status) as invoice_count, in_status " \
#                             "from invoice_header " \
#                             "where invoice_no in ( " \
#                         	"	select invoice_no " \
#                         	"		from assignment " \
#                             "       where ( isgroup = 'y' and app = %s ) or ( isgroup = 'n' and app = %s ) ) " \
#                             "group by in_status"
#                         values = ( member["group_id"], member["member_id"] )
                        
#                         mycursor.execute(sqlQuery,values)
                        
#                     else:
#                         mycursor.execute("select count(in_status) as invoice_count, in_status from invoice_header group by in_status")
                    
#                     for each in mycursor:
#                         total_count = total_count + int(each["invoice_count"])
#                         countrec[each['in_status']] = each['invoice_count']
                    
#                     if "" in countrec:
#                         del countrec['']
                    
#                     if "new" not in countrec:
#                         countrec["new"] = 0
                        
#                     if "draft" not in countrec:
#                         countrec["draft"] = 0
                        
#                     if "inapproval" not in countrec:
#                         countrec["inapproval"] = 0
                        
#                     if "tosap" not in countrec:
#                         countrec["tosap"] = 0
                        
#                     if "rejected" not in countrec:
#                         countrec["rejected"] = 0
                        
#                     countrec["total_count"] = total_count
                        
#                 else:
#                     mycursor.execute("select count(sup_status) as invoice_count, sup_status from invoice_header where from_supplier = 'y' group by sup_status")
                    
#                     for each in mycursor:
#                         total_count = total_count + int(each["invoice_count"])
#                         countrec[each['sup_status']] = each['invoice_count']
                    
#                     if "" in countrec:
#                         del countrec['']
                        
#                     if None in countrec:
#                         del countrec[None]
                        
#                     if "draft" not in countrec:
#                         countrec["draft"] = 0
                        
#                     if "inapproval" not in countrec:
#                         countrec["inapproval"] = 0
                        
#                     if "approved" not in countrec:
#                         countrec["approved"] = 0
                        
#                     if "rejected" not in countrec:
#                         countrec["rejected"] = 0
                        
#                     countrec["total_count"] = total_count
    
#     except:
#         return {
#             'statuscode': 500,
#             'body': json.dumps("Internal Failure!")
#         }
    
#     finally:
#         mydb.close()
    
#     return {
#         'statuscode': 200,
#         'body': countrec
#     }

# setNotificationEmail
state = ""
# CLIENTSECRETS_LOCATION = 'client_secret.json'
# REDIRECT_URI = 'https://7firau5x7b.execute-api.eu-central-1.amazonaws.com/einvoice-v1/gmail-s3'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.send'
    # 'https://www.googleapis.com/auth/gmail.modify',
    # 'https://www.googleapis.com/auth/gmail.compose',
    # 'https://www.googleapis.com/auth/gmail.addons.current.action.compose'
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

        s3 = boto3.client("s3")
        encoded_file = s3.get_object(Bucket=bucket_name, Key=bucket_folder+user_id)
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
    except Exception as excep:
        creds = None
        raise NoUserIdException(excep)


def get_authorization_url(user_id=None, state=None):
    # print("ok")
    flow = flow_from_clientsecrets(CLIENTSECRETS_LOCATION, ' '.join(SCOPES))
    # print("ok")
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    flow.params['login_hint'] = user_id
    flow.params['state'] = state
    return flow.step1_get_authorize_url(redirect_uri=REDIRECT_URI)


def get_credentials(state=None, user_id=None):

    try:
        if user_id:
            credentials = get_stored_credentials(user_id)
            if credentials and credentials.refresh_token is not None:
                return credentials
            else:
                False

    except NoUserIdException:
        logging.error('No user ID could be retrieved.')
        # No refresh token has been retrieved.
        authorization_url = get_authorization_url(user_id, state)
        raise NoRefreshTokenException(authorization_url)


def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)


def setNotificationEmail(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    secret = event["stage-variables"]["secreat"]

    global bucket_name
    bucket_name = event["stage-variables"]["bucket_gmail_credential"]
    # bucket_name = "file-bucket-emp"
    
    global bucket_folder
    bucket_folder = event["stage-variables"]["ocr_bucket_folder"]

    global REDIRECT_URI
    REDIRECT_URI = event["stage-variables"]["oauth_ret"]
    # REDIRECT_URI = "https://7firau5x7b.execute-api.eu-central-1.amazonaws.com/einvoice-v1/gmail-s3"

    global CLIENTSECRETS_LOCATION
    CLIENTSECRETS_LOCATION = event["stage-variables"]["clientsec_location"]
    # CLIENTSECRETS_LOCATION = "client_secret.json"

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
        cursorclass=pymysql.cursors.DictCursor
    )

    state = "hole_access_check"   

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            user = event["params"]["querystring"]["user_id"]
            
            mail = None
            cred = None
            
            mycursor.execute("SELECT * FROM elipo_setting where key_name = 'notification-mail'")
            mail = mycursor.fetchone()

            if "notification_id" not in event["params"]["querystring"]:

                if mail:
                    cred = get_credentials(user_id=mail['value1'], state=state)
                    if cred:
                        return {
                            'statuscode': 200,
                            'body': {
                                'msg': "Notification mail is already added",
                                'notification_id': mail['value1']
                            }
                        }
                    else:
                        return {
                            'statuscode': 205,
                            'body': {
                                'msg': "Notification mail is not added",
                                'notification_id': ""
                            }
                        }

            else:
                notification_id = event["params"]["querystring"]["notification_id"]
                
                if mail['value1'] == notification_id:

                    cred = get_credentials(user_id=notification_id, state=state)
    
                    if cred:
                        return {
                            'statuscode': 200,
                            'body': json.dumps("Notification mail is already added")
                        }
                    else:
                        cred = get_credentials(user_id=notification_id, state=state)
                else:
                    cred = get_credentials(user_id=notification_id, state=state)
                    



    except NoRefreshTokenException as ex:
        print("NoRefreshTokenException")
        return {
            'statuscode': 201,
            'body': ex.authorization_url
        }

    except CodeExchangeException as ex:
        print("CodeExchangeException")
        return {
            'statuscode': 201,
            'body': ex.authorization_url
        }

    finally:
        # mydb.close()
        pass

# getOcrDataSupplier
def getOcrDataSupplier(event, context):
    
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
    
    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            file_name = event["params"]["querystring"]["file_name"]
            mycursor.execute("select * from mail_message where filename = %s", file_name)
            data = mycursor.fetchone()
            
            if data:
                if data["invoice_no"]:
                    
                    items = []
                    invoice_files = []
                    
                    mycursor.execute("select attach_id, file_id, name, mime_type, file_link from file_storage where file_id = %s", data["invoice_no"])
                    for row in mycursor:
                        record = {
                            'attach_id': row['attach_id'],    
                            "invoice_id" : row["file_id"],
                            "file_name" : row["name"],
                            "mime_type" : row["mime_type"],
                            "file_link" : row["file_link"]
                        }
                        invoice_files.append(record)
                    
                    values = (data["invoice_no"],)
                    # mycursor.execute("select * from invoice_header where invoice_no = %s and from_supplier = 'y'", values)
                    mycursor.execute("select * from invoice_header where invoice_no = %s", values)
                    invoice_header = mycursor.fetchone()
                    
                    if invoice_header:
                        records = {
                            "invoice_no": data["invoice_no"],
                            "user_invoice_id": invoice_header["user_invoice_id"],
                            "invoice_no" :invoice_header["invoice_no"],
                            "in_status" : invoice_header["sup_status"],
                            "ref_po_num" : invoice_header["ref_po_num"],
                            "company_code" : invoice_header["company_code"],
                            "payment_method" : invoice_header["payment_method"],
                            "invoice_date" : str(invoice_header["invoice_date"]),
                            "baseline_date" : str(invoice_header["baseline_date"]),
                            "amount" : invoice_header["amount"],
                            "currency" : invoice_header["currency"],
                            "gl_account" : invoice_header["gl_account"],
                            "business_area" : invoice_header["business_area"],
                            "supplier_id" : invoice_header["supplier_id"],
                            "supplier_name" : invoice_header["supplier_name"],
                            "supplier_comments": invoice_header['supplier_comments'],
                            "taxable_amount" : invoice_header["taxable_amount"],
                            "discount_per" : invoice_header["discount_per"],
                            "total_discount_amount" : invoice_header["total_discount_amount"],
                            "is_igst" : invoice_header["is_igst"],
                            "tax_per" : invoice_header["tax_per"],
                            "cgst_tot_amt": invoice_header["cgst_tot_amt"],
                            "sgst_tot_amt": invoice_header["sgst_tot_amt"],
    	                    "igst_tot_amt": invoice_header["igst_tot_amt"],
                            "tds_per": invoice_header["tds_per"],
                            "tds_tot_amt": invoice_header["tds_tot_amt"],
                            "payment_terms" :invoice_header["payment_terms"],
                            "adjustment" : invoice_header["adjustment"],
                            "tcs" : invoice_header["tcs"],
                            "npo": invoice_header["npo"],
                            'invoice_files' : invoice_files,
                            "items" : items,
                            "gstin": invoice_header['gstin'],
                            "document_type": invoice_header["document_type"]              
                        }
                    
                        mycursor.execute("select * from invoice_item where invoice_no = %s", values)
                        
                        for row in mycursor:
                            record = {
                                "item_no":row["item_no"],
                                "material":row["material"],
                                "material_desc":row["material_desc"],
                                "quantity":row["quantity"],
                                "unit":row["unit"],
                                "amount":row["amount"],
                                "currency": row["currency"],
                                "amt_per_unit" : row["amt_per_unit"],
                                "cgst_per": row["cgst_per"],
                                "cgst_amount":row["cgst_amount"],
                                "tax_code":row["tax_code"],
                                "ref_po_no":row["ref_po_no"],
                                "plant":row["plant"],
                                "discount":row["discount"],
                                "discount_amount" : row["discount_amount"],
                                "gross_amount" : row["gross_amount"],
                                "sgst_per": row["sgst_per"],
                                "sgst_amount": row["sgst_amount"],
                                "igst_per": row["igst_per"],
                                "igst_amount": row["igst_amount"],
                                "taxable_amount": row["taxable_amount"],
                                "tax_value_amount": row["tax_value_amount"],
                                "gst_per": row["gst_per"],
                                "hsn_code": row["hsn_code"]         
                            }
                            items.append(record)
                            
                        records["items"] = items
                    
                else:
                    return {
                        'statuscode': 201,
                        'body': json.dumps("OCR in process. Wait for sometime!")
                    }
            
    # except:
    #     return {
    #         'statuscode': 500,
    #         'body': json.dumps("Internal Error")
    #     }
            
    finally:
        mydb.close()
        
    return {
        'statuscode': 200,
        'body': records
    }

# getOcrLabels
def getOcrLabels(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='eu-central-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )

    secret = event["stage-variables"]["secreat"]
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
        cursorclass=pymysql.cursors.DictCursor
    )

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            label_name = event["params"]["querystring"]['label_name']
            userid = event["params"]["querystring"]['userid']
            values = (label_name,)

            mycursor.execute('select * from ocr_label where label_for = %s', values)
            labels = mycursor.fetchall()

            if labels:
                for each in labels:
                    records.append({"label_id":each['label_id'],"label": each['value1']})

    except:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': records
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records
    }

# patchOcrLabels
def postPaperAiResponse(event=None, context=None):
    # print(event)   
    
    s= requests.Session()

    s.headers.update({'Connection': 'keep-alive'})

    url = "https://vxx4jwamw0.execute-api.sa-east-1.amazonaws.com/dev/event"


    # sap_responce = s.post(url, json=event)
        
    def get_stored_credentials(user_id):
        try:
            s3 = boto3.client("s3",region_name='eu-central-1',
                    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
                    aws_secret_access_key='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')
            encoded_file = s3.get_object(Bucket=elipo_bucket, Key=user_id)
            creds = pickle.loads(encoded_file["Body"].read())
            return creds
        except Exception as excep:
            creds = None
            # print(str(excep))
            # raise NoUserIdException(excep)


    def create_message(sender, to, subject, message_text, cc):
        message = email.mime.text.MIMEText(message_text, 'html')

        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        message['cc'] = cc

        encoded = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
        return {'raw': encoded.decode("utf-8")}


    def send_message(service, user_id, message):
        try:
            message = (service.users().messages().send(userId=user_id, body=message).execute())
            # print("Message Id: ", message['id'])
            return message
        # except errors.HttpError as error:
        except Exception as error:
            print("An error occurred: ", error)


    def build_service(credentials):
        http = httplib2.Http()
        http = credentials.authorize(http)
        return build('gmail', 'v1', http=http)


    def sendMailNotifications(invoice_id, emails, body1=None, user=None):
        # user_id = "mosbyted116@gmail.com"
        user_id = elipo_email

        if not body1:
            body1 = ''

        credentials = get_stored_credentials(user_id)

        if credentials and credentials.refresh_token is not None:
            service = build_service(credentials=credentials)

            mail_subject = 'ELIPO Notification'
            mail_cc = ''

            message_body = '''<html>
                    <body  >
                <div style="  max-width: 500px; margin: auto; padding: 10px; ">
                        <div style=" width:100%; align-content: center;text-align: center;">
                            <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/ELIPO+logo.png" alt="Italian Trulli" style="vertical-align:middle; width: 140px;height:50px;text-align: center;"  >
                        </div>

                        <div style=" width:100%; align-content:left;text-align:left;">
                                <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                            </div>
                        <b>

                    <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Dear User,
                    </span> 
                    <br><br>
                    <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Invoice No: <span style="font: 500  15px/22px ;">{},</span>
                    </span> 

                    <br>
                    <span style="vertical-align: middle;text-align: left;font: 600  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                    Is generated by OCR and assigned for approval to you.
                    </span> 
                    </b> 
                    <br>
                    <br>
                    <div style=" width:100%;align-content: center;text-align: center; ">
                        <a href="https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/production/login" target="_blank">
                            <button style="border: none;box-shadow: 1px 1px 5px 1px #5a9e9b; background:rgb(80, 219, 212) 0% 0% no-repeat padding-box; border-radius: 7px;opacity: 1;width:180px; height: 35px;outline: none;border: none;" > 
                                <span style="vertical-align: middle; text-align: left;font: 600 16px/23px Open Sans;letter-spacing: 0px;color: whitesmoke;white-space: nowrap;opacity: 1;">Login to ELIPO</span>
                            </button>
                        </a>
                    </div>

                    <br><br>
                    <div style="width:100%;">
                    <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Regards,</span>
                    <br>
                    <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Team ELIPO</span>
                    </div>
                <div style=" width:100%; align-content:left;text-align:left;">
                            <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                        </div>


                    <div style="width:100%;align-content: center;text-align: center;">
                        <span style=" text-align: center;font: 600 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 0.7;">This message was sent to you by ELIPO</span>
                    </div>
                    <div style="width:100%;align-content: center;text-align: center;">
                        <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/elipo+logo_2.png" alt="Italian Trulli" style="text-align: center;width: 80px;height: 30px;" >
                    </div>

                    <br>
                </div>
                    </body></html>'''.format(invoice_id)

            message = create_message(sender=elipo_email, to=emails, subject=mail_subject,
                                    message_text=str(message_body), cc=mail_cc)

            send_message(service=service, user_id="me", message=message)


    def find_vendor(mycursor, r_vendor, idate):

        vendor_data = None
        vendor = {}

        if r_vendor['gstin']:

            sqlQuery = "SELECT v.*, d.value2 FROM vendor_master v " \
                    "left join dropdown d on v.gst_treatment = d.value1 where " \
                    "(v.gstin_uin = ? and d.drop_key = 'vendor_gst_treatment')"
            values = (r_vendor['gstin'],)
            mycursor.execute(sqlQuery,values)
            vendor = mycursor.fetchone()


        if not vendor and r_vendor['vendor_name']:

            mycursor.execute("SELECT v.*, d.value2 FROM vendor_master v left join dropdown d on v.gst_treatment = d.value1")
            allVendors = mycursor.fetchall()

            # fuzzScore = 0

            for eachVendor in allVendors:

                dist_sc = fuzz.ratio(eachVendor['vendor_name'].lower(), r_vendor['vendor_name'].lower())
                if dist_sc > 75:
                # if dist_sc > 75 and fuzzScore < dist_sc:
                    vendor = eachVendor
                    # fuzzScore = dist_sc
                    break

        if vendor:

            due = None

            igst = 'n'

            if idate and vendor['payment_terms']:

                due = idate

                if vendor['payment_terms'] == "On the day invoice raised":
                    due = idate
                elif vendor['payment_terms'] == "On the month end":
                    last = calendar.monthrange(idate.year, idate.month)
                    idate = datetime.datetime.strptime(idate, '%Y-%m-%d')
                    due = idate.date() + datetime.timedelta(days=last[1] - idate.day)
                else:
                    idate = datetime.datetime.strptime(idate, '%Y-%m-%d')
                    due = idate.date() + datetime.timedelta(days=int(vendor['payment_terms']))

            if vendor['gst_per'] == "igst":
                igst = 'y'
            else:
                igst = 'n'

            vendor_data = {
                'currency': vendor['currency'],
                'payment_terms': vendor['payment_terms'],
                'due_date': due,
                'vendor_code': vendor['vendor_no'],
                'vendor_name': vendor['vendor_name'],
                'is_igst': igst,
                'tds': vendor['tds'],
                'gst_treatment': vendor['gst_treatment'],
                'gstin': vendor['gstin_uin']
            }

        return vendor_data


    def fetch_default_vendor(mycursor, idate=None):
        vendor_data = None

        mycursor.execute("SELECT * FROM dropdown where drop_key = 'default-master-detail'")
        d_master = mycursor.fetchall()

        defaults = {}
        vendor = {}

        if d_master:

            for each in d_master:
                defaults[each['value1']] = each['value2']

            if defaults['supplier_id']:
                values = (defaults['supplier_id'],)
                mycursor.execute(
                    "SELECT v.*, d.value2 FROM vendor_master v left join dropdown d "
                    "on v.gst_treatment = d.value1 where v.vendor_no = ?", values)
                vendor = mycursor.fetchone()

            due = None

            igst = 'n'

            if idate and vendor['payment_terms']:

                due = idate

                if vendor['payment_terms'] == "On the day invoice raised":
                    due = idate
                elif vendor['payment_terms'] == "On the month end":
                    last = calendar.monthrange(idate.year, idate.month)
                    idate = datetime.datetime.strptime(idate, '%Y-%m-%d')
                    due = idate.date() + datetime.timedelta(days=last[1] - idate.day)
                else:
                    idate = datetime.datetime.strptime(idate, '%Y-%m-%d')
                    due = idate.date() + datetime.timedelta(days=int(vendor['payment_terms']))

            if vendor['gst_per'] == "igst":
                igst = 'y'
            else:
                igst = 'n'

            vendor_data = {
                'currency': vendor['currency'],
                'payment_terms': vendor['payment_terms'],
                'due_date': due,
                'vendor_code': vendor['vendor_no'],
                'vendor_name': vendor['vendor_name'],
                'is_igst': igst,
                'tds': vendor['tds'],
                'gst_treatment': vendor['gst_treatment'],
                'gstin': vendor['gstin_uin'],
                'company_code': defaults['company_code'],

            }

        return vendor_data

    def clearDate(rawDate):
        dateF = None

        for index in range(6):
            try:
                date_time_strtt = str(rawDate)
                date_time_strtt = date_time_strtt.strip()
                date_time_str = ""

                for c in date_time_strtt:
                    if c.isalnum():
                        date_time_str += c

                if index == 0:
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%d%m%Y')

                elif index == 1:
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%d%B%Y')

                elif index == 2:
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%d%b%Y')

                elif index == 3:
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%d%b%y')

                elif index == 4:
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%d%B%y')

                elif index == 5:
                    date_time_str = date_time_str[0:1] + date_time_str[3:]
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%d%B%Y')

                dateF = str(date_time_obj.date())

                return dateF

            except ValueError as e:
                pass


    def fetchSAP_PoDetails(poNumber):
        item_category = []
        try:

            s = requests.Session()
            s.headers.update({'Connection': 'keep-alive'})

            url = "http://182.72.219.94:8000/zgetpo/GetPo"
            params = {'sap-client': '800'}

            headersFetch = {'X-CSRF-TOKEN': 'Fetch'}
            y = s.get(url, auth=HTTPBasicAuth('developer31', 'peol@123'), headers=headersFetch, params=params, timeout=10)
            token = y.headers["X-CSRF-TOKEN"]

            headers = {"X-CSRF-TOKEN": token, 'Content-type': 'application/json'}
            records = {
                "ebeln": poNumber
            }

            x = s.post(url, json=records, auth=HTTPBasicAuth('developer31', 'peol@123'), headers=headers, params=params,
                    timeout=10)

            if x.status_code != 500:
                payload = x.json()

                # item_category = []
                for each in payload[0]['POITEM']:
                    item_category.append(each['ITEM_CAT'])

        except requests.exceptions.RequestException as msg:
            pass

        except requests.exceptions.ConnectionError as msg:
            pass

        return item_category


    def create_approvals(mycursor, invoice_id, decider, working_person):
        try:

            mycursor.execute(
                "SELECT a.* FROM rule a inner join rule_snro b on a.rule_id = b.rule_id where b.is_approval = 'y' and a.is_on = 'y'")
            all_rules = mycursor.fetchall()

            rule_ids = [sub['rule_id'] for sub in all_rules]
            rule_ids = set(rule_ids)
            rule_ids = list(rule_ids)

            rule = []

            default = []
            for ruleID in rule_ids:
                rules = []

                for row in all_rules:
                    if not default and row[
                        'decider'] == "default":  # ruleID == row['rule_id'] and row['decider'] != "default":
                        default.append(row)

                    elif row['decider'] == "default_assignment":
                        pass

                    elif ruleID == row['rule_id']:
                        rules.append(row)

                noOfRules = len(rules)
                countMatches = 0

                for row in rules:

                    if row['decider_type'] == "number":

                        if row['decider'] == "amount" or row["decider"] == "discount":
                            d_value = float(decider[row['decider']])
                        else:
                            d_value = int(decider[row['decider']])

                        if row['operator'] == "=" and d_value == int(row['d_value']):
                            countMatches += 1
                        elif row['operator'] == ">" and d_value > int(row['d_value']):
                            countMatches += 1
                        elif row['operator'] == "<" and d_value < int(row['d_value']):
                            countMatches += 1
                        elif row['operator'] == "between" and int(row['d_value']) <= d_value <= int(row['d_value2']):
                            countMatches += 1

                    elif row['decider_type'] == "string":
                        if row["decider"] == "item_category":
                            for each in decider["item_category"]:
                                if each == str(row['d_value']):
                                    countMatches += 1
                                    break

                        elif decider[row['decider']] == str(row['d_value']):
                            countMatches += 1

                if noOfRules == countMatches and noOfRules != 0:
                    rule.append(row)

            if not rule and default:
                rule.append(default[0])

            if rule:

                values = [sub['rule_id'] for sub in rule]
                values = set(values)
                values = list(values)

                format_strings = ','.join(['?'] * len(values))
                sqlQuery = "select distinct r.*, ru.approval_type, ru.ifnot_withindays from rule_approver r " \
                        "left join rule ru on r.rule_key = ru.rule_id " \
                        "where r.rule_key in ("+format_strings+") " \
                        "order by field(approval_type, 'series', 'parallel', 'single'), " \
                        "r.level desc, r.rule_key" 
                mycursor.execute(sqlQuery, tuple(values))
                all_approvers = mycursor.fetchall()

                multiple_app = []
                allrules = []

                main_rule = None
                main_rule = all_approvers[0]

                for row in all_approvers:

                    if row["approver"] == 999999999:
                        return False

                    allrules.append(row['rule_key'])

                    if all_approvers[0]['rule_key'] == row['rule_key']:
                        data = {
                            "isgroup": row["isgroup"],
                            "approver": row["approver"],
                            'level': row['level'],
                            'approval_type': main_rule['approval_type'],
                            'rule_id': row['rule_key']
                        }
                        multiple_app.append(data)

                allrules = set(allrules)
                allrules = list(allrules)
                allrules.remove(all_approvers[0]['rule_key'])

                add_level = all_approvers[0]['level']

                for rule in allrules:

                    level_s = 0

                    for row in all_approvers:

                        if rule == row['rule_key']:

                            dupl_app = False

                            for exec in multiple_app:
                                if exec['isgroup'] == row['isgroup'] and exec['approver'] == row['approver']:
                                    dupl_app = True
                                    break

                            if dupl_app:
                                continue

                            if level_s < row['level']:
                                level_s = row['level']

                            data = {
                                "isgroup": row["isgroup"],
                                "approver": row["approver"],
                                'level': row['level'] + add_level,
                                'approval_type': row['approval_type'],
                                'rule_id': row['rule_key']
                            }
                            multiple_app.append(data)

                    if level_s > 0:
                        add_level += level_s

                values = []
                exc_days = int(main_rule['ifnot_withindays'])

                escalate_when = datetime.date.today() + datetime.timedelta(days=exc_days)

                groups = []
                members = []

                for row in multiple_app:

                    if row['isgroup'] == 'y' and (
                            (row['approval_type'] == "single" or row['approval_type'] == "parallel") or row['level'] == 1):
                        groups.append(row['approver'])

                    elif (row['approval_type'] == 'single' or row['approval_type'] == 'parallel') or row['level'] == 1:
                        members.append(row['approver'])

                    value = (
                        row['isgroup'], row['approver'], invoice_id, "n", row['level'], row['approval_type'], escalate_when,
                        row['rule_id'])
                    values.append(value)

                format_strings_grp = ','.join(['?'] * len(groups))
                format_strings_mem = ','.join(['?'] * len(members))
                emails = None

                if members and groups:
                    mix = members + groups
                    mycursor.execute(
                        "select email from member where member_id in ({}) or group_id in ({})".format(
                            format_strings_mem, format_strings_grp), tuple(mix))
                    emails = mycursor.fetchall()

                elif groups:
                    mycursor.execute(
                        "select email from member where group_id in ({})".format(format_strings_grp),
                        tuple(groups))
                    emails = mycursor.fetchall()

                else:
                    mycursor.execute(
                        "select email from member where member_id in ({})".format(format_strings_mem),
                        tuple(members))
                    emails = mycursor.fetchall()

                if values:
                    for i in values:
                        mycursor.execute(
                        "INSERT INTO approval (isgroup, approver, invoice_no, isapproved,"
                        " approval_level, approval_type, escalate_date, rule_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        tuple(i))

                    if emails:

                        email_Add = None
                        for each in emails:
                            if not email_Add:
                                email_Add = each['email']
                            else:
                                email_Add += "," + each['email']

                        # sendMailNotifications(invoice_id=invoice_id, mycursor=mycursor, emails=emails, user=working_person)
                        sendMailNotifications(invoice_id=invoice_id, emails=email_Add, user=working_person)

                return True

            else:
                return False

        finally:
            return event
            pass


    # invoice_id = 856
    # decider = {
    #                 'discount': 0,
    #                 'amount': 150001.24,
    #                 'cost_center': '1000',
    #                 'currency': 'INR',
    #                 'gl_account': '113310',
    #                 'npo': 'n',
    #                 'vendor_no': '2000000075',
    #                 'department_id': '13',
    #                 'item_category': ['0']
    #             }

    # with mydb.cursor() as mycursor:
    #     print(create_approvals(mycursor, invoice_id, decider))


    def assign_approcessor(mycursor, invoice_id, decider):
        try:
            default = None
            email_str = ""

            mycursor.execute("SELECT * FROM elipo_setting where key_name = 'app_assignment'")
            appdet = mycursor.fetchone()

            if appdet:

                email_str = ''

                if appdet['value1'] == "on":

                    mycursor.execute(
                        "SELECT a.* FROM rule a inner join rule_snro b"
                        " on a.rule_id = b.rule_id "
                        "where b.is_approval = 'n' and a.is_on = 'y'")
                    all_rules = mycursor.fetchall()

                    rule_ids = []
                    email_str = ''
                    rule = None

                    if all_rules:
                        rule_ids = [sub['rule_id'] for sub in all_rules]
                        rule_ids = set(rule_ids)
                        rule_ids = list(rule_ids)

                        rule = []

                        rules = {}

                        for ruleId in rule_ids:
                            rules[ruleId] = []

                        default = None

                        for row in all_rules:
                            if row['decider'] == 'default_assignment':
                                default = row
                            else:
                                rules[row['rule_id']].append(row)

                        if default:
                            rule_ids.remove(default['rule_id'])
                            del rules[default['rule_id']]

                    if rule_ids:
                        # noOfRules = len(rules)

                        for eachRule in rules:

                            countMatches = 0
                            noOfCondn = len(rules[eachRule])

                            for row in rules[eachRule]:

                                if row['decider_type'] == "number":

                                    if row['decider'] == "invoice_value":
                                        d_value = float(decider[row['decider']])
                                    else:
                                        d_value = int(decider[row['decider']])

                                    if row['operator'] == "=" and d_value == int(row['d_value']):
                                        countMatches += 1
                                    elif row['operator'] == ">" and d_value > int(row['d_value']):
                                        countMatches += 1
                                    elif row['operator'] == "<" and d_value < int(row['d_value']):
                                        countMatches += 1
                                    elif row['operator'] == "between" and int(row['d_value']) <= d_value <= int(
                                            row['d_value2']):
                                        countMatches += 1

                                elif row['decider_type'] == "string":
                                    if row["decider"] == "invoice_type":
                                        for each in decider["invoice_type"]:
                                            if each == str(row['d_value']):
                                                countMatches += 1
                                                break

                                    elif decider[row['decider']] == str(row['d_value']):
                                        countMatches += 1

                            if noOfCondn == countMatches:
                                rule.append(row)

                    # print(default)
                    if not rule and default:
                        rule.append(default)

                    if rule:
                        # print(rule)

                        values = [sub['rule_id'] for sub in rule]
                        values = set(values)
                        values = list(values)

                        format_strings = ','.join(['?'] * len(values))

                        sqlQuery = "select isgroup, approver from rule_approver where rule_key in (" + format_strings +")"
                        # print(sqlQuery, values)
                        mycursor.execute(sqlQuery, tuple(values))
                        all_app = mycursor.fetchall()

                        all_approvers = [dict(t) for t in {tuple(d.items()) for d in all_app}]

                        groups = []
                        members = []
                        values = []

                        for row in all_approvers:

                            value = (
                                row['isgroup'], row['approver'], invoice_id)
                            values.append(value)

                            if row['isgroup'] == 'y':
                                groups.append(row['approver'])
                            else:
                                members.append(row['approver'])

                        format_strings_grp = ','.join(['?'] * len(groups))
                        format_strings_mem = ','.join(['?'] * len(members))
                        emails = None

                        audit_trail = 'Invoice ' + str(invoice_id) + ' assigned to '
                        trail_grp = ''

                        if members and groups:
                            mix = members + groups
                            mycursor.execute(
                                "select (fs_name|| ' '|| ls_name) as name, email, group_id from member "
                                "where member_id in ({}) or group_id in ({})".format(
                                    format_strings_mem, format_strings_grp), tuple(mix))
                            emails = mycursor.fetchall()

                            # mycursor.execute(
                            #     "select group_id, name from group where group_id in ({})".format(
                            #         format_strings_grp), tuple(groups))
                            # grp_details = mycursor.fetchall()

                            sqlQueryt = 'select group_id, name from "GROUP" where group_id in ({})'.format(
                                format_strings_grp)
                            mycursor.execute(sqlQueryt, tuple(groups))
                            grp_details = mycursor.fetchall()

                            if grp_details:
                                for each in grp_details:
                                    if not trail_grp:
                                        trail_grp += each['name']
                                    else:
                                        trail_grp += ', ' + each['name']

                        elif groups:
                            mycursor.execute(
                                "select (fs_name|| ' '|| ls_name) as name, email, group_id from member "
                                "where group_id in ({})".format(format_strings_grp),
                                tuple(groups))
                            emails = mycursor.fetchall()

                            # mycursor.execute(
                            #     "select group_id, name from group where group_id in ({})".format(
                            #         format_strings_grp), tuple(groups))
                            # grp_details = mycursor.fetchall()

                            sqlQuery = 'select group_id, name from "GROUP" where group_id in ({})'.format(
                                format_strings_grp)

                            mycursor.execute(sqlQuery, tuple(groups))
                            grp_details = mycursor.fetchall()

                            if grp_details:
                                for each in grp_details:
                                    if not trail_grp:
                                        trail_grp += each['name']
                                    else:
                                        trail_grp += ', ' + each['name']

                        else:
                            mycursor.execute(
                                "select (fs_name|| ' '|| ls_name) as name, email, group_id from member "
                                "where member_id in ({})".format(format_strings_mem),
                                tuple(members))
                            emails = mycursor.fetchall()

                        if emails:

                            for each in emails:
                                if not email_str:
                                    email_str = each['email']
                                else:
                                    email_str += ',' + each['email']
                                if not each['group_id'] in groups:
                                    if not trail_grp:
                                        trail_grp += each['name']
                                    else:
                                        trail_grp += ', ' + each['name']

                            audit_trail += trail_grp

                        if values:
                            for i in values:
                                mycursor.execute(
                                "INSERT INTO assignment (isgroup, app, invoice_no) VALUES (?, ?, ?)",
                                tuple(i))

                            values = (invoice_id, '', 'new', audit_trail)
                            sqlQuery = "insert into invoice_audit (invoice_no, prev_status, " \
                                    "new_status, msg) values (?, ?, ?, ?)"
                            mycursor.execute(sqlQuery, values)

                            return True, email_str


                else:
                    values = ("y", 6, invoice_id)
                    mycursor.execute(
                        "INSERT INTO assignment (isgroup, app, invoice_no) VALUES (?, ?, ?)", values)

                    mycursor.execute(
                        "select (fs_name|| ' '||ls_name) as name, email, group_id from member "
                        "where group_id = '6'")
                    emails = mycursor.fetchall()

                    if emails:
                        for each in emails:
                            if email_str:
                                email_str += "," + each['email']
                            else:
                                email_str = each['email']

                    return False, email_str

            return False, email_str

        except Exception as e:
            print(e)
            pass

        finally:
            pass



    pdfTextExtractionJobId = event['params']['querystring']['task_id']
    # pdfTextExtractionJobId = pdfTextExtractionJobId[0]

    pdfTextExtractionStatus = "processed"
    length = len( pdfTextExtractionJobId)
    name = event['body-json']['input_filename']
    

    # # pdfTextExtractionS3ObjectName = json.loads(json.dumps(pdfTextExtractionDocumentLocation))['S3ObjectName']
    # pdfTextExtractionS3ObjectName = 'old-dev/'+ name[length+1::]
    # # pdfTextExtractionS3Bucket = json.loads(json.dumps(pdfTextExtractionDocumentLocation))['S3Bucket']
    pdfTextExtractionS3Bucket = "textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db"


    # client = boto3.client(
    # 'secretsmanager',
    # region_name='eu-central-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )

    secret = "test/einvoice/secret"

    # secret = os.environ.get('secret')

    global elipo_bucket
    elipo_bucket = 'file-bucket-emp'
    # elipo_bucket = os.environ.get('user_cred_bucket')

    global elipo_email
    elipo_email = 'elipotest@gmail.com'
    # elipo_email = os.environ.get('email_notification_mail')


    # global dbScehma

    # resp = client.get_secret_value(
    #     SecretId=secret
    # )

    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    if pdfTextExtractionStatus == 'processed':

        try:
            with mydb.cursor() as mycursor:
                
                values = (pdfTextExtractionJobId, )
                
                mycursor.execute("SELECT * FROM mail_message where job_id = ?", values)
                job_details = mycursor.fetchone()
                
                if job_details:
                    pdfTextExtractionS3ObjectName = job_details['filename']

                faulty_invoice = False

                ocr_folder_name = pdfTextExtractionS3ObjectName.split('/')

                # values = (ocr_folder_name[0],)
                values = ("old-dev",)
                
                mycursor.execute('select * from schemas_confg where ocr_folder = ?', values)
                ocr_folder = mycursor.fetchone()

                defSchemaQuery = "set schema " + ' DBADMIN '
                mycursor.execute(defSchemaQuery)

                dbScehma = ocr_folder['schema_name']


                header = {
                    "status": "new",
                    "ref_po_num": None,
                    "user_invoice_no": None,
                    "company_code": None,
                    "invoice_date": None,
                    "posting_date": "",
                    "baseline_date": "",
                    "payment_terms": None,
                    "payment_method": None,
                    "amount": 0.00,
                    "currency": None,
                    "gl_account": None,
                    "business_area": "",
                    "supplier_id": None,
                    "approver_id": "",
                    "supplier_name": None,
                    "discount": "",
                    "cost_center": None,
                    "tds": None,
                    "npo": None,
                    "is_igst": '',
                    "doc_type": '',
                    "gstin": ''
                }

                headerKeyValues = {
                    'Vendor Name': "",
                    'Vendor Tax ID': "",
                    'Customer Name': "",
                    'Invoice Number': "",
                    'PO Number': "",
                    'Bill of Lading Number': "",
                    'Invoice Date': "",
                    'Due Date': "",
                    'Sub Total': "",
                    'Tax Amount': "",
                    'Total Amount': "",
                    'Amount Paid': "",
                    'Amount Due': "",
                    'Currency': "",
                    'Payment Terms': "",
                }

                for each in event['body-json']['key_value_pairs']:
                    headerKeyValues[each['display_name']] = each['value']

                header['invoice_date'] = clearDate(rawDate=headerKeyValues['Invoice Date'].strip())
                header["user_invoice_no"] = headerKeyValues['Invoice Number'].strip().replace(' ','')
                header["gstin"] = headerKeyValues['Vendor Tax ID'].strip().replace(' ','')
                header["ref_po_num"] = headerKeyValues['PO Number'].strip().replace(' ','')
                # header['doc_type'] =

                header_flags = {'usr_invoice': False,
                                'gstin': False,
                                'pan': False,
                                'invoice_date': False,
                                'posting_date': False,
                                'po': False
                                }


                vendor = {}

                if headerKeyValues['Vendor Name'] or headerKeyValues['Vendor Tax ID']:
                    vendor = find_vendor(mycursor=mycursor,
                                         r_vendor={
                                             'vendor_name': headerKeyValues['Vendor Name'],
                                             'gstin': headerKeyValues['Vendor Tax ID']
                                         },
                                         idate=header['invoice_date']
                            )

                if not vendor:
                    vendor = fetch_default_vendor(mycursor=mycursor,
                                                  idate=header['invoice_date'])

                if vendor:
                    header['currency'] = str(vendor['currency'])
                    header['supplier_name'] = str(vendor['vendor_name'])
                    header['baseline_date'] = str(vendor['due_date'])
                    header["payment_terms"] = str(vendor['payment_terms'])
                    header['supplier_id'] = str(vendor['vendor_code'])
                    header['is_igst'] = str(vendor['is_igst'])
                    header['tds'] = vendor['tds']
                    header['gstin'] = vendor['gstin']

                mycursor.execute(
                    "select value1, value2 from dropdown where drop_key = 'default-master-detail' ")
                default_data = mycursor.fetchall()

                d_currency = None
                d_glaccountItem = None
                d_paymentTerms = None
                d_taxPer = None
                d_tdsPer = None

                for each in default_data:
                    if each['value1'] == 'company_code':
                        header["company_code"] = each['value2']
                    elif each['value1'] == 'cost_center':
                        header["cost_center"] = each['value2']
                    elif each['value1'] == 'currency':
                        d_currency = each['value2']
                    if each['value1'] == 'gl_account_header':
                        header["gl_account"] = each['value2']
                    elif each['value1'] == 'gl_account_item':
                        d_glaccountItem = each['value2']
                    elif each['value1'] == 'payment_method':
                        header["payment_method"] = each['value2']
                    if each['value1'] == 'payment_terms':
                        d_paymentTerms = each['value2']
                    elif each['value1'] == 'plant':
                        header["plant"] = each['value2']
                    elif each['value1'] == 'tax_per':
                        header["tax_per"] = each['value2']
                    elif each['value1'] == 'tds_per':
                        d_tdsPer = each['value2']

                if not header['supplier_id']:
                    header["currency"] = d_currency
                    header["payment_terms"] = d_paymentTerms
                    header['tds'] = d_tdsPer

                    if header['invoice_date'] and d_paymentTerms:
                        if d_paymentTerms == 'On the month end':
                            noofday = str(calendar.monthrange(header['invoice_date'].year, header['invoice_date'].month)[1])
                            header["baseline_date"] = str(
                                (header['invoice_date'] + datetime.timedelta(int(noofday) - int(header['invoice_date'].day))).date())
                        else:
                            header["baseline_date"] = str(
                                (header['invoice_date'] + datetime.timedelta(int(d_paymentTerms))).date())

                npo = None

                if header['ref_po_num']:
                    npo = 'n'
                else:
                    npo = 'y'

                sup_status = ""
                from_supplier = ""

                tename = pdfTextExtractionS3ObjectName.split("/")

                if len(tename) > 1 and tename[1][0] == "S":
                    header["status"] = ""
                    sup_status = "draft"
                    from_supplier = "y"

                sqlQuery = "INSERT INTO invoice_header (in_status, sup_status, from_supplier, user_invoice_id, ref_po_num, " \
                           " company_code, invoice_date, posting_date, baseline_date, amount, currency, payment_method, gl_account," \
                           " business_area, supplier_id, supplier_name, cost_center, is_igst, tds_per, payment_terms, npo, document_type, gstin) " \
                           "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

                # header["posting_date"] = str(datetime.date.today())
                for i in header.keys():
                    if header[i] == 'None'  and type(header[i])==str:
                        header[i] = None
                

                values = (header["status"], sup_status, from_supplier, header["user_invoice_no"], header["ref_po_num"],
                          header["company_code"],
                          header["invoice_date"], header["posting_date"], header["baseline_date"], header["amount"],
                          header["currency"], header["payment_method"], header["gl_account"], header["business_area"],
                          header["supplier_id"], header["supplier_name"], header["cost_center"], header['is_igst'],
                          header['tds'],
                          header["payment_terms"], npo, header['doc_type'], header['gstin'])

                # print(sqlQuery)
                # print(values)
                mycursor.execute(sqlQuery, values)
                mycursor.execute("select (invoice_no) from invoice_header order by invoice_no desc")
                invoice_n = mycursor.fetchone()
                # invoice_no = convertValuesTodict(mycursor.description,invoice_no)
                invoice_no = invoice_n[0]
                
                if not header["user_invoice_no"] or not header["ref_po_num"] or not header["invoice_date"] or not \
                header["supplier_id"]:
                    faulty_invoice = True

                item = {
                    "invoice_no": "",
                    "item_no": "",
                    "material": "",
                    "quantity": "",
                    "amount": "",
                    "payment_method": "",
                    "tax_amount": "",
                    "tax_code": "",
                    "ref_po_no": "",
                    "plant": ""
                }


                # paper-entry format

                rowItemsByPaperAi = []

                for eachItem in event['body-json']['line_items']:

                    d_ItemPaperAi = {
                        'hsn_code': "",
                        'material':"",
                        'material_desc': "",
                        'quantity':0,
                        'unit':"",
                        'amount':0,
                        'currency':"",
                        'amt_per_unit':"",
                        'gst_per':0,
                        'gl_account':""
                    }

                    for each in eachItem:
                        if each == "Product Description":
                            d_ItemPaperAi['material_desc'] = eachItem[each]
                        elif each == "Rate":
                            d_ItemPaperAi['amt_per_unit'] = eachItem[each]
                        elif each == "Unit of Measure":
                            d_ItemPaperAi['unit'] = eachItem[each]
                        elif each == "Quantity":
                            if not eachItem[each]:
                                d_ItemPaperAi['quantity'] = int(0)
                            else:
                                d_ItemPaperAi['quantity'] = eachItem[each]                               
                        elif each == "Currency":
                            d_ItemPaperAi['currency'] = eachItem[each]
                        elif each == "Product Code":
                            d_ItemPaperAi['hsn_code'] = eachItem[each]
                        elif each == "Line Total":
                            d_ItemPaperAi['amount'] = eachItem[each]
                        # elif each == "":
                        #     d_ItemPaperAi[''] = eachItem[each]
                        # elif each == "":
                        #     d_ItemPaperAi[''] = eachItem[each]
                    rowItemsByPaperAi.append(d_ItemPaperAi)

                if rowItemsByPaperAi:
                    
                    # print(rowItemsByPaperAi)     

                    mycursor.execute("SELECT * FROM material_master")
                    materials = mycursor.fetchall()

                    mycursor.execute("SELECT * FROM master where master_id = 6")
                    db_units = mycursor.fetchall()
                    units = []
                    for cur in db_units:
                        units.append(cur['code'])
                    del db_units
                    
                    exclude_lines = ['net price','CGST', 'CGST %', 'CGST @ %',
                                     'SGST', 'SGST %', 'SGST @ %',
                                     'IGST', 'IGST %', 'IGST @ %',
                                     'TOTAL', 'UTGST/SGST', 'Conditions', 
                                     'Exchange Rate USD to EUR', 'Q 10-14898 RECEIVED 19 AUG 2020 Facilities DA']
                                     
                    exclude_no = []
                    
                    
                    # for row in rowItemsByPaperAi:
                    for index, row in enumerate(rowItemsByPaperAi):
                        
                        flag1 = None
                        
                        for exclude in exclude_lines:
                            
                            fuz_dist22 = fuzz.partial_ratio(exclude.lower(), row['material_desc'].lower())
                                    
                            if fuz_dist22 > 70 and not len(exclude) * 4 < len(row['material_desc']):        
                                flag1 = True
                                exclude_no.append(index)
                                break   
                            
                        if flag1:
                            continue

                        match_per = 0
                        db_matnr = {}

                        row['currency'] = row['currency'].strip()

                        row['unit'] = row['unit'].strip()
                        if row['unit'] and not row['unit'] in units:
                            row['unit'] = None

                        if not row['amt_per_unit']:
                            row['amt_per_unit'] = None

                        for mater in materials:

                            value = row['material_desc'][0:48]

                            # print(fuzz.ratio(row_name.lower(), mater['name'].lower()), "ratio")
                            # print(fuzz.token_set_ratio(row_name, mater['name']), "token_set_ratio")
                            # fuz_dist = fuzz.token_set_ratio(value.lower(), mater['material_name'].lower())
                            # fuz_dist = fuzz.ratio(value.lower(), mater['material_name'].lower())

                            fuz_dist = fuzz.WRatio(value.lower(), mater['material_name'].lower())

                            if fuz_dist >= 70 and fuz_dist > match_per:
                                match_per = fuz_dist
                                db_matnr = mater

                        if db_matnr:

                            row['material'] = db_matnr['material_no']
                            row['material_desc'] = db_matnr['material_name']

                            if not row['amt_per_unit']:
                                row['amt_per_unit'] = db_matnr['unit_price']

                            row['hsn_code'] = db_matnr['hsn_code']

                            if not row['unit']:
                                row['unit'] = db_matnr['uom']

                            row['gst_per'] = db_matnr['gst_per']
                            row['gl_account'] = db_matnr['gl_account' \
                                                         '']
                            row['ocr_matched'] = 'y'
                            # row[''] = db_matnr['']

                            # if no rate, quantity and amount there rate = amount
                            # if not quantity then make as 1

                            # df.loc[index, 'gross_amount'] = amoty + (
                            #         amoty * (int(db_matnr['gst_per']) / 100))

                        else:
                            row['ocr_matched'] = 'n'

                    if exclude_no:
                        temp_rowItems = rowItemsByPaperAi
                        rowItemsByPaperAi = []
                        
                        for index, eachItm in enumerate(temp_rowItems):
                            if index not in exclude_no:
                                rowItemsByPaperAi.append(eachItm)
                                
                        del temp_rowItems
                                
                    del exclude_no
                    del exclude_lines   
                    

                    sqlFields = "invoice_no, item_no"
                    sqlPer = "?, ?"

                    # item_category = fetchSAP_PoDetails(header['ref_po_num'])

                    # supplier_type = ''
                    # vendor_no = ''
                    # vendor_currency = ''

                    # if vendor:
                    #     if vendor['gst_treatment'] == 'overseas':
                    #         supplier_type = 'export'
                    #     else:
                    #         supplier_type = 'domestic'

                    #     vendor_no = header['supplier_id']
                    #     vendor_currency = header['currency']

                    # d_decider = {
                    #     'supplier_type': supplier_type,
                    #     'invoice_value': headerAmount,
                    #     'invoice_type': item_category,
                    #     'vendor_no': vendor_no,
                    #     'currency': vendor_currency,
                    #     'document_type': header['doc_type']
                    # }

                    # success, emails = assign_approcessor(mycursor=mycursor, invoice_id=invoice_no, decider=d_decider)
    
                    row = rowItemsByPaperAi[0]  
                    
                    for each in row:
                        sqlFields = sqlFields + ", " + str(each)
                        sqlPer = sqlPer + ", ?"

                    # if flag['quantity']:
                    #     sqlFields = sqlFields + ", " + "quantity"
                    #     sqlPer = sqlPer + ", ?"

                    # print("SQL FIELDS", sqlFields)
                    # print("SQL PERCENTAGE", sqlPer)

                    # for line in final_values:
                    #     print(int(line))

                    try:
                        sqlQuery = "INSERT INTO invoice_item ( " + sqlFields + ") " \
                                                                               "VALUES ( " + sqlPer + " )"

                        final_values = []
                        for index, row in enumerate(rowItemsByPaperAi):

                            raw_list = [invoice_no,index+1]

                            for value in row.values():
                                raw_list.append(value)

                            final_values.append(tuple(raw_list))
                            mycursor.execute(sqlQuery, tuple(raw_list))

                        print(sqlQuery)
                        print(final_values)

                        

                    except Exception as e:
                        print(e, "ened")

                else:
                    faulty_invoice = True

                # item_category = fetchSAP_PoDetails(header['ref_po_num'])
                
                item_category = []

                supplier_type = ''
                vendor_no = ''
                vendor_currency = ''

                if vendor:
                    if vendor['gst_treatment'] == 'overseas':
                        supplier_type = 'export'
                    else:
                        supplier_type = 'domestic'

                    vendor_no = header['supplier_id']
                    vendor_currency = header['currency']

                d_decider = {
                    'supplier_type': supplier_type,
                    # 'invoice_value': headerAmount,
                    'invoice_value': 0,
                    'invoice_type': item_category,
                    'vendor_no': vendor_no,
                    'currency': vendor_currency,
                    'document_type': header['doc_type']
                }

                success, emails = assign_approcessor(mycursor=mycursor, invoice_id=invoice_no, decider=d_decider)

                flagg = 'n'
                if faulty_invoice:
                    flagg = 'y'

                link = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/dev/attachment?file_name=" \
                       + pdfTextExtractionS3ObjectName + "&bucket=" + pdfTextExtractionS3Bucket

                filenamett, file_extension = os.path.splitext(pdfTextExtractionS3ObjectName)

                # print(file_extension)
                content_type = ''

                if file_extension == ".pdf":
                    content_type = "application/pdf"
                elif file_extension == ".png":
                    content_type == "image/png"
                elif file_extension == ".jpg":
                    content_type == "image/jpg"
                elif file_extension == ".jpeg":
                    content_type == "image/jpg"

                values = (invoice_no, pdfTextExtractionS3ObjectName, content_type, pdfTextExtractionS3Bucket, link)
                sqlQuery = "INSERT INTO file_storage (file_id, name, mime_type, file_path, file_link) VALUES ( ?, ?, ?, ?, ?)"

                mycursor.execute(sqlQuery, values)

                values = (invoice_no, pdfTextExtractionS3ObjectName)
                mycursor.execute(
                    "UPDATE mail_message SET invoice_no = ? WHERE filename = ?", values)
                print(values)

                mycursor.execute("SELECT * FROM elipo_setting where key_name = 'approval_auto_trigger'")
                detgb = mycursor.fetchone()

                res = False
                instatus = "new"

                if detgb:
                    if detgb['value1'] == "on":

                        if flagg != "y":

                            npo = ""

                            if header['ref_po_num']:
                                npo = "y"
                            else:
                                npo = "n"

                            r_decider = {
                                'discount': 0,
                                # 'amount': headerAmount,
                                'amount': 0,
                                'cost_center': "",
                                'currency': header['currency'],
                                'gl_account': str(header["gl_account"]),
                                'npo': header["npo"],
                                'vendor_no': str(header["supplier_id"]),
                                'department_id': "",
                                'item_category': item_category,
                                'document_type': header['doc_type']
                            }

                            res = create_approvals(mycursor=mycursor, invoice_id=invoice_no, decider=r_decider,
                                                   working_person="ocr")

                if res == False:
                    # if emails:
                    #     sendMailNotifications(invoice_id=invoice_no, emails=emails)
                    pass
                else:
                    instatus = "inapproval"

                sqlQuery = "update invoice_header set in_status = ?, amount = ?, faulty_invoice= ? " \
                           "where invoice_no = ?"
                # values = (instatus, str(headerAmount), flagg, invoice_no)
                values = (instatus, str(0), flagg, invoice_no)

                mycursor.execute(sqlQuery, values)

                mydb.commit()

        except Exception as e:
            print(e)
            mydb.rollback()

            try:
                with mydb.cursor() as mycursor:

                    values = (pdfTextExtractionS3ObjectName,)
                    # mycursor.execute("DELETE FROM mail_message WHERE filename = ?", values)
                    mycursor.execute(
                        "UPDATE mail_message SET is_processed = 'n' WHERE filename = ?",
                        values)

                    mydb.commit()

            finally:
                pass

        finally:
            sap_responce = s.post(url, json=event)
            mydb.close()

    else:

        try:
            with mydb.cursor() as mycursor:

                values = ("new",)

                mycursor.execute("INSERT INTO invoice_header (in_status) VALUES (?)", values)

                invoice_no = mycursor.lastrowid

                link = "https://l8m6p8a76e.execute-api.eu-central-1.amazonaws.com/dev/attachment?file_name=" \
                       + pdfTextExtractionS3ObjectName + "&bucket=" + pdfTextExtractionS3Bucket

                filenamett, file_extension = os.path.splitext(pdfTextExtractionS3ObjectName)

                # print(file_extension)
                content_type = ''

                if file_extension == ".pdf":
                    content_type = "application/pdf"
                elif file_extension == ".png":
                    content_type == "image/png"
                elif file_extension == ".jpg":
                    content_type == "image/jpg"
                elif file_extension == ".jpeg":
                    content_type == "image/jpg"

                values = (invoice_no, pdfTextExtractionS3ObjectName, content_type, pdfTextExtractionS3Bucket, link)
                sqlQuery = "INSERT INTO file_storage (file_id, name, mime_type, file_path, file_link) VALUES ( ?, ?, ?, ?, ?)"

                mycursor.execute(sqlQuery, values)

                values = (invoice_no, pdfTextExtractionS3ObjectName)
                mycursor.execute(
                    "UPDATE mail_message SET invoice_no = ? WHERE filename = ?", values)

                # values = (pdfTextExtractionS3ObjectName,)
                # # mycursor.execute("DELETE FROM mail_message WHERE filename = ?", values)
                # mycursor.execute("UPDATE mail_message SET is_processed = 'n' WHERE filename = ?",
                #                  values)
                mydb.commit()

        except Exception as e:
            print(e)
            mydb.rollback()

        finally:
            sap_responce = s.post(url, json=event)
            mydb.close()
            
# postSapError
# from here secretsmanager not done
def postSapError(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    list_item = []

    try:
        for row in event["body-json"]:
            record = {
                "type": "", 
                "msg": ""
            }
            
            for value in row:
                if value in record:
                    record[value] = row[value]
            list_item.append(record)
            
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "invoice_no" in event["params"]["querystring"]:
                invoice_no = str(event["params"]["querystring"]["invoice_no"])
                # print(invoice_no)
                
                error_list = []
                for count, each in enumerate(list_item, 1):
                    if count == 1:
                        mycursor.execute("delete from sap_error_log where invoice_no = %s", invoice_no)
                        
                    error_dict = ( invoice_no, str(count), each["type"], each["msg"] )
                    error_list.append(error_dict)
                
                sqlQuery = "insert into sap_error_log (invoice_no, item, error_type, error_msg) values (%s, %s, %s, %s)"
                # print(sqlQuery, error_list)
                mycursor.executemany(sqlQuery, error_list)
            
                mydb.commit()
    
    except Exception as e:  
        mydb.rollback()
        return {
            'statuscode': 500, 
            'body': json.dumps("Internal Failure")
        }
        
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Successful!"),
    }

# getReportInvoices
def getReportInvoices(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
    
    records = {}
    # print(event)

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "invoice_no" in event["params"]["querystring"]:
                
                items = []
                
                values = (event["params"]["querystring"]["invoice_no"],)
                mycursor.execute("select * from invoice_header where invoice_no = %s", values)
    
                invoice_header = mycursor.fetchone()
                
                records = {
                    
                    "invoice_no" :invoice_header["invoice_no"],
                    "in_status" : invoice_header["in_status"],
                    "ref_po_num" : invoice_header["ref_po_num"],
                    "company_code" : invoice_header["company_code"],
                    "invoice_date" : str(invoice_header["invoice_date"]),
                    "posting_date" : str(invoice_header["posting_date"]),
                    "amount" : invoice_header["amount"],
                    "currency" : invoice_header["currency"],
                    "gl_account" : invoice_header["gl_account"],
                    "business_area" : invoice_header["business_area"],
                    "supplier_id" : invoice_header["supplier_id"],
                    "supplier_name" : invoice_header["supplier_name"],
                    "approver_id" : invoice_header["approver_id"],
                    "approver_comments" : invoice_header["approver_comments"],
                    "items" : items
                }
                
                mycursor.execute("select * from invoice_item where invoice_no = %s", values)
                
                for row in mycursor:
                    record = {
                      "item_no":row["item_no"],
                      "material":row["material"],
                      "quantity":row["quantity"],
                      "amount":row["amount"],
                      "payment_method":row["payment_method"],
                      "tax_amount":row["tax_amount"],
                      "tax_code":row["tax_code"],
                      "ref_po_no":row["ref_po_no"],
                      "plant":row["plant"]
                      }
                    items.append(record)
                    
                records["items"] = items
                
            
            elif "condn" in event["body-json"]:
            
                val_list = []
                pos = 0
                condn = ""
                records = {}
    
                for row in event["body-json"]["condn"]:
                    if pos != 0:
                        condn = condn + " and "
                    elif pos == 0:
                        pos = pos + 1
    
                    if str(row["operator"]) == "like":
                        val_list.append("%" + row["value"] + "%")
                    else:
                        val_list.append(row["value"])
                    
                    condn = condn + row["field"] + " " + str(row["operator"]) + " " + "%s"
                    
                sqlQuery = "SELECT invoice_no, in_status, invoice_date, posting_date, supplier_name, " \
                            "ref_po_num, amount FROM invoice_header" \
                            " where " + condn
        
                values = tuple(val_list,)
                # print(condn)
        
                mycursor.execute(sqlQuery, values)
        
                invoices = []
                invoice_files = [{"file_name":"dumb"}]
        
                for row in mycursor:
                    record = {
                          "invoice_no":row["invoice_no"],
                          "in_status":row["in_status"],
                          "invoice_date":str(row["invoice_date"]),
                          "due_date":str(row["posting_date"]),
                          "supplier_name":row["supplier_name"],
                          "ref_po_num": row["ref_po_num"],
                          "amount":row["amount"],
                          'invoice_files' : invoice_files
                    }
                    invoices.append(record)
                        
                records["invoices"] = invoices
            
            else:
                
                invoices = []
                invoice_files = [{"file_name":"dumb"}]
                
                records = {}
                # mycursor.execute("select * from invoice_header where date(invoice_date) > date(now() - interval 7 day)")
                
                mycursor.execute("select invoice_no, in_status, invoice_date, posting_date, supplier_name,"
                " ref_po_num, amount FROM invoice_header where date(invoice_date) > date(now() - interval 7 day)")
                     
                invoices = []
                    
                for row in mycursor:
                    record = {
                          "invoice_no":row["invoice_no"],
                          "in_status":row["in_status"],
                          "invoice_date":str(row["invoice_date"]),
                          "due_date":str(row["posting_date"]),
                          "supplier_name":row["supplier_name"],
                          "ref_po_num": row["ref_po_num"],
                          "amount":row["amount"],
                          'invoice_files' : invoice_files
                    }
                    invoices.append(record)
                records["invoices"] = invoices
                     
                
    except:
        return {
        'statuscode': 500,
        'body': json.dumps("error occured while fetching") 
    }
            
    finally:
        mydb.close()
        
    # if not records["invoice_no"]:
    #     return {
    #         'statuscode': 200,
    #         'body': json.dumps("no matching records check key")
    #     }
    return {
        'statuscode': 200,
        'body': records
    }

# getSearchDetailsSup
def getSearchDetailsSup(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            srch_field = []
            
            sqlQuery = "select s.operator, s.ui_element, s.search_id, s.is_multivalued, " \
            " s.help_required, d.value2 from serach_options s inner join" \
            " dropdown d on s.operator = d.value1 where s.search_field = %s and d.drop_key = 'operators'"
                
            values = (event["params"]["querystring"]["search_field"],)

            mycursor.execute(sqlQuery, values)
                    
            for row in mycursor:
                record = {
                    # 'search_field': row["search_field"],
                    'operator': row["operator"],
                    'operator_name' : row["value2"],
                    'ui_element': row["ui_element"],
                    'search_id': row["search_id"],
                    'is_multivalued': row["is_multivalued"],
                    'help_required': row["help_required"]
                }
                srch_field.append(record)

            records["srch_field"] = srch_field
            
    except:
        return {
        'statuscode': 500,
        'body': json.dumps("Internal Failure!") 
    }
                    
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': records,
    }

# getSearchHelp
def getSearchHelp(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = {}
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            search_help = []
            
            if "master_id" in event["params"]["querystring"] and "description" in event["params"]["querystring"]:
                
                sqlQuery = "select code, master_name, description from master where master_id = %s and description like %s"
                temp = event["params"]["querystring"]["description"] + "%%"
                values = (event["params"]["querystring"]["master_id"], temp)
                mycursor.execute(sqlQuery, values)
                
                for row in mycursor:
                    record = {
                        'code': row['code'],
                        'master_name': row['master_name'], 
                        'description': row['description']
                    }
                    search_help.append(record)
                records['search_help'] = search_help 
                
            elif "master_id" in event["params"]["querystring"] and event["params"]["querystring"]["master_id"] == "8":
                        
                mycursor.execute("select * from material_master")
                        
                for row in mycursor:
                    record = {
                        "master_id" : event["params"]["querystring"]["master_id"],
                        "material_no" : row["material_no"], 
                        "material_name" : row["material_name"], 
                        "gst_per" : row["gst_per"], 
                        "unit_price" : row["unit_price"], 
                        "gl_account" : row["gl_account"]
                    }
                    search_help.append(record)
                records['search_help'] = search_help
                
            elif "master_id" in event["params"]["querystring"]:
                
                sqlQuery = "select code, master_name, description from master where master_id = %s"
                values = (event["params"]["querystring"]["master_id"])
                mycursor.execute(sqlQuery, values)
                
                for row in mycursor:
                    record = {
                        'code': row['code'],
                        'master_name': row['master_name'], 
                        'description': row['description']
                    }
                    search_help.append(record)
                records['search_help'] = search_help 
    
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

# getReportSearchHelp
def getReportSearchHelp(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            search_help = []
            
            if "col_name" in event["params"]["querystring"]:
                colName = event["params"]["querystring"]["col_name"]
                mycursor.execute("select * from dropdown where drop_key = %s", colName)
                
                for row in mycursor:
                    record = {
                        'master_name': colName, 
                        'code': row['value1'],
                        'description': row['value2'] 
                    }
                    search_help.append(record)
                records['search_help'] = search_help   
            
            if "in_status" in event["params"]["querystring"]:
                mycursor.execute("select * from dropdown where drop_key = 'document_status' ")
                
                for row in mycursor:
                    record = {
                        'master_name': "Document Status", 
                        'code': row['value1'],
                        'description': row['value2'] 
                    }
                    search_help.append(record)
                records['search_help'] = search_help 
                
            if "payment_terms" in event["params"]["querystring"]:
                mycursor.execute("select * from dropdown where drop_key = 'payment_term' ")
                
                for row in mycursor:
                    record = {
                        'master_name': "Payment Terms", 
                        'code': row['value1'],
                        'description': row['value2'] 
                    }
                    search_help.append(record)
                records['search_help'] = search_help 
                
            if "roles" in event["params"]["querystring"]:
                mycursor.execute("select * from dropdown where drop_key = 'user_type' ")
                
                for row in mycursor:
                    record = {
                        'master_name': "Roles", 
                        'code': row['value1'],
                        'description': row['value2'] 
                    }
                    search_help.append(record)
                records['search_help'] = search_help 
                
            if "po_type" in event["params"]["querystring"]:
                mycursor.execute("select * from dropdown where drop_key = 'po_type' ")
                
                for row in mycursor:
                    record = {
                        'master_name': "PO Type", 
                        'code': row['value1'],
                        'description': row['value2'] 
                    }
                    search_help.append(record)
                records['search_help'] = search_help
                
            if "department" in event["params"]["querystring"]:
                mycursor.execute("select department_id, department_name from departmental_budget_master")
                
                for row in mycursor:
                    record = {
                        'master_name': "Department", 
                        'code': row['department_id'],
                        'description': row['department_name'] 
                    }
                    search_help.append(record)
                records['search_help'] = search_help
                
            if "document_type" in event["params"]["querystring"]:
                mycursor.execute("select * from dropdown where drop_key = 'document_type' order by value2 desc")
                
                for row in mycursor:
                    record = {
                        'master_name': "Document Type", 
                        'code': row['value1'],
                        'description': row['value2'] 
                    }
                    search_help.append(record)
                records['search_help'] = search_help
                
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

# getVendorSearchHelp
def getVendorSearchHelp(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    # TODO implement
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = {}
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute("SELECT vendor_no, vendor_name FROM vendor_master")
            
            search_help = []
            for vendor in mycursor:
                record = {
                    "code" : vendor["vendor_no"],
                    "description" : vendor["vendor_name"]
                }
                search_help.append(record)
                
            records["search_help"] = search_help
            
    except :
        
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }
            
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': records
    }

# postInvoiceDetailsSup

class FailedToCreateApprocalsException(Exception):
    """"""

def notify_approvers(members, body):
    pass

class ApprovalException(Exception):
    pass

def get_stored_credentials(user_id):
    try:
        s3 = boto3.client("s3")
        encoded_file = s3.get_object(Bucket=elipo_cred, Key=user_id)   
        creds = pickle.loads(encoded_file["Body"].read())
        return creds
    except Exception as excep:
        creds = None

def create_message(sender, to, cc, subject, message_text):
    message = email.mime.text.MIMEText(message_text, 'html')
    message['to'] = to
    message['cc'] = cc
    message['from'] = sender
    message['subject'] = subject
    encoded = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {'raw': encoded.decode("utf-8")}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        return message
    except Exception as error:
        print("An error occurred: ", error)

def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)

def sendMailNotifications(invoice_id, mycursor, emails):
    
    user_id = elipo_email
    credentials = get_stored_credentials(user_id)

    if credentials and credentials.refresh_token is not None:
        service = build_service(credentials=credentials)

        mycursor.execute("select * from rule_notification where invoice_status = 'sup-sendto-customer'")
        notification = mycursor.fetchone()

        mail_cc = ''
        mail_subject = 'ELIPO Notification'
        mail_body = ''

        if notification:
            if notification['subject']:
                mail_subject = notification['subject']
            if notification['mail_cc']:
                mail_cc = notification['mail_cc']
            if notification['body']:
                mail_body = notification['body']

        body = '''<a href="https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/production/landing/invoice/my-inbox">My Inbox</a> '''

        message_body = '''<html>
            <body  >
                <div style=" width:30%;">
                        <div style=" width:100%; align-content: center;text-align: center;">
                            <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/ELIPO+logo.png" alt="Italian Trulli" style="vertical-align:middle; width: 140px;height:50px;text-align: center;"  >
                        </div>
                	<div style=" width:100%; align-content:left;text-align:left;">
                            <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                        </div>
                    <b>

                    <span style="vertical-align: middle;text-align: left;font: 600 bold 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Dear User,  
                    </span> 
                    <br>            
                    <br> {}
                    <br>
                    <span style="vertical-align: middle;text-align: left;font: 600 bold 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;" >
                        Invoice No: <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">{},</span>
                    </span>
                    </b> 
                    <br>
                    <br>
                    <div style=" width:100%;align-content: center;text-align: center;">
                        <a href="https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/production/login" target="_blank">
                            <button style="border: none; background:rgb(80, 219, 212) 0% 0% no-repeat padding-box; border-radius: 7px;opacity: 1;width:180px; height: 35px;outline: none;border: none;" > 
                                <span style="vertical-align: middle; text-align: left;font: 600 bold 16px/23px Open Sans;letter-spacing: 0px;color: whitesmoke;white-space: nowrap;opacity: 1;">Login to ELIPO</span>
                            </button>
                        </a>
                    </div>

                    <br><br>
                    <div style="width:100%;"> 
                    <span style="vertical-align: middle; text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Regards,</span>
                    <br>
                    <span style="vertical-align: middle;text-align: left;font: 500  16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 1;">Team ELIPO</span>
                    </div>
                <div style=" width:100%; align-content:left;text-align:left;">
                            <hr style="width:100%; text-align: center; border: 2px solid #0000001A;opacity: 0.5; border-radius: 2px;" >
                        </div>


                    <div style="width:100%;align-content: center;text-align: center;">
                        <span style=" text-align: center;font: 600 bold 16px/23px Open Sans;letter-spacing: 0px;color: #000000;white-space: nowrap;opacity: 0.7;">This message was sent to you by ELIPO</span>
                    </div>
                    <div style="width:100%;align-content: center;text-align: center;">
                        <img src="https://einvoice-public-images.s3.ap-south-1.amazonaws.com/elipo+logo_2.png" alt="Italian Trulli" style="text-align: center;width: 90px;height: 50px;" >
                    </div>

                    <br>
                </div>
            </body></html>'''.format(mail_body, invoice_id)

        message = create_message(sender=user_id, to=emails, cc=mail_cc, subject=mail_subject, message_text=message_body)
        send_message(service=service, user_id="me", message=message)


def fetchSAP_PoDetails(poNumber):
    s = requests.Session()
    s.headers.update({'Connection': 'keep-alive'})

    url = "http://182.72.219.94:8000/zgetpo/GetPo"
    params = {'sap-client': '800'}

    headersFetch = {'X-CSRF-TOKEN': 'Fetch'}
    y = s.get(url, auth=HTTPBasicAuth('developer31', 'peol@123'), headers=headersFetch, params=params)
    token = y.headers["X-CSRF-TOKEN"]

    headers = {"X-CSRF-TOKEN": token, 'Content-type': 'application/json'}
    records = {
        "ebeln": poNumber
    }

    x = s.post(url, json=records, auth=HTTPBasicAuth('developer31', 'peol@123'), headers=headers, params=params)

    payload = x.json()

    item_category = []
    for each in payload[0]['POITEM']:
        item_category.append(each['ITEM_CAT'])

    return item_category


def assign_approcessor(mycursor, invoice_id, decider):

    email_str = ''      

    try:
        mycursor.execute("select * from elipo_setting where key_name = 'app_assignment'")
        setting = mycursor.fetchone()

        if setting["value1"] == 'on':
            mycursor.execute("SELECT a.* FROM rule a inner join rule_snro b"
                             " on a.rule_id = b.rule_id "
                             "where b.is_approval = 'n' and a.is_on = 'y'")
            all_rules = mycursor.fetchall()

            rule_ids = []
            email_str = ''

            if all_rules:
                rule_ids = [sub['rule_id'] for sub in all_rules]
                rule_ids = set(rule_ids)
                rule_ids = list(rule_ids)

                rule = []
                rules = {}

                for ruleId in rule_ids:
                    rules[ruleId] = []

                default = None

                for row in all_rules:
                    if row['decider'] == 'default_assignment':
                        default = row
                    else:
                        rules[row['rule_id']].append(row)

                if default:
                    rule_ids.remove(default['rule_id'])
                    del rules[default['rule_id']]

            if rule_ids:
                for eachRule in rules:

                    countMatches = 0
                    noOfCondn = len(rules[eachRule])

                    for row in rules[eachRule]:

                        if row['decider_type'] == "number":

                            if row['decider'] == "invoice_value":
                                d_value = float(decider[row['decider']])
                            else:
                                d_value = int(decider[row['decider']])

                            if row['operator'] == "=" and d_value == int(row['d_value']):
                                countMatches += 1
                            elif row['operator'] == ">" and d_value > int(row['d_value']):
                                countMatches += 1
                            elif row['operator'] == "<" and d_value < int(row['d_value']):
                                countMatches += 1
                            elif row['operator'] == "between" and int(row['d_value']) <= d_value <= int(
                                    row['d_value2']):
                                countMatches += 1

                        elif row['decider_type'] == "string":
                            if row["decider"] == "invoice_type":
                                for each in decider["invoice_type"]:
                                    if each == str(row['d_value']):
                                        countMatches += 1
                                        break

                            elif decider[row['decider']] == str(row['d_value']):
                                countMatches += 1

                    if noOfCondn == countMatches:
                        rule.append(row)

            if not rule and default:
                rule.append(default)

            if rule:

                values = [sub['rule_id'] for sub in rule]
                values = set(values)
                values = list(values)

                format_strings = ','.join(['%s'] * len(values))

                sqlQuery = "select isgroup, approver from rule_approver where rule_key in (%s) " % format_strings
                mycursor.execute(sqlQuery, tuple(values))
                all_app = mycursor.fetchall()

                all_approvers = [dict(t) for t in {tuple(d.items()) for d in all_app}]

                groups = []
                members = []
                values = []

                for row in all_approvers:
                    value = (row['isgroup'], row['approver'], invoice_id)
                    values.append(value)

                    if row['isgroup'] == 'y':
                        groups.append(row['approver'])
                    else:
                        members.append(row['approver'])

                format_strings_grp = ','.join(['%s'] * len(groups)) 
                format_strings_mem = ','.join(['%s'] * len(members))
                emails = None

                audit_trail = 'Invoice No ' + str(invoice_id) + ' assigned to '
                trail_grp = ''

            else:
                groups = []
                mycursor.execute("select group_id from " + dbScehma + ".group where name = 'Shared Service User'")
                grp_det = mycursor.fetchone()

                if grp_det:
                    groups.append(grp_det["group_id"])

            if members and groups:
                mix = members + groups
                mycursor.execute(
                    "select concat(fs_name, ' ', ls_name) as name, email, group_id from member "
                    "where member_id in ({}) or group_id in ({})".format(format_strings_mem, format_strings_grp),
                    tuple(mix))
                emails = mycursor.fetchall()

                mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in ({})".format(
                    format_strings_grp), tuple(groups))
                grp_details = mycursor.fetchall()

                if grp_details:
                    for each in grp_details:
                        if not trail_grp:
                            trail_grp += each['name']

                        else:
                            trail_grp += ', ' + each['name']

            elif groups:
                mycursor.execute(
                    "select concat(fs_name, ' ', ls_name) as name, email, group_id from member "
                    "where group_id in ({})".format(format_strings_grp), tuple(groups))
                emails = mycursor.fetchall()

                mycursor.execute("select group_id, name from " + dbScehma + ".group where group_id in ({})".format(
                    format_strings_grp), tuple(groups))
                grp_details = mycursor.fetchall()

                if grp_details:
                    for each in grp_details:
                        if not trail_grp:
                            trail_grp += each['name']
                        else:
                            trail_grp += ', ' + each['name']

            else:
                mycursor.execute(
                    "select concat(fs_name, ' ', ls_name) as name, email, group_id from member "
                    "where member_id in ({})".format(format_strings_mem), tuple(members))
                emails = mycursor.fetchall()

            if emails:
                for each in emails:
                    if not email_str:
                        email_str = each['email']

                    else:
                        email_str += ',' + each['email']

                    if not each['group_id'] in groups:
                        if not trail_grp:
                            trail_grp += each['name']

                        else:
                            trail_grp += ', ' + each['name']

                audit_trail += trail_grp

            if values:
                mycursor.executemany(
                    "INSERT INTO assignment (isgroup, app, invoice_no) VALUES (%s, %s, %s)", values)

                values = (invoice_id, '', 'new', audit_trail)
                sqlQuery = "insert into invoice_audit (invoice_no, prev_status, new_status, msg) values (%s, %s, %s, %s)"
                mycursor.execute(sqlQuery, values)

                return True, email_str

            else:
                return False, email_str

        else:
            values = ("y", 6, invoice_id)
            mycursor.execute(
                "INSERT INTO assignment (isgroup, app, invoice_no) VALUES (%s, %s, %s)", values)

            mycursor.execute(
                "select concat(fs_name, ' ', ls_name) as name, email, group_id from member "
                "where group_id = '6'")
            emails = mycursor.fetchall()

            if emails:
                for each in emails:
                    if email_str:
                        email_str += "," + each['email']
                    else:
                        email_str = each['email']
            print(email_str)
            return False, email_str

    except Exception as e:
        print(e)
        pass

    finally:
        pass


def postInvoiceDetailsSup(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
 
    global elipo_email
    elipo_email = event["stage-variables"]["notification_email"]
    
    global elipo_cred
    elipo_cred = event["stage-variables"]['bucket_gmail_credential']
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )
    secret = event["stage-variables"]["secreat"]
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
        cursorclass=pymysql.cursors.DictCursor
    )

    header = {
        "user_invoice_id": "",
        "sup_status": "",
        "ref_po_num": "",
        "posting_date": "",
        "invoice_date": "",
        "baseline_date": "",
        "amount": "",
        "payment_method": "",
        "currency": "",
        "taxable_amount": "",
        "discount_per": "",
        "total_discount_amount": "",
        "is_igst": "",
        "tax_per": "",
        "cgst_tot_amt": "",
        "sgst_tot_amt": "",
        "igst_tot_amt": "",
        "tds_per": "",
        "tds_tot_amt": "",
        "payment_terms": "",
        "adjustment": "",
        "tcs": 0,
        "approver_comments": "",
        "working_person": "",
        "supplier_name": "",
        "npo": "",
        "document_type": "",
        "gstin": "",
        "irn": ""
    }

    list_item = []
    response = {}
    msg = "Provide invoice status!"
    tb_data = {}
    values = {}

    try:
        for value in event["body-json"]["header"]:
            if value in header:
                header[value] = event["body-json"]["header"][value]

        for row in event["body-json"]["item"]:
            item = {
                "invoice_no": "",
                "item_no": "",
                "hsn_code": "",
                "material": "",
                "material_desc": "",
                "quantity": "",
                "unit": "",
                "currency": "",
                "amt_per_unit": "",
                "cgst_per": "",
                "cgst_amount": "",
                "tax_code": "",
                "plant": "",
                "discount": "",
                "discount_amount": "",
                "gross_amount": 0,
                "sgst_per": "",
                "sgst_amount": "",
                "igst_per": "",
                "igst_amount": "",
                "taxable_amount": "",
                "tax_value_amount": "",
                "gl_account": "",
                "gst_per": ""
            }
            for value in row:
                if value in item:
                    item[value] = row[value]
            list_item.append(item)
            
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if header["sup_status"] == "inapproval" or header["sup_status"] == "draft":

                if "invoice_no" not in event["params"]["querystring"]:

                    if header["sup_status"] == "inapproval":

                        user_id = event["params"]["querystring"]["userid"]
                        in_status = "new"

                        vendor = ""

                        mycursor.execute("select a.fs_name, a.ls_name, b.vendor_no, b.currency, b.gst_treatment " \
                            "from member a " \
                            "left join vendor_master b " \
                            "on a.member_id = b.member_id " \
                            "where a.email = %s", user_id)
                        member = mycursor.fetchone()

                        if member:
                            vendor = member['vendor_no']
                            header["working_person"] = member['fs_name'] + " " + member['ls_name']

                        sqlQuery = "INSERT INTO invoice_header (user_invoice_id, in_status, sup_status, ref_po_num, invoice_date," \
                                   "baseline_date, posting_date, amount, payment_method, currency, taxable_amount, discount_per, total_discount_amount, is_igst, tax_per, " \
                                   "cgst_tot_amt, sgst_tot_amt, igst_tot_amt, tds_per, tds_tot_amt, payment_terms, adjustment, tcs, supplier_comments, supplier_id, " \
                                   "from_supplier, working_person, supplier_name, npo, document_type, gstin, irn) " \
                                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                        values = (header["user_invoice_id"], in_status, header["sup_status"], header["ref_po_num"], header["invoice_date"], \
                                  header["baseline_date"], header["posting_date"], header["amount"], header["payment_method"], header["currency"], header["taxable_amount"], \
                                  header["discount_per"], header["total_discount_amount"], header["is_igst"], header["tax_per"], header["cgst_tot_amt"], \
                                  header["sgst_tot_amt"], header["igst_tot_amt"], header["tds_per"], header["tds_tot_amt"], header["payment_terms"], header["adjustment"], \
                                  header["tcs"], header["approver_comments"], vendor, 'y', header['working_person'], header["supplier_name"], header["npo"], header["document_type"], \
                                  header["gstin"], header["irn"])
                        
                        mycursor.execute(sqlQuery, values)

                        invoice_num = mycursor.lastrowid

                        msg = "Invoice " + str(invoice_num) + " created and submitted to customer."

                        response = {
                            "invoice_no": invoice_num,
                            "msg": msg
                        }

                    elif header["sup_status"] == "draft":

                        user_id = event["params"]["querystring"]["userid"]

                        in_status = ""
                        vendor = ""

                        mycursor.execute("select a.fs_name, a.ls_name, b.vendor_no, b.vendor_no, b.currency, b.gst_treatment " \
                            "from member a " \
                            "left join vendor_master b " \
                            "on a.member_id = b.member_id " \
                            "where a.email = %s", user_id)
                        member = mycursor.fetchone()

                        if member:
                            vendor = member['vendor_no']
                            header["working_person"] = member['fs_name'] + " " + member['ls_name']

                        sqlQuery = "INSERT INTO invoice_header (user_invoice_id, in_status, sup_status, ref_po_num, invoice_date, posting_date, baseline_date, " \
                            "amount, payment_method, currency, taxable_amount, discount_per, total_discount_amount, is_igst, tax_per, cgst_tot_amt, sgst_tot_amt, igst_tot_amt," \
                            " tds_per, tds_tot_amt, payment_terms, adjustment, tcs, supplier_comments, from_supplier, working_person, supplier_name, document_type, gstin, irn) " \
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

                        values = (header["user_invoice_id"], in_status, header["sup_status"], header["ref_po_num"], header["invoice_date"], header["posting_date"], \
                            header["baseline_date"], header["amount"], header["payment_method"], header["currency"], header["taxable_amount"], \
                            header["discount_per"], header["total_discount_amount"], header["is_igst"], header["tax_per"], header["cgst_tot_amt"], \
                            header["sgst_tot_amt"], header["igst_tot_amt"], header["tds_per"], header["tds_tot_amt"], header["payment_terms"], \
                            header["adjustment"], header["tcs"], header["approver_comments"], 'y', header['working_person'], header['supplier_name'], \
                            header["document_type"], header["gstin"], header["irn"])
                        
                        mycursor.execute(sqlQuery, values)
                        invoice_num = mycursor.lastrowid

                        msg = "Invoice No " + str(invoice_num) + " created and saved as draft."

                        response = {
                            "invoice_no": invoice_num,
                            "msg": msg
                        }

                    del sqlQuery
                    del values

                    headerAmount = 0.00

                    if invoice_num:

                        itemValue = []

                        for row in list_item:
                            item = ( str(invoice_num), row["item_no"], row["hsn_code"], row["material"], row["material_desc"], row["quantity"], row["unit"], row["currency"],
                            row["amt_per_unit"], row["cgst_per"], row["cgst_amount"], row["tax_code"], row["plant"], row["discount"],
                            row["discount_amount"], row["gross_amount"], row["sgst_per"], row["sgst_amount"], row["igst_per"], row["igst_amount"],
                            row["taxable_amount"], row["tax_value_amount"], row["gl_account"], row["gst_per"])
                            
                            itemValue.append(item)
                            headerAmount += float(row["gross_amount"])

                        sqlQuery = "INSERT INTO invoice_item (invoice_no, item_no, hsn_code, material, material_desc, quantity, unit, currency, " \
                            "amt_per_unit, cgst_per, cgst_amount, tax_code, plant, discount, discount_amount, gross_amount, sgst_per, sgst_amount," \
                            "igst_per, igst_amount, taxable_amount, tax_value_amount, gl_account, gst_per) " \
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        
                        mycursor.executemany(sqlQuery, itemValue)

                    if header["sup_status"] == "inapproval":

                        item_category = []

                        if header['ref_po_num']:
                            item_category = fetchSAP_PoDetails(header["ref_po_num"])

                        supplier_type = ''
                        vendor_no = ''
                        vendor_currency = ''

                        if member:
                            if member['gst_treatment'] == 'overseas':
                                supplier_type = 'export'
                            else:
                                supplier_type = 'domestic'

                            vendor_no = member['vendor_no']
                            vendor_currency = member['currency']

                        d_decider = {
                            'supplier_type': supplier_type,
                            'invoice_value': headerAmount,
                            'invoice_type': item_category,
                            'vendor_no': vendor_no,
                            'currency': vendor_currency,
                            'document_type': header["document_type"]
                        }

                        success, emails = assign_approcessor(mycursor=mycursor, invoice_id=invoice_num, decider=d_decider)

                        if emails:
                            sendMailNotifications(invoice_id=invoice_num, mycursor=mycursor, emails=emails)

                else:

                    itemValue = []
                    invoice_id = event["params"]["querystring"]["invoice_no"]

                    if header["sup_status"] == "inapproval":
                        user_id = event["params"]["querystring"]["userid"]
                        in_status = "new"
                        vendor = ""

                        mycursor.execute("select a.fs_name, a.ls_name, a.member_id, b.vendor_no, b.currency, b.gst_treatment " \
                            "from member a " \
                            "left join vendor_master b " \
                            "on a.member_id = b.member_id " \
                            "where a.email = %s", user_id)
                        member = mycursor.fetchone()

                        if member:
                            vendor = member['vendor_no']
                            header["working_person"] = member["member_id"]

                        sqlQuery = "update invoice_header set user_invoice_id = %s, in_status = %s, sup_status = %s, ref_po_num = %s, " \
                            "invoice_date = %s, baseline_date = %s, posting_date = %s, amount = %s, payment_method = %s, currency = %s, taxable_amount = %s, discount_per = %s, " \
                            "total_discount_amount = %s, is_igst = %s, tax_per = %s, cgst_tot_amt = %s, sgst_tot_amt = %s, igst_tot_amt = %s, tds_per = %s," \
                            "tds_tot_amt = %s, payment_terms = %s, adjustment = %s, tcs = %s, supplier_comments = %s, supplier_id = %s, working_person = %s, supplier_name = %s, " \
                            "npo = %s, document_type = %s, gstin = %s, irn = %s where invoice_no = %s"

                        values = (header["user_invoice_id"], in_status, header["sup_status"], header["ref_po_num"], header["invoice_date"], header["baseline_date"], \
                            header["posting_date"], header["amount"], header["payment_method"], header["currency"], header["taxable_amount"], header["discount_per"], \
                            header["total_discount_amount"], header["is_igst"], header["tax_per"], header["cgst_tot_amt"], header["sgst_tot_amt"], header["igst_tot_amt"], \
                            header["tds_per"], header["tds_tot_amt"], header["payment_terms"], header["adjustment"], header["tcs"], header["approver_comments"], vendor, \
                            header['working_person'], header['supplier_name'], header['npo'], header["document_type"], header["gstin"], header["irn"], invoice_id)
                        
                        mycursor.execute(sqlQuery, values)
                        invoice_num = mycursor.lastrowid

                        msg = "Invoice No " + str(invoice_id) + " submitted to customer."

                        response = {
                            "invoice_no": invoice_id,
                            "msg": msg
                        }

                    elif header["sup_status"] == "draft":

                        vendor = ""
                        user_id = event["params"]["querystring"]["userid"]

                        mycursor.execute("select a.fs_name, a.ls_name, a.member_id,b.vendor_no, b.gst_treatment " \
                            "from member a " \
                            "left join vendor_master b " \
                            "on a.member_id = b.member_id " \
                            "where a.email = %s", user_id)
                        member = mycursor.fetchone()

                        if member:
                            vendor = member['vendor_no']
                            header["working_person"] = member["member_id"]

                        in_status = ""
                        sqlQuery = "update invoice_header set user_invoice_id = %s, in_status = %s, sup_status = %s, ref_po_num = %s, " \
                            "invoice_date = %s, baseline_date = %s, posting_date = %s, amount = %s, payment_method = %s, currency = %s, taxable_amount = %s, discount_per = %s, " \
                            "total_discount_amount = %s, is_igst = %s, tax_per = %s, cgst_tot_amt = %s, sgst_tot_amt = %s, igst_tot_amt = %s, tds_per = %s," \
                            "tds_tot_amt = %s, payment_terms = %s, adjustment = %s, tcs = %s, supplier_comments = %s, working_person = %s, supplier_name= %s, " \
                            "document_type = %s, gstin = %s, irn = %s where invoice_no = %s"

                        values = (header["user_invoice_id"], in_status, header["sup_status"], header["ref_po_num"], header["invoice_date"], header["baseline_date"], header["posting_date"], \
                            header["amount"], header["payment_method"], header["currency"], header["taxable_amount"], header["discount_per"], header["total_discount_amount"], \
                            header["is_igst"], header["tax_per"], header["cgst_tot_amt"], header["sgst_tot_amt"], header["igst_tot_amt"], header["tds_per"], header["tds_tot_amt"], \
                            header["payment_terms"], header["adjustment"], header["tcs"], header["approver_comments"], header['working_person'], header['supplier_name'], \
                            header["document_type"], header["gstin"], header["irn"], invoice_id)
                        
                        mycursor.execute(sqlQuery, values)
                        invoice_num = mycursor.lastrowid

                        msg = "Invoice No " + str(invoice_id) + " saved as draft."

                        response = {
                            "invoice_no": invoice_id,
                            "msg": msg
                        }

                    # item data update

                    headerAmount = 0.00

                    if invoice_id != "":
                        sqlQuery = "delete from invoice_item where invoice_no = %s"
                        values = (invoice_id,)
                        mycursor.execute(sqlQuery, invoice_id)

                        for row in list_item:
                            item = (invoice_id, row["item_no"], row["hsn_code"], row["material"], row["material_desc"], row["quantity"], row["unit"], row["currency"],
                                row["amt_per_unit"], row["cgst_per"], row["cgst_amount"], row["tax_code"], row["plant"], row["discount"],
                                row["discount_amount"], row["gross_amount"], row["sgst_per"], row["sgst_amount"], row["igst_per"], row["igst_amount"],
                                row["taxable_amount"], row["tax_value_amount"], row["gl_account"], row["gst_per"])
                            itemValue.append(item)
                            
                            headerAmount += float(row["gross_amount"])
                        
                        sqlQuery = "INSERT INTO invoice_item (invoice_no, item_no, hsn_code, material, material_desc, quantity, unit, currency, " \
                                   "amt_per_unit, cgst_per, cgst_amount, tax_code, plant, discount, discount_amount, gross_amount, sgst_per, " \
                                   "sgst_amount, igst_per, igst_amount, taxable_amount, tax_value_amount, gl_account, gst_per ) " \
                                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        
                        mycursor.executemany(sqlQuery, itemValue)
                        
                    if header["sup_status"] == "inapproval":

                        item_category = []

                        mycursor.execute("select count(*) as count from assignment where invoice_no = %s", invoice_id)
                        data = mycursor.fetchone()

                        if data and data['count'] == 0:
                            if header['ref_po_num']:
                                item_category = fetchSAP_PoDetails(header["ref_po_num"])

                            supplier_type = ''
                            vendor_no = ''
                            vendor_currency = ''

                            if member:
                                if member['gst_treatment'] == 'overseas':
                                    supplier_type = 'export'
                                    
                                else:
                                    supplier_type = 'domestic'

                                if member['vendor_no']:
                                    vendor_no = member['vendor_no']
                                    
                                if member['currency']:
                                    vendor_currency = member['currency']

                            d_decider = {
                                'supplier_type': supplier_type,
                                'invoice_value': headerAmount,
                                'invoice_type': item_category,
                                'vendor_no': vendor_no,
                                'currency': vendor_currency,
                                'document_type': header["document_type"]
                            }

                            sucess, emails = assign_approcessor(mycursor=mycursor, invoice_id=invoice_id, decider=d_decider)

                            if emails:
                                sendMailNotifications(invoice_id=invoice_id, mycursor=mycursor, emails=emails)

                mydb.commit()

    except pymysql.err.IntegrityError as e:
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Dulpicate Entry")
        }

    except Exception as e: 
        mydb.rollback()
        return {
            'statuscode': 500,
            'body': json.dumps("Interal Failure")
        }

    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': response
    }

# getVendorDetails
def getVendorDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = {}  

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            if "querystring" in event["params"]:
                if "vendor_no" in event["params"]["querystring"]:
                    values =  event["params"]["querystring"]["vendor_no"]
                    
                    sqlQuery = "select * from vendor_master where vendor_no = %s"
                    mycursor.execute(sqlQuery, values)
                    vendor = mycursor.fetchone()
                    
                if vendor:
                    mycursor.execute("select * from vendor_user where vendor_no = %s", values)
                    vendor_email = mycursor.fetchall()
                    
                    sup_emails = []
                    for each in vendor_email:
                        if row["vendor_no"] == each["vendor_no"]:
                            sup_emails.append(each["email"])
                        
                    records = {
                        "vendor_no" : vendor["vendor_no"], 
                        "vendor_name" : vendor["vendor_name"], 
                        "gst_treatment" : vendor["gst_treatment"], 
                        "gstin_uin" : vendor["gstin_uin"], 
                        "source_of_supply" : vendor["source_of_supply"], 
                        "currency" : vendor["currency"], 
                        "payment_terms" : vendor["payment_terms"], 
                        "tds" : str(vendor["tds"]), 
                        "gst_per" : vendor["gst_per"], 
                        "pan" : vendor["pan"],
                        "sup_emails": sup_emails
                    }
                    
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

# API ============================ einvoice-masters=================================================
# ==================================================================================================
# ==================================================================================================
# setDefaultDepartment
def setDefaultDepartment(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    output1 = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "sr_no" in event["params"]["querystring"] and "member_id" in event["params"]["querystring"]:
                sqlQuery = "update department_master set default_master_check = %s where member_id = %s"
                values = ('n', event["params"]["querystring"]["member_id"])
                mycursor.execute(sqlQuery, values)
                
                sqlQuery = "update department_master set default_master_check = %s where sr_no = %s"
                values = ('y', event["params"]["querystring"]["sr_no"])
                mycursor.execute(sqlQuery, values)
                
                mycursor.execute("select department_id from department_master where sr_no = %s", event["params"]["querystring"]["sr_no"])
                depID = mycursor.fetchone()
                
                sqlQuery = "update member set department_id = %s where member_id = %s"
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

#  getDefaultMasters
def getDefaultMasters(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            mycursor.execute("select value1, value2 from dropdown where drop_key = 'default-master-detail' ")
            raw_data = mycursor.fetchall()
            
            for row in raw_data:
                master_value = None
                master_value2 = None
                
                if row["value1"] == 'tds_per':
                    mycursor.execute("select value2, value3 from dropdown where drop_key = 'vendor_tds' and value1 = %s ", row["value2"])
                    data = mycursor.fetchone()
                    if data:
                        master_value = data["value2"]
                        master_value2 = data["value3"]
                    
                elif row["value1"] == 'plant':
                    mycursor.execute("select description FROM master where master_id = '7' and code = %s ", row["value2"])
                    data = mycursor.fetchone()
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
                
                else:
                    record = {
                        "master_name": row["value1"],
                        "master_value": master_value,
                        "value": row["value2"],
                        "value2": ""
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

# postDefaultMaster
#working fine for event passed
def postDefaultMaster(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='ap-south-1',
    # aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    # aws_secret_access_key='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' )
    # secret = event["stage-variables"]["secreat"]
    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 
    # secretDict = json.loads(resp['SecretString'])

    mydb = hdbcliConnect()

    record = {
        "company_code": None,
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
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if record["company_code"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'company_code' "
                mycursor.execute(sqlQuery, record["company_code"])
                
            if record["payment_terms"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'payment_terms' "
                mycursor.execute(sqlQuery, record["payment_terms"])
                
            if record["payment_method"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'payment_method' "
                mycursor.execute(sqlQuery, record["payment_method"])    
            
            if record["currency"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'currency' "
                mycursor.execute(sqlQuery, record["currency"])
            
            if record["gl_account_header"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'gl_account_header' "
                mycursor.execute(sqlQuery, record["gl_account_header"])
            
            if record["cost_center"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'cost_center' "
                mycursor.execute(sqlQuery, record["cost_center"])
                
            if record["tax_per"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'tax_per' "
                mycursor.execute(sqlQuery, record["tax_per"])
                
            if record["tds_per"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'tds_per' "
                mycursor.execute(sqlQuery, record["tds_per"])
                
            if record["gl_account_item"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'gl_account_item' "
                mycursor.execute(sqlQuery, record["gl_account_item"])
                
            if record["plant"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'plant' "
                mycursor.execute(sqlQuery, record["plant"])
                
            if record["supplier_id"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'supplier_id' "
                mycursor.execute(sqlQuery, record["supplier_id"])
            
            if record["date_range"] != None:
                sqlQuery = "update dropdown set value2 = ? where drop_key = 'default-master-detail' and value1 = 'date_range' "
                mycursor.execute(sqlQuery, record["date_range"])
                
            if record["document_type"] != None:
                sqlQuery = "select value2 from dropdown where drop_key = 'document_type' and value1 = ? "
                mycursor.execute(sqlQuery, record["document_type"])
                doc_desc = mycursor.fetchone()
                
                sqlQuery = "update dropdown set value2 = ?, value3 = ? where drop_key = 'default-master-detail' and value1 = 'document_type' "
                values = (record["document_type"], doc_desc["value2"])
                mycursor.execute(sqlQuery, values)
                
            mydb.commit()
            
    except:
        return {
            'statuscode': 500,
            'body': json.dumps("Update Unsuccessful!")
        }
           
    finally:
        mydb.close()

    return {
        'statuscode': 200,
        'body': json.dumps("Update Successful!")
    }


# event = {'body-json': {'company_code': '1000', 'payment_method': 0, 'currency': 'KWD', 'gl_account_header': '101000', 'cost_center': '1000', 'tax_per': '00', 'tds_per': 'gulf', 'gl_account_item': '0', 'supplier_id': 2000000135, 'plant': '1000', 'document_type': 'RE'}, 'params': {'path': {}, 'querystring': {}, 'header': {'accept': 'application/json, text/plain, */*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'Authorization': 'eyJraWQiOiJ1RXlLMTdnUjUzTVVMcXUrYkRsQUZ2NHRSUTR0VVM5KzM4NlwvZnpxMWorQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5NDkxOTNiMi1hZWQ2LTQxZGUtOTM2YS04MGRjMTEzNjUxNzIiLCJhdWQiOiIyNGJqZTRqdWQ4aDNmOHJzbmtraGcwYmx2MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJldmVudF9pZCI6IjE5M2M0NDI0LTdkNWQtNGFmZC05YzYwLWYzYzBhM2Q2MmMwYSIsInRva2VuX3VzZSI6ImlkIiwiYXV0aF90aW1lIjoxNjQ3MDc5MTA1LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuZXUtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2V1LWNlbnRyYWwtMV9QOXJubnFpTHUiLCJjb2duaXRvOnVzZXJuYW1lIjoiOTQ5MTkzYjItYWVkNi00MWRlLTkzNmEtODBkYzExMzY1MTcyIiwiZXhwIjoxNjQ3MDgyNzA1LCJpYXQiOjE2NDcwNzkxMDUsImVtYWlsIjoiZWludm9pY2Vwb3J0YWxAZ21haWwuY29tIn0.cywTSO3WhIU1FJ-a-cj7DT5qvioCyQrJ4IjhV5fyDuYPQbeVa97kDNofdBtO3qWuuBkLqdIDojb5bsjHVQseNsKE1fXlO2ESPAnALPjGnIPPVWYNtOUh6waUNJOZ5va3sOcPzyxlN0E-EGgF6sF3xSftUJ9Kq8j3WvKUo7vGMvz0dvjhWEoenWMaahysHyGuQNqpyQ447kVSO3E1WpTDYoH45mhQBLjfUPs2aYQDTXS4ioEAhK-8ymxIDUE1jE3wG6zv6D4nEX3Vdila7icOaW7Q7IBXTEgM7sNsmtNvPupCnEf-KnCXNDSkQqLuEaK6ZVOvlQ8TUYS5Hs4SAC1wCQ', 'content-type': 'application/json', 'Host': 'eplvie2jwe.execute-api.eu-central-1.amazonaws.com', 'origin': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com', 'referer': 'https://ywi7o0pxhc.execute-api.eu-central-1.amazonaws.com/', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Windows"', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36', 'X-Amzn-Trace-Id': 'Root=1-622c6f9c-2df51d8a6bffa81c14191fff', 'X-Forwarded-For': '157.45.191.95', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}}, 'stage-variables': {'schema': 'einvoice_db_portal', 'lambda_alias': 'dev', 'secreat': 'test/einvoice/secret'}, 'context': {'account-id': '', 'api-id': 'eplvie2jwe', 'api-key': '', 'authorizer-principal-id': '', 'caller': '', 'cognito-authentication-provider': '', 'cognito-authentication-type': '', 'cognito-identity-id': '', 'cognito-identity-pool-id': '', 'http-method': 'POST', 'stage': 'master-v1', 'source-ip': '157.45.191.95', 'user': '', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36', 'user-arn': '', 'request-id': '5169ea36-57c8-4e6e-b3fb-b96db1c4df9f', 'resource-id': 'drd1md', 'resource-path': '/default-master'}}

# print(postDefaultMaster(event, ' '))

# deleteDepartmentMaster
def deleteDepartmentMaster(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
                if "sr_no" in event["params"]["querystring"]:
                    if len(event["params"]["querystring"]["sr_no"].split(',')) == 1:
                        mycursor.execute("select * from department_master WHERE sr_no = ? ",event["params"]["querystring"]["sr_no"])
                        data = mycursor.fetchone()
                        
                        mycursor.execute("DELETE FROM department_master WHERE sr_no = %s ",event["params"]["querystring"]["sr_no"])
                        
                        values = ( None, data["member_id"] )
                        mycursor.execute("UPDATE member SET department_id = %s WHERE member_id = %s", values)
                        
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

# getDepartmentMaster
def getDepartmentMaster(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]


    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            
            if "userid" in event["params"]["querystring"]:
                mycursor.execute("select member_id, CONCAT(fs_name, ' ',ls_name) as mem_name from member where email = %s", event["params"]["querystring"]["userid"])
                member = mycursor.fetchone()
                
                if member:
                    mycursor.execute("select * from department_master where member_id = %s order by member_id", member["member_id"])
                    data = mycursor.fetchall()
                    
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
                mycursor.execute("select member_id from member where email = %s", event["params"]["querystring"]["userid_dep"])
                member = mycursor.fetchone()
                
                if member:
                    mycursor.execute("select * from department_master where member_id = %s", member["member_id"])
                    data = mycursor.fetchall()
                    
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
                mycursor.execute("select a.*, CONCAT(b.fs_name, ' ',b.ls_name) as mem_name, b.email " \
                	"from department_master a " \
                    "left join member b " \
                    "on a.member_id = b.member_id " \
                    "order by mem_name, department_id")
                    
                for row in mycursor:
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

# patchDepartmentMaster
def patchDepartmentMaster(event, context): 
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
                defSchemaQuery = "use " + dbScehma
                mycursor.execute(defSchemaQuery)
                sr_no = event["params"]["querystring"]["sr_no"]
                
                sqlQuery = "update department_master set department_id = %s, department_name = %s, cost_center = %s, " \
                    "gl_account = %s, member_id = %s, internal_order = %s where sr_no = %s"
                    
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

# postDepartmentMaster
def postDepartmentMaster(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    list_item = []
    
    try:
        print(event)
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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
                
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
                    
                    format_strings_email = ','.join(['%s'] * len(emails))
                    format_strings_depName = ','.join(['%s'] * len(dep_name))
                    
                    sqlQuery = "select member_id, email from member where email in (%s)" % format_strings_email
                    mycursor.execute(sqlQuery, tuple(emails))
                    memberEmail = mycursor.fetchall()
                    
                    sqlQuery = "select department_id, department_name from departmental_budget_master where department_name in (%s)" % format_strings_depName
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
                        
                    sqlQuery = "select count(*) as count from department_master where department_id = %s and department_name = %s " \
                        "and cost_center = %s and gl_account = %s and member_id = %s and internal_order = %s"
                    
                    mycursor.executemany(sqlQuery, values)
                    dup = mycursor.fetchone()
                    
                    msg = "Duplicate Entry!"
                        
                    if dup["count"] != 1:
                        sqlQuery = "insert into department_master (department_id, department_name, cost_center, gl_account, member_id, internal_order) " \
                            "values (%s, %s, %s, %s, %s, %s)"
                        mycursor.executemany(sqlQuery, values)
                        msg = "Inserted Successfully!"
                    
                else:
                    for row in list_item:
                        touple = (row["department_id"], row["department_name"], row["cost_center"], row["gl_account"], row["member_id"], row["internal_order"])
                        values.append(touple)
                    
                    sqlQuery = "select count(*) as count from department_master where department_id = %s and department_name = %s " \
                        "and cost_center = %s and gl_account = %s and member_id = %s and internal_order = %s"
                    
                    mycursor.executemany(sqlQuery, values)
                    dup = mycursor.fetchone()
                    msg = "Duplicate Entry!"
                        
                    if dup["count"] != 1:
                        sqlQuery = "insert into department_master (department_id, department_name, cost_center, gl_account, member_id, internal_order) " \
                            "values (%s, %s, %s, %s, %s, %s)"
                            
                        mycursor.executemany(sqlQuery, values)
                        msg = "Inserted Successfully!"
            
            else:
                sr_no = event["params"]["querystring"]["sr_no"]
                
                sqlQuery = "update department_master set department_id = %s, department_name = %s, cost_center = %s, " \
                    "gl_account = %s, member_id = %s, internal_order = %s where sr_no = %s"
                    
                values = ( record["department_id"], record["department_name"], record["cost_center"], record["gl_account"], record["member_id"], record['internal_order'], sr_no )
                
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

# deleteDepartmentalBudgetMaster
def deleteDepartmentalBudgetMaster(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
                
                if "department_id" in event["params"]["querystring"]:
                    
                    if len(event["params"]["querystring"]["department_id"].split(',')) == 1:
                        values = event["params"]["querystring"]["department_id"]
                        mycursor.execute("DELETE FROM departmental_budget_master WHERE department_id = %s ", values)
                        
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

#  getDepartmentalBudgetMaster
# PASS

# patchDepartmentalBudgetMaster
def patchDepartmentalBudgetMaster(event, context): 
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            if "department_id" in event["params"]["querystring"]:
                
                department_id = event["params"]["querystring"]["department_id"]
                
                sqlQuery = "update departmental_budget_master set department_name = %s, budget = %s, limit_per = %s, warning_per = %s, valid_from = %s, valid_to = %s where department_id = %s"
                    
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

#postDepartmentalBudgetOrder
def postDepartmentalBudgetOrder(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
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
                    
            sqlQuery = "insert into departmental_budget_master (department_name, budget, warning_per, limit_per, valid_from, valid_to) values (%s, %s, %s, %s, %s, %s)"
        
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

# getSapMaterials
def getSapMaterials(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
    
    s3 = boto3.client("s3")
    
    reocrds = {}
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            if "po_number" in event["params"]["querystring"]:
                po_number = event["params"]["querystring"]["po_number"]
                
                mycursor.execute("select material, material_desc, item_no from po_detail where po_number = %s order by item_no", po_number)
                records = mycursor.fetchall()
                
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

# getIrnDetails
def getIrnDetails(event=None, context=None):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )
    secret = event["stage-variables"]["secreat"]
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
        cursorclass=pymysql.cursors.DictCursor
    )
    
    irn = event["params"]["querystring"]["irn"]

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)    

            mycursor.execute('SELECT * FROM elipo_setting where key_name = "master_gst_details"')
            mastergst = mycursor.fetchall()

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
                                        'body': json.dumps('Requested data is not available')
                                    }

                            elif responce.status_code == 404:
                                return {
                                    'statuscode': 404,
                                    'body': json.dumps("Not Found.")
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

# deleteMaterialMasterDetails
#event not found
def deleteMaterialMasterDetails(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='ap-south-1',
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

# getMasterMasterDetails
def getMasterMasterDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "material_no" in event["params"]["querystring"]:
                
                material_no = event["params"]["querystring"]["material_no"]
                mycursor.execute("select mm.*, m.description from material_master mm left join master m on mm.uom = m.code " \
                    "where material_no = %s", material_no)
                
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

# patchMaterialMasterDetails
def patchMaterialMasterDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
                
            if "material_no" in event["params"]["querystring"]:
                
                material_no = event["params"]["querystring"]["material_no"]
                
                sqlQuery = "update material_master set material_name = %s, gst_per = %s, unit_price = %s, gl_account = %s, uom = %s, hsn_code = %s where material_no = %s"
                    
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

# postMaterialMasterDetails
def postMaterialMasterDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    list_item = []
    
    try:
        
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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "import_entries" in event["params"]["querystring"]:
                mycursor.execute("TRUNCATE material_master")
            
            values = []
            
            for row in list_item:
                touple = (row["material_no"], row["material_name"], row["gst_per"], row["unit_price"], row["gl_account"], row["uom"], row["hsn_code"])
                values.append(touple)
                
            sqlQuery = "insert into material_master (material_no, material_name, gst_per, unit_price, gl_account, uom, hsn_code)" \
                "values (%s, %s, %s, %s, %s, %s, %s)"
                        
            mycursor.executemany(sqlQuery, values)
                        
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

# getMaterialMasterSearchHelp
def getMaterialMasterSearchHelp(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
        
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

# deleteTaxCodeMaster
#event not found
def deleteTaxCodeMaster(event, context):
    global dbScehma 
    dbScehma = ' DBADMIN '
    
    # client = boto3.client(
    # 'secretsmanager',
    # region_name='ap-south-1',
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

# getTaxCodeMaster
def getTaxCodeMaster(event, context): 
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = []
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "company_code" in event["params"]["querystring"]:
                company_code = event["params"]["querystring"]["company_code"]
                
                mycursor.execute("select * from tax_code where company_code = %s", company_code)
                records = mycursor.fetchall()
                
            else:
                mycursor.execute("select * from tax_code")
                records = mycursor.fetchall()
            
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

# patchTaxCodeMaster
def patchTaxCodeMaster(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "company_code" in event["params"]["querystring"] and "tax_code" in event["params"]["querystring"]:
                company_code = event["params"]["querystring"]["company_code"]
                tax_code = event["params"]["querystring"]["tax_code"]
                
                sqlQuery = "update tax_code set company_code = %s, tax_code = %s, tax_per = %s, description = %s where company_code = %s and tax_code = %s"
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

# postTaxCodeMaster
def postTaxCodeMaster(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "import_entries" in event["params"]["querystring"]:
                mycursor.execute("TRUNCATE TABLE tax_code")
            
            values = []
            
            for row in list_item:
                touple = (row["company_code"], row["tax_code"], row["tax_per"], row["description"])
                values.append(touple)
                
            sqlQuery = "insert into tax_code (company_code, tax_code, tax_per, description) values (%s, %s, %s, %s)"
            mycursor.executemany(sqlQuery, values)
                        
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

# deleteAttachment
def deleteAttachment(event, context):
    global dbScehma 
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
            dbScehma = event["stage-variables"]["schema"]
            
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
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

# getVendor
def getVendor(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    # TODO implement

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    record = {}

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            vendor = None

            if "vendor_no" in event["params"]["querystring"]:
                vendor_no = event["params"]["querystring"]["vendor_no"]
            
                mycursor.execute("SELECT v.*, d.value2 " \
                    "FROM vendor_master v " \
                    "left join dropdown d " \
                    "on v.gst_treatment = d.value1 " \
                    "where v.vendor_no = %s and d.drop_key = 'vendor_gst_treatment'", vendor_no)
                record = mycursor.fetchone()

            elif 'userid' in event["params"]["querystring"]:
                values = (event["params"]["querystring"]["userid"],)
                sqlQuery = "select member_id from member where email = %s"
                mycursor.execute(sqlQuery, values)
                member = mycursor.fetchone()

                if member:
                    values = (member['member_id'],)
                    mycursor.execute(
                        "SELECT v.*, d.value2 FROM vendor_master v "
                        "left join dropdown d on v.gst_treatment = d.value1 "
                        "where v.member_id = %s and d.drop_key = 'vendor_gst_treatment'",
                        values)
                    vendor = mycursor.fetchone()

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

# getVendorList
def getVendorList(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    # TODO implement
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = []
    
    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
            if "unassigned_vednor" in event["params"]["querystring"]:
                mycursor.execute("SELECT vendor_no, vendor_name FROM vendor_master where member_id = NU")
                
            else:
                mycursor.execute("SELECT vendor_no, vendor_name FROM vendor_master")
                
                search_help = []
                for vendor in mycursor:
                    record = {
                        "code" : vendor["vendor_no"],
                        "description" : vendor["vendor_name"]
                    }
                    records.append(record)
                    
                # records["search_help"] = search_help
            
    except :
        
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }
            
    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': records
    }

# deleteVendorMasterDetails
def deleteVendorMasterDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
            
            if "vendor_no" in event["params"]["querystring"]:
                
                if len(event["params"]["querystring"]["vendor_no"].split(',')) == 1:
                    mycursor.execute("DELETE FROM vendor_master WHERE vendor_no = %s ",event["params"]["querystring"]["vendor_no"])
                    mycursor.execute("DELETE FROM vendor_user WHERE vendor_no = %s ",event["params"]["querystring"]["vendor_no"])
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

#getVendorMasterDetails
def getVendorMasterDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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

    records = []

    try:
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)
            
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

# patchVendorMasterDetails
def patchVendorMasterDetails(event, context):
    global dbScehma 
    dbScehma = event["stage-variables"]["schema"]
    
    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
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
        "vendor_name": "", 
        "gst_treatment": "", 
        "gstin_uin": "", 
        "source_of_supply": "", 
        "currency": "",
        "payment_terms": "", 
        "tds": "", 
        "international_code": "",
        "gst_per": "", 
        "pan": "",
        "member_id": ""
    }

    try:
        for value in event["body-json"]:
            if value in record:
                record[value] = event["body-json"][value]
                
        with mydb.cursor() as mycursor:
            defSchemaQuery = "use " + dbScehma
            mycursor.execute(defSchemaQuery)

            
            if "vendor_no" in event["params"]["querystring"]:
                vendor_no = event["params"]["querystring"]["vendor_no"]
                
                sqlQuery = "update vendor_master set vendor_name = %s, gst_treatment = %s, gstin_uin = %s, source_of_supply = %s, currency = %s, " \
                    "payment_terms = %s, tds = %s, international_code = %s, gst_per = %s, pan = %s, member_id = %s where vendor_no = %s"
                    
                values = ( record["vendor_name"], record["gst_treatment"], str(record["gstin_uin"]).upper(), record["source_of_supply"], record["currency"], record["payment_terms"], 
                            record["tds"], str(record["international_code"]).upper(), record["gst_per"], str(record["pan"]).upper(), record["member_id"], vendor_no )
                            
                # print(sqlQuery, values)
                mycursor.execute(sqlQuery, values)
                
                mycursor.execute("delete from vendor_user where vendor_no = %s", vendor_no)
                
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
                    
                    sqlQuery = "insert into vendor_user (vendor_no, email) values (%s, %s)"
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

# postVendorMasterDetails
def postVendorMasterDetails(event, context):
    global dbScehma
    dbScehma = event["stage-variables"]["schema"]

    # print(event)      

    client = boto3.client(
    'secretsmanager',
    region_name='ap-south-1',
    aws_access_key_id='AKIAXUCMAX6S27NZCRFL',
    aws_secret_access_key='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' )
    secret = event["stage-variables"]["secreat"]
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
        cursorclass=pymysql.cursors.DictCursor
    )

    records = {}
    try:
        list_item = []
        for row in event["body-json"]:
            item = {
                "vendor_no": "",
                "vendor_name": "",
                "gst_treatment": "",
                "gstin_uin": "",
                "email": "",
                "source_of_supply": "",
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
            defSchemaQuery = "use " + dbScehma
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

            format_strings = ','.join(['%s'] * len(emailids))
            sqlQuery = "select member_id, email from member where email in ({})".format(format_strings)

            mycursor.execute(sqlQuery, tuple(emailids))
            members = mycursor.fetchall()

            for row in list_item:
                member_id = None

                if members:
                    for mem in members:
                        if row['email'] == mem['email']:
                            member_id = mem['member_id']
                            break

                touple = (
                str(row["vendor_no"]).strip(), row["vendor_name"], row["gst_treatment"], str(row["gstin_uin"]).upper(),
                row["source_of_supply"], row["currency"], row["payment_terms"], row["tds"],
                row["international_code"].upper(),
                row["gst_per"], str(row["pan"]).upper(), member_id)
                values.append(touple)

                vendor.append(row["vendor_no"])


                if row["sup_emails"] != None or row["sup_emails"] != []:
                    for each in row["sup_emails"]:
                        if each:
                            temp = (str(row["vendor_no"]).strip(), each)
                            email_values.append(temp)

            sqlQuery = "insert into vendor_master (vendor_no, vendor_name, gst_treatment, gstin_uin, source_of_supply, currency, " \
                       "payment_terms, tds, international_code, gst_per, pan, member_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            mycursor.executemany(sqlQuery, values)

            if email_values:
                finalEmail_values = []
                for i in range(len(email_values)):
                    if email_values[i] not in email_values[i + 1:]:
                        finalEmail_values.append(email_values[i])

                if finalEmail_values:
                    sqlQuery = "insert into vendor_user (vendor_no, email) values (%s, %s)"
                    mycursor.executemany(sqlQuery, finalEmail_values)

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

# correct event data not found
def getPo(event, context):
    data = ''
    val = ''
    print(event)
    # TODO implement
    dbScehma = ' DBADMIN '
    # client = boto3.client('secretsmanager')
    # secret = event["stage-variables"]["secreat"]

    # resp = client.get_secret_value(
    #     SecretId= secret
    # ) 

    # secretDict = json.loads(resp['SecretString'])
    # print(secretDict)

    mydb = hdbcliConnect()
    # print(resp['SecretString'])
    # payload = []
    # vendor_data = {}
    
    try:
        print(event)
        with mydb.cursor() as mycursor:
            defSchemaQuery = "set schema " + dbScehma
            mycursor.execute(defSchemaQuery)


            if "tabname" in event["params"]["querystring"]:
                tabname = event["params"]["querystring"]['tabname']
            if 'pageno' in event["params"]["querystring"]:
                start_idx = int(event["params"]["querystring"]['pageno'])
            if 'nooflines' in event["params"]["querystring"]:
                end_idx = int(event["params"]["querystring"]['nooflines'])
                

            if 'pageno' in event["params"]["querystring"] and 'nooflines' in event["params"]["querystring"] and "tabname" in event["params"]["querystring"]:   
                start_idx = (start_idx -1 ) * end_idx
                val = (tabname ,end_idx ,start_idx)

            if val != '':
                mycursor.execute(" select po_number , ref_po_no , buyer , po_date,modified_date   from po_header where in_status = ? order by ref_po_no desc limit ? offset ? " ,val)
                data = mycursor.fetchall()
                data = convertValuesTodict(mycursor.description , data)

                for d in data:
                    mycursor.execute(" SELECT * FROM file_storage where file_id = ? and attach_id > 7000 " , d['ref_po_no'])
                    d['file'] = mycursor.fetchall()
                    d['file'] = convertValuesTodict(mycursor.description, d['file'])

            mydb.commit()
    
    except :
        return {
            'statusCode': 500,
            'body': json.dumps("Internal Failure")
        }

    finally:
        mydb.close()
        
    return {
        'statusCode': 200,
        'body': data
    }