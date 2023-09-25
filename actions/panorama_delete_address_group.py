# File: delete_address_group.py
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


class DeleteAddressGroup(BaseAction):

    def execute(self, connector):

        connector.debug_print("starting delete address group action")
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        address_group_name = self._param["name"]

        get_address_xpath = f"{consts.REF_ADDR_GRP_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param), address_group_name=address_group_name)}"

        data = {
            "type": "config",
            'action': "delete",
            'key': connector.util._key,
            'xpath': get_address_xpath
        }

        status, _ = connector.util._make_rest_call(data, action_result)
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("deleting address group", action_result.get_message()))

        action_result.update_summary({"message": "successfully deleted address group"})

        message = action_result.get_message()

        if self._param.get('should_commit_changes', False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
