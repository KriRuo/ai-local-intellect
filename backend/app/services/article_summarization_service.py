from backend.app.services.lm_studio_client import LMStudioClient
from backend.app.db.models import Post

class ArticleSummarizationService:
    def __init__(self, lm_client: LMStudioClient):
        self.lm_client = lm_client

    async def summarize_article(self, post: Post):
        prompt = (
            f"Source: {post.source}\n"
            f"URL: {post.url}\n"
            f"Publish Date: {post.timestamp}\n"
            f"Title: {post.title}\n"
            f"Content: {post.content}\n"
            f"Author: {post.author}"
        )
        system_prompt = (
            "Summarize the following article in a concise paragraph, focusing on the main points and key information. "
            "Respond with only the summary."
        )
        return await self.lm_client.generate_response(prompt, system_prompt) 