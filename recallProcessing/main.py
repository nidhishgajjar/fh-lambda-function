import json
import asyncio
from transcription import transcribe_url
from db import save_meeting_recording, save_meeting_transcription
from dwnld_file import download_file
from apis import get_meeting_details, send_for_curation


# Hardcoded JSON variables
event = {
    "body": json.dumps({
        "data": {
            "bot_id": "3d68cf41-00d8-4e0e-88a1-01fc29f86026",
            "status": {
                "code": "done",
                "created_at": "2024-08-06T01:23:07.420047+00:00",
                "message": None,
                "sub_code": None
            }
        },
        "event": "bot.status_change"
    })
}

async def async_lambda_handler(event, context=None):
    print("Lambda function started")
    print(f"Received event: {json.dumps(event)}")

    # Check if the event is coming from API Gateway or direct invocation
    if 'body' in event:
        body = json.loads(event['body'])
    else:
        body = event

    print(f"Processed body: {json.dumps(body)}")

    # Extract the data from the webhook payload
    data = body.get('data', {})
    bot_status = data.get('status', {})
    print(f"Bot status: {bot_status}")

    # Check if the bot status is 'done'
    if bot_status.get('code') == 'done':
        # Once we get done event wait for 10 seconds to make sure the bot is fully processed
        # await asyncio.sleep(10)
        
        bot_id = data.get('bot_id')
        if bot_id:
            print(f"Bot ID found: {bot_id}")
            # Call the Recall API to get the bot details
            recording_details = await get_meeting_details(bot_id)
            # Print the download URL
            # print(f"Download URL: {download_url}")
            
            
            # Transcribe the file
            transcription = await transcribe_url(recording_details['video_url'])

            # Download the file
            local_filename = await download_file(recording_details['video_url'])
            print(f"File downloaded as: {local_filename}")
            
            # Save meeting recording and transcription to the database
            await save_meeting_recording(recording_details,local_filename)
            await save_meeting_transcription(transcription, recording_details)

            # Send the transcription to the curator
            await send_for_curation(transcription, recording_details)

            return {
                'statusCode': 200,
                'body': json.dumps({'intents_and_topics': transcription['intents_and_topics'], 'summary': transcription['summary'], 'diarized_transcript': transcription['diarized_transcript']})
            }
        else:
            print("Bot ID not found in the webhook payload")
            return {
                'statusCode': 400,
                'body': json.dumps('Bot ID not found in the webhook payload')
            }

    print("Webhook processed successfully")
    return {
        'statusCode': 200,
        'body': json.dumps('Webhook processed successfully')
    }



# Synchronous wrapper for Lambda
def lambda_handler(event, context=None):
    return asyncio.get_event_loop().run_until_complete(async_lambda_handler(event, context))

# Main execution
if __name__ == "__main__":
    result = lambda_handler(event)
    print(f"Lambda handler result: {json.dumps(result, indent=2)}")






# ==============================================================================================================================================================================================

# main.py (python example)

# import os

# from deepgram import (
#     DeepgramClient,
#     PrerecordedOptions,
# )


