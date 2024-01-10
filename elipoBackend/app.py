import mymodule1
import mymodule2
import mymodule3
import mymodule4

from flask import Flask, request
import json
import mymodule1

from flask_cors import CORS
import cfenv

app_env = cfenv.AppEnv()
port = app_env.port

function_names = {
    "rules": {
        "GET": "getRuleDetails",
        "POST": "postRuleDetails",
        "PATCH": "patchRuleDetails",
        "DELETE": "deleteRuleDetails",
    },
    "enablexraytraces": {"POST": "EnableXRayTraces"},
    "enablexraytracesindividually": {"POST": "EnableXRayTracesIndividually"},
    "getemail": {"GET": "GetUserEmails"},
    "getmasterdetailssap": {"GET": "getmasterdetailssap"},
    "attachment": {
        "DELETE": "deleteAttachment",
        "GET": "downloadAttachments",
        "POST": "uploadAttachments",
    },
    "company-logo": {"POST": "einvoice_upload_company_logo"},
    "supplier-ocr-upload": {"POST": "supplier_ocr_attch_upload"},
    "upload": {"DELETE": "deleteAttachment", "POST": "einvoice_upload_attachment"},
    "upload-enquiry-attachment": {
        "DELETE": "deleteEnquiryAttachment",
        "POST": "einvoice_upload_enquiry_attachment",
    },
    "upload-profile-photo": {"POST": "einvoice_upload_profile_photo"},
    "default-department": {"PATCH": "setDefaultDepartment"},
    "default-master": {"GET": "getDefaultMasters", "POST": "postDefaultMaster"},
    "default_master1": {
        "DELETE": "deleteDefaultMaster",
        "GET": "getAllDefaultMaster",
        "PATCH": "patchDefaultMasterDetail",
        "POST": "postDefaultMasterDetail",
    },
    "department-master": {
        "DELETE": "deleteDepartmentMaster",
        "GET": "getDepartmentMaster",
        "PATCH": "patchDepartmentMaster",
        "POST": "postDepartmentMaster",
    },
    "departmental-budget-master": {
        "DELETE": "deleteDepartmentalBudgetMaster",
        "GET": "getDepartmentalBudgetMaster",
        "PATCH": "patchDepartmentalBudgetMaster",
        "POST": "postDepartmentalBudgetOrder",
    },
    "get-po-material": {"GET": "getSapMaterials"},
    "irn-details": {"GET": "getIrnDetails"},
    "material-master": {
        "DELETE": "deleteMaterialMasterDetails",
        "GET": "getMasterMasterDetails",
        "PATCH": "patchMaterialMasterDetails",
        "POST": "postMaterialMasterDetails",
    },
    "material-master-searchhelp": {"GET": "getMaterialMasterSearchHelp"},
    "tax-code": {
        "DELETE": "deleteTaxCodeMaster",
        "GET": "getTaxCodeMaster",
        "PATCH": "patchTaxCodeMaster",
        "POST": "postTaxCodeMaster",
    },
    "upload": {"DELETE": "deleteAttachment"},
    "Vendor": {"GET": "getVendor"},
    "list": {"GET": "getVendorList"},
    "vendor-master": {
        "DELETE": "deleteVendorMasterDetails",
        "GET": "getVendorMasterDetails",
        "PATCH": "patchVendorMasterDetails",
        "POST": "postVendorMasterDetails",
    },
    "aging-report": {"POST": "getAgingReportDetails"},
    "dia-analytics": {"POST": "getDiaAnalyticReport"},
    "key-process-analytics-report": {"POST": "getKeyProcessAnalyticsReport"},
    "liability-report": {"POST": "getLiabilityReportDetails"},
    "liability-based-on-amount": {"GET": "getLiabilityGraphBasedOnAmount"},
    #"overview": {"GET": "overview"},
    "account-payable": {"GET": "getAccountsPayableOverview"},
    "invoice-overview": {"GET": "getInvoiceOverview"},
    #"productivity-overview": {"GET": "getProductivityOverview"},
    "user-productivity": {"GET": "getUserProductivityOverview"},
    "overview-supplier": {"GET": "getOverviewSup"},
    "account-recivable": {"GET": "getAccountsRecivableOverviewSup"},
    #"invoice-overview": {"GET": "getInvoiceOverviewSup"},
    "productivity-report": {"POST": "getProductivityReport"},
   # "topvendors": {"GET": "getTopFiveVendors"},
    #  mumbai region
    # "attachment": {
    #     "DELETE": "deleteAttachment",
    #     "GET": "downloadAttachments",
    #     "POST": "uploadAttachments",
    # },
    "member-profile-upload": {
        "POST": "uploadUserProfilePhoto",
    },
    "ocr-b64-image": {
        "POST": "getTextFromImage",  # (pass)
    },
    "upload": {"GET": "Simple Storage Service (S3)"},  # (pass)
    "{bucket}": {"GET": "downloadFileHandlingApi", "POST": "uploadFileHandlingApi"},
    "comment-templates": {
        "DELETE": "deleteCommentTemplates",
        "GET": "getCommentTemplates",
        "POST": "postCommentTemplates",
    },
    "invoice-assignment": {"POST": "postInvoiceAssignment"},
    "reply": {"POST": "postReplyToEnquiry"},
    "setting": {"GET": "getSettingParameter", "PATCH": "patchSetting"},
    "supplier-enquiry": {
        "GET": "getDetailedSupplierEnquiry",
        "POST": "getSupplierEnquiry",
    },
    # "aging-report": {"POST": "getAgingReportDetails"},
    "dia-analytics": {"POST": "getDiaAnalyticReport"},
    "key-process-analytics-report": {"POST": "getKeyProcessAnalyticsReport"},
    "liability-report": {"POST": "getLiabilityReportDetails"},
    # "liability-based-on-amount": {"GET": "getLiabilityGraphBasedOnAmount"},
    # "overview": {"GET": "overview"},
    "account-payable": {"GET": "getAccountsPayableOverview"},
    #"invoice-overview": {"GET": "getInvoiceOverview"},
    "productivity-overview": {"GET": "getProductivityOverview"},
    "user-productivity": {"GET": "getUserProductivityOverview"},
    "overview-supplier": {"GET": "getOverviewSup"},
   # "account-recivable": {"GET": "getAccountsRecivableOverviewSup"},
    #"invoice-overview": {"GET": "getInvoiceOverviewSup"},
    "productivity-report": {"POST": "getProductivityReport"},
    "topvendors": {"GET": "getTopFiveVendors"},
    # singapore region
    "ocr-upload": {"POST": "einvoice_ocr"},
    "getTextFromImage-API": {"getTextFromImage-API"},  # (PASS)
    "bnn": {"GET": "einvoice_ocr"},
    "demores": {"GET": "getTextFromS3PDF"},
    "member-profile-upload": {"POST": "uploadUserProfilePhoto"},
    "ocr-b64-image": {"POST": "getTextFromImage"},
    "flask-gmail": {"GET": "getEmailDetails"},
    "gmail": {"GET": "fetchEmailData"},
    "multi-tenant": {"GET": "multiTenentDemo"},
    "rolemaster": {"GET": "RDSQueryExample"},
    "accuracy": {"GET": "getAccuracyFieldsList", "PATCH": "patchAccuracyFieldsList"},
    "comment-templates": {
        "DELETE": "deleteCommentTemplates",
        "GET": "getCommentTemplates",
        "POST": "postCommentTemplates",
    },
    "invoice-assignment": {"POST": "postInvoiceAssignment"},
    "reply": {"POST": "postReplyToEnquiry"},
    "setting": {"GET": "getSettingParameter", "PATCH": "patchSetting"},
    # "supplier-enquiry": {
    #     "GET": "getDetailedSupplierEnquiry",
    #     "POST": "getSupplierEnquiry",
    # },
    # ...........................einvoice-approval-p2...................
    "budget-alert": {"GET": "getDepartmentBudget"},
    "checkpo": {
        "GET": "getDuplicatePO",
    },
    "delete-invoice": {"DELETE": "deleteInvoice"},
    "duplicate-invoice": {"GET": "checkInvoiceAndVendor"},
    # "fetch-invoice": {"POST": "getSearchedInvoice"},
    "gmail-attachment": {"GET": "invoice_fetch_mail_attachments"},
    "updatesmm":{
        "POST": "updateMailMessage"
    },
    "gmail-s3": {
        "DELETE": "einvoice_revoke_email_access",
        "GET": "einvoice_gmail_attachments_tos3",
        "POST": "einvoice_prosess_gmail_msg",
    },
    "gst-codes": {"GET": "getGstinDetails"},
    "invoice-count": {"GET": "getInvoiceCount"},
    "invoice-excel": {"GET": ""},
    "notificationmail": {
        "POST": "setNotificationEmail",
    },
    "oc_data_check": {"GET": "getOcrDataSupplier"},
    "ocr_lable": {
        "DELETE": "deleteOcrLabel",
        "GET": "getOcrLabels",
        "PATCH": "patchOcrLabels",
        "POST": "postOcrLabel",
    },
    "paper-ai": {
        "POST": "postPaperAiResponse",
    },
    "paper-entry": {"PATCH": "patchPaperAIResponce", "POST": "postPaperAiResponse"},
    "post-sap-error": {"POST": "postSapError"},
    "report-invoices": {"POST": "getReportInvoices"},
    "search-criteria": {"GET": "getSearchDetailsSup"},
    "search-help": {
        "GET": "getSearchHelp",
        # "report": {"GET": "getReportSearchHelp"},
        "vendor": {"GET": "getVendorSearchHelp"},
    },
    "supplier": {"POST": "postInvoiceDetailsSup"},
    "vendor": {"GET": "getVendorDetails"},
    "test": {"GET": "GetUserEmails"},
    "getdemo": {"GET": "eventbridge-ex{PASS}"},
    "getemail": {"GET": "GetUserEmails{PASS}"},
    "getlogs": {"GET": "Elipo-logs"},
    # ..............................................mumbai ......................................................
    "approver": {
        "DELETE": "deleteAprroverDetails",
        "GET": "getApproverDetails",
        "PATCH": "patchApproverDetails",
        "POST": "postApproverDetails",
    },
    "assignment-approver": {
        "GET": "getMemberNGroupDetails",
    },
    "attachments": {"GET": "downloadAttachments", "POST": "uploadAttachments"},
    "change-password": {"POST": "postChangPassword"},
    # "dropdown": {"GET": "einvoice-fetch-dropdown"},
    "fetch-invoice": {"GET": "getSearchedInvoice", "POST": "getSearchedInvoice"},
    "get-sap-po": {"GET": "getSapPoDetail"},
    "group": {
        "DELETE": "deleteGroup",
        "GET": "getGroupDetails",
        "PATCH": "patchGroup",
        "POST": "",
    },
    "inbox": {"POST": "getInboxApprovals"},
    "invoice": {"POST": "postInvoiceDetails"},
    #"invoice-log": {"DELETE": "deleteInvoiceLog", "GET": "getErrorLog"},
    "master": {
        "DELETE": "deleteMasterDetails",
        "GET": "getMasterDetails",
        "PATCH": "patchMasterDetails",
        "POST": "postMasterDetails",
    },
#    "member": {
#        "DELETE": "deleteMemberDetail",
#        "GET": "getMemberDetails",
#        "PATCH": "patchMemberDetails",
#        "POST": "postMemberDetails",
#     },
    "npo-rule": {"GET": "getNpoRuleDetail", "POST": "getNpoRuleDetail"},
    "overview": {"GET": "getOverviewDetails"},
    "post-invoice": {"PATCH": "patchInvoiceStatus", "POST": "postInvoiceDetail"},
    "refered-invoice": {"PATCH": "patchReferInvoice"},
    "rule-notification": {
        "GET": "getRuleNotification",
        "PATCH": "patchRuleNotification",
        "POST": "postRuleNotification",
    },
    "rule-status": {"PATCH": "patchRuleStatus"},
    "rules": {
        "DELETE": "deleteRuleDetails",
        "GET": "getRuleDetails",
        "PATCH": "patchRuleDetails",
        "POST": "postRuleDetails",
    },
    "search-criteria": {"GET": "getSearchDetails"},
    "track-invoice": {"POST": "getTrackInvoices"},
    "user": {
        "GET": "getEinvoiceInitialData",
        "POST": "postUserRoleTabs",
        "user-data": {"GET": "getUserRoleTabs"},
    },
    "users-role": {"GET": "getMemberRoles", "PATCH": "patchMemberRole"},
    "verify-mastergst": {"GET": " getGSTinVerification:prod(PASS)"},
    "upload": {"DELETE": "deleteAttachment", "POST": "einvoice_upload_attachment"},
    "upload-enquiry-attachment": {
        "DELETE": "deleteEnquiryAttachment",
        "POST": "einvoice_upload_enquiry_attachment",
    },
    "upload-profile-photo": {"POST": "einvoice_upload_profile_photo"},
    "getpo": {"GET": "getPo", "PATCH": "updatePoDetails", "POST": "fetchPoDetails"},
    "reject": {"POST": "rejectInvoice"},
    "s3": {"GET": "s3logs"},
    "salesorder": {"POST": "postSalesOrder"},
    "tracing": {"GET": "getUserId", "PATCH": " patchUserId"},
    "trackso": {"POST": "getTrackSalesOrders"},
    "user_logintime": {"PATCH": "fetchlogintime", "POST": "fetchlogintime"},
    "vendor": {
        "DELETE": "deleteVendordemo",
        "GET": "getVendordemo",
        "PATCH": "patchVendordemo",
        "POST": "postVendordemo",
    },
    # =========================================================================
    # API - einvoice-approval
    "approver": {
        "DELETE": "deleteAprroverDetails",
        "GET": "getApproverDetails",
        "PATCH": "patchApproverDetails",
        "POST": "postApproverDetails",
    },
    # "assignment-approver": {"GET": "getMemberNGroupDetails"},
    # "attachments": {"GET": "downloadAttachments", "POST": "uploadAttachments"},
    "change-password": {"POST": "postChangPassword"},
    "dropdown": {"GET": "einvoice_fetch_dropdown"},
    # "fetch-invoice": {"GET": "getSearchedInvoice", "POST": "getSearchedInvoice"},
    # "get-sap-po": {"GET": "getSapPoDetail"},
    "group": {
        "DELETE": "deleteGroup",
        "GET": "getGroupDetails",
        "PATCH": "patchGroup",
        "POST": "postGroupDetails",
    },
   # "inbox": {"POST": "getInboxApprovals"},
    "invoice-log": {"DELETE": "deleteInvoiceLog", "GET": "getErrorLog"},
    "master": {
        "DELETE": "deleteMasterDetails",
        "GET": "getMasterDetails",
        "PATCH": "patchMasterDetails",
        "POST": "postMasterDetails",
    },
    "member": {
        "DELETE": "deleteMemberDetail",
        "GET": "getMemberDetails",
        "PATCH": "patchMemberDetails",
        "POST": "postMemberDetails",
    },
    # "npo-rule": {"GET": "getNpoRuleDetail", "POST": "getNpoRuleDetail"},
    # "overview": {"GET": "getOverviewDetails"},
    # "post-invoice": {
    #     "PATCH": "patchInvoiceStatus",
    # },
    "refered-invoice": {"PATCH": "patchReferInvoice"},
    "rule-notification": {
        "GET": "getRuleNotification",
        "PATCH": "patchRuleNotification",
        "POST": "postRuleNotification",
    },
    "rule-status": {"PATCH": "patchRuleStatus"},
    "rules": {
        "DELETE": "deleteRuleDetails",
        "GET": "getRuleDetails",
        "PATCH": "patchRuleDetails",
        "POST": "postRuleDetails",
    },
    "search-criteria": {"GET": "getSearchDetails"},
    # "track-invoice": {"POST": "getTrackInvoices"},
    # "user": {"GET": "getEinvoiceInitialData", "POST": "postUserRoleTabs"},
    "user-data": {"GET": "getUserRoleTabs"},
    "userauthentication": {"GET": "userAuthentication"},
    "users-role": {"GET": "getMemberRoles", "PATCH": "patchMemberRole"},
    "verify-mastergst": {"GET": "getGSTinVerification"},
    # MUMBAI REGION
    "budget-alert": {"GET": "getDepartmentBudget"},
    "checkpo": {"GET": "getDuplicatePO"},
    "delete-invoice": {"DELETE": "deleteInvoice"},
    "duplicate-invoice": {"GET": "checkInvoiceAndVendor"},
    # "fetch-invoice": {"POST": "getSearchedInvoiceSup"},
    "gmail-attachment": {"GET": "einvoice_fetch_mail_attachments"},
    # "gmail-s3": {
    #     "GET": "einvoice_gmail_attachments_tos3",
    #     "POST": "einvoice_prosess_gmail_msg",
    # },
    "gst-codes": {"GET": "getGstinDetails"},
    # "invoice-count": {"GET": "getInvoiceCount"},
    "invoice-excel": {"GET": "getInvoiceExcelFile"},  # PASS
    # "notificationmail": {"POST": "setNotificationEmail"},
    "ocr-data-check": {"GET": "getOcrDataSupplier"},
    "ocr-lable": {"GET": "getOcrLabels", "PATCH": "patchOcrLabels"},
    # "paper-entry": {"POST": "postPaperAiResponse"},
    "post-sap-error": {"POST": "postSapError"},
    "report-invoices": {"POST": "getReportInvoices"},
    "search-criteria": {"GET": "getSearchDetailsSup"},
    "search-help": {"GET": "getSearchHelp"},
    "report": {"GET": "getReportSearchHelp"},
    # "vendor": {"GET": ""},
    "supplier": {"POST": "postInvoiceDetailsSup"},
    "vendor": {"GET": "getVendorDetails"},
    # API ----------   einvoice-masters
    "default-department": {"PATCH": "setDefaultDepartment"},
    "default-master": {"GET": "getDefaultMasters", "POST": "postDefaultMaster"},
    # "department-master": {
    #     "DELETE": "deleteDepartmentMaster",
    #     "GET": "getDepartmentMaster",
    #     "PATCH": "patchDepartmentMaster",
    #     "POST": "postDepartmentMaster",
    # },
    # "departmental-budget-master": {
    #     "DELETE": "deleteDepartmentalBudgetMaster",
    #     "GET": " getDepartmentalBudgetMaster",  # (PASS),
    #     "PATCH": "patchDepartmentalBudgetMaster",
    #     "POST": "postDepartmentalBudgetOrder",
    # },
    "get-po-material": {"GET": "getSapMaterials"},
    "irn-details": {"GET": "getIrnDetails"},
    "material-master": {
        "DELETE": "deleteMaterialMasterDetails",
        "GET": "getMasterMasterDetails",
        "PATCH": "patchMaterialMasterDetails",
        "POST": "postMaterialMasterDetails",
    },
    "material-master-searchhelp": {"GET": "getMaterialMasterSearchHelp"},
    "tax-code": {
        "DELETE": "deleteTaxCodeMaster",
        "GET": "getTaxCodeMaster",
        "PATCH": "patchTaxCodeMaster",
        "POST": "postTaxCodeMaster",
    },
    "upload": {"DELETE": "deleteAttachment"},
    "vendor": {"GET": "getVendor"},
    "list": {"GET": "getVendorList"},
    "vendor-master": {
        "DELETE": "deleteVendorMasterDetails",
        "GET": "getVendorMasterDetails",
        "PATCH": "patchVendorMasterDetails",
        "POST": "postVendorMasterDetails",
    },
    # einvoice-attachment
    # "attachment": {"DELETE": "deleteAttachment"},
    "company-logo": {"POST": "einvoice_upload_company_logo"},
    "supplier-ocr-upload": {"POST": "supplier_ocr_attch_upload"},
    "upload": {"DELETE": "deleteAttachment", "POST": "einvoice_upload_attachment"},
    "upload-enquiry-attachment": {"DELETE": "deleteEnquiryAttachment"},
}

