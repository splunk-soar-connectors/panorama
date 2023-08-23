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

from panorama_consts import BLOCK_APP_GROUP_NAME, PAN_JSON_APPLICATION, PAN_JSON_DEVICE_GRP, MAX_NODE_NAME_LEN, PAN_ERROR_MESSAGE, APP_GRP_XPATH, DEL_APP_XPATH
from actions import BaseAction

class UnblockApplication(BaseAction):

    def execute(self):

        self._connector.debug_print("Removing the Blocked Application")

        block_app = self._param[PAN_JSON_APPLICATION]

        app_group_name = BLOCK_APP_GROUP_NAME.format(device_group=self._param[PAN_JSON_DEVICE_GRP])
        app_group_name = app_group_name[:MAX_NODE_NAME_LEN].strip()

        # Delete the given application name from Objects > Application Groups > Phantom App List for your device group
        xpath = "{0}{1}".format(
            APP_GRP_XPATH.format(config_xpath=self._connector.util._get_config_xpath(self._param), app_group_name=app_group_name),
            DEL_APP_XPATH.format(app_name=block_app))

        data = {'type': 'config',
                'action': 'delete',
                'key': self._connector.util._key,
                'xpath': xpath}

        status, response = self._connector.util._make_rest_call(data, self._action_result)
        self._action_result.update_summary({'delete_application_from_application_group': response})
        if phantom.is_fail(status):
            return self._action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("unblocking application", self._action_result.get_message()))

        message = self._action_result.get_message()

        if self._param.get('should_commit_changes', True):
            status = self._connector.util._commit_and_commit_all(self._param, self._action_result)
            if phantom.is_fail(status):
                return self._action_result.get_status()

        return self._action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
