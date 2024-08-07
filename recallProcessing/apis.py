import os, aiohttp, json, asyncio

# Add retry logic so if the bot is not ready yet, we can retry after 10 seconds. max 2 retries
async def get_meeting_details(bot_id):
    max_retries = 2
    retry_delay = 10

    for attempt in range(max_retries + 1):
        try:
            recall_api_url = f"https://us-west-2.recall.ai/api/v1/bot/{bot_id}/"
            api_key = os.environ["RECALL_API_KEY"]
            headers = {
                "accept": "application/json",
                "Authorization": f"{api_key}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(recall_api_url, headers=headers) as response:
                    response.raise_for_status()
                    bot_details = await response.json()
                    video_url = bot_details.get('video_url')
                    
                    meeting_id = bot_details['meeting_url']['meeting_id']
                    platform = bot_details['meeting_url']['platform']
                    
                    if not video_url:
                        raise ValueError("Video URL not found in bot details")
                    print(f"Full bot details: {json.dumps(bot_details, indent=2)}")
                    return {
                        "video_url": video_url,
                        "meeting_id": meeting_id,
                        "platform": platform
                    }
        except (aiohttp.ClientError, ValueError) as e:
            if attempt < max_retries:
                print(f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print(f"Failed to retrieve bot details after {max_retries + 1} attempts: {str(e)}")
                raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise
        
        
        

async def send_for_curation(transcription, meeting_info):
    print("Sent for curation")
    pass