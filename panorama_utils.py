
# File: panorama_utils.py
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
import ipaddress
import re
import time

import dict2xml
import encryption_helper
import phantom.app as phantom
import requests
import xmltodict
from phantom.action_result import ActionResult

import panorama_consts as consts


class RetVal(tuple):
    """This class returns the tuple of two elements."""

    def __new__(cls, val1, val2=None):
        """Create a new tuple object."""
        return tuple.__new__(RetVal, (val1, val2))


class PanoramaUtils(object):

    def __init__(self, connector=None):
        self._connector = connector
        self._version = None
        self._key = None
        if connector:
            connector.state = self._decrypt_state(connector.state)
            self._key = connector.state.get(consts.PAN_KEY_TOKEN)

    def _get_error_message_from_exception(self, e):
        """Get an appropriate error message from the exception.

        :param e: Exception object
        :return: error message
        """
        error_code = None
        error_msg = consts.PAN_ERROR_MESSAGE_UNAVAILABLE

        self._connector.error_print("Error occurred.", e)
        try:
            if hasattr(e, "args"):
                if len(e.args) > 1:
                    error_code = e.args[0]
                    error_msg = e.args[1]
                elif len(e.args) == 1:
                    error_msg = e.args[0]
        except Exception as e:
            self._connector.error_print(f"Error occurred while fetching exception information. Details: {str(e)}")

        if not error_code:
            error_text = f"Error message: {error_msg}"
        else:
            error_text = f"Error code: {error_code}. Error message: {error_msg}"

        return error_text

    def _load_pan_version(self, action_result):
        """Load the current version of panorama

        Args:
            action_result : Object of ActionResult class

        Returns:
            phantom.APP_ERROR/phantom.APP_SUCCESS: Boolean value of app status
        """

        data = {
            "type": "version",
            "key": self._key
        }

        status, _ = self._make_rest_call(data, action_result)
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_MESSAGE.format(self._connector.get_action_identifier(), action_result.get_message())
            )

        result_data = action_result.get_data()
        if len(result_data) == 0:
            return phantom.APP_ERROR

        result_data = result_data.pop(0)
        # Version should be in this format '7.1.4', where the 1st digit determines the major version.
        self._version = result_data.get('sw-version')

        if not self._version:
            return phantom.APP_ERROR

        return status

    def _validate_string(self, action_result, string_to_validate, param_name, max_len):
        """ Validate given param input string

        Args:
            action_result : Object of ActionResult class
            string_to_validate : string that need to validate
            param_name : parameter name
            max_len : Maximum allowed length of string

        Returns:
            status: phantom.APP_ERROR/phantom.APP_SUCCESS
        """
        regex = "^[A-Za-z0-9][A-Za-z0-9_. -]*$"
        if param_name == "tag":
            regex = r"^[^'\]\[]*$"
        string_len = len(string_to_validate)

        if not (0 < string_len <= max_len):
            return action_result.set_status(
                phantom.APP_ERROR,
                f"Maximum character limit for {param_name} parameter exceeded. Please provide {max_len} or less characters and try again."
            )

        if not re.search(regex, string_to_validate):
            if param_name == "tag":
                message = " ' [ ] are not supported characters for tag names"
            else:
                message = consts.VALIDATE_STRING_ERROR_MSG.format(param_name=param_name)
            return action_result.set_status(
                phantom.APP_ERROR,
                message
            )
        return phantom.APP_SUCCESS

    def _get_config_xpath(self, param, device_entry_name=""):
        """Return the xpath to the specified device group

        device_entry_name should default to 'localhost.localdomain'.
        """

        device_group = param[consts.PAN_JSON_DEVICE_GRP]

        if device_group.lower() == consts.PAN_DEV_GRP_SHARED:
            return "/config/shared"

        formatted_device_entry_name = ""
        if device_entry_name:
            formatted_device_entry_name = "[@name='{}']".format(device_entry_name)

        return consts.DEVICE_GRP_XPATH.format(formatted_device_entry_name=formatted_device_entry_name, device_group=device_group)

    def _make_rest_call(self, data, action_result):
        """ This function is used to make the REST call.

        Args:
            data : dictionary of request body
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message), response obtained by making an API call
        """

        self._connector.debug_print("Making rest call")
        try:
            response = requests.post(
                self._connector.base_url,
                data=data,
                verify=self._connector.config[phantom.APP_JSON_VERIFY],
                timeout=consts.DEFAULT_TIMEOUT
            )
        except Exception as e:
            self._connector.debug_print(consts.PAN_ERROR_DEVICE_CONNECTIVITY, e)
            return (action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_DEVICE_CONNECTIVITY,
                self._get_error_message_from_exception(e)
            ), e)

        xml = response.text

        action_result.add_debug_data(xml)

        try:
            response_dict = xmltodict.parse(xml)
        except Exception as e:
            self._connector.save_progress(consts.PAN_ERROR_UNABLE_TO_PARSE_REPLY)
            return (action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_UNABLE_TO_PARSE_REPLY.format(error=self._get_error_message_from_exception(e))),
            )

        status = self._parse_response(response_dict, action_result)
        if phantom.is_fail(status):
            return action_result.get_status(), response_dict

        return action_result.get_status(), response_dict

    def _add_url_to_url_category(self, param, action_result, url_prof_name):
        """Add the given url to Objects > Custom Objects > URL Category > Phantom URL List for your device group

        The URL category is usually created prior to linking it to a URL filtering.
        """

        block_url = param[consts.PAN_JSON_URL]

        xpath = consts.URL_CATEGORY_XPATH.format(config_xpath=self._get_config_xpath(param), url_profile_name=url_prof_name)
        element = consts.URL_CATEGORY_ELEM.format(url=block_url)

        data = {
            'type': 'config',
            'action': 'set',
            'key': self._key,
            'xpath': xpath,
            'element': element
        }

        status, response = self._make_rest_call(data, action_result)
        action_result.update_summary({'add_url_to_url_category': response})

        return status

    def _generate_token(self, action_result):
        """ This function is used to generate key

        Args:
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """

        # get credentials to generate a key
        username = self._connector.config["username"]
        password = self._connector.config["password"]

        data = {
            "type": "keygen",
            "user": username,
            "password": password
        }

        self._connector.debug_print("Make a rest call to generate key token")
        try:
            response = requests.post(
                self._connector.base_url,
                data=data,
                verify=self._connector.config.get("verify_server_cert", True),
                timeout=consts.DEFAULT_TIMEOUT
            )
        except Exception as e:
            self._connector.debug_print(consts.PAN_ERROR_DEVICE_CONNECTIVITY)
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_DEVICE_CONNECTIVITY,
                self._get_error_message_from_exception(e)
            )
        self._connector.debug_print("Done making a rest call to generate key token")

        xml = response.text

        # parse xml response into dict
        try:
            response_dict = xmltodict.parse(xml)
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_UNABLE_TO_PARSE_REPLY,
                self._get_error_message_from_exception(e)
            )

        response = response_dict.get("response")

        if response is None:
            message = consts.PAN_ERROR_REPLY_FORMAT_KEY_MISSING.format(key=response)
            return action_result.set_status(phantom.APP_ERROR, message)

        status = response.get("@status")

        if status is None:
            message = consts.PAN_ERROR_REPLY_FORMAT_KEY_MISSING.format(key="response/status")
            return action_result.set_status(phantom.APP_ERROR, message)

        if status != "success":
            message = consts.PAN_ERROR_REPLY_NOT_SUCCESS.format(status=status)
            return action_result.set_status(phantom.APP_ERROR, message)

        result = response.get('result')

        if result is None:
            message = consts.PAN_ERROR_REPLY_FORMAT_KEY_MISSING.format(key="response/result")
            return action_result.set_status(phantom.APP_ERROR, message)

        key = result.get('key')

        if key is None:
            message = consts.PAN_ERROR_REPLY_FORMAT_KEY_MISSING.format(key="response/result/key")
            return action_result.set_status(phantom.APP_ERROR, message)

        self._key = key
        self._connector.state[consts.PAN_KEY_TOKEN] = self._key
        self._connector.is_state_updated = True
        return phantom.APP_SUCCESS

    def _add_commit_status(self, job, action_result):
        """Update the given result based on the given Finish job

        :param job: job returned from performing Commit action. The job is already in Finish state
        :param action_result: Object of ActionResult class
        """
        self._connector.debug_print('Update action result with the finished job: %s' % job)

        if job['result'] == 'OK':
            detail = job['details']
            return action_result.set_status(phantom.APP_SUCCESS, detail)

        status_string = ""

        if job['result'] == 'FAIL':
            action_result.set_status(phantom.APP_ERROR)

            try:
                status_string = '{}{}'.format(status_string, '\n'.join(job['details']['line']))
            except Exception as e:
                self._connector.debug_print(
                    "Parsing commit status dict",
                    self._get_error_message_from_exception(e)
                )

            try:
                status_string = '\n'.join(job['warnings']['line'])
            except Exception as e:
                self._connector.debug_print('Failed to retrieve warning message from job. Reason: %s' % e)

        action_result.append_to_message("\n{0}".format(status_string))

        return phantom.APP_SUCCESS

    def _commit_config(self, param, action_result):
        """Commit candidate changes to the firewall by default

        With enabled partial, we commit admin-level changes on a firewall by including the administrator name in the request. # noqa
        Example: https://docs.paloaltonetworks.com/pan-os/8-1/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api/commit.html # noqa
        Commit doc: https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-web-interface-help/panorama-web-interface/panorama-commit-operations.html # noqa
        """
        self._connector.debug_print("START Committing Config changes")

        cmd = '<commit></commit>'

        use_partial_commit = param.get('use_partial_commit', False)
        if use_partial_commit:
            username = self._connector.config[phantom.APP_JSON_USERNAME]
            cmd = '<commit><partial><admin><member>{}</member></admin></partial></commit>'.format(username)

        data = {
            'type': 'commit',
            'cmd': cmd,
            'key': self._key
        }

        if use_partial_commit:
            data.update({'action': 'partial'})

        self._connector.debug_print('Committing with data: %s' % data)
        status, _ = self._make_rest_call(data, action_result)

        if phantom.is_fail(status):
            self._connector.debug_print(
                'Failed to commit Config changes. Reason: %s' % action_result.get_message()
            )
            return action_result.get_status()

        # Get the job id of the commit call from the result_data, also pop it since we don't need it
        # to be in the action result
        result_data = action_result.get_data()

        if len(result_data) == 0:
            self._connector.debug_print('NO result data')
            return action_result.get_status()

        # Monitor the job from the result of commit config above
        result_data = result_data.pop()

        if not isinstance(result_data, dict):
            error_message = "Failed to retrieve job id from %s" % result_data
            self._connector.debug_print(error_message)
            return action_result.set_status(phantom.APP_ERROR, error_message)

        job_id = result_data.get('job')

        if not job_id:
            self._connector.debug_print("Failed to commit Config changes. Reason: NO job id")
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_NO_JOB_ID)

        self._connector.debug_print("Successful committed change with job_id: %s" % job_id)
        self._connector.debug_print("Commit Job id: %s" % job_id)

        # Keep querying Job info until we find a Finished job
        # Update the action result with the finished job
        while True:
            data = {
                'type': 'op',
                'key': self._key,
                'cmd': '<show><jobs><id>{job}</id></jobs></show>'.format(job=job_id)
            }

            status_action_result = ActionResult()

            status, _ = self._make_rest_call(data, status_action_result)

            if phantom.is_fail(status):
                action_result.set_status(phantom.APP_SUCCESS, status_action_result.get_message())
                self._connector.debug_print("Failed to get info for job id: %s" % job_id)
                return action_result.get_status()

            self._connector.debug_print("status", status_action_result)

            result_data = status_action_result.get_data()
            try:
                job = result_data[0]['job']
                job_status = job['status']
                self._connector.debug_print('Job status: %s' % job_status)

                if job_status == 'FIN':
                    self._connector.debug_print('Finished job: %s' % job)
                    self._add_commit_status(job, action_result)
                    action_result.update_summary({'commit_config': {'finished_job': job}})
                    break
            except Exception as e:
                self._connector.debug_print("Failed to find a finished job. Reason: %s" % e)
                error = self._get_error_message_from_exception(e)
                return action_result.set_status(
                    phantom.APP_ERROR,
                    "Error occurred while processing response from server. {}".format(error)
                )

            # send the % progress
            self._connector.send_progress(consts.PAN_PROG_COMMIT_PROGRESS, progress=job.get('progress'))

            time.sleep(2)

        self._connector.debug_print("DONE Committing Config changes")
        return action_result.get_status()

    def _get_all_device_groups(self, param, action_result):
        """ Get all the device groups configured on the system

        Args:
            param : Dictionary of parameters
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message), list of device groups
        """

        self._connector.debug_print('Start retrieving all device groups')

        device_groups = []

        data = {'type': 'config',
                'action': 'get',
                'key': self._key,
                'xpath': "/config/devices/entry/device-group"}

        status, _ = self._make_rest_call(data, action_result)

        if phantom.is_fail(status):
            return (action_result.get_status(), device_groups)

        # Get the data, if the policy existed, we will have some data
        result_data = action_result.get_data()

        if not result_data:
            return (action_result.set_status(phantom.APP_ERROR, "Got empty list for device groups"), device_groups)

        self._connector.debug_print('Getting Device Groups config from %s' % result_data)
        device_groups_config = result_data.pop()

        if not isinstance(device_groups_config, dict):
            error_message = "Invalid Device Group config: %s" % device_groups_config
            self._connector.debug_print(error_message)
            return action_result.set_status(phantom.APP_ERROR, error_message), []

        try:
            device_groups = device_groups_config['device-group']['entry']
        except Exception as e:
            self._connector.debug_print('Failed to extracted device_groups from %s. Reason: %s' % (device_groups_config, e))
            return (action_result.set_status(phantom.APP_ERROR,
                                             "Unable to parse response for the device group listing"), self._get_error_message_from_exception(e))

        try:
            device_groups = [x['@name'] for x in device_groups]
        except:
            device_groups = [device_groups['@name']]

        # remove the data from action_result
        action_result.set_data_size(0)
        action_result.set_status(phantom.APP_ERROR)

        return phantom.APP_SUCCESS, device_groups

    def _get_device_commit_details_string(self, commit_all_device_details):

        if type(commit_all_device_details) == str:
            return commit_all_device_details

        if type(commit_all_device_details) == dict:
            try:
                return "{0}, warnings: {1}".format('\n'.join(commit_all_device_details['msg']['errors']['line']),
                                                   '\n'.join(commit_all_device_details['msg']['warnings']['line']))
            except Exception as e:
                self._connector.debug_print("Parsing commit all device details dict, ",
                                            self._get_error_message_from_exception(e))
                return "UNKNOWN"

    def _parse_device_group_job_response(self, job, action_result):

        status_string = ''
        device_group_status = phantom.APP_ERROR

        if job['result'] == 'OK':
            device_group_status |= phantom.APP_SUCCESS

        devices = []

        try:
            devices = job['devices']['entry']
        except TypeError as e:
            self._connector.debug_print(
                "Parsing commit all message, ",
                self._get_error_message_from_exception(e)
            )
            devices = []
        except Exception as e:
            self._connector.debug_print(
                "Parsing commit all message, ",
                self._get_error_message_from_exception(e)
            )
            devices = []

        if isinstance(devices, dict):
            devices = [devices]

        status_string = '{}<ul>'.format(status_string)
        if not devices:
            status_string = '{}<li>No device status found, possible that no devices configured</li>'.format(status_string)

        for device in devices:
            try:
                if device['result'] != 'FAIL':
                    device_group_status |= phantom.APP_SUCCESS

                device_status = "Device Name: {0}, Result: {1}, Details: {2}".format(device['devicename'], device['result'],
                                                                                     self._get_device_commit_details_string(device['details']))
                status_string = "{0}<li>{1}</li>".format(status_string, device_status)
            except Exception as e:
                self._connector.debug_print("Parsing commit all message for a single device, ",
                                            self._get_error_message_from_exception(e))

        status_string = '{}</ul>'.format(status_string)

        status_string = "Commit status for device group '{0}':\n{1}".format(job['dgname'], status_string)

        return action_result.set_status(device_group_status, status_string)

    def _commit_device_group(self, device_group, action_result):
        """Commit changes for the Device group

        we then query the Commit job until it's finished to update the given action result.
        """
        self._connector.debug_print("Committing Config changes for the device group '{0}'".format(device_group))

        cmd = (
            '<commit-all>'
            '<shared-policy>'
            '<device-group><entry name="{0}"/></device-group>'
            '</shared-policy>'
            '</commit-all>'.format(device_group))

        data = {'type': 'commit',
                'action': 'all',
                'cmd': cmd,
                'key': self._key}

        rest_call_action_result = ActionResult()

        status, _ = self._make_rest_call(data, rest_call_action_result)

        if phantom.is_fail(status):
            return action_result.set_status(rest_call_action_result.get_status(), rest_call_action_result.get_message())

        # Get the job id of the commit call from the result_data, also pop it since we don't need it
        # to be in the action result
        result_data = rest_call_action_result.get_data()

        if len(result_data) == 0:
            return action_result.set_status(rest_call_action_result.get_status(), rest_call_action_result.get_message())

        # We want to process the response from the Commit request we've just done
        # https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api/commit.html#id4e36ab51-cce0-4bd1-8953-2413189ab1c6 # noqa
        result_data = result_data.pop()

        if not isinstance(result_data, dict):
            error_message = "Failed to retrieve job id from %s" % result_data
            self._connector.debug_print(error_message)
            return action_result.set_status(phantom.APP_ERROR, error_message)

        job_id = result_data.get('job')

        if not job_id:
            self._connector.debug_print('Failed to find Job id')
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_NO_JOB_ID)

        self._connector.debug_print("commit job id: ", job_id)

        while True:
            data = {'type': 'op',
                    'key': self._key,
                    'cmd': '<show><jobs><id>{job}</id></jobs></show>'.format(job=job_id)}

            status_action_result = ActionResult()

            status, _ = self._make_rest_call(data, status_action_result)

            if phantom.is_fail(status):
                action_result.set_status(phantom.APP_SUCCESS, status_action_result.get_message())
                return action_result.get_status()

            self._connector.debug_print("status", status_action_result)

            # get the result_data and the job status
            result_data = status_action_result.get_data()
            try:
                job = result_data[0]['job']
                job_status = job['status']
                self._connector.debug_print('Job status: %s' % job_status)

                if job_status == 'FIN':
                    self._connector.debug_print('Finished job: %s' % job)
                    self._parse_device_group_job_response(job, action_result)
                    action_result.update_summary({'commit_device_group': {'finished_job': job}})
                    break
            except Exception as e:
                error = self._get_error_message_from_exception(e)
                return action_result.set_status(phantom.APP_ERROR, "Error occurred while processing response from server. {}".format(error))

            # send the % progress
            self._connector.send_progress(consts.PAN_PROG_COMMIT_PROGRESS, progress=job.get('progress'))

            time.sleep(2)

        self._connector.debug_print("Done committing Config changes for the device group '{0}'".format(device_group))

        return action_result.get_status()

    def _commit_and_commit_all(self, param, action_result):
        """ Commit Config changes and Commit Device Group changes

        Args:
            param : Dictionary of parameters
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """

        self._connector.debug_print('Start Commit actions')

        status = self._commit_config(param, action_result)

        if phantom.is_fail(status):
            return action_result.get_status()

        device_group = param[consts.PAN_JSON_DEVICE_GRP]
        device_groups = [device_group]

        self._connector.debug_print('Device groups to commit: %s' % device_groups)

        if device_group.lower() == consts.PAN_DEV_GRP_SHARED:
            # get all the device groups
            status, device_groups = self._get_all_device_groups(param, action_result)
            if phantom.is_fail(status):
                return action_result.get_status()

        if not device_groups:
            error_message = 'Got empty device group list'
            self._connector.debug_print(error_message)
            return action_result.set_status(phantom.APP_ERROR, error_message)

        # Reset the action_result object to error
        action_result.set_status(phantom.APP_ERROR)

        self._connector.debug_print('Processing device groups: %s' % device_groups)

        dev_groups_ar = []
        for device_group in device_groups:
            dev_grp_ar = ActionResult()
            dev_groups_ar.append(dev_grp_ar)
            self._commit_device_group(device_group, dev_grp_ar)

        status = phantom.APP_ERROR
        status_message = ''

        for dev_group_ar in dev_groups_ar:
            status |= dev_group_ar.get_status()
            status_message = '{}{}'.format(status_message, dev_group_ar.get_message())

        action_result.set_status(status, status_message)
        action_result.update_summary({
            'commit_device_groups': [dev_grp_ar.get_summary()['commit_device_group'] for dev_grp_ar in dev_groups_ar]
        })

        self._connector.debug_print('Done Commit actions')

        return action_result.get_status()

    def _get_security_policy_xpath(self, param, action_result):
        """Return the xpath to the given Security Policy name"""
        try:
            config_xpath = self._get_config_xpath(param)
            rules_xpath = '{config_xpath}/{policy_type}/security/rules'.format(
                config_xpath=config_xpath,
                policy_type=param[consts.PAN_JSON_POLICY_TYPE]
            )
            policy_name = param[consts.PAN_JSON_POLICY_NAME]
            rules_xpath = "{rules_xpath}/entry[@name='{policy_name}']".format(rules_xpath=rules_xpath, policy_name=policy_name)
        except Exception as e:
            return (action_result.set_status(phantom.APP_ERROR, "Unable to create xpath to the security policies",
                                             self._get_error_message_from_exception(e)), None)

        return (phantom.APP_SUCCESS, rules_xpath)

    def _does_policy_exist(self, param, action_result):
        """ Checking the policy is exist or not

        Args:
            param : Dictionary of parameters
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS, true if policy existing else false
        """
        status, rules_xpath = self._get_security_policy_xpath(param, action_result)
        if phantom.is_fail(status):
            return action_result.get_status()

        data = {'type': 'config',
                'action': 'get',
                'key': self._key,
                'xpath': rules_xpath}

        status, response = self._make_rest_call(data, action_result)
        action_result.update_summary({'does_policy_exist': response})

        self._connector.debug_print('Check if policy exists for xpath: %s' % rules_xpath)

        if phantom.is_fail(status):
            self._connector.debug_print('No Policy rule for xpath %s. Reason: %s' % (rules_xpath, action_result.get_message()))
            return action_result.get_status(), None

        # Get the data, if the policy existed, we will have some data
        result_data = action_result.get_data()

        if not result_data:
            return (phantom.APP_SUCCESS, False)

        total_count = 0

        try:
            total_count = int(result_data[0]['@total-count'])
        except Exception as e:
            self._connector.debug_print("_does_policy_exist: ", e)
            return (phantom.APP_SUCCESS, False)

        if not total_count:
            return (phantom.APP_SUCCESS, False)

        return (phantom.APP_SUCCESS, True)

    def _does_address_group_exist(self, param, action_result):
        """ Checking the address is exist or not

        Args:
            param : Dictionary of parameters
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS, true if address group existing else false
        """

        self._connector.debug_print("Checking whether the address group exists or not...")

        add_grp_name = param["name"]

        get_add_grp_xpath = f"{consts.ADDR_GRP_XPATH.format(config_xpath= self._get_config_xpath(param), ip_group_name=add_grp_name)}"

        data = {
            "type": "config",
            'action': "get",
            'key': self._key,
            'xpath': get_add_grp_xpath
        }

        status, _ = self._make_rest_call(data, action_result)
        if phantom.is_fail(status):
            self._connector.debug_print('Error occurred fetching address group. Error - %s' % action_result.get_message())
            return phantom.APP_ERROR

        result_data = action_result.get_data().pop()
        self._connector.debug_print(f"result_data {result_data}")

        if result_data.get("@total-count") == "0":
            self._connector.debug_print("No Address Group found")
            return phantom.APP_ERROR

        try:
            result_data = result_data.get('entry')
        except Exception as e:
            error = self._get_error_message_from_exception(e)
            self._connector.debug_print("Error occurred while processing response from server. {}".format(error))
            return phantom.APP_ERROR

        return phantom.APP_SUCCESS

    def _does_address_exist(self, param, action_result):
        """ Checking the address is exist or not

        Args:
            param : Dictionary of parameters
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS, true if address existing else false
        """

        self._connector.debug_print("Checking the address is exist or not...")

        address_name = param["name"]

        get_address_xpath = f"{consts.ADDRESS_XPATH.format(config_xpath= self._get_config_xpath(param), name=address_name)}"

        data = {
            "type": "config",
            'action': "get",
            'key': self._key,
            'xpath': get_address_xpath
        }

        status, _ = self._make_rest_call(data, action_result)
        if phantom.is_fail(status):
            self._connector.debug_print('Error occur while checking the existence of address. Error - %s' % action_result.get_message())
            return phantom.APP_ERROR

        result_data = action_result.get_data().pop()

        if result_data.get("@total-count") == "0":
            self._connector.debug_print("No Address found")
            return phantom.APP_ERROR

        try:
            result_data = result_data.get('entry')
        except Exception as e:
            error = self._get_error_message_from_exception(e)
            self._connector.debug_print("Error occurred while processing response from server. {}".format(error))
            return phantom.APP_ERROR

        return phantom.APP_SUCCESS

    def _does_tag_exist(self, param, tag, action_result):
        """ Checking the tag is exist or not

        Args:
            param : Dictionary of parameters
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS, true if tag existing else false
        """

        self._connector.debug_print("Checking the tag is exist or not...")

        get_tag_xpath = f"""{consts.GET_TAG_XPATH.format(
            config_xpath=self._get_config_xpath(param),
            name=tag)}"""

        data = {
            "type": "config",
            'action': "get",
            'key': self._key,
            'xpath': get_tag_xpath
        }

        status, _ = self._make_rest_call(data, action_result)
        if phantom.is_fail(status):
            self._connector.debug_print('Error occur while checking the existence of tag. Error - %s' % action_result.get_message())
            return phantom.APP_ERROR

        result_data = action_result.get_data().pop()

        if result_data.get("@total-count") == "0":
            self._connector.debug_print("No Tag found")
            return phantom.APP_ERROR

        try:
            result_data = result_data.get('entry')
        except Exception as e:
            error = self._get_error_message_from_exception(e)
            self._connector.debug_print("Error occurred while processing response from server. {}".format(error))
            return phantom.APP_ERROR
        self._connector.debug_print("out from Checking the tag is exist or not...")

        return phantom.APP_SUCCESS

    def _update_security_policy(self, param, sec_policy_type, action_result, name=None, use_source=False):
        """
        Perform any Policy updates on the xpath to the given Security Policy name
        Different updates are done on the xpath based on the given sec_policy_type.
        """
        self._connector.debug_print('Start _update_security_policy')
        if param['policy_type'] not in consts.POLICY_TYPE_VALUE_LIST:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.VALUE_LIST_VALIDATION_MESSAGE.format(consts.POLICY_TYPE_VALUE_LIST, 'policy_type')
            )

        # Check if policy is present or not
        status, policy_present = self._does_policy_exist(param, action_result)
        action_result.set_data_size(0)
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_MESSAGE.format(self._connector.get_action_identifier(), action_result.get_message())
            )

        if not policy_present:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_POLICY_NOT_PRESENT_CONFIG_DONT_CREATE
            )

        sec_policy_name = param[consts.PAN_JSON_POLICY_NAME]
        self._connector.debug_print("Updating Security Policy", sec_policy_name)

        # Update different policy's elements based on the given flag
        if (sec_policy_type == consts.SEC_POL_IP_TYPE) and (not use_source):
            element = consts.IP_GRP_SEC_POL_ELEM.format(ip_group_name=name)
        elif (sec_policy_type == consts.SEC_POL_IP_TYPE) and (use_source):
            element = consts.IP_GRP_SEC_POL_ELEM_SRC.format(ip_group_name=name)
        elif sec_policy_type == consts.SEC_POL_APP_TYPE:
            element = consts.APP_GRP_SEC_POL_ELEM.format(app_group_name=name)
        elif sec_policy_type == consts.SEC_POL_URL_TYPE:
            # Link the URL filtering with the name to the Profile settings of this policy
            element = consts.URL_PROF_SEC_POL_ELEM.format(url_prof_name=name)
        else:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_CREATE_UNKNOWN_TYPE_SEC_POL
            )

        status, rules_xpath = self._get_security_policy_xpath(param, action_result)

        if phantom.is_fail(status):
            return action_result.get_status()

        data = {
            'type': 'config',
            'action': 'set',
            'key': self._key,
            'xpath': rules_xpath,
            'element': element
        }

        status, response = self._make_rest_call(data, action_result)
        action_result.update_summary({"update_security_policy": response})

        if phantom.is_fail(status):
            return action_result.get_status()

        # If Audit comment is provided, we need to update it prior to committing all changes.
        status = self._update_audit_comment(param, action_result)
        if phantom.is_fail(status):
            return action_result.get_status()

        self._connector.debug_print('Done _update_security_policy')
        return phantom.APP_SUCCESS

    def _parse_response_msg(self, response, action_result, response_message):
        """ Parse and append response message into action result

        Args:
            response : Response dictionary
            action_result : Object of ActionResult class
            response_message : response messages that need to be append response message into action result

        Returns:
            Return response message if available else return None
        """

        msg = response.get("msg")

        if msg is None:
            return

        # parse it as a dictionary
        if isinstance(msg, dict):
            line = msg.get("line")
            if line is None:
                return
            if isinstance(line, list):
                response_message = "{} message: '{}'".format(response_message, ', '.join(line))
                action_result.append_to_message(', '.join(line))
            elif isinstance(line, dict):
                response_message = "{} message: '{}'".format(response_message, line.get('line', ''))
                action_result.append_to_message(line.get('line', ''))
            else:
                response_message = "{} message: '{}'".format(response_message, line)
                action_result.append_to_message(line)
            return

        # parse it as a string
        if type(msg) == str:
            response_message = "{} message: '{}'".format(response_message, msg)
            action_result.append_to_message(msg)

        return response_message

    def _parse_response(self, response_dict, action_result):
        """ Parse the response obtained by making an API call and add in into data

        Args:
            response_dict : response dictionary of REST call
            action_result : Object of ActionResult class

        Returns:
            Status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """

        # multiple keys could be present even if the response is a failure
        response = response_dict.get('response')
        response_message = None

        if response is None:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_REPLY_FORMAT_KEY_MISSING.format(key='response')
            )

        status = response.get('@status')

        if status is None:
            return action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_REPLY_FORMAT_KEY_MISSING.format(key='response/status')
            )

        code = response.get('@code')
        error_msg = consts.PAN_ERR_MSG.get(code) if (code and code not in ["19", "20"]) else consts.PAN_CODE_NOT_PRESENT_MSG

        if status == "success":
            response_message = consts.PAN_SUCCESS_REST_CALL_PASSED
            action_result.set_status(phantom.APP_SUCCESS)
            if code and code not in ["19", "20"]:
                action_result.set_status(
                    phantom.APP_ERROR,
                    consts.PAN_ERROR_REPLY_NOT_SUCCESS.format(status=error_msg)
                )
        else:
            action_result.set_status(
                phantom.APP_ERROR,
                consts.PAN_ERROR_REPLY_NOT_SUCCESS.format(status=error_msg)
            )
        if code is not None:
            response_message = "{} code: '{}'".format(response_message, code)

        response_message = self._parse_response_msg(response, action_result, response_message)
        self._connector.debug_print(response_message)

        result = response.get('result')

        if result is not None:
            self._connector.debug_print('action_result.add_data: response_dict: %s' % response_dict)
            action_result.add_data(result)

        return action_result.get_status()

    def _get_pan_major_version(self):
        # version follows this format '7.1.4'.
        return int(self._version.split('.')[0])

    def encrypt_state(self, state):
        """Encrypt the state file.

        :param state: state dictionary to be encrypted
        :return: state dictionary with encrypted token
        """
        try:
            if state.get(consts.PAN_KEY_TOKEN):
                state[consts.PAN_KEY_TOKEN] = encryption_helper.encrypt(
                    state[consts.PAN_KEY_TOKEN], self._connector.get_asset_id())
        except Exception as e:
            self._connector.debug_print("Error occurred while encrypting the state file.", e)
            state = {"app_version": self._connector.get_app_json().get("app_version")}
        return state

    def _decrypt_state(self, state):
        """Decrypt the state file.

        :param state: state dictionary to be decrypted
        :return: state dictionary with decrypted token
        """
        try:
            if state.get(consts.PAN_KEY_TOKEN):
                state[consts.PAN_KEY_TOKEN] = encryption_helper.decrypt(
                    state[consts.PAN_KEY_TOKEN], self._connector.get_asset_id())
        except Exception as e:
            self._connector.debug_print("Error occurred while decrypting the state file.", e)
            state = {"app_version": self._connector.get_app_json().get("app_version")}
        return state

    def _get_edl_data(self, param, action_result):
        """Getting the data of given eld

        Args:
            param : Parameters
            action_result : Object of ActionResult class

        Returns:
            status: Phantom app status
            response: Dictionary of response
        """

        edl_name = param["name"]
        get_edl_xpath = f"{consts.EDL_XPATH.format(config_xpath=self._get_config_xpath(param))}/entry[@name='{edl_name}']"

        data = {
            "type": "config",
            'action': "get",
            'key': self._key,
            'xpath': get_edl_xpath
        }

        status, _ = self._make_rest_call(data, action_result)

        if phantom.is_fail(status):
            return phantom.APP_ERROR

        return phantom.APP_SUCCESS

    def _update_audit_comment(self, param, action_result):
        """
        Create or Update Audit comment for the Policy rule
        Precondition: The policy name must be provided
        If the given Audit comment is empty, we won't be sending any update.
        Adding an Audit comment does not require Commit after.
        If Commit is called on a rule, the comments on that rule will be cleared.
        Audit comments must be done on the same xpath as the associated Policy rule.
        """
        self._connector.debug_print('Start Create/Update Audit comment with param %s' % param)
        audit_comment = param.get('audit_comment', '')
        if not audit_comment:
            self._connector.debug_print('No Audit comment to update')
            return action_result.get_status()

        if len(audit_comment) > 256:
            error_message = "The length of an Audit comment can be at most 256 characters."
            self._connector.debug_print(error_message)
            return action_result.set_status(phantom.APP_ERROR, error_message)

        self._connector.debug_print('Audit comment to submit %s' % audit_comment)

        # If the device entry name is missing, you won't see the comment on the Web UI.
        # If "Require audit comment on policies" option is enabled, the rule_path must match the one used on commit config update. # noqa
        status, rule_path = self._get_security_policy_xpath(param, action_result)
        if phantom.is_fail(status):
            return action_result.get_status()

        cmd = (
            '<set><audit-comment>'
            '<comment>{audit_comment}</comment>'
            '<xpath>{policy_rule_xpath}</xpath>'
            '</audit-comment></set>'.format(audit_comment=audit_comment, policy_rule_xpath=rule_path))

        self._connector.debug_print('Updating Audit comment with cmd: %s' % cmd)
        data = {
            'type': 'op',
            'key': self._key,
            'cmd': cmd
        }

        status, response = self._make_rest_call(data, action_result)
        action_result.update_summary({'update_audit_comment': response})
        if phantom.is_fail(status):
            self._connector.debug_print('Failed to update audit comment for xpath {} with comment {}. Reason: {}'.format(
                rule_path, audit_comment, action_result.get_message()))
            return action_result.get_status()

        self._connector.debug_print('Successfully Updated Audit comment')

        return action_result.get_status()

