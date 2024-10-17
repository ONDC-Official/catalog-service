import json

import requests

from config import get_config_by_name
from logger.custom_logging import log, log_error


def get_provider_search_tags(provider_id):
    try:
        url = f'{get_config_by_name("OMS_ENDPOINT")}/api/widget/tags/providers/all'
        log(f"Making provider-search-tags call on OMS for {provider_id}")
        response = requests.get(url, params={"providerId": provider_id})
        print(f"Got respponse as {response}")
        return json.loads(response.text)
    except Exception as e:
        log_error(f"Got exception for error: {e}")
        return []


# def get_provider_search_tags_function(url, payload, headers=None):
#     try:
#         log(f"Making provider-search-tags call on OMS for {payload}")
#         response = requests.get(url, params={"providerId": provider_id})
#         return json.loads(response.text), response.status_code
#     except Exception as e:
#         return {"error": f"Something went wrong {e}!"}, 500
#
#
# def get_provider_search_tags_cached(endpoint, payload, headers=None):
#     # Generate cache key
#     cache_key = hash_key(endpoint, payload, headers)
#
#     # Check if result is in cache
#     if cache_key in lookup_cache:
#         return lookup_cache[cache_key], 200
#
#     # Make the API request (replace with actual API call)
#     response, status_code = lookup_call_function(endpoint, payload, headers)
#
#     if status_code == 200 and len(response) > 0:
#         # Cache the response if status code is 200
#         lookup_cache[cache_key] = response
#         return response, 200
#     else:
#         # Do not cache the result if status code is not 200
#         return {"error": "API request failed"}, status_code
