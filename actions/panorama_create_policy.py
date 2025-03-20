# File: panorama_create_policy.py
#
# Copyright (c) 2016-2025 Splunk Inc.
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

import phantom.app as phantom
from phantom.action_result import ActionResult

from actions import BaseAction
from panorama_consts import *


class CreatePolicy(BaseAction):
    def make_rest_call_helper(self, connector, xpath, element, action_result):
        data = {"type": "config", "action": "set", "key": connector.util._key, "xpath": xpath, "element": element}
        status, response = connector.util._make_rest_call(data, action_result)
        return status, response

    def execute(self, connector, action_result=None):
        connector.debug_print("Inside Create policy rule action")

        if connector.get_action_identifier() != "custom_block_policy":
            action_result = connector.add_action_result(ActionResult(dict(self._param)))

        parameter = self._param.copy()

        where = parameter.get(PAN_JSON_WHERE, None)
        dst = parameter.get(PAN_JSON_DST, None)
        policy_type = parameter.get(PAN_JSON_POLICY_TYPE)
        rule_type = parameter.get(PAN_JSON_RULE_TYPE)
        audit_comment = parameter.get(PAN_JSON_AUDIT_COMMENT, None)
        description = parameter.get(PAN_JSON_DESC, None)
        # validate description length
        if description and len(description) > 1024:
            return action_result.set_status(phantom.APP_ERROR, "The length of description is too long. It should not exceed 1024 characters.")

        if connector.get_action_identifier() != "modify_policy":
            for param in CREATE_POL_REQ_PARAM_LIST:
                param_list = parameter[param].split(",")
                param_list = [value.strip() for value in param_list if value.strip("")]
                if len(param_list) == 0:
                    return action_result.set_status(phantom.APP_ERROR, f"'{param}' is a required value hence please add a valid input")
        # parameter mapping for preparing the element
        for param in parameter.copy():
            if param in param_mapping:
                new_key = param_mapping.get(param)
                parameter[new_key] = parameter.get(param)
                del parameter[param]
        # value list validation for action
        if parameter.get(PAN_JSON_ACTION):
            if parameter.get(PAN_JSON_ACTION).lower() not in ACTION_VALUE_LIST:
                return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(ACTION_VALUE_LIST, PAN_JSON_ACTION))
            else:
                parameter[PAN_JSON_ACTION] = parameter[PAN_JSON_ACTION].lower()
        # value list validation for negate source
        if parameter.get(PAN_JSON_NEGATE_SOURCE):
            if parameter.get(PAN_JSON_NEGATE_SOURCE).lower() not in ["yes", "no"]:
                return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(["Yes", "No"], "negate_source"))
            else:
                parameter[PAN_JSON_NEGATE_SOURCE] = parameter.get(PAN_JSON_NEGATE_SOURCE).lower()
        # value list validation for negate destination
        if parameter.get(PAN_JSON_NEGATE_DESTINATION):
            if parameter.get(PAN_JSON_NEGATE_DESTINATION).lower() not in ["yes", "no"]:
                return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(["Yes", "No"], "negate_destination"))
            else:
                parameter[PAN_JSON_NEGATE_DESTINATION] = parameter.get(PAN_JSON_NEGATE_DESTINATION).lower()
        # value list validation for icmp_unreachable
        if parameter.get(PAN_JSON_ICMP_UNREACHABLE):
            if parameter.get(PAN_JSON_ICMP_UNREACHABLE).lower() not in ["yes", "no"]:
                return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(["Yes", "No"], "icmp_unreachable"))
            else:
                parameter[PAN_JSON_ICMP_UNREACHABLE] = parameter.get(PAN_JSON_ICMP_UNREACHABLE).lower()
        # value list validation for disable
        if parameter.get(PAN_JSON_DISABLE):
            if parameter.get(PAN_JSON_DISABLE).lower() not in ["yes", "no"]:
                return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(["Yes", "No"], "disable"))
            else:
                parameter[PAN_JSON_DISABLE] = parameter.get(PAN_JSON_DISABLE).lower()
        # check if a policy with same name exists
        status, policy_present = connector.util._does_policy_exist(parameter, action_result)

        if policy_present and connector.get_action_identifier() != "modify_policy":
            return action_result.set_status(phantom.APP_ERROR, "A policy with this name already exists. Please use another policy name.")

        elif not policy_present and connector.get_action_identifier() == "modify_policy":
            return action_result.set_status(phantom.APP_ERROR, "This policy is not present. Please enter a valid policy name.")
        # validate policy type
        if policy_type:
            if policy_type.lower() not in POLICY_TYPE_VALUE_LIST:
                return action_result.set_status(
                    phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(POLICY_TYPE_VALUE_LIST, PAN_JSON_POLICY_TYPE)
                )
            else:
                parameter[PAN_JSON_POLICY_TYPE] = parameter.get(PAN_JSON_POLICY_TYPE).lower()
        # validate object type in case of create custom block policy

        if parameter.get(PAN_JSON_OBJ_TYPE):
            if parameter.get(PAN_JSON_OBJ_TYPE).lower() not in OBJ_TYPE_VALUE_LIST:
                return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(OBJ_TYPE_VALUE_LIST, PAN_JSON_OBJ_TYPE))
            else:
                parameter[PAN_JSON_OBJ_TYPE] = parameter.get(PAN_JSON_OBJ_TYPE).lower()
        # validate rule type
        if rule_type:
            if rule_type.lower() not in RULE_TYPE_VALUE_LIST:
                return action_result.set_status(
                    phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(RULE_TYPE_VALUE_LIST, PAN_JSON_RULE_TYPE)
                )
            else:
                parameter["rule-type"] = parameter.get("rule-type").lower()
        # value list validation for where
        if where:
            if where.lower() not in WHERE_VALUE_LIST:
                return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(WHERE_VALUE_LIST, PAN_JSON_WHERE))
            elif where.lower() in ["before", "after"] and not dst:
                return action_result.set_status(
                    phantom.APP_ERROR,
                    'dst is a required parameter\
                                             for the entered value of "where"',
                )
            else:
                parameter[PAN_JSON_WHERE] = parameter.get(PAN_JSON_WHERE).lower()

        element = connector.util._get_action_element(parameter)

        result = connector.util._get_security_policy_xpath(parameter, action_result)
        if result[0]:
            xpath = result[1]
        else:
            return action_result.get_status()

        if parameter.get("tag"):
            tags = [value.strip() for value in parameter.get("tag").split(",") if value.strip()]
            if tags:
                status, tag_element_string = connector.util._create_tag(connector, action_result, parameter, tags)
                message = action_result.get_message()
                if phantom.is_fail(status):
                    return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("creating the tags: ", message))
                element += tag_element_string

        status, _ = self.make_rest_call_helper(connector, xpath, element, action_result)

        message = action_result.get_message()
        # if nothing to modify in policy, but audit comment needs to be added or it has to be enabled
        # or disabled while modifying then do not display the message returned due to empty element from API yet
        if not ((not element and phantom.is_fail(status)) and (audit_comment or parameter.get(PAN_JSON_DISABLE))):
            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("creating policy: ", message))
        if audit_comment:
            status = connector.util._update_audit_comment(parameter, action_result)
            message1 = action_result.get_message()
            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("adding audit comment: ", message1))

        if where and where != "bottom":
            data = {"type": "config", "action": "move", "key": connector.util._key, "xpath": xpath, "where": where}
            if dst:
                data.update({"dst": dst})
            status, _ = connector.util._make_rest_call(data, action_result)
            message1 = action_result.get_message()
            if phantom.is_fail(status):
                return action_result.set_status(
                    phantom.APP_SUCCESS,
                    f"The policy has been created but unable to move \
                                                it to the specified location: {PAN_ERROR_MESSAGE.format('moving policy', message1)}",
                )

        if parameter.get(PAN_JSON_DISABLE):
            if parameter.get(PAN_JSON_DISABLE) == "yes":
                element = "<disabled>yes</disabled>"
            else:
                element = "<disabled>no</disabled>"
            status, _ = self.make_rest_call_helper(connector, xpath, element, action_result)
            message1 = action_result.get_message()
            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("disabling policy :", {message1}))

        if parameter.get("should_commit_changes", False):
            status = connector.util._commit_and_commit_all(parameter, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()
        return action_result.set_status(phantom.APP_SUCCESS, f"Response Received: {message}")
