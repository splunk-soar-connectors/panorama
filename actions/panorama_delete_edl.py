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

import panorama_consts as consts
from actions import BaseAction


class DeleteEdl(BaseAction):
    
    def execute(self):
        

        self._connector.debug_print('Deleting EDL...')
        edl_name =  self._param["name"]
        
        delete_xpath = f"{consts.EDL_XPATH.format(config_xpath=self._connector.util._get_config_xpath(self._param))}/entry[@name='{edl_name}']"
        self._connector.debug_print(f"delete_xpath data : {delete_xpath}")
     

        data = {
            'type': 'config',
            'action': 'delete',
            'key': self._connector.util._key,
            'xpath':  delete_xpath,
        }

        status, response  =  self._connector.util._make_rest_call(data, self._action_result)

        self._action_result.update_summary({'delete_edl': response})
        if phantom.is_fail(status):
            return self._action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("deleting edl", self._action_result.get_message()))
        
        message = self._action_result.get_message()

        if self._param.get('should_commit_changes', True):
            status = self._connector.util._commit_and_commit_all(self._param, self._action_result)
            if phantom.is_fail(status):
                return self._action_result.get_status()

        return self._action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
        





