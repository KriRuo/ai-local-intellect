import logging

logger = logging.getLogger(__name__)

class ArticleBatchSummarizationService:
    def __init__(self, fetch_service, summarization_service, storage_service):
        self.fetch_service = fetch_service
        self.summarization_service = summarization_service
        self.storage_service = storage_service

    async def summarize_articles(self, sources, start_date, end_date):
        logger.info("Called summarize_articles (per-article)")
        summaries = []
        for source in sources:
            posts = self.fetch_service.fetch_articles(source, start_date, end_date)
            for post in posts:
                summary = await self.summarization_service.summarize_article(post)
                self.storage_service.store_summary(post.id, summary)
                summaries.append({"post_id": post.id, "source": source, "summary": summary})
        return summaries

    async def summarize_articles_combined(self, sources, start_date, end_date):
        logger.info("Called summarize_articles_combined")
        # Gather all posts from all sources in the date range
        all_posts = []
        for source in sources:
            posts = self.fetch_service.fetch_articles(source, start_date, end_date)
            all_posts.extend(posts)
        if not all_posts:
            return "No articles found for the given sources and date range."

        # Build a prompt listing all articles
        prompt_lines = []
        for idx, post in enumerate(all_posts, 1):
            prompt_lines.append(f"Article {idx}:")
            prompt_lines.append(f"Source: {getattr(post, 'source', '')}")
            prompt_lines.append(f"URL: {getattr(post, 'url', '')}")
            prompt_lines.append(f"Publish Date: {getattr(post, 'timestamp', '')}")
            prompt_lines.append(f"Title: {getattr(post, 'title', '')}")
            prompt_lines.append(f"Content: {getattr(post, 'content', '')}")
            prompt_lines.append(f"Author: {getattr(post, 'author', '')}")
            prompt_lines.append("")
        prompt = "\n".join(prompt_lines)

        logger.info(f"Combined prompt: {prompt}")

        # Use the same system prompt as in ArticleSummarizationService
        system_prompt = (
            "You are an expert analyst tracking AI and tech news."
            " Read through them as a whole and extract the most important"
            " overarching trends, themes, or insights."
            " Do not summarize each article individually—"
            "combine the information to generate a single unified list of key takeaways.:"
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
        return await self.summarization_service.lm_client.generate_response(prompt, system_prompt)
    