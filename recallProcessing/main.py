import json
import asyncio
import aiohttp
import os

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
        bot_id = data.get('bot_id')
        if bot_id:
            print(f"Bot ID found: {bot_id}")
            # Call the Recall API to get the bot details
            download_url = await get_download_url(bot_id)
            # Print the download URL
            print(f"Download URL: {download_url}")
            return {
                'statusCode': 200,
                'body': json.dumps({'download_url': download_url})
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

async def get_download_url(bot_id):
    recall_api_url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/"
    api_key = os.environ["RECALL_API_KEY"]
    headers = {
        "accept": "application/json",
        "Authorization": f"{api_key}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(recall_api_url, headers=headers) as response:
                response.raise_for_status()  # Raises an ClientResponseError for bad responses
                bot_details = await response.json()
                video_url = bot_details.get('video_url')
                if not video_url:
                    raise ValueError("Video URL not found in bot details")
                print(f"Full bot details: {json.dumps(bot_details, indent=2)}")  # Add this line for debugging
                return video_url
    except aiohttp.ClientError as e:
        print(f"Failed to retrieve bot details: {str(e)}")
        raise
    except ValueError as e:
        print(str(e))
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

# Synchronous wrapper for Lambda
def lambda_handler(event, context=None):
    return asyncio.get_event_loop().run_until_complete(async_lambda_handler(event, context))

# Main execution
if __name__ == "__main__":
    result = lambda_handler(event)
    print(f"Lambda handler result: {json.dumps(result, indent=2)}")