# Remove the slash in the ip if present, PAN does not like slash in the names
    def _rem_slash(x):
        return re.sub(r'(.*)/(.*)', r'\1 mask \2', x)

    def _get_addr_name(self, ip):

        name = "{0} {1}".format(self._rem_slash(ip), consts.PHANTOM_ADDRESS_NAME)
        return name

    def _get_action_element(self, param):
        element = ""
        status = False
        for params in param.keys():
            if param[params]:
                if params in consts.SEC_POLICY_WITHOUT_MEMBER:
                    status, result = self._element_prep(params, param[params])
                elif params in consts.SEC_POLICY_WITH_MEMBER:
                    status, result = self._element_prep(params, param[params], member=True)
                if status:
                    element += result
                    status = False
        return element

    def _element_prep(self, param_name, param_val, member=False):

        temp_element = ""
        temp_dict = {}
        status = True
        param_list = []
        try:
            param_list = param_val.split(",")
            param_list = [value.strip() for value in param_list if value.strip()]
            if len(param_list) == 0 and member:
                status = False
                return status, temp_element
        except Exception:
            pass
        if param_name == "target":
            if len(param_list) >= 1:
                entries = ""
                for device in param_list:
                    entries += f'<entry name ="{device}"/>'
                param_val = entries
            temp_element = f'<{param_name}><devices>{param_val}</devices></{param_name}>'
            return status, temp_element
        elif param_name == "profile-setting":
            temp_element = f'<{param_name}><{param_val}/></{param_name}>'
            return status, temp_element
        elif param_name == "dynamic":
            param_val = f"<{param_name}><filter>{param_val}</filter></{param_name}>"
            return status, param_val
        if member:
            if len(param_list) >= 1:
                temp_dict["member"] = param_list
                param_val = dict2xml.dict2xml(temp_dict)
            if param_name == "policy_name":
                return status, param_val

        temp_element = f'<{param_name}>{param_val}</{param_name}>'
        return status, temp_element

    def _validate_ip_as_per_type(self, connector, action_result, ip_type, ip_address):
        """ Figure out the type of IP and checking the validate as per IP type

        Args:
            ip_type : IP type
            ip_address : IP address
            action_result : Object of ActionResult class

        Returns:
            APP_SUCCESS/APP_ERROR: Phantom success/error boolean object
        """
        connector.debug_print(f"Starting checking type of - {ip_address}")
        if ip_type == 'IP Wildcard Mask' and self._validate_ip_wildcard_mask(action_result, ip_address):
            return phantom.APP_SUCCESS
        elif ip_type == 'IP Netmask' and self._is_ip(action_result, ip_address):
            return phantom.APP_SUCCESS
        elif ip_type == 'IP Range' and self._validate_ip_range(action_result, ip_address):
            return phantom.APP_SUCCESS
        elif ip_type == 'FQDN' and self._validate_fqdn(action_result, ip_address):
            return phantom.APP_SUCCESS

        connector.debug_print(f"Ending checking type of - {ip_address}")
        return phantom.APP_ERROR

    def _create_tag(self, connector, action_result, param, tags, comment=consts.TAG_COMMENT, color=None):
        """ Create tag based on provided parameters

        Args:
            connector: phantom connector object
            action_result: Object of ActionResult class
            param (dict): parameters dictionary
            tags (str): Tags that need to create
            comment (str, optional): Comment added in tag. Defaults to consts.TAG_COMMENT.
            color (str, optional): Color provided to tag. Defaults to None.

        Returns:
            APP_SUCCESS/APP_ERROR: Phantom success/error boolean object
            xml_tag_string = XML string regarding tag
        """
        xml_tag_string = None
        if tags:
            xml_tag_string = "<tag>"

            for tag in tags:
                connector.debug_print(f'Creating - {tag} tag...')
                tag_status = self._does_tag_exist(param, tag, action_result)
                if tag_status:
                    connector.debug_print(f'Tag - {tag} already present, Skipping creating tag...')
                    xml_tag_string += f"<member>{tag}</member>"
                    continue

                element_xml = consts.START_TAG.format(tag=tag)
                if color:
                    element_xml += "<color>{color}</color>".format(color=color)
                if comment:
                    element_xml += "<comments>{tag_comment}</comments>".format(tag_comment=comment)
                element_xml += consts.END_TAG

                data = {
                    'type': 'config',
                    'action': 'set',
                    'key': self._key,
                    'xpath': consts.TAG_XPATH.format(config_xpath=self._get_config_xpath(param)),
                    'element': element_xml
                }
                status, response = self._make_rest_call(data, action_result)
                summary = ({'add_tag': response})
                if phantom.is_fail(status):
                    action_result.update_summary({'add_address_entry': summary})
                    return action_result.get_status(), None

                connector.debug_print(f'Done adding {tag} tag...')
                xml_tag_string += f"<member>{tag}</member>"

            xml_tag_string += "</tag>"

        return phantom.APP_SUCCESS, xml_tag_string

    def _is_ip(self, action_result, input_ip_address):
        """
        Function that checks given address and return True if address is valid IPv4 or IPV6 address.

        :param input_ip_address: IP address
        :return: status (success/failure)
        """

        try:
            ipaddress.ip_address(input_ip_address)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, f"Invalid value for IP Netmask type. Error - {e}")
            return phantom.APP_ERROR
        return phantom.APP_SUCCESS

    def _validate_fqdn(self, action_result, dn):
        """ Validating FQDN
        Args:
            dn : Hostname
        Returns:
            :return: status (success/failure)
        """

        if dn.endswith('.'):
            dn = dn[:-1]
        if len(dn) < 1 or len(dn) > 253:
            action_result.set_status(phantom.APP_ERROR, "Invalid value for FQDN type.")
            return phantom.APP_ERROR
        ldh_re = re.compile('^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$',
                            re.IGNORECASE)
        if not all(ldh_re.match(x) for x in dn.split('.')):
            action_result.set_status(phantom.APP_ERROR, "Invalid value for FQDN type.")
            return phantom.APP_ERROR
        return phantom.APP_SUCCESS

    def _validate_ip_range(self, action_result, ip_address):
        """validating IP range

        Args:
            ip_address : IP address
        Returns:
            :return: status (success/failure)
        """

        ips = ip_address.split('-')
        if len(ips) == 2:
            try:
                # Parse the start and end IP addresses
                # If the start IP is less than or equal to the end IP then pass else fail
                if ipaddress.IPv4Address(ips[0]) >= ipaddress.IPv4Address(ips[1]):
                    action_result.set_status(phantom.APP_ERROR, "Invalid value for IP Range type. \
                        Please provide start IP lower than end IP")
                    return phantom.APP_ERROR
            except Exception as e:
                action_result.set_status(phantom.APP_ERROR, f"Invalid value for IP Range type. Error - {e}")
                return phantom.APP_ERROR
            return phantom.APP_SUCCESS
        else:
            action_result.set_status(phantom.APP_ERROR, "Invalid value for IP Range type")
            return phantom.APP_ERROR

    def _validate_ip_wildcard_mask(self, action_result, ip_address):
        """Validate IP wildcard mask

        Args:
            action_result : Object of ActionResult class
            ip_address : IP address

        Returns:
            :return: status (success/failure)
        """
        ip_mask = ip_address.split("/")
        if len(ip_mask) == 2:
            try:
                if not ipaddress.IPv4Address(ip_mask[0]) and ipaddress.IPv4Address(ip_mask[1]):
                    action_result.set_status(phantom.APP_ERROR, "Invalid value for IP Wildcard Mask type")
                    return phantom.APP_ERROR
            except Exception as e:
                action_result.set_status(phantom.APP_ERROR, f"Invalid value for IP Wildcard Mask type. Error - {e}")
                return phantom.APP_ERROR
            return phantom.APP_SUCCESS
        else:
            action_result.set_status(phantom.APP_ERROR, "Invalid value for IP Wildcard Mask type")
            return phantom.APP_ERROR

    def _common_param_check(self, action_result, param):
        """ Validate the common parameters

        Args:
            param : dictionary of parameters

        Returns:
            True/False: action status
        """
        self._connector.debug_print("start validating common parameters...")
        # Validation for device group parameter if present
        if param.get(consts.PAN_JSON_DEVICE_GRP):
            status = self._validate_string(
                action_result, param[consts.PAN_JSON_DEVICE_GRP], " ".join(consts.PAN_JSON_DEVICE_GRP.split("_")), consts.MAX_DEVICE_GRP_NAME_LEN
            )
            if phantom.is_fail(status):
                return action_result.get_status()

        # Validation for name parameter if present
        if param.get(consts.EDL_ADR_POLICY_NAME) or param.get(consts.PAN_JSON_POLICY_NAME):
            if param.get(consts.PAN_JSON_POLICY_NAME):
                policy_names = [value.strip() for value in param.get(consts.PAN_JSON_POLICY_NAME).split(',') if value.strip()]
                for policy_name in policy_names:
                    if not self._validate_string(action_result, policy_name, consts.PAN_JSON_POLICY_NAME, consts.MAX_NAME_LEN):
                        return action_result.get_status()
            elif not self._validate_string(action_result, param[consts.EDL_ADR_POLICY_NAME], consts.EDL_ADR_POLICY_NAME, consts.MAX_NAME_LEN):
                return action_result.get_status()

        # Validation for tag parameter if present
        if param.get(consts.PAN_JSON_TAGS):
            tags = [value.strip() for value in param.get(consts.PAN_JSON_TAGS).split(',') if value.strip()]
            if tags:
                for tag in tags:
                    status = self._validate_string(
                        action_result, tag, consts.PAN_JSON_TAGS, consts.MAX_TAG_NAME_LEN
                    )
                    if phantom.is_fail(status):
                        return action_result.get_status()
        self._connector.debug_print("validated common parameters...")
        return phantom.APP_SUCCESS
