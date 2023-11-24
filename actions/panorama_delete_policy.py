# File: panorama_delete_policy.py
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
from panorama_consts import PAN_ERROR_MESSAGE, PAN_JSON_POLICY_TYPE, POLICY_TYPE_VALUE_LIST, VALUE_LIST_VALIDATION_MESSAGE


class DeletePolicy(BaseAction):

    def execute(self, connector):
        connector.debug_print("Inside delete policy action")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        parameter = self._param.copy()

        if parameter[PAN_JSON_POLICY_TYPE].lower() not in POLICY_TYPE_VALUE_LIST:
            return action_result.set_status(
                phantom.APP_ERROR,
                VALUE_LIST_VALIDATION_MESSAGE.format(POLICY_TYPE_VALUE_LIST, PAN_JSON_POLICY_TYPE)
            )
        else:
            parameter[PAN_JSON_POLICY_TYPE] = parameter[PAN_JSON_POLICY_TYPE].lower()

        xpath = connector.util._get_security_policy_xpath(parameter, action_result)
        data = {
            'type': 'config',
            'action': 'delete',
            'key': connector.util._key,
            'xpath': xpath[1]
        }
        status, response = connector.util._make_rest_call(data, action_result)
        message = action_result.get_message()
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("delete policy rule", message))

        action_result.add_data(response)

        if parameter.get('should_commit_changes', False):
            status = connector.util._commit_and_commit_all(parameter, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
