class ArticleBatchSummarizationService:
    def __init__(self, fetch_service, summarization_service, storage_service):
        self.fetch_service = fetch_service
        self.summarization_service = summarization_service
        self.storage_service = storage_service

    async def summarize_articles(self, sources, start_date, end_date):
        summaries = []
        for source in sources:
            posts = self.fetch_service.fetch_articles(source, start_date, end_date)
            for post in posts:
                summary = await self.summarization_service.summarize_article(post)
                self.storage_service.store_summary(post.id, summary)
                summaries.append({"post_id": post.id, "source": source, "summary": summary})
        return summaries 