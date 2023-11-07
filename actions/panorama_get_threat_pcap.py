# File: panorama_get_threat_pcap.py
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

import os
import shutil
import uuid
from datetime import datetime

import phantom.app as phantom
import phantom.rules as phrules
import requests
from phantom.action_result import ActionResult
from phantom.vault import Vault

import panorama_consts as consts
from actions import BaseAction


class GetThreatPcap(BaseAction):

    def _save_pcap_to_vault(self, connector, filename, response, container_id, action_result):

        # Creating temporary directory and file
        try:
            if hasattr(Vault, 'get_vault_tmp_dir'):
                temp_dir = Vault.get_vault_tmp_dir()
            else:
                temp_dir = "/opt/phantom/vault/tmp/"
            temp_dir = temp_dir + '/{}'.format(uuid.uuid4())
            os.makedirs(temp_dir)
            file_path = os.path.join(temp_dir, filename)

            with open(file_path, 'wb') as file_obj:
                file_obj.write(response)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Error while writing to temporary file", e), None

        # Adding pcap to vault
        connector.save_progress("Adding pcap to vault")
        vault_status, vault_message, vault_id = phrules.vault_add(container_id, file_path, filename)

        # Removing temporary directory created to download file
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, "Unable to remove temporary directory", e), None

        # Updating data with vault details
        if vault_status:
            vault_details = {
                phantom.APP_JSON_VAULT_ID: vault_id,
                'file_name': filename
            }
            return phantom.APP_SUCCESS, vault_details

        # Error while adding report to vault
        connector.debug_print('Error adding file to vault:', vault_message)
        connector.action_result.append_to_message('. {}'.format(vault_message))

        # Set the action_result status to error, the handler function will most probably return as is
        return phantom.APP_ERROR, None

    def _make_rest_download(self, connector, params, action_result, method="get"):

        connector.debug_print("Making rest call")

        try:
            request_method = getattr(requests, method)
        except AttributeError:
            return False, "invalid method: {}".format(method)

        try:
            response = request_method(
                connector.base_url,
                params=params,
                verify=connector.config[phantom.APP_JSON_VERIFY],
                timeout=consts.DEFAULT_TIMEOUT
            )
        except Exception as e:
            connector.debug_print(consts.PAN_ERROR_DEVICE_CONNECTIVITY, e)
            return (
                action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_DEVICE_CONNECTIVITY, connector.util._get_error_message_from_exception(e)
                ),
                e
            )
        if 200 <= response.status_code < 399:
            return True, response.content

        return action_result.set_status(
            phantom.APP_SUCCESS,
            f"Unable to get PCAP - {response.text}"
        )

    def execute(self, connector):

        connector.debug_print("Inside Get Threat PCAP Action")

        action_result = connector.add_action_result(ActionResult(dict(self._param)))

        pcap_id = self._param["pcap_id"]
        device_name = self._param["device_name"]
        session_id = self._param["session_id"]
        search_time = self._param["search_time"]
        try:
            datetime.strptime(search_time, "%Y/%m/%d %H:%M:%S")
        except ValueError as e:
            error = connector.util._get_error_message_from_exception(e)
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("fetching Threat PCAP", error))
        filename = self._param.get("filename", pcap_id)

        data = {
            'type': 'export',
            'key': connector.util._key,
            'category': 'threat-pcap',
            'pcap-id': pcap_id,
            'device_name': device_name,
            'sessionid': session_id,
            'search-time': search_time
        }

        status, response_content = self._make_rest_download(connector, data, action_result)
        # action_result.update_summary({'get_threat_pcap': response})
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, consts.PAN_ERROR_MESSAGE.format("fetching Threat PCAP", action_result.get_message()))

        # Move things around, so that result data is an array of applications
        result_data = response_content

        connector.save_progress("Saving PCAP file in vault")
        ret_val, vault_details = self._save_pcap_to_vault(connector, "{}.pcap".format(
            filename), result_data, connector.get_container_id(), action_result)

        if (phantom.is_fail(ret_val)):
            return action_result.get_status()

        action_result.update_data([vault_details])
        action_result.set_summary({"message": "PCAP file added successfully to the vault"})

        return action_result.set_status(phantom.APP_SUCCESS)
