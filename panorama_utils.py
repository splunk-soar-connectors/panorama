import requests
import panorama_consts as consts
import xmltodict

import phantom.app as phantom
from phantom.action_result import ActionResult
import encryption_helper
import re
import time

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

    def _get_addr_name(self, ip):

        # Remove the slash in the ip if present, PAN does not like slash in the names
        rem_slash = lambda x: re.sub(r'(.*)/(.*)', r'\1 mask \2', x)
        name = "{0} {1}".format(rem_slash(ip), consts.PHANTOM_ADDRESS_NAME)

        return name
    
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
        
        self._connector.debug_print("Inside load pan version function")
        data = {
            "type": "version", 
            "key": self._key
        }
        
        status, _ = self._make_rest_call(data, action_result)
        if phantom.is_fail(status):
            return action_result.set_status(
                phantom.APP_ERROR, 
                consts.PAN_ERROR_MESSAGE.format("blocking url", action_result.get_message())
            )
        self._connector.debug_print("after make rest call")
        result_data = action_result.get_data()
        if len(result_data) == 0:
            return phantom.APP_ERROR

        result_data = result_data.pop(0)
        # Version should be in this format '7.1.4', where the 1st digit determines the major version.
        self._version = result_data.get('sw-version')
        self._connector.debug_print(f"software version found : {self._version}")

        if not self._version:
            return phantom.APP_ERROR

        return status

    def _get_config_xpath(self, param , device_entry_name = ""):
        """Return the xpath to the specified device group

        device_entry_name should default to 'localhost.localdomain'.
        TODO (Ravenclaw): We've been using blank device_entry_name, which works for our test suite.
        We need to look into using the valid device_entry_name later. This can be done as per customer request.
        Source: https://live.paloaltonetworks.com/t5/automation-api-discussions/xml-api-do-we-need-to-specify-quot-localhost-localdomain-quot-in/m-p/470501#M2965 # noqa
        """

        device_group = param[consts.PAN_JSON_DEVICE_GRP]

        if device_group.lower() == consts.PAN_DEV_GRP_SHARED:
            return "/config/shared"
        
        formatted_device_entry_name = ""
        if device_entry_name:
            formatted_device_entry_name = "[@name='{}']".format(device_entry_name)
        
        return consts.DEVICE_GRP_XPATH.format(
            formatted_device_entry_name = formatted_device_entry_name,
            device_group=device_group
        )

    
    def _make_rest_call(self, data, action_result):

        self._connector.debug_print("Making rest call")

        try:
            response = requests.post(
                self._connector.base_url, 
                data=data, 
                verify= self._connector.config[phantom.APP_JSON_VERIFY], 
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
                consts.PAN_ERROR_UNABLE_TO_PARSE_REPLY,
                self._get_error_message_from_exception(e)),
                xml)

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

        # get credentials to generate a key
        username = self._connector.config["username"]
        password = self._connector.config["password"]

        data = {
            "type" : "keygen",
            "user" : username,
            "password" : password
        }

        self._connector.debug_print("Make a rest call to generate key token")
        try:
            response =  requests.post(
                self._connector.base_url,
                data= data,
                verify= self._connector.config.get("verify_server_cert", True),
                timeout= consts.DEFAULT_TIMEOUT
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
            response_dict =  xmltodict.parse(xml)
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
        self._connector.state[consts.PAN_KEY_TOKEN] =  self._key
        self._connector.is_state_updated = True
        return phantom.APP_SUCCESS


    def _add_commit_status(self, job, action_result):
        """Update the given result based on the given Finish job

        :param job: job returned from performing Commit action. The job is already in Finish state
        :param action_result:
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
                    "Parsing commit status dict, handled exception", 
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
        self._connector.debug_print("Successful committed change with job_id: %s" % job_id)

        if not job_id:
            self._connector.debug_print("Failed to commit Config changes. Reason: NO job id")
            return action_result.set_status(phantom.APP_ERROR, consts.PAN_ERROR_NO_JOB_ID)

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
        """Get all the device groups configured on the system"""

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

        try:
            if type(commit_all_device_details) == str or type(commit_all_device_details) == unicode:
                return commit_all_device_details
        except:
            if type(commit_all_device_details) == str:
                return commit_all_device_details

        if type(commit_all_device_details) == dict:
            try:
                return "{0}, warnings: {1}".format('\n'.join(commit_all_device_details['msg']['errors']['line']),
                        '\n'.join(commit_all_device_details['msg']['warnings']['line']))
            except Exception as e:
                self._connector.debug_print("Parsing commit all device details dict, handled exception", self._get_error_message_from_exception(e))
                return "UNKNOWN"
    
    def _parse_device_group_job_response(self, job, action_result):

        status_string = ''
        device_group_status = phantom.APP_ERROR

        if job['result'] == 'OK':
            device_group_status |= phantom.APP_SUCCESS

        devices = []

        try:
            devices = job['devices']['entry']
        except Exception as e:
            self._connector.debug_print(
                "Parsing commit all message, handled exception", 
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
                self._connector.debug_print("Parsing commit all message for a single device, handled exception", self._get_error_message_from_exception(e))

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
            self.send_progress(consts.PAN_PROG_COMMIT_PROGRESS, progress=job.get('progress'))

            time.sleep(2)

        self._connector.debug_print("Done committing Config changes for the device group '{0}'".format(device_group))

        return action_result.get_status()

    def _commit_and_commit_all(self, param, action_result):
        """Commit Config changes and Commit Device Group changes"""

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
            self._connector.debug_print("_does_policy_exist handled exception: ", e)
            return (phantom.APP_SUCCESS, False)

        if not total_count:
            return (phantom.APP_SUCCESS, False)

        return (phantom.APP_SUCCESS, True)
    
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
                consts.PAN_ERROR_MESSAGE.format("blocking ip", action_result.get_message())
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
        action_result.update_summary({ "update_security_policy": response })

        if phantom.is_fail(status):
            return action_result.get_status()

        # If Audit comment is provided, we need to update it prior to committing all changes.
        status = self._update_audit_comment(param, action_result)
        if phantom.is_fail(status):
            return action_result.get_status()

        self._connector.debug_print('Done _update_security_policy')
        return phantom.APP_SUCCESS
    
    def _parse_response_msg(self, response, action_result, response_message):

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
        try:
            if type(msg) == str or type(msg) == unicode:
                response_message = "{} message: '{}'".format(response_message, msg)
                action_result.append_to_message(msg)
        except:
            if type(msg) == str:
                response_message = "{} message: '{}'".format(response_message, msg)
                action_result.append_to_message(msg)
        return response_message
    
    def _parse_response(self, response_dict, action_result):

        # multiple keys could be present even if the response is a failure
        self._connector.debug_print('response_dict', response_dict)

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

        if status != 'success':
            action_result.set_status(
                phantom.APP_ERROR, 
                consts.PAN_ERROR_REPLY_NOT_SUCCESS.format(status=status)
            )
        else:
            response_message = consts.PAN_SUCCESS_REST_CALL_PASSED
            action_result.set_status(phantom.APP_SUCCESS)

        code = response.get('@code')
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
        
        
        
        
        