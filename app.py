from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

app = Flask(__name__)

@app.route('/api/subtitles', methods=['GET'])
def get_subtitles():
    video_id = request.args.get('videoID')

    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400

    try:
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript
        formatter = JSONFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        
        return jsonify({'subtitles': formatted_transcript})
    except Exception as e:
        print(f"Error fetching subtitles: {e}")
        return jsonify({'error': 'Failed to fetch subtitles'}), 500

if __name__ == '__main__':
    app.run(port=5000)
