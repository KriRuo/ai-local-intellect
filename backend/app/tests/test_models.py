import unittest
from backend.app.db.models import Post

class TestPostModel(unittest.TestCase):
    """Unit tests for the Post model methods.
    These tests verify the correct serialization and deserialization of tags,
    ensuring that the Post model's tag handling is robust and consistent.
    """

    def test_get_tags_empty(self):
        """
        Test that get_tags returns an empty list when:
        - tags is None (never set)
        - tags is an empty string (set to "")
        This ensures the method is robust to both uninitialized and empty tag fields.
        """
        post = Post(tags=None)
        self.assertEqual(post.get_tags(), [])  # Should handle None gracefully
        post = Post(tags="")
        self.assertEqual(post.get_tags(), [])  # Should handle empty string gracefully

    def test_set_and_get_tags(self):
        """
        Test that set_tags serializes a list of tags to a JSON string,
        and get_tags deserializes it back to the same list.
        This ensures round-trip integrity for tag storage and retrieval.
        """
        post = Post()
        tags = ["AI", "NLP", "Test"]
        post.set_tags(tags)
        self.assertEqual(post.get_tags(), tags)  # Should match the original list

    def test_set_tags_empty(self):
        """
        Test that set_tags([]) stores an empty JSON array ("[]") in the tags field,
        and get_tags returns an empty list.
        This ensures that clearing tags is handled consistently and does not store None or "".
        """
        post = Post()
        post.set_tags([])
        self.assertEqual(post.tags, "[]")  # Should store as JSON empty array
        self.assertEqual(post.get_tags(), [])  # Should return empty list

if __name__ == "__main__":
    unittest.main() 