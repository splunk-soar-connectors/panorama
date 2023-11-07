# File: panorama_consts.py
#
# Copyright (c) 2016-2023 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

PAN_ERROR_REPLY_FORMAT_KEY_MISSING = "None '{key}' missing in reply from device"
PAN_ERROR_REPLY_NOT_SUCCESS = "REST call returned '{status}'"
PAN_ERROR_UNABLE_TO_PARSE_REPLY = "Unable to parse reply from device : {error}"
PAN_SUCCESS_TEST_CONNECTIVITY_PASSED = "Test connectivity passed"
PAN_ERROR_TEST_CONNECTIVITY_FAILED = "Test connectivity failed"
PAN_SUCCESS_REST_CALL_PASSED = "REST Api call passed"
PAN_ERROR_CREATE_UNKNOWN_TYPE_SEC_POL = "Asked to create unknown type of security policy"
PAN_ERROR_INVALID_IP_FORMAT = "Invalid ip format"
PAN_ERROR_DEVICE_CONNECTIVITY = "Error in connecting to device"
PAN_ERROR_PARSE_POLICY_DATA = "Unable to parse security policy config"
PAN_ERROR_NO_POLICY_ENTRIES_FOUND = "Could not find any security policies to update"
PAN_ERROR_NO_ALLOW_POLICY_ENTRIES_FOUND = ("Did not find any policies with an 'allow' action for device group '{dev_sys_value}' and "
                                           "type '{policy_type}'.")
PAN_ERROR_NO_ALLOW_POLICY_ENTRIES_FOUND += "\nNeed atleast one such policy"
PAN_ERROR_POLICY_NOT_PRESENT_CONFIG_DONT_CREATE = "Policy not found. Please verify that provided parameter values are correct"
PAN_ERROR_NO_JOB_ID = "Could not find Job ID in response body"
PAN_ERROR_MESSAGE = "Error occurred while {}. Details: {}"

PAN_PROG_USING_BASE_URL = "Using base URL '{base_url}'"
PAN_PROG_GOT_REPLY = "Got reply, parsing..."
PAN_PROG_PARSED_REPLY = "Done"
PAN_PROG_COMMIT_PROGRESS = "Commit completed {progress}%"
PAN_PROG_COMMIT_ALL_PROGRESS = "Commit on device group: {device_group} completed {progress}%"
PAN_PROG_COMMIT_PROGRESS_PENDING = "Commit completed {progress}%, but still Pending on remote device"

PAN_JSON_DEVICE_GRP = "device_group"
PAN_JSON_URL = "url"
PAN_JSON_APPLICATION = "application"
PAN_JSON_IP = "ip"
PAN_JSON_TOTAL_APPLICATIONS = "total_applications"
PAN_JSON_TOTAL_EDL = "total_external_dynamic_lists"
PAN_JSON_TOTAL_ADR_GRP = "total_address_groups"

PAN_JSON_SEC_POLICY = "sec_policy"
PAN_JSON_POLICY_TYPE = "policy_type"
PAN_JSON_POLICY_NAME = "policy_name"
PAN_JSON_CREATE_POLICY = "create_policy"
PAN_JSON_SOURCE_ADDRESS = "is_source_address"
PAN_JSON_QUERY = "query"
PAN_JSON_LOG_TYPE = "log_type"
PAN_DEFAULT_SOURCE_ADDRESS = False

# Name consts
SEC_POL_NAME = "Phantom {sec_policy_type} Security Policy"
SEC_POL_NAME_SRC = "Phantom src {type} Security Policy"
BLOCK_URL_PROF_NAME = "Phantom URL List for {device_group}"
BLOCK_IP_GROUP_NAME = "Phantom Network List for {device_group}"
BLOCK_IP_GROUP_NAME_SRC = "PhantomNtwrkSrcLst{device_group}"
BLOCK_APP_GROUP_NAME = "Phantom App List for {device_group}"
PHANTOM_ADDRESS_NAME = "Added By Phantom"
PAN_DEV_GRP_SHARED = "shared"
DEVICE_GRP_XPATH = "/config/devices/entry{formatted_device_entry_name}/device-group/entry[@name='{device_group}']"
VSYS_XPATH = "/config/device/entry/vsys/entry"

