# File: panorama_block_ip.py
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


class BlockIp(BaseAction):

    def _add_address_entry(self, connector, action_result):
        connector.debug_print('Start adding address entry with param %s' % self._param)

        ip_type = None
        name = None
        tag = connector.get_container_id()
        block_ip = self._param[consts.PAN_JSON_IP]
        should_add_tag = self._param.get('should_add_tag', True)
        connector.debug_print('should_add_tag: %s' % should_add_tag)

        summary = {}

        # Add the tag to the system: Make this optional
        if should_add_tag:
            connector.debug_print('Adding tag...')
            data = {
                'type': 'config',
                'action': 'set',
                'key': connector.util._key,
                'xpath': consts.TAG_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param)),
                'element': consts.TAG_ELEM.format(tag=tag, tag_comment=consts.TAG_CONTAINER_COMMENT, tag_color=consts.TAG_COLOR)
            }

            status, response = connector.util._make_rest_call(data, action_result)
            summary.update({'add_tag': response})
            if phantom.is_fail(status):
                action_result.update_summary({'add_address_entry': summary})
                return action_result.get_status(), name

            connector.debug_print('Done adding tag...')

        # Try to figure out the type of ip
        if block_ip.find('/') != -1:
            ip_type = 'ip-netmask'
        elif block_ip.find('-') != -1:
            ip_type = 'ip-range'
        elif phantom.is_ip(block_ip):
            ip_type = 'ip-netmask'
        elif phantom.is_hostname(block_ip):
            ip_type = 'fqdn'
        else:
            return (action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_INVALID_IP_FORMAT), name)

        name = connector.util._get_addr_name(block_ip)

        address_xpath = consts.IP_ADDR_XPATH.format(
            config_xpath=connector.util._get_config_xpath(self._param),
            ip_addr_name=name
        )
        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': address_xpath,
            'element': "{0}{1}".format(
                consts.IP_ADDR_ELEM.format(ip_type=ip_type, ip=block_ip),
                consts.IP_ADDR_TAG_ELEM.format(tag=tag) if should_add_tag else '')
        }
        connector.debug_print('Updating address entry with data: %s' % data)

        status, response = connector.util._make_rest_call(data, action_result)
        summary.update({'link_tag_to_ip': response})
        if phantom.is_fail(status):
            action_result.update_summary({'add_address_entry': summary})
            return action_result.get_status(), name

        connector.debug_print('Done adding address entry with param')
        action_result.update_summary({'add_address_entry': summary})
        return phantom.APP_SUCCESS, name

    def execute(self, connector):

        connector.debug_print('Start blocking ip')

        # making action result object
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        # Next create the ip
        connector.debug_print("Adding the IP Group")

        # Check where the IP should go
        use_source = self._param.get(consts.PAN_JSON_SOURCE_ADDRESS, consts.PAN_DEFAULT_SOURCE_ADDRESS)

        status, addr_name = self._add_address_entry(connector, action_result)

        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("blocking ip", action_result.get_message())
            )

        if use_source:
            block_ip_grp = consts.BLOCK_IP_GROUP_NAME_SRC.format(device_group=self._param[consts.PAN_JSON_DEVICE_GRP])
        else:
            block_ip_grp = consts.BLOCK_IP_GROUP_NAME.format(device_group=self._param[consts.PAN_JSON_DEVICE_GRP])

        ip_group_name = block_ip_grp
        ip_group_name = ip_group_name[:consts.MAX_NODE_NAME_LEN].strip()

        # Add the address to the phantom address group
        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': consts.ADDR_GRP_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param), ip_group_name=ip_group_name),
            'element': consts.ADDR_GRP_ELEM.format(addr_name=addr_name)
        }

        status, response = connector.util._make_rest_call(data, action_result)
        action_result.update_summary({'add_ip_to_address_group': response})
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("blocking ip", action_result.get_message()))

        message = action_result.get_message()

        if self._param.get('policy_name', ''):
            status = connector.util._update_security_policy(
                self._param, consts.SEC_POL_IP_TYPE, action_result, ip_group_name, use_source=use_source)
            if phantom.is_fail(status):
                return action_result.get_status()

        if self._param.get('should_commit_changes', False):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
