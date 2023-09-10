# File: unblock_ip.py
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
from panorama_consts import (ADDR_GRP_XPATH, BLOCK_IP_GROUP_NAME, BLOCK_IP_GROUP_NAME_SRC, DEL_ADDR_GRP_XPATH, MAX_NODE_NAME_LEN,
                             PAN_DEFAULT_SOURCE_ADDRESS, PAN_ERROR_MESSAGE, PAN_JSON_DEVICE_GRP, PAN_JSON_IP, PAN_JSON_SOURCE_ADDRESS)


class UnblockIp(BaseAction):

    def execute(self, connector):

        connector.debug_print("Removing the Blocked IP")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        # Create the ip addr name
        unblock_ip = self._param[PAN_JSON_IP]

        addr_name = connector.util._get_addr_name(unblock_ip)

        # Check if src or dst
        use_source = self._param.get(PAN_JSON_SOURCE_ADDRESS, PAN_DEFAULT_SOURCE_ADDRESS)

        if use_source:
            block_ip_grp = BLOCK_IP_GROUP_NAME_SRC.format(device_group=self._param[PAN_JSON_DEVICE_GRP])
        else:
            block_ip_grp = BLOCK_IP_GROUP_NAME.format(device_group=self._param[PAN_JSON_DEVICE_GRP])

        ip_group_name = block_ip_grp
        ip_group_name = ip_group_name[:MAX_NODE_NAME_LEN].strip()

        xpath = "{0}{1}".format(
            ADDR_GRP_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param), ip_group_name=ip_group_name),
            DEL_ADDR_GRP_XPATH.format(addr_name=addr_name))

        # Remove the address from the phantom address group
        data = {'type': 'config',
                'action': 'delete',
                'key': connector.util._key,
                'xpath': xpath}

        status, response = connector.util._make_rest_call(data, action_result)
        action_result.update_summary({'delete_ip_from_address_group': response})
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, PAN_ERROR_MESSAGE.format("unblocking ip", action_result.get_message()))

        message = action_result.get_message()

        if self._param.get('should_commit_changes', True):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