SEC_POL_URL_TYPE = "URL"
SEC_POL_APP_TYPE = "App"
SEC_POL_IP_TYPE = "IP"

EDL_ADR_POLICY_NAME = "name"
MAX_NAME_LEN = 63
MAX_DEVICE_GRP_NAME_LEN = 31
MAX_NODE_NAME_LEN = 31
MAX_TAG_NAME_LEN = 127
MAX_QUERY_COUNT = 5000

# Various xpaths and elem nodes

# This one is used to get all the policies
SEC_POL_RULES_XPATH = "{config_xpath}/{policy_type}/security/rules"

# This one is used while adding a security policy
SEC_POL_XPATH = "{config_xpath}/{policy_type}/security/rules/entry[@name='{sec_policy_name}']"

SEC_POL_DEF_ELEMS = "<from><member>any</member></from>"
SEC_POL_DEF_ELEMS += "<to><member>any</member></to>"
SEC_POL_DEF_ELEMS += "<source><member>any</member></source>"
SEC_POL_DEF_ELEMS += "<source-user><member>any</member></source-user>"
SEC_POL_DEF_ELEMS += "<category><member>any</member></category>"
SEC_POL_DEF_ELEMS += "<service><member>application-default</member></service>"
SEC_POL_DEF_ELEMS += "<hip-profiles><member>any</member></hip-profiles>"
SEC_POL_DEF_ELEMS += "<description>Created by Phantom for Panorama, please don't edit</description>"

ACTION_NODE_DENY = "<action>deny</action>"
ACTION_NODE_ALLOW = "<action>allow</action>"
URL_PROF_SEC_POL_ELEM = "<profile-setting>"
URL_PROF_SEC_POL_ELEM += "<profiles><url-filtering><member>{url_prof_name}</member></url-filtering></profiles>"
URL_PROF_SEC_POL_ELEM += "</profile-setting>"

IP_GRP_SEC_POL_ELEM = "<destination><member>{ip_group_name}</member></destination>"
IP_GRP_SEC_POL_ELEM_SRC = "<source><member>{ip_group_name}</member></source>"
APP_GRP_SEC_POL_ELEM = "<application><member>{app_group_name}</member></application>"

URL_PROF_XPATH = "{config_xpath}/profiles/url-filtering/entry[@name='{url_profile_name}']"
DEL_URL_CATEGORY_XPATH = "/list/member[text()='{url}']"

# URL_PROF_ELEM for version 8 and below. block-list is no longer supported from 9.0 and above.
URL_PROF_ELEM = "<description>Created by Phantom for Panorama</description>"
URL_PROF_ELEM += "<action>block</action><block-list><member>{url}</member></block-list>"

# URL_PROF_ELEM for version 9 and above.
URL_PROF_ELEM_9 = "<credential-enforcement>"
URL_PROF_ELEM_9 += "<mode><disabled/></mode><log-severity>medium</log-severity>"
URL_PROF_ELEM_9 += "<block><member>{url_category_name}</member></block>"
URL_PROF_ELEM_9 += "</credential-enforcement>"
URL_PROF_ELEM_9 += "<block><member>{url_category_name}</member></block>"

URL_CATEGORY_XPATH = "{config_xpath}/profiles/custom-url-category/entry[@name='{url_profile_name}']"

# We can make this work on version 8 and below as well by removing <type>URL List</type>.
# However, </list><type>URL List</type> is required for version 9 and above.
URL_CATEGORY_ELEM = "<description>Created by Phantom for Panorama</description>"
URL_CATEGORY_ELEM += "<list><member>{url}</member></list>"
URL_CATEGORY_ELEM += "<type>URL List</type>"

DEL_URL_XPATH = "/block-list/member[text()='{url}']"

APP_GRP_XPATH = "{config_xpath}/application-group/entry[@name='{app_group_name}']"
APP_GRP_ELEM = "<members><member>{app_name}</member></members>"
DEL_APP_XPATH = "/members/member[text()='{app_name}']"

