# File: create_address.py
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


class CreateAddress(BaseAction):

    def _generate_xml_string_for_address(self, connector, action_result):
        """Create a tag and add tags into Panorama plateform as per tags. Generate the XML string based on given input parameters.

        Args:
            connector: Connector object
            action_result: Action result object

        Returns:
            xml_string: XML string
        """
        xml_tag_string = None
        address_ip = self._param[consts.PAN_JSON_IP]

        status, ip_type = connector.util._get_ip_type(connector, action_result, address_ip)
        if phantom.is_fail(status):
            return action_result.get_status()

        xml_string = f"<{ip_type}>{address_ip}</{ip_type}>"

        # address tags Add tags into panorama platform
        address_tags = self._param.get("tags", "")
        address_tags = [value.strip() for value in address_tags.split(',') if value.strip()]
        if address_tags:
            tag_status, xml_tag_string = connector.util._create_tag(connector, action_result, self._param, address_tags)
            if phantom.is_fail(tag_status):
                return action_result.get_status()
            if xml_tag_string:
                xml_string += xml_tag_string

        # Address description
        address_description = self._param.get("description", "")
        if address_description:
            xml_string += f"<description>{address_description}</description>"

        # if its not shared group
        device_group = self._param["device_group"]
        if device_group != "shared":
            disable_override = self._param.get("disable_override")
            override = "yes" if disable_override else "no"
            xml_string += f"<disable-override>{override}</disable-override>"

        return phantom.APP_SUCCESS, xml_string

    def execute(self, connector):

        connector.debug_print("starting create address action")
        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        address_name = self._param["name"]

        create_xpath = f"{consts.ADDRESS_XPATH.format(config_xpath=connector.util._get_config_xpath(self._param), name=address_name)}"

        xml_status, element_xml = self._generate_xml_string_for_address(connector=connector, action_result=action_result)

        if phantom.is_fail(xml_status):
            return action_result.get_status()

        data = {
            'type': 'config',
            'action': 'set',
            'key': connector.util._key,
            'xpath': create_xpath,
            'element': element_xml
        }
        status, response = connector.util._make_rest_call(data, action_result)

        action_result.update_summary({'create_address': response})
        if phantom.is_fail(status):
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("create address", action_result.get_message()))

        message = action_result.get_message()

        if self._param.get('should_commit_changes', True):
            status = connector.util._commit_and_commit_all(self._param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        return action_result.set_status(phantom.APP_SUCCESS, "Response Received: {}".format(message))
