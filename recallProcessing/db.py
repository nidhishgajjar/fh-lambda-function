from supabase import create_client
import os
import time
import html




SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

# Initialize Supabase client (assuming it's already set up elsewhere)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



# TODO: Get user details from redis


# Save the meeting recording and transcript files to Supabase
async def save_meeting_recording(meeting_info, file_path):
    try:        

        # Read the file content
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Generate a unique file name
        file_name = f"{meeting_info['meeting_id']}_{meeting_info['platform']}_{int(time.time())}.json"

        # Specify the folder path within the bucket
        folder_path = "user_007/"  # Add a trailing slash
        full_path = folder_path + file_name

        # Upload the file to the 'recall_meetings' bucket in the specified folder
        response = supabase.storage.from_('recall_meetings').upload(
            path=full_path,
            file=file_content,
            file_options={"content-type": "application/json"}
        )

        # Check if the upload was successful
        if isinstance(response, dict) and response.get('error'):
            raise Exception(f"Failed to upload file: {response['error']}")

        # Get the public URL of the uploaded file
        public_url = supabase.storage.from_('recall_meetings').get_public_url(full_path)
        
        

        # Delete the local file after successful upload
        os.remove(file_path)
        
        return {"status": "Success", "message": "Meeting saved to Supabase", "public_url": public_url}
        
        
        

    except Exception as e:
        print(f"Error saving to Supabase: {str(e)}")
        return {"status": "Error", "message": str(e)}
    


async def save_meeting_transcription(transcription, meeting_info):
    try:
        # Create the formatted HTML file
        html_file_path = await create_formatted_html(transcription, meeting_info)
        
        # Read the file content
        with open(html_file_path, 'rb') as file:
            file_name = os.path.basename(html_file_path)
            file_content = file.read()
        
        # Specify the folder path within the bucket
        folder_path = "user_007/"  # Add a trailing slash
        full_path = folder_path + file_name
        
        # Upload the file to the 'recall_meetings' bucket in the specified folder
        response = supabase.storage.from_('user_hubs').upload(
            path=full_path,
            file=file_content,
            file_options={"content-type": "text/html"}
        )
        
        # Check if the upload was successful
        if isinstance(response, dict) and response.get('error'):
            raise Exception(f"Failed to upload file: {response['error']}")
        
        # Get the public URL of the uploaded file
        public_url = supabase.storage.from_('recall_meetings').get_public_url(full_path)
        
        # Optionally, remove the local file after uploading
        os.remove(html_file_path)
        
        return {
            "status": "Success",
            "message": "Meeting transcription saved to Supabase",
            "public_url": public_url
        }
    except Exception as e:
        print(f"Error saving meeting transcription to Supabase: {str(e)}")
        return {"status": "Error", "message": str(e)}




async def create_formatted_html(transcription, meeting_info):
    # Map platform to title
    platform_name = "Google Meet" if meeting_info['platform'] == 'google_meet' else meeting_info['platform'].capitalize()
    
    # Get first 2 intents or topics to name the meeting
    meeting_name = (transcription.get('intents_and_topics', [])[0]) or "Untitled Meeting"
    
    # Format the date
    creation_date = time.strftime("%B %d, %Y", time.localtime())
    
    # Create formatted content
    content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{html.escape(meeting_name)} on {html.escape(platform_name)}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                padding: 30px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #2980b9;
                margin-top: 30px;
            }}
            .creation-date {{
                font-style: italic;
                color: #7f8c8d;
                margin-bottom: 20px;
            }}
            .summary, .transcription {{
                background-color: #ecf0f1;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin-top: 10px;
                border-radius: 4px;
            }}
            .platform {{
                font-weight: bold;
                color: #e74c3c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{html.escape(meeting_name)}</h1>
            <p class="creation-date">Created on {html.escape(creation_date)} | Platform: <span class="platform">{html.escape(platform_name)}</span></p>
            
            <h2>Summary</h2>
            <div class="summary">
                <p>{html.escape(transcription.get('summary', 'No summary available'))}</p>
            </div>
            
            <h2>Transcription</h2>
            <div class="transcription">
                <p>{html.escape(transcription.get('diarized_transcript', 'No transcription available'))}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create a unique filename
    meeting_name_clean = ' '.join(word.capitalize() for word in meeting_name.split())
    filename = f"{meeting_name_clean} - {meeting_info['meeting_id']}.html"
    filepath = os.path.join(os.getcwd(), filename)

    
    # Write content to file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return filepath