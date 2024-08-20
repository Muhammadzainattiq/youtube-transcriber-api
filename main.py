from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = FastAPI(
    title="Youtube Video Transcriber API",
    description="API for getting/extracting transcripts of youtubue videos.",
    version="1.0.0",
    servers=[
        {
            "url": "https://youtube-transcriber-m5luuhf8j-zain-attiqs-projects.vercel.app/",
            "description": "Production server"
        }
    ]
)

def extract_transcript(video_id):
    """Extracts the transcript from a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        for transcript in transcript_list:
            transcript_text_list = transcript.fetch()
            transcript_text = ""
            if transcript.language_code == 'en':
                for line in transcript_text_list:
                    transcript_text += " " + line["text"]
                return transcript_text
            elif transcript.is_translatable:
                english_transcript_list = transcript.translate('en').fetch()
                for line in english_transcript_list:
                    transcript_text += " " + line["text"]
                return transcript_text
        return None
    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No transcript found for this video.")
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="Video unavailable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcript/")
async def get_transcript(video_url: str):
    try:
        # Extract the video ID from the full YouTube URL
        if "v=" in video_url:
            video_id = video_url.split("v=")[1]
            ampersand_position = video_id.find("&")
            if ampersand_position != -1:
                video_id = video_id[:ampersand_position]
        else:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL format.")
        
        transcript = extract_transcript(video_id)
        if transcript:
            return {"video_id": video_id, "transcript": transcript}
        else:
            raise HTTPException(status_code=404, detail="Transcript extraction failed. Please check the video URL.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/", summary="Root endpoint", description="Welcome message for the API.")
async def read_root():
    return {"message": "Welcome to the Youtube Video Transcriber GPT"}
