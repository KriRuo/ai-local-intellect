
import { Post } from './store';

// Changed from localhost:8000 to use relative path
const API_BASE_URL = '/api';

export async function fetchPosts(): Promise<Post[]> {
  try {
    // First attempt to fetch from the API
    const response = await fetch(`${API_BASE_URL}/posts`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch posts: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching posts:', error);
    
    // Return mock data as fallback when API fails
    return [
      {
        id: "1",
        title: "OpenAI Releases GPT-5 with Enhanced Reasoning Capabilities",
        summary: "The latest iteration of GPT focuses on logical reasoning and mathematical problem solving, addressing previous limitations in complex cognitive tasks.",
        tags: ["OpenAI", "GPT-5", "AI Models"],
        source: "OpenAI Blog",
        published_at: new Date().toISOString(),
        url: "https://example.com/openai-gpt5",
      },
      {
        id: "2",
        title: "Google DeepMind's Breakthrough in Protein Folding Accelerates Drug Discovery",
        summary: "New advancements in AlphaFold technology have made protein structure prediction even more accurate, potentially reducing drug development timelines by years.",
        tags: ["Google DeepMind", "AlphaFold", "Protein Folding", "Drug Discovery"],
        source: "Google AI Blog",
        published_at: new Date(Date.now() - 86400000).toISOString(),
        url: "https://example.com/deepmind-protein",
      },
      {
        id: "3",
        title: "Meta's LLAMA 3 Goes Open Source",
        summary: "Meta has released their latest large language model to the public, allowing researchers and companies to build on top of their work with fewer restrictions.",
        tags: ["Meta", "LLAMA 3", "Open Source", "LLM"],
        source: "Meta AI",
        published_at: new Date(Date.now() - 172800000).toISOString(),
        url: "https://example.com/meta-llama3",
      },
      {
        id: "4",
        title: "New Benchmark Shows Anthropic Claude 3 Outperforming GPT-4 on Complex Reasoning Tasks",
        summary: "Recent evaluations suggest Claude 3 has superior performance in areas requiring nuanced understanding of context and multi-step reasoning problems.",
        tags: ["Anthropic", "Claude 3", "Benchmarks", "AI Comparison"],
        source: "Anthropic Research",
        published_at: new Date(Date.now() - 259200000).toISOString(),
        url: "https://example.com/claude3-benchmark",
      },
      {
        id: "5",
        title: "AI Safety Researchers Propose New Framework for Model Evaluation",
        summary: "A coalition of AI safety organizations has published guidelines for evaluating large language models before deployment, emphasizing transparency and risk assessment.",
        tags: ["AI Safety", "Evaluation", "Research", "Guidelines"],
        source: "AI Safety Center",
        published_at: new Date(Date.now() - 345600000).toISOString(),
        url: "https://example.com/ai-safety-framework",
      }
    ];
  }
}

export async function sendChatMessage(message: string): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: message }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to send chat message: ${response.status}`);
    }
    
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error sending chat message:', error);
    return "I'm currently offline. Please try again later when I'm connected to the server.";
  }
}
