[comment]: # "Auto-generated SOAR connector documentation"
# Panorama

Publisher: Splunk Community  
Connector Version: 5.0.0  
Product Vendor: Palo Alto Networks  
Product Name: Panorama  
Product Version Supported (regex): ".\*"  
Minimum Product Version: 6.0.2  

This app integrates with the Palo Alto Networks Panorama product to support several containment and investigative actions

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2016-2023 Splunk Inc."
[comment]: # ""
[comment]: # "  Licensed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.txt)"
[comment]: # ""
### Overview

The Panorama app has been tested with PanOS version 7.0.4 and should work with any version above.

All the containment actions (like **block ip** etc.), take a policy name and the policy type as
parameters. The action first creates an object (Application Group, Address Group, etc.) on the
Panorama device to represent the object being blocked. This object is then added to the specified
policy. It does not modify any other policy parameters including the **Action** . Therefore you must
pre-configure the policy action as **Drop** .

Most of the actions execute a commit on the panorama device followed by a commit on the device
group. This second commit results in Panorama sending the commit to each device that belongs to a
device group, which could take some time. It is a good idea to add a time interval between two
panorama actions when executing a playbook

Panorama restricts object names to 31 characters. This could result in object names that are created
by Phantom being truncated in some cases.

It is usually a good idea to have one Policy created on the Panorama device to handle the **block**
of each type of object. The panorama_app playbook that is available on the community github repo
assumes this type of configuration. Note that to block URLs on Panorama, they are included in a URL
Filtering profile that is usually added to an **Allow** policy. Please see the PanOS documentation
for more details.

### Commit Configuration

You can use the commit API request to commit a candidate configuration to a firewall. Commit actions
are called at the end of all Contain actions (e.g. BlockIP).

You can learn more about Commit Configuration below: (API)

-   [Commit and
    Commit-All](https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/commit-configuration-api.html)
-   [Panorama Commit Operations - Learn about Partial
    commits](https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-web-interface-help/panorama-web-interface/panorama-commit-operations.html)

### Audit Comment Archive

If the option "Require audit comment on policies" (Panorama -> Management) is enabled, Audit
comments must be specified to a given Policy rule before committing any changes to that rule.

WARNING: Additionally, the length of an Audit comment can be at most 256 characters.

You can learn more about Audit comment below:

-   [Audit Comment
    Archive](https://docs.paloaltonetworks.com/pan-os/10-1/pan-os-web-interface-help/policies/audit-comment-archive.html)
-   [Making changes to Audit comments via
    API](https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-panorama-api/pan-os-xml-api-request-types/run-operational-mode-commands-api.html)


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Panorama asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device** |  required  | string | Device IP/Hostname
**verify_server_cert** |  optional  | boolean | Verify server certificate
**username** |  required  | string | Username
**password** |  required  | password | Password

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity  
[block url](#action-block-url) - Block an URL  
[unblock url](#action-unblock-url) - Unblock an URL  
[block application](#action-block-application) - Block an application  
[unblock application](#action-unblock-application) - Unblock an application  
[block ip](#action-block-ip) - Block an IP  
[unblock ip](#action-unblock-ip) - Unblock an IP  
[list applications](#action-list-applications) - List the applications that the device knows about and can block  
[run query](#action-run-query) - Run a query on Panorama  
[commit changes](#action-commit-changes) - Commit changes to the firewall and device groups  
[get threat pcap](#action-get-threat-pcap) - Export a Threat PCAP file  
[list edl](#action-list-edl) - List External Dynamic List's  

## action: 'test connectivity'
Validate the asset configuration for connectivity

Type: **test**  
Read only: **True**

This action logs into the device using a REST Api call to check the connection and credentials configured.

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'block url'
Block an URL

Type: **contain**  
Read only: **False**

This action does the following to block a URL:<ul><li>Create an URL Filtering profile object named '<b>Phantom URL List for [device_group]</b>' containing the URL to block.</br>If the profile is already present, then it will be updated to include the URL to block. IMPORTANT: For Version 9 and above, a URL Filtering profile no longer includes allow-list/block-list. The official workaround is to use a Custom URL category instead. Therefore, we create a new Custom URL category with the same name as the profile and link it to the profile. Then, We configure the profile to block the URL category on both 'SITE ACCESS' and 'USER CREDENTIAL SUBMISSION' columns.</li><li>If a <b>policy_name</b> is provided, re-configure the policy (specified in the <b>policy_name</b> parameter) to use the created URL Filtering profile. The URL filtering profile created in the previous step will be linked to the Profile Settings of the specified policy.</br>If the policy is not found on the device, the action will return an error.</li><li>If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**url** |  required  | URL to block | string |  `url` 
**device_group** |  required  | Device group to configure, or 'shared' | string | 
**policy_type** |  optional  | Block policy type | string | 
**policy_name** |  optional  | Policy to use | string | 
**use_partial_commit** |  optional  | Whether to perform Partial commit admin-level changes. Config's username is included as the administrator name in the request. Otherwise, plain commit is used by default | boolean | 
**audit_comment** |  optional  | Audit comment to be used with the policy name. Maximum 256 characters | string | 
**should_commit_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.url | string |  `url`  |  
action_result.parameter.device_group | string |  |  
action_result.parameter.policy_type | string |  |  
action_result.parameter.policy_name | string |  |  
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.audit_comment | string |  |  
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.data | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |   command succeeded 
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'unblock url'
Unblock an URL

Type: **correct**  
Read only: **False**

For Version 8 and below, this action will remove the URL from the URL Filtering profile that was created/updated in the <b>block url</b> action. For Version 9 and above, this action will remove the URL from the Custom URL category that was created/updated in the <b>block url</b> action. If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**url** |  required  | URL to unblock | string |  `url` 
**device_group** |  required  | Device group to configure, or 'shared' | string | 
**use_partial_commit** |  optional  | Whether to perform Partial commit admin-level changes. Config's username is included as the administrator name in the request. Otherwise, plain commit is used by default | boolean | 
**should_commit_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.url | string |  `url`  |  
action_result.parameter.device_group | string |  |  
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.data | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |   command succeeded 
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'block application'
Block an application

Type: **contain**  
Read only: **False**

This action does the following to block an application:<ul><li>Create an Application group named '<b>Phantom App List for [device_group]</b>' containing the application to block.</br>If the group is already present, then it will be updated to include the application.</li><li>If a <b>policy_name</b> is provided, re-configure the policy (specified in the <b>policy_name</b> parameter) to use the created application group.</br>If the policy is not found on the device, the action will return an error.</li><li>If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.</li></ul>To get a list of applications that can be blocked, execute the <b>list applications</b> action.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**application** |  required  | Application to block | string |  `network application` 
**device_group** |  required  | Device group to configure, or 'shared' | string | 
**policy_type** |  optional  | Block policy type | string | 
**policy_name** |  optional  | Policy to use | string | 
**use_partial_commit** |  optional  | Whether to perform Partial commit admin-level changes. Config's username is included as the administrator name in the request. Otherwise, plain commit is used by default | boolean | 
**audit_comment** |  optional  | Audit comment to be used with the policy name. Maximum 256 characters | string | 
**should_commit_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.application | string |  `network application`  |  
action_result.parameter.device_group | string |  |  
action_result.parameter.policy_type | string |  |  
action_result.parameter.policy_name | string |  |  
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.audit_comment | string |  |  
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.data | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |   command succeeded 
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'unblock application'
Unblock an application

Type: **correct**  
Read only: **False**

This action will remove the application from the Application group that was created/updated in the <b>block application</b> action. If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.<br>Note: This action will pass for any non-existing application name as API doesn't return an error for an incorrect application name.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**application** |  required  | Application to unblock | string |  `network application` 
**device_group** |  required  | Device group to configure or 'shared' | string | 
**use_partial_commit** |  optional  | Whether to perform Partial commit admin-level changes. Config's username is included as the administrator name in the request. Otherwise, plain commit is used by default | boolean | 
**should_commit_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.application | string |  `network application`  |  
action_result.parameter.device_group | string |  |  
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.data | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |   command succeeded 
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'block ip'
Block an IP

Type: **contain**  
Read only: **False**

<p>This action uses a multistep approach to block an IP. The approach differs whether <b>is_source_address</b> is true or not.  By default, it is false.  The procedure is as follows:</p><ul><li>Create an address entry named '<b>[ip_address] Added By Phantom</b>' with the specified IP address<li>If the option <b>should_add_tag</b> is enabled, the container id of the phantom action is added as a tag to the address entry when it's created<li>If <b>is_source_address</b> is false:<ul><li> add this entry to an address group called <b>Phantom Network List for [device_group]</b></li><li>The address entry and group will be created in the device group specified in the <b>device_group</b> parameter</li><li>If a <b>policy_name</b> is provided, configure the address group as a <i>destination</i> to the policy specified in the <b>policy_name</b> parameter</li></ul>If <b>is_source_address</b> is true:<ul><li>add this entry to an address group called <b>PhantomNtwrkSrcLst[device_group]</b></li><li>The address entry and group will be created in the device group specified in the <b>device_group</b> parameter</li><li>If a <b>policy_name</b> is provided, configure the address group as a <i>source</i> to the policy specified in the <b>policy_name</b> parameter</ul><b>Note:</b> If the policy is not found on the device, the action will return an error.<li>If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.</li></ul><p><b>Please Note:</b> If the Panorama Policy that is used to block a source or destination address has 'Any' in the Source Address or Destination Address field, Block IP will succeed but it will not work.  Therefore, make sure that the policy that the address group will be appended to has no 'Any' in the field that you are blocking from.  i.e, if you are blocking an IP from source, make sure the policy does not have 'Any' under Source Address.</p><p>The address group name is limited to 32 characters.  The device group chosen will be appended to the address group name created.  If the resulting name is too long, the name will be trimmed, which may result in clipped or unusual names.  This is as intended, as it is a limitation by Panorama.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  required  | IP to block | string |  `ip` 
**is_source_address** |  optional  | Source address | boolean | 
**device_group** |  required  | Device group to configure, or 'shared' | string | 
**policy_type** |  optional  | Block policy type | string | 
**policy_name** |  optional  | Policy to use | string | 
**use_partial_commit** |  optional  | Whether to perform Partial commit admin-level changes. Config's username is included as the administrator name in the request. Otherwise, plain commit is used by default | boolean | 
**audit_comment** |  optional  | Audit comment to be used with the policy name. Maximum 256 characters | string | 
**should_add_tag** |  optional  | Whether a new tag should added as part of adding a new IP address | boolean | 
**should_commit_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.ip | string |  `ip`  |  
action_result.parameter.is_source_address | boolean |  |  
action_result.parameter.device_group | string |  |  
action_result.parameter.policy_type | string |  |  
action_result.parameter.policy_name | string |  |  
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.audit_comment | string |  |  
action_result.parameter.should_add_tag | boolean |  |   True  False 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.data | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |   command succeeded 
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'unblock ip'
Unblock an IP

Type: **correct**  
Read only: **False**

This action will remove the address entry from the Address group that was created/updated in the <b>block ip</b> action.  This action behaves differently based upon whether <b>is_source_address</b> is true or false.  By default, it is false.<br>If <b>is_source_address</b> is false:<ul><li>The given IP address will be removed from the <b>Phantom Network List for [device_group]</b> Address Group.</li></ul>If <b>is_source_address</b> is true:<ul><li>The given IP address will be removed from the <b>PhantomNtwrkSrcLst[device_group]</b> Address Group.</li></ul>If <b>should_commit_changes</b> is true, the action then proceeds to <b>commit</b> the changes to Panorama, followed by a commit to the device group. If the device group happens to be <b>shared</b>, then a commit will be sent to all the device groups belonging to it.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** |  required  | IP to unblock | string |  `ip` 
**is_source_address** |  optional  | Source address | boolean | 
**device_group** |  required  | Device group to configure, or 'shared' | string | 
**use_partial_commit** |  optional  | Whether to perform Partial commit admin-level changes. Config's username is included as the administrator name in the request. Otherwise, plain commit is used by default | boolean | 
**should_commit_changes** |  optional  | Whether to commit both changes to firewall and changes to device groups at the end of this action | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.ip | string |  `ip`  |  
action_result.parameter.device_group | string |  |  
action_result.parameter.is_source_address | boolean |  |  
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.parameter.should_commit_changes | boolean |  |   True  False 
action_result.data | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |   command succeeded 
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'list applications'
List the applications that the device knows about and can block

Type: **investigate**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.@name | string |  `network application`  |  
action_result.data.\*.category | string |  |  
action_result.data.\*.has-known-vulnerability | string |  |  
action_result.data.\*.used-by-malware | string |  |  
action_result.data.\*.@ori_country | string |  |  
action_result.data.\*.description | string |  |  
action_result.data.\*.consume-big-bandwidth | string |  |  
action_result.data.\*.able-to-transfer-file | string |  |  
action_result.data.\*.technology | string |  |  
action_result.data.\*.pervasive-use | string |  |  
action_result.data.\*.@ori_lauguage | string |  |  
action_result.data.\*.subcategory | string |  |  
action_result.data.\*.prone-to-misuse | string |  |  
action_result.data.\*.default.port.member | string |  |  
action_result.data.\*.evasive-behavior | string |  |  
action_result.data.\*.references.entry.link | string |  |  
action_result.data.\*.references.entry.@name | string |  |  
action_result.data.\*.tunnel-other-application | string |  |  
action_result.data.\*.@id | string |  |  
action_result.data.\*.risk | string |  |  
action_result.data.\*.application-container | string |  |  
action_result.data.\*.use-applications.member.#text | string |  |  
action_result.data.\*.use-applications.member.@minver | string |  |  
action_result.data.\*.use-applications.@minver | string |  |  
action_result.data.\*.@minver | string |  |  
action_result.data.\*.references.entry.\*.link | string |  |  
action_result.data.\*.references.entry.\*.@name | string |  |  
action_result.data.\*.use-applications.member | string |  |  
action_result.data.\*.file-type-ident | string |  |  
action_result.data.\*.virus-ident | string |  |  
action_result.data.\*.use-applications.member | string |  |  
action_result.data.\*.tunnel-applications.member | string |  |  
action_result.data.\*.data-ident | string |  |  
action_result.data.\*.implicit-use-applications.member | string |  |  
action_result.data.\*.default.port.member | string |  |  
action_result.data.\*.udp-timeout | string |  |  
action_result.data.\*.default.ident-by-ip-protocol | string |  |  
action_result.data.\*.file-forward | string |  |  
action_result.data.\*.use-applications.member.\*.#text | string |  |  
action_result.data.\*.use-applications.member.\*.@minver | string |  |  
action_result.data.\*.tunnel-applications.member.\*.#text | string |  |  
action_result.data.\*.tunnel-applications.member.\*.@minver | string |  |  
action_result.data.\*.tunnel-applications.@minver | string |  |  
action_result.data.\*.ottawa-name | string |  |  
action_result.data.\*.implicit-use-applications.member | string |  |  
action_result.data.\*.decode | string |  |  
action_result.data.\*.breaks-decryption | string |  |  
action_result.data.\*.tunnel-applications.member.#text | string |  |  
action_result.data.\*.tunnel-applications.member.@minver | string |  |  
action_result.data.\*.tunnel-applications.member | string |  |  
action_result.data.\*.related-applications.member | string |  |  
action_result.data.\*.child | string |  |  
action_result.data.\*.timeout | string |  |  
action_result.data.\*.analysis | string |  |  
action_result.data.\*.not-support-ssl | string |  |  
action_result.data.\*.enable-url-filter | string |  |  
action_result.data.\*.decode.#text | string |  |  
action_result.data.\*.decode.@minver | string |  |  
action_result.data.\*.correlate.rules.entry.threshold | string |  |  
action_result.data.\*.correlate.rules.entry.interval | string |  |  
action_result.data.\*.correlate.rules.entry.protocol | string |  |  
action_result.data.\*.correlate.rules.entry.track-by.member | string |  |  
action_result.data.\*.correlate.rule-match | string |  |  
action_result.data.\*.correlate.interval | string |  |  
action_result.data.\*.correlate.key-by.member | string |  |  
action_result.data.\*.tunnel-other-application.#text | string |  |  
action_result.data.\*.tunnel-other-application.@minver | string |  |  
action_result.data.\*.tcp-timeout | string |  |  
action_result.data.\*.ident-by-dport | string |  |  
action_result.data.\*.file-forward | string |  |  
action_result.data.\*.ident-by-sport | string |  |  
action_result.data.\*.preemptive | string |  |  
action_result.data.\*.use-applications.\*.member | string |  |  
action_result.data.\*.netx-vmotion | string |  |  
action_result.data.\*.ha-safe | string |  |  
action_result.data.\*.timeout | string |  |  
action_result.data.\*.doc-review | string |  |  
action_result.data.\*.default.\*.ident-by-ip-protocol | string |  |  
action_result.data.\*.default.\*.port.member | string |  |  
action_result.data.\*.discard-timeout | string |  |  
action_result.data.\*.udp-discard-timeout | string |  |  
action_result.data.\*.default.ident-by-icmp-type | string |  |  
action_result.data.\*.deprecated | string |  |  
action_result.data.\*.alg-disable-capability | string |  |  
action_result.data.\*.risk | string |  |  
action_result.data.\*.tcp-discard-timeout | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |   Total applications: 2421 
action_result.summary.total_applications | numeric |  |   1 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'run query'
Run a query on Panorama

Type: **investigate**  
Read only: **True**

This action runs a query on Panorama and returns the set of logs matching the search criteria.<br><br>Use the <b>range</b> parameter to limit the number of logs returned by the action. If no range is given, the action will use the range <b>1-5000</b>. The action can retrieve up to a maximum of 5000 logs. If more logs need to be retrieved, rerun the action with the next sequential range of values.<br><br>The <b>log_type</b> parameter can be one of the following:<ul><li><b>traffic</b> - traffic logs</li><li><b>url</b> - URL filtering logs</li><li><b>data</b> - data filtering logs</li><li><b>threat</b> - threat logs</li><li><b>config</b> - config logs</li><li><b>system</b> - system logs</li><li><b>hipmatch</b> - HIP match logs</li><li><b>wildfire</b> - wildfire logs</li><li><b>corr</b> - correlated event logs</li><li><b>corr-categ</b> - correlated events by category</li><li><b>corr-detail</b> - correlated event details.</li></ul>

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**log_type** |  required  | Log type to query | string | 
**query** |  required  | Query to run | string | 
**range** |  optional  | Range of result logs to retrieve (e.g 1-5000 or 100-700) | string | 
**direction** |  optional  | Direction to search | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.query | string |  |   ( port.dst eq 161 ) 
action_result.parameter.log_type | string |  |   traffic 
action_result.parameter.direction | string |  |   backward 
action_result.parameter.range | string |  |   1-5000 
action_result.data.\*.job.id | string |  |   1316 
action_result.data.\*.job.tdeq | string |  |   15:46:37 
action_result.data.\*.job.tenq | string |  |   15:46:37 
action_result.data.\*.job.tlast | string |  |   16:00:00 
action_result.data.\*.job.status | string |  |   FIN 
action_result.data.\*.job.cached-logs | string |  |   21 
action_result.data.\*.log.logs.entry.\*.to | string |  |   Internal Zone 
action_result.data.\*.log.logs.entry.\*.app | string |  |   snmp-base 
action_result.data.\*.log.logs.entry.\*.dst | string |  `ip`  |   10.18.3.2 
action_result.data.\*.log.logs.entry.\*.src | string |  `ip`  |   10.10.0.18 
action_result.data.\*.log.logs.entry.\*.from | string |  |   Internal Zone 
action_result.data.\*.log.logs.entry.\*.rule | string |  |   Phantom URL Security Policy 
action_result.data.\*.log.logs.entry.\*.type | string |  |   TRAFFIC 
action_result.data.\*.log.logs.entry.\*.vsys | string |  |   vsys1 
action_result.data.\*.log.logs.entry.\*.bytes | string |  |   79 
action_result.data.\*.log.logs.entry.\*.dport | string |  `port`  |   161 
action_result.data.\*.log.logs.entry.\*.flags | string |  |   0x64 
action_result.data.\*.log.logs.entry.\*.proto | string |  |   udp 
action_result.data.\*.log.logs.entry.\*.seqno | string |  |   1715 
action_result.data.\*.log.logs.entry.\*.sport | string |  `port`  |   64453 
action_result.data.\*.log.logs.entry.\*.start | string |  |   2017/06/23 15:35:21 
action_result.data.\*.log.logs.entry.\*.@logid | string |  |   7592 
action_result.data.\*.log.logs.entry.\*.action | string |  |   allow 
action_result.data.\*.log.logs.entry.\*.domain | string |  `domain`  |   1 
action_result.data.\*.log.logs.entry.\*.dstloc | string |  |   10.0.0.0-10.255.255.255 
action_result.data.\*.log.logs.entry.\*.logset | string |  |   Forward all logs from DG2 
action_result.data.\*.log.logs.entry.\*.serial | string |  |   007200000031753 
action_result.data.\*.log.logs.entry.\*.srcloc | string |  |   10.0.0.0-10.255.255.255 
action_result.data.\*.log.logs.entry.\*.elapsed | string |  |   0 
action_result.data.\*.log.logs.entry.\*.packets | string |  |   1 
action_result.data.\*.log.logs.entry.\*.padding | string |  |   0 
action_result.data.\*.log.logs.entry.\*.pbf-c2s | string |  |   no 
action_result.data.\*.log.logs.entry.\*.pbf-s2c | string |  |   no 
action_result.data.\*.log.logs.entry.\*.subtype | string |  |   end 
action_result.data.\*.log.logs.entry.\*.vsys_id | string |  |   1 
action_result.data.\*.log.logs.entry.\*.category | string |  |   any 
action_result.data.\*.log.logs.entry.\*.cpadding | string |  |   0 
action_result.data.\*.log.logs.entry.\*.flag-nat | string |  |   no 
action_result.data.\*.log.logs.entry.\*.natdport | string |  |   0 
action_result.data.\*.log.logs.entry.\*.natsport | string |  |   0 
action_result.data.\*.log.logs.entry.\*.flag-pcap | string |  |   no 
action_result.data.\*.log.logs.entry.\*.pkts_sent | string |  |   1 
action_result.data.\*.log.logs.entry.\*.repeatcnt | string |  |   1 
action_result.data.\*.log.logs.entry.\*.sessionid | string |  |   58 
action_result.data.\*.log.logs.entry.\*.bytes_sent | string |  |   79 
action_result.data.\*.log.logs.entry.\*.config_ver | string |  |   1 
action_result.data.\*.log.logs.entry.\*.flag-proxy | string |  |   no 
action_result.data.\*.log.logs.entry.\*.inbound_if | string |  |   ethernet1/1 
action_result.data.\*.log.logs.entry.\*.sym-return | string |  |   no 
action_result.data.\*.log.logs.entry.\*.actionflags | string |  |   0x8000000000000000 
action_result.data.\*.log.logs.entry.\*.device_name | string |  |   PA-VM 
action_result.data.\*.log.logs.entry.\*.outbound_if | string |  |   ethernet1/1 
action_result.data.\*.log.logs.entry.\*.transaction | string |  |   no 
action_result.data.\*.log.logs.entry.\*.flag-flagged | string |  |   no 
action_result.data.\*.log.logs.entry.\*.receive_time | string |  |   2017/06/23 15:35:54 
action_result.data.\*.log.logs.entry.\*.action_source | string |  |   from-policy 
action_result.data.\*.log.logs.entry.\*.non-std-dport | string |  |   no 
action_result.data.\*.log.logs.entry.\*.pkts_received | string |  |   0 
action_result.data.\*.log.logs.entry.\*.time_received | string |  |   2017/06/23 15:35:50 
action_result.data.\*.log.logs.entry.\*.bytes_received | string |  |   0 
action_result.data.\*.log.logs.entry.\*.captive-portal | string |  |   no 
action_result.data.\*.log.logs.entry.\*.decrypt-mirror | string |  |   no 
action_result.data.\*.log.logs.entry.\*.time_generated | string |  |   2017/06/23 15:35:50 
action_result.data.\*.log.logs.entry.\*.dg_hier_level_1 | string |  |   17 
action_result.data.\*.log.logs.entry.\*.dg_hier_level_2 | string |  |   0 
action_result.data.\*.log.logs.entry.\*.dg_hier_level_3 | string |  |   0 
action_result.data.\*.log.logs.entry.\*.dg_hier_level_4 | string |  |   0 
action_result.data.\*.log.logs.entry.\*.flag-url-denied | string |  |   no 
action_result.data.\*.log.logs.entry.\*.temporary-match | string |  |   no 
action_result.data.\*.log.logs.entry.\*.session_end_reason | string |  |   aged-out 
action_result.data.\*.log.logs.@count | string |  |   21 
action_result.data.\*.log.logs.@progress | string |  |   1 
action_result.status | string |  |   success  failed 
action_result.message | string |  |   Num logs: 1 
action_result.summary.num_logs | numeric |  |   21 
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'commit changes'
Commit changes to the firewall and device groups

Type: **generic**  
Read only: **False**

The action then proceeds to commit the changes to Panorama, followed by a commit to the device group. If the device group happens to be shared, then a commit will be sent to all the device groups belonging to it.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**device_group** |  required  | Device group to configure, or 'shared' | string | 
**use_partial_commit** |  optional  | Whether to perform Partial commit admin-level changes. Config's username is included as the administrator name in the request. Otherwise, plain commit is used by default | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.device_group | string |  |  
action_result.parameter.use_partial_commit | boolean |  |   True  False 
action_result.data | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |   command succeeded 
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1   

## action: 'get threat pcap'
Export a Threat PCAP file

Type: **generic**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**pcap_id** |  required  | PCAP ID required to fetch Threat PCAP | string |  `panorama pcap id` 
**device_name** |  required  | Device Name required to fetch Threat PCAP | string |  `panorama device name` 
**session_id** |  required  | Session ID required to fetch Threat PCAP | string |  `panorama session id` 
**search_time** |  required  | Search time that the Threat PCAP was received on the firewall (yyyy/mm/dd hr:min:sec) | string |  `timestamp` 
**filename** |  optional  | Filename of exported PCAP file | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.pcap_id | string |  `panorama pcap id`  |  
action_result.parameter.device_name | string |  `panorama device name`  |  
action_result.parameter.session_id | string |  `panorama session id`  |  
action_result.parameter.search_time | string |  `timestamp`  |  
action_result.parameter.filename | string |  |  
action_result.status | string |  |   success  failed 
action_result.message | string |  |  
action_result.data | string |  |  
action_result.summary | numeric |  |  
summary.total_objects | numeric |  |  
summary.total_objects_successful | numeric |  |    

## action: 'list edl'
List External Dynamic List's

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**device_group** |  required  | Device group to configure, or 'shared' | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.device_group | string |  |  
action_result.data.\*.@name | string |  `network application`  |  
action_result.status | string |  |   success  failed 
action_result.data | string |  |  
action_result.message | string |  |   command succeeded 
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1 