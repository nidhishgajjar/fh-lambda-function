import requests


async def download_file(url, local_filename=None):
    # If no filename is specified, use the last part of the URL as the filename
    if local_filename is None:
        local_filename = url.split('/')[-1].split('?')[0]
    
    # Send a GET request to the URL
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # Will raise an exception for HTTP errors
        
        # Open the local file and write the content
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    return local_filename