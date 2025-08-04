from flask import Flask, request, jsonify
import yt_dlp
import json
import tempfile
import os
import urllib.request
from flask_cors import CORS

app = Flask(__name__)

# ✅ Use specific frontend origin for CORS (update your domain here)
CORS(app, resources={r"/api/*": {"origins": "https://younote-app.vercel.app/"}})

@app.route('/api/subtitles', methods=['GET'])
def get_subtitles():
    video_id = request.args.get('videoID')
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400

    url = f'https://www.youtube.com/watch?v={video_id}'

    try:
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'skip_download': True,
            'subtitlesformat': 'json3',
            'outtmpl': tempfile.gettempdir() + '/%(title)s.%(ext)s'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})

            subtitle_data = None
            if 'en' in subtitles:
                subtitle_url = subtitles['en'][0]['url']
            elif 'en' in automatic_captions:
                subtitle_url = automatic_captions['en'][0]['url']
            else:
                return jsonify({'error': 'No subtitles available'}), 404

            with urllib.request.urlopen(subtitle_url, timeout=10) as response:
                subtitle_content = response.read().decode('utf-8')
                subtitle_data = json.loads(subtitle_content)

            formatted_subtitles = []
            if 'events' in subtitle_data:
                for event in subtitle_data['events']:
                    if 'segs' in event:
                        text = ''.join([seg.get('utf8', '') for seg in event['segs']])
                        if text.strip():
                            formatted_subtitles.append({
                                'text': text.strip(),
                                'start': event.get('tStartMs', 0) / 1000,
                                'duration': event.get('dDurationMs', 0) / 1000
                            })

            return jsonify({'subtitles': formatted_subtitles})

    except Exception as e:
        print(f"Error fetching subtitles: {e}")
        return jsonify({'error': 'Failed to fetch subtitles'}), 500


@app.route('/api/subtitles/simple', methods=['GET'])
def get_subtitles_simple():
    video_id = request.args.get('videoID')
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400

    url = f'https://www.youtube.com/watch?v={video_id}'

    try:
        import subprocess

        result = subprocess.run([
            'yt-dlp',
            '--write-auto-subs',
            '--sub-lang', 'en',
            '--sub-format', 'json3',
            '--skip-download',
            '--print', '%(automatic_captions.en.0.url)s',
            url
        ], capture_output=True, text=True, check=True)

        subtitle_url = result.stdout.strip()

        if subtitle_url and subtitle_url != 'NA':
            with urllib.request.urlopen(subtitle_url, timeout=10) as response:
                subtitle_content = response.read().decode('utf-8')
                subtitle_data = json.loads(subtitle_content)

            formatted_subtitles = []
            if 'events' in subtitle_data:
                for event in subtitle_data['events']:
                    if 'segs' in event:
                        text = ''.join([seg.get('utf8', '') for seg in event['segs']])
                        if text.strip():
                            formatted_subtitles.append({
                                'text': text.strip(),
                                'start': event.get('tStartMs', 0) / 1000,
                                'duration': event.get('dDurationMs', 0) / 1000
                            })

            return jsonify({'subtitles': formatted_subtitles})
        else:
            return jsonify({'error': 'No subtitles available'}), 404

    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to fetch subtitles'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to fetch subtitles'}), 500


if __name__ == '__main__':
    # ✅ No debug mode in production
    app.run(host='0.0.0.0', port=5000)
