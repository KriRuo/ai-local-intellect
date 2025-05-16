import httpx

class LMStudioClient:
    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1"):
        self.base_url = base_url
        self.model = "deepseek-r1-distill-qwen-7b"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def generate_summary(self, text: str, max_tokens: int = 150) -> str:
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that creates concise summaries. Focus on the main points and key information."
                        },
                        {
                            "role": "user",
                            "content": f"Please summarize the following text in {max_tokens} tokens or less:\n\n{text}"
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": max_tokens,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    async def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": -1,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    async def close(self):
        await self.client.aclose() 