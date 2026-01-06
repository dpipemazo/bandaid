import os
import unittest
from unittest.mock import MagicMock, patch

from django.test import TestCase, Client
from django.urls import reverse, resolve


class IndexViewTests(TestCase):
    """Tests for the index view."""

    def setUp(self):
        self.client = Client()

    def test_index_view_renders(self):
        """Test that index view renders successfully."""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Text to Speech")
        self.assertContains(response, "Play audio")


class TextToSpeechViewTests(TestCase):
    """Tests for the text-to-speech API view."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("text_to_speech")
        self.test_text = "Hello, this is a test."
        self.test_api_key = "test_api_key_12345"
        self.mock_audio_data = b"fake_audio_data"

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test_api_key_12345"})
    @patch("tts_app.views.ElevenLabs")
    def test_text_to_speech_success(self, mock_elevenlabs_class):
        """Test successful text-to-speech conversion."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_elevenlabs_class.return_value = mock_client_instance
        mock_client_instance.text_to_speech.convert.return_value = self.mock_audio_data

        # Make request
        response = self.client.post(self.url, {"text": self.test_text})

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "audio/mpeg")
        self.assertEqual(response.content, self.mock_audio_data)

        # Verify ElevenLabs was called correctly
        mock_elevenlabs_class.assert_called_once_with(api_key=self.test_api_key)
        mock_client_instance.text_to_speech.convert.assert_called_once_with(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_multilingual_v2",
            text=self.test_text,
            output_format="mp3_44100_128",
        )

    def test_text_to_speech_empty_text(self):
        """Test that empty text returns 400 error."""
        response = self.client.post(self.url, {"text": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Text is required."})

    def test_text_to_speech_whitespace_only_text(self):
        """Test that whitespace-only text returns 400 error."""
        response = self.client.post(self.url, {"text": "   \n\t  "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Text is required."})

    def test_text_to_speech_missing_text_parameter(self):
        """Test that missing text parameter returns 400 error."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Text is required."})

    @patch.dict(os.environ, {}, clear=True)
    def test_text_to_speech_missing_api_key(self):
        """Test that missing API key returns 500 error."""
        response = self.client.post(self.url, {"text": self.test_text})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(), {"error": "ElevenLabs API key is not configured."}
        )

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test_api_key_12345"})
    @patch("tts_app.views.ElevenLabs")
    def test_text_to_speech_api_error(self, mock_elevenlabs_class):
        """Test that API errors are handled gracefully."""
        # Setup mock to raise exception
        mock_client_instance = MagicMock()
        mock_elevenlabs_class.return_value = mock_client_instance
        mock_client_instance.text_to_speech.convert.side_effect = Exception(
            "API Error"
        )

        # Make request
        response = self.client.post(self.url, {"text": self.test_text})

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"error": "Failed to generate audio."})

    def test_text_to_speech_get_method_not_allowed(self):
        """Test that GET requests are not allowed."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_text_to_speech_put_method_not_allowed(self):
        """Test that PUT requests are not allowed."""
        response = self.client.put(self.url, {"text": self.test_text})
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test_api_key_12345"})
    @patch("tts_app.views.ElevenLabs")
    def test_text_to_speech_preserves_text_content(self, mock_elevenlabs_class):
        """Test that text content is preserved correctly."""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_elevenlabs_class.return_value = mock_client_instance
        mock_client_instance.text_to_speech.convert.return_value = self.mock_audio_data

        # Test with text that has leading/trailing whitespace
        text_with_whitespace = "  Hello World  "
        response = self.client.post(self.url, {"text": text_with_whitespace})

        # Should strip whitespace before sending to API
        self.assertEqual(response.status_code, 200)
        mock_client_instance.text_to_speech.convert.assert_called_once()
        call_args = mock_client_instance.text_to_speech.convert.call_args
        self.assertEqual(call_args.kwargs["text"], text_with_whitespace.strip())


class URLTests(TestCase):
    """Tests for URL routing."""

    def test_index_url_resolves(self):
        """Test that index URL resolves to index_view."""
        url = reverse("index")
        self.assertEqual(url, "/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "index_view")

    def test_text_to_speech_url_resolves(self):
        """Test that text-to-speech URL resolves to text_to_speech_view."""
        url = reverse("text_to_speech")
        self.assertEqual(url, "/api/text-to-speech/")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, "text_to_speech_view")


class ElevenLabsIntegrationTests(TestCase):
    """Integration test that hits the real ElevenLabs API via the Django view."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("text_to_speech")

    @unittest.skipUnless(
        os.getenv("ELEVENLABS_API_KEY"),
        "ELEVENLABS_API_KEY not set for live integration test",
    )
    def test_live_text_to_speech(self):
        """Call the live API and verify we get audio bytes back."""
        response = self.client.post(self.url, {"text": "Hello from integration test"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "audio/mpeg")
        self.assertGreater(len(response.content), 0)
        # Check common MP3 signatures: ID3 tag or MPEG frame header
        self.assertTrue(
            response.content.startswith(b"ID3")
            or response.content[:2] == b"\xff\xfb",
            "Response does not look like MP3 audio",
        )
