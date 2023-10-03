# File: panorama_reference_address_group.py
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


class GetAddressGroup(BaseAction):

    def execute(self, connector):

        connector.debug_print("starting reference address groups action")
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        address_group_name = self._param["name"]

        get_address_xpath = f"""{consts.REF_ADDR_GRP_XPATH.format(
            config_xpath=connector.util._get_config_xpath(self._param), address_group_name=address_group_name)}"""

        data = {
            "type": "config",
            'action': "get",
            'key': connector.util._key,
            'xpath': get_address_xpath
        }

        status, _ = connector.util._make_rest_call(data, action_result)
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("reference address group", action_result.get_message()))

        result_data = action_result.get_data()
        result_data = result_data.pop()

        if result_data.get("@total-count") == "0":
            return action_result.set_status(phantom.APP_ERROR, "No address group found")

        try:
            result_data = result_data.get('entry')
        except Exception as e:
            error = connector.util._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, "Error occurred while processing response from server. {}".format(error))

        action_result.update_data([result_data])

        return action_result.set_status(phantom.APP_SUCCESS, "Successfully fetched address group details")