ADDR_GRP_XPATH = "{config_xpath}/address-group/entry[@name='{ip_group_name}']"
ADDR_GRP_ELEM = "<static><member>{addr_name}</member></static>"
DEL_ADDR_GRP_XPATH = "/static/member[text()='{addr_name}']"
GET_ADDR_GRP_XPATH = "{config_xpath}/address-group"
REF_ADDR_GRP_XPATH = "{config_xpath}/address-group/entry[@name='{address_group_name}']"

IP_ADDR_XPATH = "{config_xpath}/address/entry[@name='{ip_addr_name}']"
IP_ADDR_ELEM = "<{ip_type}>{ip}</{ip_type}>"
IP_ADDR_TAG_ELEM = "<tag><member>{tag}</member></tag>"

TAG_CONTAINER_COMMENT = "Phantom Container ID"
TAG_COLOR = "color7"
TAG_XPATH = "{config_xpath}/tag"
EDL_XPATH = "{config_xpath}/external-list"
TAG_ELEM = "<entry name='{tag}'><color>{tag_color}</color><comments>{tag_comment}</comments></entry>"

START_TAG = "<entry name='{tag}'>"
END_TAG = "</entry>"
TAG_COMMENT = "Tag created from Splunk SOAR"
GET_TAG_XPATH = "{config_xpath}/tag/entry[@name='{name}']"
ADDRESS_XPATH = "{config_xpath}/address/entry[@name='{name}']"

APP_LIST_XPATH = "/config/predefined/application"
COMMIT_ALL_DEV_GRP_DEV_CMD = '<commit-all><shared-policy>'
COMMIT_ALL_DEV_GRP_DEV_CMD += '<device-group>'
COMMIT_ALL_DEV_GRP_DEV_CMD += '<entry name="{device_group}"><devices><entry name="{dev_ser_num}"/></devices></entry>'
COMMIT_ALL_DEV_GRP_DEV_CMD += '</device-group>'
COMMIT_ALL_DEV_GRP_DEV_CMD += '</shared-policy></commit-all>'

# Constants relating to value_list check
POLICY_TYPE_VALUE_LIST = ["pre-rulebase", "post-rulebase"]
RULE_TYPE_VALUE_LIST = ["universal", "intrazone", "interzone"]
LOG_TYPE_VALUE_LIST = ["traffic", "url", "corr", "data", "threat", "config", "system", "hipmatch", "wildfire", "corr-categ", "corr-detail"]
DIRECTION_VALUE_LIST = ["backward", "forward"]
VALUE_LIST_VALIDATION_MESSAGE = "Please provide valid input from {} in '{}' action parameter"

DEFAULT_TIMEOUT = 30

PAN_KEY_TOKEN = "key_token"
PAN_ERROR_MESSAGE_UNAVAILABLE = "Error message unavailable. Please check the asset configuration and|or action parameters"

PAN_EDL_TYPES = {
    "predefined ip list": "predefined-ip",
    "predefined url list": "predefined-url",
    "ip list": "ip",
    "domain list": "domain",
    "url list": "url",
    "subscriber identity list": "imsi",
    "equipment identity list": "imei"
}

PAN_EDL_TYPES_STR = " The valid list types for EDL are : Predefined IP List, Predefined Url\
      List, IP List, Domain List, URL List, Subscriber Identity List, Equipment Identity List"

PAN_EDL_CHECK_UPDATE_STR = "The valid values for check for update are : five-minute, hourly, daily, weekly, monthly"

PAN_EDL_WEEK_DAY_STR = "The valid values for day are : monday, tuesday, wednesday, thursday, friday, saturday, sunday"

