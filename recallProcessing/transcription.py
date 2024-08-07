import os
from heapq import heappush, heappop
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

async def transcribe_url(url):
    API_KEY = os.environ["DEEPGRAM_API_KEY"]
    
    try:
        
        url=f"{url}"
        
        AUDIO_URL = {
            "url": url
        }
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(API_KEY)

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            summarize="v2",
            topics=True,
            intents=True,
            smart_format=True,
            punctuate=True,
            redact=["pci", "ssn"],
            diarize=True,
            filler_words=True,
        )

        # STEP 3: Call the transcribe_url method with the audio payload and options
        response = deepgram.listen.rest.v("1").transcribe_url(AUDIO_URL, options)
        
        transcript = response.results.channels[0].alternatives[0].transcript
        diarized_transcript = response.results.channels[0].alternatives[0].paragraphs.transcript
        summary = response.results.summary.short
        intent_segments = response.results.intents.segments
        topic_segments = response.results.topics.segments
        
        intents_and_topics = await retreive_intents_and_topics(intent_segments, topic_segments)
        
        

        # STEP 4: Print the response and return the transcript
        # print(response.to_json(indent=4))
        print(transcript)
        return {
            "transcript": transcript,
            "diarized_transcript": diarized_transcript,
            "summary": summary,
            "intents_and_topics": intents_and_topics
        }
        
        

    except Exception as e:
        print(f"Exception: {e}")
        
        
# async def retreive_intents_and_topics(intent_segments, topic_segments):
#     intents_and_topics = []
#     desired_confidence_score = 0.25
#     for segment in intent_segments:
#         if segment.intents[0].confidence_score > desired_confidence_score:
#             intents_and_topics.append(segment.intents[0].intent)
#     for segment in topic_segments:
#         if segment.topics[0].confidence_score > desired_confidence_score:
#             intents_and_topics.append(segment.topics[0].topic)
        
#     return intents_and_topics
    

async def retreive_intents_and_topics(intent_segments, topic_segments):
    desired_confidence_score = 0.25
    max_heap = []
    
    # Process topics
    for segment in topic_segments:
        if segment.topics[0].confidence_score > desired_confidence_score:
            heappush(max_heap, (-segment.topics[0].confidence_score, 'topic', segment.topics[0].topic))
    
    # Process intents
    for segment in intent_segments:
        if segment.intents[0].confidence_score > desired_confidence_score:
            heappush(max_heap, (-segment.intents[0].confidence_score, 'intent', segment.intents[0].intent))
    
    # Extract items from heap
    intents_and_topics = []
    while max_heap:
        _, item_type, item = heappop(max_heap)
        intents_and_topics.append(item)
    
    return intents_and_topics