# RSS Feeds JSON Format

> For backend setup, running instructions, and API usage, see `backend/README.md`.

This file documents the structure and usage of `rss_feeds.json`, which contains scraped RSS feed posts in a format matching the backend and frontend `Post` interface.

## Input
- This file is not meant to be edited by hand for normal operation. It is generated by the backend scraper or can be used as a mock/fallback data source.
- Each entry in the `posts` array represents a single RSS feed post.

## Output Structure
Each post object should have the following fields:

| Field       | Type    | Required | Description                                      |
|-------------|---------|----------|--------------------------------------------------|
| id          | number  | Yes      | Unique identifier for the post                   |
| source      | string  | Yes      | Name of the source (e.g., 'OpenAI Blog')         |
| platform    | string  | Yes      | Platform type (e.g., 'Blog', 'RSS')              |
| url         | string  | Yes      | URL of the post                                  |
| title       | string  | No       | Title of the post                                |
| content     | string  | Yes      | Main content of the post                         |
| summary     | string  | No       | Short summary of the post                        |
| timestamp   | string  | Yes      | ISO 8601 datetime string of publication          |
| thumbnail   | string  | No       | URL to a thumbnail image                         |
| author      | string  | No       | Author of the post                               |
| created_at  | string  | Yes      | ISO 8601 datetime string when post was created   |
| updated_at  | string  | No       | ISO 8601 datetime string when post was updated   |

## Example

```
{
  "posts": [
    {
      "id": 1,
      "source": "OpenAI Blog",
      "platform": "Blog",
      "url": "https://openai.com/blog/gpt-5-release",
      "title": "OpenAI Releases GPT-5 with Enhanced Reasoning Capabilities",
      "content": "The latest iteration of GPT focuses on logical reasoning and mathematical problem solving, addressing previous limitations in complex cognitive tasks.",
      "summary": "The latest iteration of GPT focuses on logical reasoning and mathematical problem solving, addressing previous limitations in complex cognitive tasks.",
      "timestamp": "2024-06-01T10:00:00Z",
      "thumbnail": "https://placehold.co/64x64?text=OpenAI",
      "author": "OpenAI Team",
      "created_at": "2024-06-01T10:00:00Z",
      "updated_at": null
    }
  ]
}
```

## Usage
- The backend can use this file as a mock or backup data source for posts.
- The frontend expects this structure when rendering posts in the feed. 