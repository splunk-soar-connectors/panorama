# File: panorama_delete_edl.py
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


class DeleteEdl(BaseAction):

    def execute(self, connector):

        # making action result object
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        edl_name = self._param["name"]

        delete_xpath = f"{consts.EDL_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param))}/entry[@name='{edl_name}']"

        data = {
            'type': 'config',
            'action': 'delete',
            'key': connector.util._key,
            'xpath':  delete_xpath,
        }

        status, response = connector.util._make_rest_call(data, action_result)

        action_result.update_summary({'delete_edl': response})
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("deleting edl", action_result.get_message()))

        message = action_result.get_message()

        if self._param.get('should_commit_changes', True):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
