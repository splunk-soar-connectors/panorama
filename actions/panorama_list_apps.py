# File: panorama_list_apps.py
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

import panorama_consts as consts
from actions import BaseAction


class ListApps(BaseAction):

    def execute(self, connector):

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        # Add the address to the phantom address group
        data = {
            "type": "config",
            'action': "get",
            'key': connector.util._key,
            'xpath': consts.APP_LIST_XPATH
        }

        status, _ = connector.util._make_rest_call(data, action_result)
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("retrieving list of application", action_result.get_message()))

        # Move things around, so that result data is an array of applications
        result_data = action_result.get_data().pop()
        try:
            result_data = result_data['application']['entry']
        except Exception as e:
            error = connector.util._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, "Error occurred while processing response from server. {}".format(error))

        action_result.update_summary({consts.PAN_JSON_TOTAL_APPLICATIONS: len(result_data)})

        action_result.update_data(result_data)

        return action_result.set_status(phantom.APP_SUCCESS)
