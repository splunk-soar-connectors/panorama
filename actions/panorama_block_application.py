# File: panorama_block_application.py
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


class BlockApplication(BaseAction):

    def execute(self, connector):

        # making action result object
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        connector.debug_print("Starting block application action")

        block_app = self._param[consts.PAN_JSON_APPLICATION]

        # Add the application name to Objects > Application Groups > Phantom App List for your device group
        app_group_name = consts.BLOCK_APP_GROUP_NAME.format(
            device_group=self._param[consts.PAN_JSON_DEVICE_GRP])
        app_group_name = app_group_name[:consts.MAX_NODE_NAME_LEN].strip()

        data = {
            "type": "config",
            "action": "set",
            "key": connector.util._key,
            "xpath": consts.APP_GRP_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param),
                                              app_group_name=app_group_name),
            "element": consts.APP_GRP_ELEM.format(app_name=block_app)}

        status, response = connector.util._make_rest_call(data, action_result)
        action_result.update_summary({"add_application_to_application_group": response})

        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("blocking application", action_result.get_message())
            )

        connector.debug_print("fetching response data")
        message = action_result.get_message()

        if self._param.get("policy_name", ""):
            status = connector.util._update_security_policy(self._param, consts.SEC_POL_APP_TYPE, action_result, app_group_name)
            if phantom.is_fail(status):
                return action_result.set_status(phantom.APP_ERROR,
                                                consts.PAN_ERROR_MESSAGE.format("blocking application", action_result.get_message()))

        if self._param.get("should_commit_changes", True):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
