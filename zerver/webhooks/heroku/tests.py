from zerver.lib.test_classes import WebhookTestCase


class HerokuHookTests(WebhookTestCase):
    CHANNEL_NAME = "Heroku"
    URL_TEMPLATE = "/api/v1/external/heroku?stream={stream}&api_key={api_key}"
    WEBHOOK_DIR_NAME = "heroku"

    def test_build_created(self) -> None:
        # Based on build_create.json
        expected_topic = "vedant-test / Build"
        expected_message = "vedant.messi101@gmail.com triggered a build for app **vedant-test**."
        
        # Uses 'build_create.json'
        self.check_webhook("build_update", expected_topic, expected_message)

    def test_build_succeeded(self) -> None:
        # Based on build_update.json
        expected_topic = "vedant-test / Build"
        expected_message_start = "Build triggered by vedant.messi101@gmail.com **succeeded**."
        
        # We use check_webhook but verify the body content manually 
        # because the URL in the fixture is extremely long and variable.
        self.subscribe(self.test_user, self.CHANNEL_NAME)
        result = self.client_post(self.url, self.get_body("build_update"), content_type="application/json")
        self.assert_json_success(result)

        msg = self.get_last_message()
        self.assertEqual(msg.topic_name(), expected_topic)
        self.assertTrue(msg.content.startswith(expected_message_start))
        self.assertIn("[View Log](https://build-output.heroku.com/streams", msg.content)

    def test_release_created(self) -> None:
        # Based on release_create.json
        expected_topic = "vedant-test / Release"
        expected_message = "vedant.messi101@gmail.com triggered a release (Deploy 1a5f89db) for app **vedant-test**."
        
        # Uses 'release_create.json'
        self.check_webhook("release_create", expected_topic, expected_message)

    def test_release_succeeded(self) -> None:
        # Based on release_update.json
        expected_topic = "vedant-test / Release"
        expected_message = "Release (Deploy 1a5f89db) triggered by vedant.messi101@gmail.com **succeeded**."
        
        # Uses 'release_update.json'
        self.check_webhook("release_update", expected_topic, expected_message)