"""
Vectra Detect Integration for Cortex XSOAR

Developer Documentation: https://xsoar.pan.dev/docs/welcome
Code Conventions: https://xsoar.pan.dev/docs/integrations/code-conventions
Linting: https://xsoar.pan.dev/docs/integrations/linting

"""
# Python linting disabled example (disable linting on error code E203)
# noqa: E203

import demistomock as demisto
from CommonServerPython import *
from CommonServerUserPython import *

import dateparser
import json
import requests
import traceback
from typing import Any, Dict, List, Optional

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

''' CONSTANTS '''

DATE_FORMAT: str = '%Y-%m-%dT%H:%M:%S.000Z'
MAX_RESULTS: int = 200
DEFAULT_FIRST_FETCH: str = '7 days'
DEFAULT_FETCH_ENTITY_TYPES: List = ['Hosts']
DEFAULT_MAX_FETCH: int = 50

API_VERSION_URL = '/api/v2.3'

API_ENDPOINT_ACCOUNTS = '/accounts'
API_ENDPOINT_DETECTIONS = '/detections'
API_ENDPOINT_HOSTS = '/hosts'

API_SEARCH_ENDPOINT_ACCOUNTS = '/search/accounts'
API_SEARCH_ENDPOINT_DETECTIONS = '/search/detections'
API_SEARCH_ENDPOINT_HOSTS = '/search/hosts'

API_TAGGING = '/tagging'

UI_ACCOUNTS = '/accounts'
UI_DETECTIONS = '/detections'
UI_HOSTS = '/hosts'

DEFAULT_ORDERING = {
    'accounts': {'ordering': 'last_detection_timestamp'},
    'detections': {'ordering': 'last_timestamp'},
    'hosts': {'ordering': 'last_detection_timestamp'},
}
DEFAULT_STATE = {'state': 'active'}

ENTITY_TYPES = ('Accounts', 'Hosts', 'Detections')


''' GLOBALS '''
global_UI_URL: Optional[str] = None

# DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'  # ISO8601 format with UTC, default in XSOAR

''' CLIENT CLASS '''