# # URL to the audio file
# AUDIO_URL = {
#     "url": f"https://us-west-2-recallai-production-bot-data.s3.amazonaws.com/3d68cf41-00d8-4e0e-88a1-01fc29f86026/AROA3Z2PRSQANGTUQXHNJ%3Ai-0ba808c3bdf73a7b2/video-b74c1f1a-3297-4250-9e2b-0f992c3d3985.mp4?AWSAccessKeyId=ASIA3Z2PRSQAKIVIGPUR&Signature=kriUVE%2Fl3LGyg8C%2FnuynZKoVGLI%3D&x-amz-security-token=IQoJb3JpZ2luX2VjECEaCXVzLXdlc3QtMiJGMEQCICT%2B1aqN3jukogNkdedeJtNpVZvezHgBm7gYXaq57fCOAiAHB1ym2SRkrNWWPA5R2WtL9GJyWSIpkce9N%2Fmn3q1gSyq5BQgaEAAaDDgxMTM3ODc3NTA0MCIMzyJpCi5el1gZKqSHKpYFTzFFEyDIn5LkjyIVJSFU6b3KWIX3rvmMBF7TLo0K7589KZg9%2Bo%2FtRV2H9JAIMV%2BfhgiQP5EfFBvSfEFrZh7wUMlXtZ48MTFT59ei7A8VRBkffClAhfLMHT8UdKYsg3pnW4uUSV2hqFxrTbu6pittGf%2BEUdGAK1ybd7JSiFLzSGu6lcZ681qWLSq0%2BbMcKgkpyYS92IAZxiuH8z5orgoNlZTT5CL3Ag1%2FK18eCZcS1Y0YR%2F2ZCogSpcTgBiNheipRDNCG5oJCIc7PrcfPeXwxCOxJxDF5RsvlGqj8O%2FbyB7U1kvbD659A3TOn6rwxw8YvDCA1G378qe1AmS0z91iGisGFqDrQU%2BRd3cRslZmbxs3MOap4BsggYjs4Y6oGO63g%2B6cvfOY%2FPA1F%2BRekaN3%2BG60AT73Ij6PWokUWPTC0mMW532kVAZIjImpg66NeQTntatWJ7GPl%2B%2B3rugwbyL1JvSBGXdLI%2F9m8Jpa5Rctd6NqJAWXAUw8qm%2BexssKoaidylDYXFeO35WGGjNiN%2FsupWVGwyRK0s3O5QmHhqbdse9xY5R2MjP2XYm%2BWMN68Dsa9RrdC8rIjqcpBOkCGHQsPVIeU4xgzd1VkOTcsaGpzod%2FryhESHKinV8jkdSGP2g7VVve12ZPZw2X%2FQez21KT%2FxnBpSybjW21YgBBsEqouDh7Yc4sQSScG6jtYOoxEsf4RbppTswo7GDwA7YKI5o0o95AtUBvb%2Fe%2F2jM7HPM0DW0aQpoZPIg2hkXteenR8utJWL%2F0agOX4cCBvif6VAFdwiar2rQ6yNG6PHGJxmhe%2FUSegsmjzTiQnQf1x74WDVlLc80lxZBMFddwJWq6MmlzwDy7OEP7udAPem1qIOzsBkWoDIeQqLbUwy9bOtQY6sgHLn2hY3m643Ds0JT7OLLRHkizBR6xqW%2FDhjUZ9GPWd%2BlwhmW1ijptAuYKvnOkbf5KG6WObPLAOBbg5IpL8NHJVezPKXtheiiuyyWTcXDFSchARnCwxeFcPUVnw2wcCIhQWtSpabyIWAylnIlrIwItPjJwZprgeWWj%2FhR8YELCpQgqapxiJvvmepi8ERZpE9%2Bmu%2FOP2R%2FUnTrdr5bhxqff7ugNUt6AlhHypWSJxZddPE75b&Expires=1723081643"
# }

# API_KEY = os.environ["DEEPGRAM_API_KEY"]


# def main():
#     try:
#         # STEP 1 Create a Deepgram client using the API key
#         deepgram = DeepgramClient(API_KEY)

#         #STEP 2: Configure Deepgram options for audio analysis
#         options = PrerecordedOptions(
#             model="nova-2",
#             smart_format=True,
#         )

#         # STEP 3: Call the transcribe_url method with the audio payload and options
#         response = deepgram.listen.rest.v("1").transcribe_url(AUDIO_URL, options)

#         # STEP 4: Print the response
#         print(response.to_json(indent=4))

#     except Exception as e:
#         print(f"Exception: {e}")


# if __name__ == "__main__":
#     main()



        
# async def get_download_url(bot_id):
#     recall_api_url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/"
#     api_key = os.environ["RECALL_API_KEY"]
#     headers = {
#         "accept": "application/json",
#         "Authorization": f"{api_key}"
#     }

#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(recall_api_url, headers=headers) as response:
#                 response.raise_for_status()  # Raises an ClientResponseError for bad responses
#                 bot_details = await response.json()
#                 video_url = bot_details.get('video_url')
#                 if not video_url:
#                     raise ValueError("Video URL not found in bot details")
#                 print(f"Full bot details: {json.dumps(bot_details, indent=2)}")  # Add this line for debugging
#                 return video_url
#     except aiohttp.ClientError as e:
#         print(f"Failed to retrieve bot details: {str(e)}")
#         raise
#     except ValueError as e:
#         print(str(e))
#         raise
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         raise
