# File: panorama_list_edl.py
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


class ListEdl(BaseAction):

    def execute(self, connector):

        # making action result object
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        connector.debug_print("starting list edl action")

        data = {
            "type": "config",
            'action': "get",
            'key': connector.util._key,
            'xpath': consts.EDL_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param))
        }

        status, _ = connector.util._make_rest_call(data, action_result)

        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format(connector.get_action_identifier(), action_result.get_message()))

        connector.debug_print("fetching result data")
        result_data = action_result.get_data().pop()

        try:
            result_data = result_data["external-list"].get("entry")
            if not result_data:
                return action_result.set_status(phantom.APP_ERROR, "No EDLs found in the device group")
        except Exception as e:
            error = connector.util._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, "Error occurred while processing response from server. {}".format(error))

        if isinstance(result_data, dict):
            result_data = [result_data]

        action_result.update_summary({consts.PAN_JSON_TOTAL_EDL: len(result_data)})
        action_result.update_data(result_data)

        return action_result.set_status(phantom.APP_SUCCESS)
