import os
import asyncio
from openai import AsyncOpenAI

class OpenAIClient:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        api_key = os.getenv("ChatGPT_API_KEY") or os.getenv("VITE_ChatGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        org_id = os.getenv("OPENAI_ORG_ID")
        project_id = os.getenv("OPENAI_PROJECT_ID")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = AsyncOpenAI(api_key=api_key, organization=org_id, project=project_id)
        self.model = model

    async def generate_summary(self, text: str, max_tokens: int = 150) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries. Focus on the main points and key information."},
                    {"role": "user", "content": f"Please summarize the following text in {max_tokens} tokens or less:\n\n{text}"}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    async def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    async def close(self):
        # No explicit close needed for openai.AsyncOpenAI, but keep for interface compatibility
        pass 