# File: panorama_create_policy.py
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
import phantom.app as phantom
from phantom.action_result import ActionResult

from actions import BaseAction
from panorama_consts import *


class CreatePolicy(BaseAction):

    def make_rest_call_helper(self, connector, xpath, element, action_result, where=None, dst=None):
        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': xpath,
            'element': element
        }
        if where and dst:
            data.update({'where': where, 'dst': dst})
        status, response = connector.util._make_rest_call(data, action_result)
        return status, response

    def execute(self, connector):

        connector.debug_print("Inside Create policy rule action")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))
        self._param[PAN_JSON_DISABLE] = self._param.get(PAN_JSON_DISABLE, False)
        where = self._param.get(PAN_JSON_WHERE, None)
        dst = self._param.get(PAN_JSON_DST, None)
        policy_type = self._param.get(PAN_JSON_POLICY_TYPE)
        policy_name = self._param[PAN_JSON_POLICY_NAME]
        rule_type = self._param.get(PAN_JSON_RULE_TYPE)
        audit_comment = self._param.get("audit_comment", None)
        self._param["should_commit_changes"] = self._param.get("should_commit_changes", False)
        self._param[PAN_JSON_NEGATE_SOURCE] = self._param.get(PAN_JSON_NEGATE_SOURCE, False)
        self._param[PAN_JSON_NEGATE_DESTINATION] = self._param.get(PAN_JSON_NEGATE_DESTINATION, False)
        device_grp = self._param[PAN_JSON_DEVICE_GRP]

        status = connector.util._validate_string(action_result, device_grp, PAN_JSON_DEVICE_GRP, 31)
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, action_result.action_result.get_message())

        status = connector.util._validate_string(action_result, policy_name, PAN_JSON_POLICY_NAME, 63)
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR,
                action_result.get_message())

        for param in self._param.copy():
            if param in param_mapping:
                new_key = param_mapping[param]
                self._param[new_key] = self._param[param]
                del self._param[param]

        status, policy_present = connector.util._does_policy_exist(self._param, action_result)
        if policy_present and connector.get_action_identifier() == "modify_policy":
            return action_result.set_status(
                phantom.APP_ERROR,
                "A policy with this name already exists. Please use another policy name."
            )

        # validate policy type
        if policy_type and policy_type.lower() not in POLICY_TYPE_VALUE_LIST:
            return action_result.set_status(
                phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(POLICY_TYPE_VALUE_LIST, PAN_JSON_POLICY_TYPE)
            )

        # validate object type in case of create custom block policy
        if self._param.get(PAN_JSON_OBJ_TYPE) and self._param.get(PAN_JSON_OBJ_TYPE) not in OBJ_TYPE_VALUE_LIST:
            return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(OBJ_TYPE_VALUE_LIST, PAN_JSON_OBJ_TYPE))

        # validate rule type
        if rule_type and rule_type.lower() not in RULE_TYPE_VALUE_LIST:
            return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(RULE_TYPE_VALUE_LIST, PAN_JSON_RULE_TYPE))

        if where in ["before", "after"] and not dst:
            return action_result.set_status(phantom.APP_ERROR, "dst is a required parameter for the entered value of \"where\"")

        element = connector.util._get_action_element(self._param)
        xpath = connector.util._get_security_policy_xpath(self._param, action_result)[1]
        status, response = self.make_rest_call_helper(connector, xpath, element, action_result, where, dst)
        action_result.add_data(response)
        message = action_result.get_message()

        if ("tag" and "not a valid") in message:
            tags = [value.strip() for value in self._param.get("tag", "").split(',') if value.strip()]
            status, _ = connector.util._create_tag(connector, action_result, self._param, tags)

            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error occurred while creating the tags."))
            else:
                status, response = self.make_rest_call_helper(connector, xpath, element, action_result, where, dst)
            action_result.add_data(response)
            message = action_result.get_message()

        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred: ", {message}))

        if audit_comment:
            status = connector.util._update_audit_comment(self._param, action_result)
            message = action_result.get_message()
            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred: ", {message}))

        if self._param["disabled"]:
            element = "<disabled>yes</disabled>"
            status, response = self.make_rest_call_helper(connector, xpath, element, action_result, where, dst)
            action_result.add_data(response)
            message = action_result.get_message()
            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred: ", {message}))

        if self._param["should_commit_changes"]:
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Successfull: {message}")
