"""
Chat Service - Handles AI model interactions
"""

from typing import List, Dict, Any, AsyncGenerator
import os
import json


class ChatService:
    def __init__(self, db):
        self.db = db
    
    async def get_chat_response(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = None,
        api_keys: Dict[str, str] | None = None
    ) -> str:
        """Get chat response from AI model"""
        
        api_keys = api_keys or {}

        # Determine provider based on model name
        if model.startswith("gpt-") or model.startswith("o1"):
            return await self._openai_chat(messages, model, temperature, max_tokens, api_keys.get("openai"))
        elif model.startswith("claude-"):
            return await self._anthropic_chat(messages, model, temperature, max_tokens, api_keys.get("anthropic"))
        elif model.startswith("gemini-"):
            return await self._google_chat(messages, model, temperature, max_tokens, api_keys.get("google"))
        else:
            # Default to OpenAI
            return await self._openai_chat(messages, model, temperature, max_tokens, api_keys.get("openai"))
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
        api_key: str | None
    ) -> str:
        """OpenAI chat"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _anthropic_chat(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
        api_key: str | None
    ) -> str:
        """Anthropic Claude chat"""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            
            # Convert messages format
            system_message = ""
            claude_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    claude_messages.append(msg)
            
            create_kwargs: Dict[str, Any] = {
                "model": model,
                "system": system_message,
                "messages": claude_messages,
                "max_tokens": max_tokens or 4096,
            }

            # Some Anthropic models no longer accept `temperature`.
            if temperature is not None:
                create_kwargs["temperature"] = temperature

            try:
                response = await client.messages.create(**create_kwargs)
            except Exception as e:
                message = str(e).lower()
                if "temperature" in message and "deprecat" in message:
                    create_kwargs.pop("temperature", None)
                    response = await client.messages.create(**create_kwargs)
                else:
                    raise
            
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _google_chat(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
        api_key: str | None
    ) -> str:
        """Google Gemini chat"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
            
            # Convert messages format
            contents = []
            for msg in messages:
                contents.append(f"{msg['role']}: {msg['content']}")
            
            model_obj = genai.GenerativeModel(model)
            response = model_obj.generate_content(
                "\n".join(contents),
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
            
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def get_streaming_response(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
        api_keys: Dict[str, str] | None = None
    ) -> AsyncGenerator[str, None]:
        """Get streaming chat response"""

        api_keys = api_keys or {}
        
        if model.startswith("gpt-") or model.startswith("o1"):
            async for chunk in self._openai_stream(messages, model, temperature, max_tokens, api_keys.get("openai")):
                yield chunk
        elif model.startswith("claude-"):
            async for chunk in self._anthropic_stream(messages, model, temperature, max_tokens, api_keys.get("anthropic")):
                yield chunk
        else:
            async for chunk in self._openai_stream(messages, model, temperature, max_tokens, api_keys.get("openai")):
                yield chunk
    
    async def _openai_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
        api_key: str | None
    ) -> AsyncGenerator[str, None]:
        """OpenAI streaming chat"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"
    
    async def _anthropic_stream(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
        api_key: str | None
    ) -> AsyncGenerator[str, None]:
        """Anthropic streaming chat"""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            
            system_message = ""
            claude_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    claude_messages.append(msg)
            
            stream_kwargs: Dict[str, Any] = {
                "model": model,
                "system": system_message,
                "messages": claude_messages,
                "max_tokens": max_tokens or 4096,
            }

            if temperature is not None:
                stream_kwargs["temperature"] = temperature

            try:
                async with client.messages.stream(**stream_kwargs) as stream:
                    async for text in stream.text_stream:
                        yield text
            except Exception as e:
                message = str(e).lower()
                if "temperature" in message and "deprecat" in message:
                    stream_kwargs.pop("temperature", None)
                    async with client.messages.stream(**stream_kwargs) as stream:
                        async for text in stream.text_stream:
                            yield text
                else:
                    raise
        except Exception as e:
            yield f"Error: {str(e)}"