class Client(BaseClient):
    """Client class to interact with the service API

    This Client implements API calls, and does not contain any XSOAR logic.
    Should only do requests and return data.
    It inherits from BaseClient defined in CommonServer Python.
    Most calls use _http_request() that handles proxy, SSL verification, etc.
    For this  implementation, no special attributes defined
    """

    def search_detections(self,
                          min_id=None, max_id=None,
                          min_threat=None, max_threat=None,
                          min_certainty=None, max_certainty=None,
                          last_timestamp=None, state: str = None,
                          search_query: str = None, search_query_only: str = None,
                          max_results=None,
                          **kwargs) -> Dict[str, Any]:
        """
        Gets Detections using the 'detections' API endpoint

        :return: dict containing all Detections details
        :rtype: ``Dict[str, Any]``
        """

        # Default params
        demisto.debug("Forcing 'page', 'order_field' and 'page_size' query arguments")
        query_params: Dict[str, Any] = {
            'page': 1,
            'order_field': 'last_timestamp'
        }
        query_params['page_size'] = sanitize_max_results(max_results)

        params: Dict[str, Any] = {}

        if search_query_only:
            # Specific search query used
            query_params['query_string'] = search_query_only
        else:
            # Test min_id / max_id
            validate_min_max('min_id', min_id, 'max_id', max_id)
            if min_id:
                params['min_id'] = min_id
            if max_id:
                params['max_id'] = max_id

            # Test min_threat / max_threat
            validate_min_max('min_threat', min_threat, 'max_threat', max_threat)
            if min_threat:
                params['min_threat'] = min_threat
            if max_threat:
                params['max_threat'] = max_threat

            # Test min_certainty / max_certainty
            validate_min_max('min_certainty', min_certainty, 'max_certainty', max_certainty)
            if min_certainty:
                params['min_certainty'] = min_certainty
            if max_certainty:
                params['max_certainty'] = max_certainty

            # Last timestamp
            if last_timestamp:
                params['last_timestamp'] = last_timestamp

            # State
            if state:
                params['state'] = state
            else:
                params['state'] = DEFAULT_STATE['state']

            # Build search query
            query_params['query_string'] = build_search_query('detection', params)

            # Adding additional search query
            if search_query:
                query_params['query_string'] += f" AND {search_query}"

        demisto.debug(f"Search query : '{query_params['query_string']}'")

        # Execute request
        demisto.debug("Executing API request")
        return self._http_request(
            method='GET',
            params=query_params,
            url_suffix=f'{API_SEARCH_ENDPOINT_DETECTIONS}'
        )

    def search_accounts(self,
                        min_id=None, max_id=None,
                        min_threat=None, max_threat=None,
                        min_certainty=None, max_certainty=None,
                        last_timestamp=None, state: str = None,
                        search_query: str = None, search_query_only: str = None,
                        max_results=None,
                        **kwargs) -> Dict[str, Any]:
        """
        Gets Accounts using the 'Search Accounts' API endpoint

        :return: dict containing all Accounts details
        :rtype: ``Dict[str, Any]``
        """

        # Default params
        demisto.debug("Forcing 'page', 'order_field' and 'page_size' query arguments")
        query_params: Dict[str, Any] = {
            'page': 1,
            'order_field': 'last_detection_timestamp'
        }
        query_params['page_size'] = sanitize_max_results(max_results)

        params: Dict[str, Any] = {}

        if search_query_only:
            # Specific search query used
            query_params['query_string'] = search_query_only
        else:
            # Test min_id / max_id
            validate_min_max('min_id', min_id, 'max_id', max_id)
            if min_id:
                params['min_id'] = min_id
            if max_id:
                params['max_id'] = max_id

            # Test min_threat / max_threat
            validate_min_max('min_threat', min_threat, 'max_threat', max_threat)
            if min_threat:
                params['min_threat'] = min_threat
            if max_threat:
                params['max_threat'] = max_threat

            # Test min_certainty / max_certainty
            validate_min_max('min_certainty', min_certainty, 'max_certainty', max_certainty)
            if min_certainty:
                params['min_certainty'] = min_certainty
            if max_certainty:
                params['max_certainty'] = max_certainty

            # Last timestamp
            if last_timestamp:
                params['last_timestamp'] = last_timestamp

            # State
            if state:
                params['state'] = state
            else:
                params['state'] = DEFAULT_STATE['state']

            # Build search query
            query_params['query_string'] = build_search_query('account', params)

            # Adding additional search query
            if search_query:
                query_params['query_string'] += f" AND {search_query}"

        demisto.debug(f"Search query : '{query_params['query_string']}'")

        # Execute request
        demisto.debug("Executing API request")
        return self._http_request(
            method='GET',
            params=query_params,
            url_suffix=f'{API_SEARCH_ENDPOINT_ACCOUNTS}'
        )

    def search_hosts(self,
                     min_id=None, max_id=None,
                     min_threat=None, max_threat=None,
                     min_certainty=None, max_certainty=None,
                     last_timestamp=None, state: str = None,
                     search_query: str = None, search_query_only: str = None,
                     max_results=None,
                     **kwargs) -> Dict[str, Any]:
        """
        Gets Hosts using the 'hosts' API endpoint

        :return: dict containing all Hosts details
        :rtype: ``Dict[str, Any]``
        """

        # Default params
        demisto.debug("Forcing 'page', 'order_field' and 'page_size' query arguments")
        query_params: Dict[str, Any] = {
            'page': 1,
            'order_field': 'last_detection_timestamp'
        }
        query_params['page_size'] = sanitize_max_results(max_results)

        params: Dict[str, Any] = {}

        if search_query_only:
            # Specific search query used
            query_params['query_string'] = search_query_only
        else:
            # Test min_id / max_id
            validate_min_max('min_id', min_id, 'max_id', max_id)
            if min_id:
                params['min_id'] = min_id
            if max_id:
                params['max_id'] = max_id

            # Test min_threat / max_threat
            validate_min_max('min_threat', min_threat, 'max_threat', max_threat)
            if min_threat:
                params['min_threat'] = min_threat
            if max_threat:
                params['max_threat'] = max_threat

            # Test min_certainty / max_certainty
            validate_min_max('min_certainty', min_certainty, 'max_certainty', max_certainty)
            if min_certainty:
                params['min_certainty'] = min_certainty
            if max_certainty:
                params['max_certainty'] = max_certainty

            # Last timestamp
            if last_timestamp:
                params['last_timestamp'] = last_timestamp

            # State
            if state:
                params['state'] = state
            else:
                params['state'] = DEFAULT_STATE['state']

            # Build search query
            query_params['query_string'] = build_search_query('host', params)

            # Adding additional search query
            if search_query:
                query_params['query_string'] += f" AND {search_query}"

        demisto.debug(f"Search query : '{query_params['query_string']}'")

        # Execute request
        return self._http_request(
            method='GET',
            params=query_params,
            url_suffix=f'{API_SEARCH_ENDPOINT_HOSTS}'
        )

    def get_pcap_by_detection_id(self, id: str):
        """
        Gets a single detection PCAP file using the detection endpoint

        - params:
            - id: The Detection ID
        - returns:
            PCAP file if available
        """

        # Execute request
        return self._http_request(
            method='GET',
            url_suffix=f'{API_ENDPOINT_DETECTIONS}/{id}/pcap',
            resp_type='response'
        )

    def markasfixed_by_detection_id(self, id: str, fixed: bool):
        """
        Mark/Unmark a single detection as fixed

        - params:
            - id: Vectra Detection ID
            - fixed: Targeted state
        - returns:
            Vectra API call result (unused)
        """

        json_payload = {
            'detectionIdList': [id],
            'mark_as_fixed': "true" if fixed else "false"
        }

        # Execute request
        return self._http_request(
            method='PATCH',
            url_suffix=API_ENDPOINT_DETECTIONS,
            json_data=json_payload
        )

    def add_tags(self, id: str, type: str, tags: List[str]):
        """
        Adds tags from Vectra entity

        - params:
            id: The entity ID
            type: The entity type
            tags: Tags list
        - returns
            Vectra API call result (unused)
        """

        # Must be done in two steps
        # 1 - get current tags
        # 2 - merge list and apply

        # Execute get request
        api_response = self._http_request(
            method='GET',
            url_suffix=f'{API_TAGGING}/{type}/{id}'
        )

        current_tags: List[str] = api_response.get('tags', [])

        json_payload = {
            'tags': list(set(current_tags).union(set(tags)))
        }

        # Execute request
        return self._http_request(
            method='PATCH',
            url_suffix=f'{API_TAGGING}/{type}/{id}',
            json_data=json_payload
        )

    def del_tags(self, id: str, type: str, tags: List[str]):
        """
        Deletes tags from Vectra entity

        - params:
            id: The entity ID
            type: The entity type
            tags: Tags list
        - returns
            Vectra API call result (unused)
        """

        # Must be done in two steps
        # 1 - get current tags
        # 2 - merge list and apply

        # Execute get request
        api_response = self._http_request(
            method='GET',
            url_suffix=f'{API_TAGGING}/{type}/{id}'
        )

        current_tags = api_response.get('tags', [])

        json_payload = {
            'tags': list(set(current_tags).difference(set(tags)))
        }

        # Execute request
        return self._http_request(
            method='PATCH',
            url_suffix=f'{API_TAGGING}/{type}/{id}',
            json_data=json_payload
        )


# ####                 #### #
# ##  HELPER FUNCTIONS   ## #
#                           #

def str2bool(value: Optional[str]) -> Optional[bool]:
    """
    Converts a string into a boolean

    - params:
        - value: The string to convert
    - returns:
        True if value matchs the 'true' list
        False if value matchs the 'false' list
        None instead
    """
    if value is None:
        output = None
    elif value.lower() in ('true', 'yes'):
        output = True
    elif value.lower() in ('false', 'no'):
        output = False
    else:
        output = None

    return output


def sanitize_max_results(max_results=None) -> int:
    """
    Cleans max_results value and ensure it's always lower than the MAX

    - params:
        max_results: The max results number
    - returns:
        The checked/enforced max results value
    """
    if max_results and isinstance(max_results, str):
        max_results = int(max_results)

    if (not max_results) or (max_results > MAX_RESULTS) or (max_results <= 0):
        return MAX_RESULTS
    else:
        return max_results


def scores_to_severity(threat: Optional[int], certainty: Optional[int]) -> str:
    """
    Converts Vectra scores to a severity String

    - params:
        - threat: The Vectra threat score
        - certainty: The Vectra certainty score
    - returns:
        The severity as text
    """
    severity = 'Unknown'
    if isinstance(threat, int) and isinstance(certainty, int):
        if threat < 50 and certainty < 50:
            severity = 'Low'
        elif threat < 50:  # and certainty >= 50
            severity = 'Medium'
        elif certainty < 50:  # and threat >= 50
            severity = 'High'
        else:  # threat >= 50 and certainty >= 50
            severity = 'Critical'

    return unify_severity(severity)


def severity_string_to_int(severity: Optional[str]) -> int:
    """
    Converts a severity String to XSOAR severity value

    - params:
        - severity: The severity as text
    - returns:
        The XSOAR severity value
    """
    output = 0
    if severity == 'Critical':
        output = 4
    elif severity == 'High':
        output = 3
    elif severity == 'Medium':
        output = 2
    elif severity == 'Low':
        output = 1

    return output


