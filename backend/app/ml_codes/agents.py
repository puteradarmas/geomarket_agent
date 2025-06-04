from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

gemini_llm = GeminiModel(
    "gemini-2.0-flash",
    provider=GoogleGLAProvider(api_key="AIzaSyCeSFDojYhLttdSUP2wgFkjiTHqrNptXfQ"),
)

gemini_agent: Agent[None, str] = Agent(gemini_llm, output_type=str)

qwen_llm = OpenAIModel(
    model_name="qwen3-4b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)
qwen_agent: Agent[str] = Agent(model=qwen_llm, output_type=str)

qwen_vlm = OpenAIModel(
    model_name="qwen2.5vl:3b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)
qwen_vlm_agent: Agent[None, str] = Agent(model=qwen_vlm, output_type=str)
