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
from panorama_consts import (CREATE_POL_REQ_PARAM_LIST, OBJ_TYPE_VALUE_LIST, PAN_ERROR_MESSAGE, PAN_JSON_AUDIT_COMMENT, PAN_JSON_DESC,
                             PAN_JSON_DISABLE, PAN_JSON_DST, PAN_JSON_NEGATE_DESTINATION, PAN_JSON_NEGATE_SOURCE, PAN_JSON_OBJ_TYPE,
                             PAN_JSON_POLICY_TYPE, PAN_JSON_RULE_TYPE, PAN_JSON_WHERE, POLICY_TYPE_VALUE_LIST, RULE_TYPE_VALUE_LIST,
                             VALUE_LIST_VALIDATION_MESSAGE, param_mapping)


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
        rule_type = self._param.get(PAN_JSON_RULE_TYPE)
        audit_comment = self._param.get(PAN_JSON_AUDIT_COMMENT, None)
        description = self._param.get(PAN_JSON_DESC, None)

        self._param[PAN_JSON_NEGATE_SOURCE] = self._param.get("negate_source", "none").lower()
        self._param[PAN_JSON_NEGATE_DESTINATION] = self._param.get("negate_destination", "none").lower()

        if description and len(description) > 1024:
            return action_result.set_status(
                phantom.APP_ERROR, "The length of description is too long. It should not exceed 1024 characters.")

        if connector.get_action_identifier() != "modify_policy":
            for param in CREATE_POL_REQ_PARAM_LIST:
                param_list = self._param[param].split(",")
                param_list = [value.strip() for value in param_list if value.strip(" ,")]
                if len(param_list) == 0:
                    return action_result.set_status(
                        phantom.APP_ERROR,
                        f"'{param}' is a required value hence please add a valid input"
                    )

        for param in self._param.copy():
            if param in param_mapping:
                new_key = param_mapping.get(param)
                self._param[new_key] = self._param.get(param)
                del self._param[param]

        if self._param[PAN_JSON_NEGATE_SOURCE] not in ["none", "true", "false"]:
            return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(["none", "true", "false"], "negate_source"))

        if self._param[PAN_JSON_NEGATE_DESTINATION] not in ["none", "true", "false"]:
            return action_result.set_status(phantom.APP_ERROR, VALUE_LIST_VALIDATION_MESSAGE.format(["none", "true", "false"],
                                                                                                    "negate_destination"))
        if self._param[PAN_JSON_NEGATE_SOURCE] == "none":
            del self._param[PAN_JSON_NEGATE_SOURCE]

        if self._param[PAN_JSON_NEGATE_DESTINATION] == "none":
            del self._param[PAN_JSON_NEGATE_DESTINATION]

        status, policy_present = connector.util._does_policy_exist(self._param, action_result)
        if policy_present and connector.get_action_identifier() != "modify_policy":
            return action_result.set_status(
                phantom.APP_ERROR,
                "A policy with this name already exists. Please use another policy name."
            )
        elif not policy_present and connector.get_action_identifier() == "modify_policy":
            return action_result.set_status(
                phantom.APP_ERROR,
                "This policy is not present. Please enter a valid policy name."
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
        if not element:
            return action_result.set_status(phantom.APP_ERROR, "Please add at least one value to modify the policy")

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
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred :", {message}))

        if audit_comment:
            status = connector.util._update_audit_comment(self._param, action_result)
            message = action_result.get_message()
            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred :", {message}))

        if self._param["disabled"] in [True, "true"]:
            element = "<disabled>yes</disabled>"
            if self._param["disabled"] in [False, "false"]:
                element = "<disabled>no</disabled>"
            status, response = self.make_rest_call_helper(connector, xpath, element, action_result, where, dst)
            action_result.add_data(response)
            message = action_result.get_message()
            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred :", {message}))

        if self._param.get("should_commit_changes", False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Successful: {message}")