def convert_date(date: Optional[str]) -> Optional[str]:
    """
    Converts a date format to an ISO8601 string

    Converts the Vectra date (YYYY-mm-ddTHH:MM:SSZ) format in a datetime.

    :type date: ``str``
    :param date: a string with the format 'YYYY-mm-DDTHH:MM:SSZ'

    :return: Parsed time in ISO8601 format
    :rtype: ``str``
    """
    if date:
        date_dt = dateparser.parse(str(date))
        if date_dt:
            return date_dt.strftime(DATE_FORMAT)
        else:
            return None
    else:
        return None


def validate_argument(label: Optional[str], value: Any) -> int:
    """
    Validates a command argument based on its type

    - params:
        - label: The argument label
        - value: The argument value
    - returns:
        The value if OK or raises an Exception if not
    """

    demisto.debug(f"Testing '{label}' argument value")
    if label in ['min_id', 'max_id']:
        try:
            if (value is None) or isinstance(value, float):
                raise ValueError('Cannot be empty or a float')
            if value and isinstance(value, str):
                value = int(value)
            if not isinstance(value, int):
                raise ValueError('Should be an int')
            if int(value) <= 0:
                raise ValueError('Should be > 0')
        except ValueError:
            raise ValueError(f'"{label}" must be an integer greater than 0')
    elif label in ['min_threat', 'min_certainty', 'max_threat', 'max_certainty']:
        try:
            if (value is None) or isinstance(value, float):
                raise ValueError('Cannot be empty or a float')
            if value and isinstance(value, str):
                value = int(value)
            if not isinstance(value, int):
                raise ValueError('Should be an int')
            if int(value) < 0:
                raise ValueError('Should be >= 0')
            if int(value) > 99:
                raise ValueError('Should be < 100')
        except ValueError:
            raise ValueError(f'"{label}" must be an integer between 0 and 99')
    elif label in ['min_privilege_level']:
        try:
            if (value is None) or isinstance(value, float):
                raise ValueError('Cannot be empty or a float')
            if value and isinstance(value, str):
                value = int(value)
            if not isinstance(value, int):
                raise ValueError('Should be an int')
            if int(value) < 1:
                raise ValueError('Should be >= 1')
            if int(value) > 10:
                raise ValueError('Should be <= 10')
        except ValueError:
            raise ValueError(f'"{label}" must be an integer between 1 and 10')
    else:
        raise SystemError('Unknow argument type')
    return value


def validate_min_max(min_label: str = None, min_value: str = None, max_label: str = None, max_value: str = None):
    """
    Validates min/max values for a specific search attribute and ensure max_value >= min_value

    - params:
        - min_label: The attribute label for the min value
        - min_value: The min value
        - max_label: The attribute label for the max value
        - max_value: The max value
    - returns:
        Return True if OK or raises Exception if not
    """
    if min_value:
        validate_argument(min_label, min_value)

    if max_value:
        validate_argument(max_label, max_value)

    if min_value and max_value:
        if int(min_value) > int(max_value):
            raise ValueError(f'"{max_label}" must be greater than or equal to "{min_label}"')

    return True


def build_search_query(object_type, params: dict) -> str:
    """
    Builds a Lucene syntax search query depending on the object type to search on (Account, Detection, Host)

    - params:
        - object_type: The object type we're searching (Account, Detection, Host)
        - params: The search params
    - returns:
        The Lucene search query
    """
    query = ''

    for key, value in params.items():
        if key.startswith('min_'):
            operator = ':>='
        elif key.startswith('max_'):
            operator = ':<='

        if key.endswith('_id'):
            attribute = 'id'
        elif key.endswith('_threat'):
            attribute = 'threat'
        elif key.endswith('_certainty'):
            attribute = 'certainty'

        if key in ['state']:
            attribute = key
            operator = ':'
            value = f'"{value}"'

        if key == 'last_timestamp':
            operator = ':>='
            if object_type == 'detection':
                attribute = 'last_timestamp'
            else:
                attribute = 'last_detection_timestamp'

        # Append query
        # No need to add "AND" as implied
        query += f' {object_type}.{attribute}{operator}{value}'

    return query.strip()


def forge_entity_url(type: str, id: Optional[str]) -> str:
    """
    Generate the UI pivot URL

    - params:
        - type: The object type ("account", "detection" or "host")
        - id: The object ID
    - returns:
        The pivot URL using server FQDN
    """
    if type == 'account':
        url_suffix = f'{UI_ACCOUNTS}/'
    elif type == 'detection':
        url_suffix = f'{UI_DETECTIONS}/'
    elif type == 'host':
        url_suffix = f'{UI_HOSTS}/'
    else:
        raise Exception(f"Unknown type : {type}")

    if not id:
        raise Exception("Missing ID")

    return urljoin(urljoin(global_UI_URL, url_suffix), str(id))


