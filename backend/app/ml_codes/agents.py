from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app import envs

gemini_llm = GeminiModel(
    "gemini-2.0-flash",
    provider=GoogleGLAProvider(api_key=envs.GEMINI_API_KEY),
)

gemini_agent: Agent[None, str] = Agent(gemini_llm, output_type=str, retries=3)

qwen_llm = OpenAIModel(
    model_name=envs.LLM_NAME,
    provider=OpenAIProvider(base_url=envs.LLM_BASE_URL),
)
qwen_agent: Agent[str] = Agent(model=qwen_llm, output_type=str, retries=3)

qwen_vlm = OpenAIModel(
    model_name=envs.VLM_NAME,
    provider=OpenAIProvider(base_url=envs.VLM_BASE_URL),
)
qwen_vlm_agent: Agent[None, str] = Agent(model=qwen_vlm, output_type=str, retries=3)
