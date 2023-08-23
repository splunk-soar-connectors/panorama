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

import panorama_consts as consts
from actions import BaseAction


class ListEdl(BaseAction):

    def execute(self):
        
        data = {
            "type": "config",
            'action': "get",
            'key': self._connector.util._key,
            'xpath': consts.EDL_XPATH.format(config_xpath=self._connector.util._get_config_xpath(self._param))
        }

        status, response  =  self._connector.util._make_rest_call(data, self._action_result)

        if phantom.is_fail(status):
            return self._action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("retrieving list of application", self._action_result.get_message()))

        result_data = self._action_result.get_data()
        result_data = result_data.pop()

        try:
            result_data = result_data['external-list']['entry']
        except Exception as e:
            error = self._connector.util._get_error_message_from_exception(e)
            return self._action_result.set_status(phantom.APP_ERROR, "Error occurred while processing response from server. {}".format(error))

        self._action_result.update_summary({consts.PAN_JSON_TOTAL_EDL: len(result_data)})

        self._action_result.update_data(result_data)

        return self._action_result.set_status(phantom.APP_SUCCESS)