def common_extract_data(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts common information from Vectra object renaming attributes on the fly.

    - params:
        - host: The Vectra object
    - returns:
        The extracted data
    """
    return {
        'Assignee'               : entity.get('assigned_to'),                              # noqa: E203
        'AssignedDate'           : convert_date(entity.get('assigned_date')),              # noqa: E203
        'CertaintyScore'         : entity.get('certainty'),                                # noqa: E203
        'ID'                     : entity.get('id'),                                       # noqa: E203
        'State'                  : entity.get('state'),                                    # noqa: E203
        'Tags'                   : entity.get('tags'),                                     # noqa: E203
        'ThreatScore'            : entity.get('threat'),                                   # noqa: E203
    }


def extract_account_data(account: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts useful information from Vectra Account object renaming attributes on the fly.

    - params:
        - host: The Vectra Account object
    - returns:
        The Account extracted data
    """
    return common_extract_data(account) | {
        'LastDetectionTimestamp' : convert_date(account.get('last_detection_timestamp')),  # noqa: E203
        'PrivilegeLevel'         : account.get('privilege_level'),                         # noqa: E203
        'PrivilegeCategory'      : account.get('privilege_category'),                      # noqa: E203
        'Severity'               : unify_severity(account.get('severity')),                # noqa: E203
        'Type'                   : account.get('account_type'),                            # noqa: E203
        'URL'                    : forge_entity_url('account', account.get('id')),         # noqa: E203
        'Username'               : account.get('name'),                                    # noqa: E203
    }


def extract_detection_data(detection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts useful information from Vectra Detection object renaming attributes on the fly.

    - params:
        - host: The Vectra Detection object
    - returns:
        The Detection extracted data
    """
    # Complex values
    detection_name = detection.get('custom_detection') if detection.get('custom_detection') else detection.get('detection')

    source_account = detection.get('src_account')
    source_account_id = source_account.get('id') if source_account else None

    source_host = detection.get('src_host')
    source_host_id = source_host.get('id') if source_host else None

    summary = detection.get('summary')
    if summary:
        description = summary.get('description')
        dst_ips = summary.get('dst_ips')
        dst_ports = summary.get('dst_ports')
    else:
        description = dst_ips = dst_ports = None

    return common_extract_data(detection) | remove_empty_elements({
        'Category'            : detection.get('category'),                                                # noqa: E203
        'Description'         : description,                                                              # noqa: E203
        'DestinationIPs'      : dst_ips,                                                                  # noqa: E203
        'DestinationPorts'    : dst_ports,                                                                # noqa: E203
        'FirstTimestamp'      : convert_date(detection.get('first_timestamp')),                           # noqa: E203
        'IsTargetingKeyAsset' : detection.get('is_targeting_key_asset'),                                  # noqa: E203
        'LastTimestamp'       : convert_date(detection.get('last_timestamp')),                            # noqa: E203
        'Name'                : detection_name,                                                           # noqa: E203
        'Severity'            : scores_to_severity(detection.get('threat'), detection.get('certainty')),  # noqa: E203
        'SensorLUID'          : detection.get('sensor'),                                                  # noqa: E203
        'SensorName'          : detection.get('sensor_name'),                                             # noqa: E203
        'SourceAccountID'     : source_account_id,                                                        # noqa: E203
        'SourceHostID'        : source_host_id,                                                           # noqa: E203
        'SourceIP'            : detection.get('src_ip'),                                                  # noqa: E203
        'TriageRuleID'        : detection.get('triage_rule_id'),                               # noqa: E203
        'Type'                : detection.get('detection'),                                               # noqa: E203
        'URL'                 : forge_entity_url('detection', detection.get('id')),                       # noqa: E203
    })


def extract_host_data(host: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts useful information from Vectra Host object renaming attributes on the fly.

    - params:
        - host: The Vectra Hosts object
    - returns:
        The Host extracted data
    """
    return common_extract_data(host) | {
        'HasActiveTraffic'       : host.get('has_active_traffic'),                      # noqa: E203
        'Hostname'               : host.get('name'),                                    # noqa: E203
        'IPAddress'              : host.get('ip'),                                      # noqa: E203
        'IsKeyAsset'             : host.get('is_key_asset'),                            # noqa: E203
        'IsTargetingKeyAsset'    : host.get('is_targeting_key_asset'),                  # noqa: E203
        'LastDetectionTimestamp' : convert_date(host.get('last_detection_timestamp')),  # noqa: E203
        'PrivilegeLevel'         : host.get('privilege_level'),                         # noqa: E203
        'PrivilegeCategory'      : host.get('privilege_category'),                      # noqa: E203
        'ProbableOwner'          : host.get('probable_owner'),                          # noqa: E203
        'SensorLUID'             : host.get('sensor'),                                  # noqa: E203
        'SensorName'             : host.get('sensor_name'),                             # noqa: E203
        'Severity'               : unify_severity(host.get('severity')),                # noqa: E203
        'URL'                    : forge_entity_url('host', host.get('id')),            # noqa: E203
    }


def detection_to_incident(detection: Dict):
    """
    Creates an incident of a Detection.

    :type detection: ``dict``
    :param detection: Single detection object

    :return: Incident representation of a Detection
    :rtype ``dict``
    """

    extracted_data = extract_detection_data(detection)

    incident_name = f"Vectra Detection ID: {extracted_data.get('ID')} - {extracted_data.get('Name')}"

    vectra_specific = {
        'entity_type': extracted_data.get('Category'),
        'UI_URL': extracted_data.get('URL'),
    }
    detection.update({'_vectra_specific': vectra_specific})

    incident = {
        'name': incident_name,                            # name is required field, must be set
        'occurred': extracted_data.get('LastTimestamp'),  # must be string of a format ISO8601
        'rawJSON': json.dumps(detection),                 # the original event,
                                                          #   this will allow mapping of the event in the mapping stage.
                                                          #   Don't forget to `json.dumps`
        'severity': severity_string_to_int(extracted_data.get('Severity')),
        # 'dbotMirrorId': extracted_data.get('ID')
    }

    incident_last_run = {
        'last_timestamp': dateparser.parse(extracted_data.get('LastTimestamp'), settings={'TO_TIMEZONE': 'UTC'}).isoformat(),
        'id': extracted_data.get('ID')
    }

    return incident, incident_last_run


def host_to_incident(host: Dict):
    """
    Creates an incident of a Host.

    :type host: ``dict``
    :param host: Single Host object

    :return: Incident representation of a Host
    :rtype ``dict``
    """

    extracted_data = extract_host_data(host)

    incident_name = f"Vectra Host ID: {extracted_data.get('ID')} - {extracted_data.get('Hostname')}"

    vectra_specific = {
        'entity_type': 'host',
        'UI_URL': extracted_data.get('URL'),
    }
    host.update({'_vectra_specific': vectra_specific})

    incident = {
        'name': incident_name,                                     # name is required field, must be set
        'occurred': extracted_data.get('LastDetectionTimestamp'),  # must be string of a format ISO8601
        'rawJSON': json.dumps(host),                               # the original event,
                                                                   #   this will allow mapping of the event in the mapping stage.
                                                                   #   Don't forget to `json.dumps`
        'severity': severity_string_to_int(extracted_data.get('Severity')),
        # 'dbotMirrorId': extracted_data.get('ID')
    }

    incident_last_run = {
        'last_timestamp': dateparser.parse(extracted_data.get('LastDetectionTimestamp'),
                                           settings={'TO_TIMEZONE': 'UTC'}).isoformat(),
        'id': extracted_data.get('ID')
    }

    return incident, incident_last_run


def account_to_incident(account: Dict):
    """
    Creates an incident of an Account.

    :type host: ``dict``
    :param host: Single Account object

    :return: Incident representation of a Account
    :rtype ``dict``
    """

    extracted_data = extract_account_data(account)

    incident_name = f"Vectra Account ID: {extracted_data.get('ID')} - {extracted_data.get('Username')}"

    vectra_specific = {
        'entity_type': 'account',
        'UI_URL': extracted_data.get('URL'),
    }
    account.update({'_vectra_specific': vectra_specific})

    incident = {
        'name': incident_name,                                     # name is required field, must be set
        'occurred': extracted_data.get('LastDetectionTimestamp'),  # must be string of a format ISO8601
        'rawJSON': json.dumps(account),                            # the original event,
                                                                   #   this will allow mapping of the event in the mapping stage.
                                                                   #   Don't forget to `json.dumps`
        'severity': severity_string_to_int(extracted_data.get('Severity')),
        # 'dbotMirrorId': extracted_data.get('ID')
    }

    incident_last_run = {
        'last_timestamp': dateparser.parse(extracted_data.get('LastDetectionTimestamp'),
                                           settings={'TO_TIMEZONE': 'UTC'}).isoformat(),
        'id': extracted_data.get('ID')
    }

    return incident, incident_last_run


def get_last_run_details(integration_params: Dict):
    # Get the config settings
    fetch_first_time = integration_params.get('first_fetch')
    fetch_entity_types = integration_params.get('fetch_entity_types', {})

    # Get the last run value
    last_run = demisto.getLastRun()
    demisto.debug(f"last run : {last_run}")

    output_last_run = dict()
    for entity_type in ENTITY_TYPES:
        if entity_type in fetch_entity_types:
            if not last_run.get(entity_type):
                demisto.debug(f"Last run is not set for '{entity_type}'. Using value from config : {fetch_first_time}")
                # This will return a relative TZaware datetime (in UTC)
                last_timestamp = dateparser.parse(fetch_first_time, settings={'TO_TIMEZONE': 'UTC'}).isoformat()
                last_id = 0
                output_last_run[entity_type] = {
                    'last_timestamp': last_timestamp,
                    'id': last_id
                }
                demisto.debug(f"New last run for {entity_type}, {output_last_run[entity_type]}")
            else:
                # This will return a relative TZaware datetime (in UTC)
                output_last_run[entity_type] = last_run.get(entity_type)

        elif last_run.get(entity_type):
            demisto.debug(f"'{entity_type} present in last run but no more used, discarding.")

    return output_last_run


def iso_date_to_vectra_start_time(iso_date: str):
    """
    Converts an iso date into a Vectra timestamp used in search query

    - params:
        - iso_date: The ISO date to convert
    - returns:
        A Vectra date timestamp
    """
    # This will return a relative TZaware datetime (in UTC)
    date = dateparser.parse(iso_date, settings={'TO_TIMEZONE': 'UTC'})

    if date:
        # We should return time in YYYY-MM-DDTHHMM format for Vectra Lucene query search ...
        start_time = date.strftime('%Y-%m-%dT%H%M')
        demisto.debug(f'Start time is : {start_time}')
    else:
        raise SystemError('Invalid ISO date')

    return start_time


def unify_severity(severity: Optional[str]) -> str:
    """
    Force severity string to be consistent across endpoints

    - params:
        - severity: The severity string
    - returns:
        The unified severity string (First capitalized letter)
    """
    if severity:
        output = severity.capitalize()
    else:
        output = 'Unknown'

    return output


class VectraException(Exception):
    """
    Custome Vectra Exception in case of Vectra API issue
    """

# ####               #### #
# ## COMMAND FUNCTIONS ## #
#                         #


def test_module(client: Client, integration_params: Dict) -> str:
    """
    Tests API connectivity and authentication.

    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    - params:
        - client: The API Client
        - integration_params: All additional integration settings
    - returns:
        'ok' if test passed, anything else if at least one test failed.
    """
    try:
        last_timestamp = None

        if integration_params.get('isFetch'):
            demisto.debug('Fetching mode is enabled. Testing settings ...')

            demisto.debug('Testing Fetch first timestamp ...')
            fetch_first_time = integration_params.get('first_fetch', DEFAULT_FIRST_FETCH)
            demisto.debug(f'Fetch first timestamp : {fetch_first_time}')
            try:
                last_timestamp = iso_date_to_vectra_start_time(fetch_first_time)
            except SystemError:
                raise ValueError('Fetch first timestamp is invalid.')
            demisto.debug('Testing Fetch first timestamp [done]')

            demisto.debug('Testing Fetch entity types ...')
            fetch_entity_types = integration_params.get('fetch_entity_types', DEFAULT_FETCH_ENTITY_TYPES)
            demisto.debug(f'Fetch entity types : {fetch_entity_types}')
            if len(fetch_entity_types) == 0:
                raise ValueError('You must select at least one entity type to fetch.')
            for entity_itt in fetch_entity_types:
                if entity_itt not in ENTITY_TYPES:
                    raise ValueError(f'This entity type "{entity_itt}" is invalid.')
            demisto.debug('Testing Fetch entity types [done]')

            accounts_fetch_query = integration_params.get('accounts_fetch_query')
            demisto.debug(f"'Accounts' fetch query : {accounts_fetch_query}")

            hosts_fetch_query = integration_params.get('hosts_fetch_query')
            demisto.debug(f"'Hosts' fetch query : {hosts_fetch_query}")

            detections_fetch_query = integration_params.get('detections_fetch_query')
            demisto.debug(f"'Detections' fetch query : {detections_fetch_query}")

            demisto.debug('Testing Max incidents per fetch ...')
            max_incidents_per_fetch = integration_params.get('max_fetch', DEFAULT_MAX_FETCH)
            demisto.debug(f'Max incidents per fetch (initial value): {max_incidents_per_fetch}')
            if isinstance(max_incidents_per_fetch, str):
                try:
                    max_incidents_per_fetch = int(max_incidents_per_fetch)
                except ValueError:
                    raise ValueError('Max incidents per fetch must be a positive integer.')
            if max_incidents_per_fetch == 0:
                raise ValueError('Max incidents per fetch must be a positive integer.')

            max_incidents_per_fetch = sanitize_max_results(max_incidents_per_fetch)
            if (max_incidents_per_fetch // len(fetch_entity_types)) == 0:
                raise ValueError(f"Max incidents per fetch ({max_incidents_per_fetch}) must be >= "
                                 f"to the number of entity types you're fetching ({len(fetch_entity_types)})")

            demisto.debug(f'Max incidents per fetch (final value): {max_incidents_per_fetch}')
            demisto.debug('Testing Max incidents per fetch [done]')

        # Client class should raise the exceptions, but if the test fails
        # the exception text is printed to the Cortex XSOAR UI.
        client.search_detections(max_results=1, last_timestamp=last_timestamp)
        message = 'ok'

    except ValueError as e:
        message = str(e)
        demisto.debug(message)
    except DemistoException as e:
        if 'Invalid token' in str(e):
            message = 'Authorization Error: make sure API Token is properly set'
            demisto.debug(message)
        elif 'Verify that the server URL parameter is correct' in str(e):
            message = 'Verify that the Vectra Server FQDN or IP is correct and that you have access to the server from your host'
            demisto.debug(message)
        else:
            raise e

    return message


def fetch_incidents(client: Client, integration_params: Dict):

    fetch_entity_types = integration_params.get('fetch_entity_types', {})
    api_response: Dict = dict()

    # Get the last run and the last fetched value
    previous_last_run = get_last_run_details(integration_params)

    incidents = []
    new_last_run: Dict = {}

    # We split the number of incidents to create into the number of remaining endpoints to call
    remaining_fetch_types: Set = fetch_entity_types
    max_created_incidents: int = sanitize_max_results(integration_params.get('max_fetch')) // len(remaining_fetch_types)

    for entity_type in ENTITY_TYPES:
        entity_incidents: List = []
        if entity_type not in fetch_entity_types:
            pass
        else:
            last_fetched_timestamp = previous_last_run[entity_type]['last_timestamp']
            last_fetched_id = previous_last_run[entity_type]['id']

            demisto.debug(f"{entity_type} - Last fetched incident"
                          f"last_timestamp : {last_fetched_timestamp} / ID : {last_fetched_id}")

            start_time = iso_date_to_vectra_start_time(last_fetched_timestamp)

            if entity_type == 'Accounts':
                api_response = client.search_accounts(
                    last_timestamp=start_time,
                    search_query=integration_params.get('accounts_fetch_query')
                )
            elif entity_type == 'Hosts':
                api_response = client.search_hosts(
                    last_timestamp=start_time,
                    search_query=integration_params.get('hosts_fetch_query')
                )
            elif entity_type == 'Detections':
                api_response = client.search_detections(
                    last_timestamp=start_time,
                    search_query=integration_params.get('detections_fetch_query')
                )

            if (api_response is None) or (api_response.get('count') is None):
                raise VectraException("API issue")

            if api_response.get('count') == 0:
                demisto.info(f"{entity_type} - No results")
            elif api_response.get('count', 0) > 0:
                demisto.debug(f"{entity_type} - {api_response.get('count')} objects fetched from Vectra")

                # To avoid duplicates, find if in this batch is present the last fetched event
                # If yes, start ingesting incident after it
                # This has to be done in two pass
                last_fetched_incident_found = False

                # 1st pass
                if api_response.get('results') is None:
                    raise VectraException("API issue")

                api_results = api_response.get('results', {})
                for event in api_results:
                    incident_last_run = None
                    if entity_type == 'Accounts':
                        incident, incident_last_run = account_to_incident(event)
                    elif entity_type == 'Hosts':
                        incident, incident_last_run = host_to_incident(event)
                    elif entity_type == 'Detections':
                        incident, incident_last_run = detection_to_incident(event)

                    if (incident_last_run is not None) \
                            and (incident_last_run.get('last_timestamp') == last_fetched_timestamp) \
                            and (incident_last_run.get('id') == last_fetched_id):
                        demisto.debug(f"{entity_type} - Object with timestamp : "
                                      f"{last_fetched_timestamp} and ID : {last_fetched_id} "
                                      f"was already fetched during previous run.")
                        last_fetched_incident_found = True
                        break

                # 2nd pass
                start_ingesting_incident = False

                for event in api_results:
                    if len(entity_incidents) >= max_created_incidents:
                        demisto.info(f"{entity_type} - Maximum created incidents has been reached ({max_created_incidents}). "
                                     f"Skipping other objects.")
                        break

                    incident_last_run = None
                    if entity_type == 'Accounts':
                        incident, incident_last_run = account_to_incident(event)
                    elif entity_type == 'Hosts':
                        incident, incident_last_run = host_to_incident(event)
                    elif entity_type == 'Detections':
                        incident, incident_last_run = detection_to_incident(event)

                    if (incident_last_run is not None) \
                            and (incident_last_run.get('last_timestamp') == last_fetched_timestamp) \
                            and (incident_last_run.get('id') == last_fetched_id):
                        # Start creating incidents after this one as already fetched during last run
                        start_ingesting_incident = True
                        continue

                    if last_fetched_incident_found and not start_ingesting_incident:
                        demisto.debug(f"{entity_type} - Skipping object "
                                      f"last_timestamp : {incident_last_run.get('last_timestamp')} "
                                      f"/ ID : {incident_last_run.get('id')}")
                    else:
                        demisto.debug(f"{entity_type} - New incident from object "
                                      f"last_timestamp : {incident_last_run.get('last_timestamp')} "
                                      f"/ ID : {incident_last_run.get('id')}")
                        entity_incidents.append(incident)
                        new_last_run[entity_type] = incident_last_run

            if len(entity_incidents) > 0:
                demisto.info(f"{entity_type} - {len(entity_incidents)} incident(s) to create")
                incidents += entity_incidents
            else:
                demisto.info(f"{entity_type} - No new incidents to create, keeping previous last_run data")
                new_last_run[entity_type] = previous_last_run[entity_type]

            # Update remaining list
            remaining_fetch_types.remove(entity_type)
            if len(remaining_fetch_types) > 0:
                max_created_incidents = (sanitize_max_results(integration_params.get('max_fetch')) - len(incidents)) \
                    // len(remaining_fetch_types)

    demisto.info(f"{len(incidents)} total incident(s) to create")

    return new_last_run, incidents


def vectra_search_accounts_command(client: Client, **kwargs) -> CommandResults:
    """
    Returns several Account objects maching the search criterias passed as arguments

    - params:
        - client: Vectra Client
        - kwargs: The different possible search query arguments
    - returns
        CommandResults to be used in War Room
    """
    api_response = client.search_accounts(**kwargs)

    count = api_response.get('count')
    if count is None:
        raise VectraException('API issue')

    accounts_data = list()
    if count == 0:
        readable_output = 'Cannot find any Detection.'
    else:
        if api_response.get('results') is None:
            raise VectraException('API issue')

        api_results = api_response.get('results', [])

        for account in api_results:
            accounts_data.append(extract_account_data(account))

        readable_output_keys = ['ID', 'Username', 'Severity', 'URL']
        readable_output = tableToMarkdown(
            name=f'Accounts table (Showing max {MAX_RESULTS} entries)',
            t=accounts_data,
            headers=readable_output_keys,
            url_keys=['URL'],
            date_fields=['AssignedDate', 'LastDetectionTimestamp']
        )

    command_result = CommandResults(
        readable_output=readable_output,
        outputs_prefix='Vectra.Account',
        outputs_key_field='ID',
        outputs=accounts_data,
        raw_response=api_response
    )

    return command_result


def vectra_search_detections_command(client: Client, **kwargs) -> CommandResults:
    """
    Returns several Detection objects maching the search criterias passed as arguments

    - params:
        - client: Vectra Client
        - kwargs: The different possible search query arguments
    - returns
        CommandResults to be used in War Room
    """
    api_response = client.search_detections(**kwargs)

    count = api_response.get('count')
    if count is None:
        raise VectraException('API issue')

    detections_data = list()
    if count == 0:
        readable_output = 'Cannot find any Detection.'
    else:
        if api_response.get('results') is None:
            raise VectraException('API issue')

        api_results = api_response.get('results', [])

        # Define which fields we want to exclude from the context output
        # detection_context_excluded_fields = list()
        # Context Keys
        # context_keys = list()

        for detection in api_results:
            detection_data = extract_detection_data(detection)
            # detection_data = {k: detection_data[k] for k in detection_data if k not in detection_context_excluded_fields}
            detections_data.append(detection_data)

        readable_output_keys = ['ID', 'Name', 'Severity', 'LastTimestamp', 'Category', 'URL']
        readable_output = tableToMarkdown(
            name=f'Detections table (Showing max {MAX_RESULTS} entries)',
            t=detections_data,
            headers=readable_output_keys,
            url_keys=['URL'],
            date_fields=['AssignedDate', 'FirstTimestamp', 'LastTimestamp'],
        )

    command_result = CommandResults(
        readable_output=readable_output,
        outputs_prefix='Vectra.Detection',
        outputs_key_field='ID',
        outputs=detections_data,
        raw_response=api_response
    )

    return command_result


def vectra_search_hosts_command(client: Client, **kwargs) -> CommandResults:
    """
    Returns several Host objects maching the search criterias passed as arguments

    - params:
        - client: Vectra Client
        - kwargs: The different possible search query arguments
    - returns
        CommandResults to be used in War Room
    """
    api_response = client.search_hosts(**kwargs)

    count = api_response.get('count')
    if count is None:
        raise VectraException('API issue')

    hosts_data = list()
    if count == 0:
        readable_output = 'Cannot find any Host.'
    else:
        if api_response.get('results') is None:
            raise VectraException('API issue')

        api_results = api_response.get('results', [])

        for host in api_results:
            hosts_data.append(extract_host_data(host))

        readable_output_keys = ['ID', 'Hostname', 'Severity', 'LastDetectionTimestamp', 'URL']
        readable_output = tableToMarkdown(
            name=f'Hosts table (Showing max {MAX_RESULTS} entries)',
            t=hosts_data,
            headers=readable_output_keys,
            url_keys=['URL'],
            date_fields=['AssignedDate', 'LastDetectionTimestamp'],
        )

    command_result = CommandResults(
        readable_output=readable_output,
        outputs_prefix='Vectra.Host',
        outputs_key_field='ID',
        outputs=hosts_data,
        raw_response=api_response
    )

    return command_result


def vectra_get_account_by_id_command(client: Client, id: str) -> CommandResults:
    """
    Gets Account details using its ID

    - params:
        - client: Vectra Client
        - id: The Account ID
    - returns
        CommandResults to be used in War Room
    """
    # Check args
    if not id:
        raise VectraException('"id" not specified')

    search_query: str = f"account.id:{id}"

    api_response = client.search_accounts(search_query_only=search_query)

    count = api_response.get('count')
    if count is None:
        raise VectraException('API issue')
    if count > 1:
        raise VectraException('Multiple Accounts found')

    account_data = None
    if count == 0:
        readable_output = f'Cannot find Account with ID "{id}".'
    else:
        if api_response.get('results') is None:
            raise VectraException('API issue')

        api_results = api_response.get('results', [])
        account_data = extract_account_data(api_results[0])

        readable_output = tableToMarkdown(
            name=f'Account ID {id} details table',
            t=account_data,
            url_keys=['URL'],
            date_fields=['LastDetectionTimestamp']
        )

    command_result = CommandResults(
        readable_output=readable_output,
        outputs_prefix='Vectra.Account',
        outputs_key_field='ID',
        outputs=account_data,
        raw_response=api_response
    )

    return command_result


def vectra_get_detection_by_id_command(client: Client, id: str) -> CommandResults:
    """
    Gets Detection details using its ID

    - params:
        - client: Vectra Client
        - id: The Detection ID
    - returns
        CommandResults to be used in War Room
    """
    # Check args
    if not id:
        raise VectraException('"id" not specified')

    search_query: str = f"detection.id:{id}"

    api_response = client.search_detections(search_query_only=search_query)

    count = api_response.get('count')
    if count is None:
        raise VectraException('API issue')
    if count > 1:
        raise VectraException('Multiple Detections found')

    detection_data = None
    if count == 0:
        readable_output = f'Cannot find Detection with ID "{id}".'
    else:
        if api_response.get('results') is None:
            raise VectraException('API issue')

        api_results = api_response.get('results', [])
        detection_data = extract_detection_data(api_results[0])

        readable_output = tableToMarkdown(
            name=f"Detection ID '{id}' details table",
            t=detection_data,
            url_keys=['URL'],
            date_fields=['FirstTimestamp', 'LastTimestamp'],
        )

    command_result = CommandResults(
        readable_output=readable_output,
        outputs_prefix='Vectra.Detection',
        outputs_key_field='ID',
        outputs=detection_data,
        raw_response=api_response
    )

    return command_result


def vectra_get_host_by_id_command(client: Client, id: str) -> CommandResults:
    """
    Gets Host details using its ID

    - params:
        - client: Vectra Client
        - id: The Host ID
    - returns
        CommandResults to be used in War Room
    """
    # Check args
    if not id:
        raise VectraException('"id" not specified')

    search_query: str = f"host.id:{id}"

    api_response = client.search_hosts(search_query_only=search_query)

    count = api_response.get('count')
    if count is None:
        raise VectraException('API issue')
    if count > 1:
        raise VectraException('Multiple Hosts found')

    host_data = None
    if count == 0:
        readable_output = f'Cannot find Host with ID "{id}".'
    else:
        if api_response.get('results') is None:
            raise VectraException('API issue')

        api_results = api_response.get('results', [])
        host_data = extract_host_data(api_results[0])

        readable_output = tableToMarkdown(
            name=f'Host ID {id} details table',
            t=host_data,
            url_keys=['URL'],
            date_fields=['LastDetectionTimestamp'],
        )

    command_result = CommandResults(
        readable_output=readable_output,
        outputs_prefix='Vectra.Host',
        outputs_key_field='ID',
        outputs=host_data,
        raw_response=api_response
    )

    return command_result


def get_detection_pcap_file_command(client: Client, id: str):
    """
    Downloads a PCAP fileassociated to a detection

    - params:
        - client: Vectra Client
        - id: The Detection ID
    - returns:
        A commandResult to use in the War Room
    """
    if not id:
        raise VectraException('"id" not specified')

    api_response = client.get_pcap_by_detection_id(id=id)

    # 404 API error will be raised by the Client class
    filename = f'detection-{id}.pcap'
    file_content = api_response.content
    pcap_file = fileResult(filename, file_content)

    return pcap_file


def mark_detection_as_fixed_command(client: Client, id: str, fixed: str) -> CommandResults:
    """
    Toggles a detection status as : fixed / Not fixed

    - params:
        - client: Vectra Client
        - id: The Detection ID
        - fixed: The Detection future state
    """

    if (id is None) or (id == ''):
        raise VectraException('"id" not specified')
    fixed_as_bool = str2bool(fixed)
    if fixed_as_bool is None:
        raise VectraException('"fixed" not specified')

    api_response = client.markasfixed_by_detection_id(id=id, fixed=fixed_as_bool)

    # 404 API error will be raised by the Client class
    command_result = CommandResults(
        readable_output=f'Detection "{id}" successfully {"marked" if fixed_as_bool else "unmarked"} as fixed.',
        raw_response=api_response
    )

    return command_result


def add_tags_command(client: Client, type: str, id: str, tags: str) -> CommandResults:
    """
    Adds several tags to an account/host/detection

    - params:
        - client: Vectra Client
        - type: The object to work with ("account", "host" or "detection")
        - id: The id ID the account/host/detection
        - tags: The tags list (comma separated)
    """

    if not type:
        raise VectraException('"type" not specified')
    if not id:
        raise VectraException('"id" not specified')
    if not tags:
        raise VectraException('"tags" not specified')

    api_response = client.add_tags(id=id, type=type, tags=tags.split(','))

    # 404 API error will be raised by the Client class
    command_result = CommandResults(
        readable_output=f'Tags "{tags}" successfully added.',
        raw_response=api_response
    )

    return command_result


def del_tags_command(client: Client, type: str, id: str, tags: str) -> CommandResults:
    """
    Removes several tags from an account/host/detection

    - params:
        - client: Vectra Client
        - type: The object to work with ("account", "host" or "detection")
        - id: The ID of the account/host/detection
        - tags: The tags list (comma separated)
    """

    if not type:
        raise VectraException('"type" not specified')
    if not id:
        raise VectraException('"id" not specified')
    if not tags:
        raise VectraException('"tags" not specified')

    api_response = client.del_tags(id=id, type=type, tags=tags.split(','))

    # 404 API error will be raised by the Client class
    command_result = CommandResults(
        readable_output=f'Tags "{tags}" successfully deleted.',
        raw_response=api_response
    )

    return command_result


''' MAIN FUNCTION '''


def main() -> None:  # pragma: no cover
    # Set some settings as global (to use them inside some functions)
    global global_UI_URL

    integration_params = demisto.params()
    command = demisto.command()
    kwargs = demisto.args()

    server_fqdn: Optional[str] = integration_params.get('server_fqdn')
    if not server_fqdn:  # Should be impossible thx to UI required settings control
        raise DemistoException("Missing integration setting : 'Server FQDN'")

    credentials: Optional[Dict] = integration_params.get('credentials')
    if not credentials:
        raise DemistoException("Missing integration setting : 'Credentials' or 'API token'")

    api_token: Optional[str] = credentials.get('password')
    if (api_token is None) or (api_token == ''):
        raise DemistoException("Missing integration setting : 'Credentials password' or 'API token'")

    # Setting default settings for fetch mode
    if integration_params.get('isFetch'):
        if integration_params.get('first_fetch') == '':
            integration_params['first_fetch'] = DEFAULT_FIRST_FETCH
            demisto.debug(f"First fetch timestamp not set, setting to default '{DEFAULT_FIRST_FETCH}'")
        if integration_params.get('fetch_entity_types') == []:
            integration_params['fetch_entity_types'] = DEFAULT_FETCH_ENTITY_TYPES
            demisto.debug(f"Fetch entity types not set, setting to default '{DEFAULT_FETCH_ENTITY_TYPES}'")
        if integration_params.get('max_fetch') == '':
            integration_params['max_fetch'] = DEFAULT_MAX_FETCH
            demisto.debug(f"Max incidents per fetch not set, setting to default '{DEFAULT_MAX_FETCH}'")

    verify_certificate: bool = not integration_params.get('insecure', False)
    use_proxy: bool = integration_params.get('use_proxy', False)

    global_UI_URL = urljoin('https://', server_fqdn)
    api_base_url = urljoin('https://', urljoin(server_fqdn, API_VERSION_URL))

    demisto.info(f'Command being called is {command}')
    try:
        headers: Dict = {"Authorization": f"token {api_token}"}

        # As the Client class inherits from BaseClient, SSL verification and system proxy are handled out of the box by it
        # Passing ``verify_certificate`` and ``proxy``to the Client constructor
        client = Client(
            proxy=use_proxy,
            verify=verify_certificate,
            headers=headers,
            base_url=api_base_url
        )

        if command == 'test-module':
            # This is the call made when pressing the integration Test button.
            results = test_module(client, integration_params)
            return_results(results)

        elif command == 'fetch-incidents':
            # Get new incidents to create if any from Vectra API
            next_run, incidents = fetch_incidents(client, integration_params)

            # Add incidents in the SOAR platform
            demisto.incidents(incidents)

            if next_run:
                demisto.info(f"Setting last run to : {next_run}")
                demisto.setLastRun(next_run)
            demisto.info("fetch-incidents action done")

        elif command == 'vectra-search-accounts':
            return_results(vectra_search_accounts_command(client, **kwargs))
        elif command == 'vectra-search-hosts':
            return_results(vectra_search_hosts_command(client, **kwargs))
        elif command == 'vectra-search-detections':
            return_results(vectra_search_detections_command(client, **kwargs))

        # ## Accounts centric commands
        elif command == 'vectra-account-describe':
            return_results(vectra_get_account_by_id_command(client, **kwargs))
        elif command == 'vectra-account-add-tags':
            return_results(add_tags_command(client, type="account", **kwargs))
        elif command == 'vectra-account-del-tags':
            return_results(del_tags_command(client, type="account", **kwargs))

        # ## Hosts centric commands
        elif command == 'vectra-host-describe':
            return_results(vectra_get_host_by_id_command(client, **kwargs))
        elif command == 'vectra-host-add-tags':
            return_results(add_tags_command(client, type="host", **kwargs))
        elif command == 'vectra-host-del-tags':
            return_results(del_tags_command(client, type="host", **kwargs))

        # ## Detections centric commands
        elif command == 'vectra-detection-describe':
            return_results(vectra_get_detection_by_id_command(client, **kwargs))
        elif command == 'vectra-detection-get-pcap':
            return_results(get_detection_pcap_file_command(client, **kwargs))
        elif command == 'vectra-detection-markasfixed':
            return_results(mark_detection_as_fixed_command(client, **kwargs))
        elif command == 'vectra-detection-add-tags':
            return_results(add_tags_command(client, type="detection", **kwargs))
        elif command == 'vectra-detection-del-tags':
            return_results(del_tags_command(client, type="detection", **kwargs))

        else:
            raise NotImplementedError()

    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(f'Failed to execute {command} command.\nError:\n{str(e)}')


''' ENTRY POINT '''


if __name__ in ('__main__', '__builtin__', 'builtins'):  # pragma: no cover
    main()
