import asyncio

import anthropic
import logfire
import openai
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

# Initialize clients
anthropic_client = anthropic.AsyncAnthropic()
openai_client = openai.AsyncClient()
anthropic_sync_client = anthropic.Anthropic()
openai_sync_client = openai.Client()

# Configure logfire and instrument both clients
logfire.configure()
logfire.instrument_anthropic(anthropic_client)
logfire.instrument_openai(openai_client)
logfire.instrument_anthropic(anthropic_sync_client)
logfire.instrument_openai(openai_sync_client)


async def test_anthropic_streaming():
    console = Console()
    with logfire.span("Testing Anthropic Streaming"):
        response = anthropic_client.messages.stream(
            max_tokens=1000,
            model="claude-3-haiku-20240307",
            system="You are a helpful assistant. Reply in markdown.",
            messages=[{"role": "user", "content": "Say a short sentence."}],
        )
        content = ""
        print("\nAnthropic Streaming Response:")
        with Live("", refresh_per_second=15, console=console) as live:
            async with response as stream:
                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        content += chunk.delta.text
                        live.update(Markdown(content))


async def test_openai_streaming():
    console = Console()
    with logfire.span("Testing OpenAI Streaming"):
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Reply in markdown.",
                },
                {"role": "user", "content": "Say a short sentence."},
            ],
            stream=True,
        )
        content = ""
        print("\nOpenAI Streaming Response:")
        with Live("", refresh_per_second=15, console=console) as live:
            async for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content += chunk.choices[0].delta.content
                    live.update(Markdown(content))


def test_anthropic_sync_streaming():
    console = Console()
    with logfire.span("Testing Anthropic Sync Streaming"):
        with anthropic_sync_client.messages.stream(
            max_tokens=1000,
            model="claude-3-haiku-20240307",
            system="You are a helpful assistant. Reply in markdown.",
            messages=[{"role": "user", "content": "Say a short sentence."}],
        ) as response:
            content = ""
            print("\nAnthropic Sync Streaming Response:")
            for chunk in response:
                if chunk.type == "content_block_delta":
                    print(chunk.delta.text, end="")


def test_openai_sync_streaming():
    console = Console()
    with logfire.span("Testing OpenAI Sync Streaming"):
        response = openai_sync_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Reply in markdown.",
                },
                {"role": "user", "content": "Say a short sentence."},
            ],
            stream=True,
        )
        content = ""
        print("\nOpenAI Sync Streaming Response:")
        with Live("", refresh_per_second=15, console=console) as live:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content += chunk.choices[0].delta.content
                    live.update(Markdown(content))


async def main():
    # Run both async streaming tests
    await test_anthropic_streaming()
    await test_openai_streaming()
    # Run both sync streaming tests
    test_anthropic_sync_streaming()
    test_openai_sync_streaming()


if __name__ == "__main__":
    asyncio.run(main())
