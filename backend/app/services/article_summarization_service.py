from backend.app.services.lm_studio_client import LMStudioClient
from backend.app.db.models import Post

class ArticleSummarizationService:
    def __init__(self, lm_client: LMStudioClient):
        self.lm_client = lm_client

    async def summarize_article(self, post: Post):
        prompt = (
            "You are given a list of recent AI-related articles."
            "Read through them as a whole and extract the most important overarching trends, themes, or" 
            "insights."
            "Do not summarize each article individually—combine the information to generate a single unified list of key takeaways."
            "Article 1:\n"
            "Source: {post.source}\n"
            "URL: {post.url}\n"
            "Publish Date: {post.timestamp}\n"
            "Title: {post.title}\n"
            "Content: {post.content}\n"
            "Author: {post.author}\n"
            "Article 2:\n"
            "Source: ...\n"
            "...\n"
        )
        system_prompt = (
            "You are an expert analyst tracking AI and tech news."
            "Based on this list, generate one summary of the data based on the instructions below:"
            "- Group related articles into themes"
            "- Provide a bullet list of the **most important updates**"
            "- Identify any **emerging trends or patterns**"
            "- End with a short executive summary (3 sentences max)"
            "- Reference claims where possible with source and URLs"
            "Output format:"
            "## Themes"
            "- Theme Name: summary and which articles relate"
            "[...]"
            "## Key Updates"
            "- Bullet list of top news"
            "[...]"
            "## Executive Summary"
            "- 3 sentences max"
        )
        return await self.lm_client.generate_response(prompt, system_prompt) 
    