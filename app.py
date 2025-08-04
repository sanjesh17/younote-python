from flask import Flask, request, jsonify
from yt_dlp_transcript import get_transcript
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/subtitles', methods=['GET'])
def get_subtitles():
    video_id = request.args.get('videoID')
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400
    
    # Construct YouTube URL
    url = f'https://www.youtube.com/watch?v={video_id}'
    
    try:
        # Get transcript using yt-dlp-transcript
        transcript = get_transcript(url)
        
        # Format similar to youtube-transcript-api
        formatted_subtitles = []
        for entry in transcript:
            formatted_subtitles.append({
                'text': entry.get('text', ''),
                'start': entry.get('start', 0),
                'duration': entry.get('duration', 0)
            })
        
        return jsonify({'subtitles': formatted_subtitles})
        
    except Exception as e:
        print(f"Error fetching subtitles: {e}")
        return jsonify({'error': 'Failed to fetch subtitles'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)