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

    def execute(self, connector):

        connector.debug_print("Inside Create policy rule action")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        where = self._param.get(PAN_JSON_WHERE)
        dst = self._param.get(PAN_JSON_DST)
        policy_type = self._param.get(PAN_JSON_POLICY_TYPE)
        rule_type = self._param.get(PAN_JSON_RULE_TYPE)

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
        xpath = connector.util._get_security_policy_xpath(self._param, action_result)

        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': xpath[1],
            'element': element
        }

        if self._param.get("where") and self._param.get("dst"):
            data.update({'where': where, 'dst': dst})

        status, response = connector.util._make_rest_call(data, action_result)
        action_result.add_data(response)
        message = action_result.get_message()
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("Error Occurred: ", {message}))
        if self._param.get('should_commit_changes', True):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, f"Successfull: {message}")