app = Flask(__name__)

CORS(app, origins="*")


@app.route("/dev/<resource_name>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def call_function(resource_name):
    function_name = ""

    try:
        print(resource_name)

        querystring = json.loads(json.dumps(request.args))
        body_json = ""
        if request.data.decode("utf-8") != "":
            body_json = json.loads(request.data.decode("utf-8"))
        header = json.loads(json.dumps(dict(request.headers)))

        event = {
            "body-json": {},
            "params": {"path": {}, "querystring": {}, "header": {}},
            "stage-variables": {
                "schema": "einvoice_db_portal",
                "lambda_alias": "dev",
                "secreat": "test/einvoice/secret",
                "notification_email": "elipotest@gmail.com",
                # "ocr_bucket_folder": "old-dev/",
                "cred_bucket": "file-bucket-emp",
                # "schema":"einvoice_db_portal",
                "non_ocr_attachment":"einvoice-attachments",
                "lambda_alias":"dev",
                "aws_mail_bucket":"application-email",
                # "notification_email":"elipotest@gmail.com",
                "ocr_bucket":"textract-console-ap-southeast-1-b8779ae1-dd77-4d3c-a56d-443a5db",
                "ocr_bucket_folder":"old-dev/",
                "oauth_ret":"https://7firau5x7b.execute-api.eu-central-1.amazonaws.com/einvoice-v1/gmail-s3",
                "bucket_gmail_credential":"file-bucket-emp",
                "clientsec_location":"client_secret.json",
                "secreat":"test/einvoice/secret",
                "attach_stage":"dev"
            },
            "context": {
                "account-id": "",
                "api-id": "5ud4f0kv53",
                "api-key": "",
                "authorizer-principal-id": "",
                "caller": "",
                "cognito-authentication-provider": "",
                "cognito-authentication-type": "",
                "cognito-identity-id": "",
                "cognito-identity-pool-id": "",
                "http-method": "GET",
                "stage": "einvoice-v1",
                "source-ip": "49.207.50.252",
                "user": "",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "user-arn": "",
                "request-id": "0dd29bb0-bd12-4dab-85d9-582a9b9ffbee",
                "resource-id": "39vsp4",
                "resource-path": "/rules",
            },
        }

        event["body-json"] = body_json
        event["params"]["querystring"] = querystring
        event["params"]["header"] = header

        if resource_name in function_names:
            function_name = function_names[resource_name][request.method]
            print(function_name)

        if hasattr(mymodule1, function_name):
            function = getattr(mymodule1, function_name)
        elif hasattr(mymodule2, function_name):
            function = getattr(mymodule2, function_name)
        elif hasattr(mymodule3, function_name):
            function = getattr(mymodule3, function_name)
        elif hasattr(mymodule4, function_name):
            function = getattr(mymodule4, function_name)
        else :
            function = getattr(mymodule1, function_name)

        

        result = function(event, "")


        return result

    except AttributeError:
        return "Function not found"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