# Constants related to Policy rule
PAN_JSON_NAME = "policy_name"
PAN_JSON_POLICY_TYPE = "policy_type"
PAN_JSON_RULE_TYPE = "rule_type"
PAN_JSON_NEGATE_SOURCE = "negate-source"
PAN_JSON_NEGATE_DESTINATION = "negate-destination"
PAN_JSON_WHERE = "where"
PAN_JSON_DST = "dst"
PAN_JSON_TAGS = "tag"
PAN_JSON_DISABLE = "disabled"
PAN_JSON_ACTION = "action"
PAN_JSON_ICMP_UNREACHABLE = "icmp-unreachable"
PAN_JSON_DESTINATION_ADDRESS = "destination_address"
PAN_JSON_CATEGORY = "category"
PAN_JSON_AUDIT_COMMENT = "audit_comment"
PAN_JSON_NEGATE_SOURCE = "negate-source"
PAN_JSON_NEGATE_DESTINATION = "negate-destination"
PAN_JSON_DESC = "description"

# Constants related to Custom Block Policy
PAN_JSON_OBJ_TYPE = "object_type"
PAN_JSON_OBJ_VAL = "object_value"
PAN_JSON_DIR = "direction"
PAN_JSON_POL_SOURCE_ADD = "source_address"

# Constants related to Address Group
PAN_JSON_ADD_GRP_TYPE = "type"
PAN_JSON_ADD_GRP_DIS_OVER = "disable-override"

OBJ_TYPE_VALUE_LIST = ["ip", "address-group", "edl", "url-category", "application"]
SEC_POLICY_WITHOUT_MEMBER = ['rule-type', 'description', 'action', 'target', 'profile-setting',
                             'log-setting', 'negate-source', 'negate-destination', 'icmp-unreachable']
SEC_POLICY_NOT_INCLUDE_BOOL_PARAM_LIST = ['use_partial_commit', 'should_commit_changes', 'disabled']
SEC_POLICY_WITH_MEMBER = ['from', 'to', 'source', 'destination', 'source-user',
                          'service', 'source-hip', 'destination-hip', 'application', 'category']
CREATE_POL_REQ_PARAM_LIST = ["source_address", "destination_address", "source_zone", "destination_zone", "service", "application"]
WHERE_VALUE_LIST = ["after", "before", "top", "bottom"]
ACTION_VALUE_LIST = ["allow", "deny", "drop", "reset client", "reset server", "reset both client and server"]
IP_ADD_TYPE = {
    "ip netmask": "ip-netmask",
    "ip range": "ip-range",
    "ip wildcard mask": "ip-wildcard",
    "fqdn": "fqdn"
}

param_mapping = {
    "rule_type": "rule-type",
    "source_user": "source-user",
    "source_device": "source-hip",
    "destination_device": "destination-hip",
    "log_forwarding": "log-setting",
    "profile_setting": "profile-setting",
    "source_address": "source",
    "destination_address": "destination",
    "source_zone": "from",
    "destination_zone": "to",
    "disable": "disabled",
    "disable_override": "disable-override",
    "icmp_unreachable": "icmp-unreachable",
    "negate_source": "negate-source",
    "negate_destination": "negate-destination"
}


PAN_ERROR_MESSAGE_FROM_CODE = {
    "400": "Bad request",
    "403": "Forbidden",
    "1": "Unknown command",
    "2": "Internal error",
    "3": "Internal error",
    "4": "Internal error",
    "5": "Internal error",
    "6": "Bad Xpath",
    "7": "Object not present",
    "8": "Object not unique",
    "10": "Reference count not zero",
    "11": "Internal error",
    "12": "Invalid object",
    "13": "Object not found",
    "14": "Operation not possible",
    "15": "Operation denied",
    "16": "Unauthorized",
    "17": "Invalid command",
    "18": "Malformed command",
    "21": "Internal error",
    "22": "Session timed out"
}
PAN_CODE_NOT_PRESENT_MESSAGE = "Unknown error returned from API"

ADD_GRP_TYPE_VAL_LIST = ["static", "dynamic"]
VALIDATE_STRING_ERROR_MESSAGE = "Invalid value provided for the {param_name} parameter. The name must start with a alphanumeric character and\
     can contain alphanumeric characters, hyphen(-), underscore(_), dot(.) and spaces"
PAN_CODE_NOT_PRESENT_MESSAGE = "Unknown error returned from API"
