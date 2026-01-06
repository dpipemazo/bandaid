## Django + ElevenLabs Text-to-Speech Demo

A minimal Django app that sends user-entered text to the ElevenLabs Text-to-Speech API and plays the returned audio in the browser.

### Prerequisites
- Python 3.10+
- ElevenLabs API key

### Setup
1. Create and activate a virtualenv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the API key (already placed in `.env` for local dev):
   ```bash
   ELEVENLABS_API_KEY=your_key_here
   ```

### Run the app
```bash
source venv/bin/activate
python manage.py migrate
python manage.py runserver
```

Open http://localhost:8000, enter text, and click **Play audio**.

### Notes
- Uses default voice `21m00Tcm4TlvDq8ikWAM` and model `eleven_multilingual_v2`.
- Audio is returned as `audio/mpeg` and played via an HTML5 `<audio>` element.
- Keep your ElevenLabs API key secret; do not commit `.env`. See official docs: https://elevenlabs.io/docs/api-reference/introduction.