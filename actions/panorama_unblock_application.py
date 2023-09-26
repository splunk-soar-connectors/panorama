# File: unblock_application.py
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
from panorama_consts import (APP_GRP_XPATH, BLOCK_APP_GROUP_NAME, DEL_APP_XPATH, MAX_NODE_NAME_LEN, PAN_ERROR_MESSAGE, PAN_JSON_APPLICATION,
                             PAN_JSON_DEVICE_GRP)


class UnblockApplication(BaseAction):

    def execute(self, connector):

        connector.debug_print("Removing the Blocked Application")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        block_app = self._param[PAN_JSON_APPLICATION]

        app_group_name = BLOCK_APP_GROUP_NAME.format(device_group=self._param[PAN_JSON_DEVICE_GRP])
        app_group_name = app_group_name[:MAX_NODE_NAME_LEN].strip()

        # Delete the given application name from Objects > Application Groups > Phantom App List for your device group
        xpath = "{0}{1}".format(
            APP_GRP_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param), app_group_name=app_group_name),
            DEL_APP_XPATH.format(app_name=block_app))

        data = {'type': 'config',
                'action': 'delete',
                'key': connector.util._key,
                'xpath': xpath}

        status, response = connector.util._make_rest_call(data, action_result)
        action_result.update_summary({'delete_application_from_application_group': response})
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("unblocking application", action_result.get_message()))

        message = action_result.get_message()

        if self._param.get('should_commit_changes', False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
