import os
import requests

bhashini_pipeline_url = 'https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline'
bhashini_translate_url = 'https://dhruva-api.bhashini.gov.in/services/inference/pipeline'


def translate(data):
    # Create a pipeline
    pipeline_data = {
        "pipelineTasks": [
            {
                "taskType": "transliteration",
                "config": {
                    "language": {
                        "sourceLanguage": data['source_language'],
                        "targetLanguage": data['target_language']
                    }
                }
            }
        ],
        "pipelineRequestConfig": {
            "pipelineId": "64392f96daac500b55c543cd"
        }
    }

    headers = {
        'userID': os.getenv('BHASHINI_USERID'),
        'ulcaApiKey': os.getenv('BHASHINI_ULCA_API_KEY'),
        'Content-Type': 'application/json'
    }

    pipeline_response = requests.post(bhashini_pipeline_url, headers=headers, json=pipeline_data)
    json_res = pipeline_response.json()

    # Prepare object for translation
    pipeline_response_config = json_res['pipelineResponseConfig']
    trans_service_id = None

    for each_resp in pipeline_response_config:
        all_config = each_resp['config']
        for each_config in all_config:
            if (each_config['language']['sourceLanguage'] == data['source_language'] and
                    each_config['language']['targetLanguage'] == data['target_language']):
                trans_service_id = each_config['serviceId']
                break
        if trans_service_id:
            break

    translation_data = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": data['source_language'],
                        "targetLanguage": data['target_language']
                    },
                    "serviceId": trans_service_id,
                    "isSentence": True
                }
            }
        ],
        "inputData": {
            "input": [
                {
                    "source": data['text']
                }
            ]
        }
    }

    headers.update({
        json_res['pipelineInferenceAPIEndPoint']['inferenceApiKey']['name']:
            json_res['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value']
    })

    translate_response = requests.post(bhashini_translate_url, headers=headers, json=translation_data)
    translation = translate_response.json()

    translated_text = None
    if translation.get('pipelineResponse') and len(translation['pipelineResponse']) > 0:
        if len(translation['pipelineResponse'][0]['output']) > 0:
            translated_text = translation['pipelineResponse'][0]['output'][0]['target'][0]

    return translated_text


if __name__ == '__main__':
    data = {
        "text": "apple",
        "source_language": "en",
        "target_language": "hi"
    }
    print(translate(data))
