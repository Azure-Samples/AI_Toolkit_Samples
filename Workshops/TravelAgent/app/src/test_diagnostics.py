#!/usr/bin/env python
"""
Voyager — Tool Diagnostic Script

Helps diagnose issues with tool registration and agent framework compatibility.
"""

import sys
import asyncio

print("\n" + "="*70)
print("Voyager — Tool Diagnostics")
print("="*70 + "\n")

# Check Python version
print(f"✓ Python: {sys.version.split()[0]}")

# Check agent_framework
try:
    import agent_framework
    print(f"✓ agent_framework: {getattr(agent_framework, '__version__', 'installed')}")
    
    # Check for key exports
    from agent_framework import kernel_function
    print(f"✓ kernel_function: available")
    
    from agent_framework import KernelPlugin
    print(f"✓ KernelPlugin: available")
    
    from agent_framework import MCPStdioTool
    print(f"✓ MCPStdioTool: available")
    
    from agent_framework.openai import OpenAIChatClient
    print(f"✓ OpenAIChatClient: available")
    
except ImportError as e:
    print(f"✗ agent_framework: {e}")
    sys.exit(1)

# Check FastAPI
try:
    import fastapi
    print(f"✓ fastapi: {fastapi.__version__}")
except ImportError:
    print(f"✗ fastapi: not installed")

# Check other deps
try:
    from openai import AsyncOpenAI
    print(f"✓ openai: available")
except ImportError:
    print(f"✗ openai: not installed")

try:
    import uvicorn
    print(f"✓ uvicorn: available")
except ImportError:
    print(f"✗ uvicorn: not installed")

# Check GITHUB_TOKEN
import os
if os.environ.get("GITHUB_TOKEN"):
    token = os.environ["GITHUB_TOKEN"]
    masked = token[:7] + "*" * (len(token) - 10) + token[-3:]
    print(f"✓ GITHUB_TOKEN: {masked}")
else:
    print(f"✗ GITHUB_TOKEN: not set (required for agent to run)")

print(f"\n{'='*70}")
print("Testing TravelInlineTools...")
print(f"{'='*70}\n")

# Test inline tools
from travel_agent import TravelInlineTools

tool_instance = TravelInlineTools()
print(f"✓ TravelInlineTools instance created: {tool_instance}")

# Check for kernel_function methods
methods = [m for m in dir(tool_instance) if not m.startswith('_')]
print(f"\nPublic methods:")
for method_name in methods:
    method = getattr(tool_instance, method_name)
    is_callable = callable(method)
    is_tool = method_name in ['calculate_trip_budget', 'check_visa_requirements', 'convert_currency']
    marker = "✓" if is_tool else " "
    print(f"  {marker} {method_name}: callable={is_callable}, is_tool={is_tool}")

print(f"\n{'='*70}")
print("Testing tool creation...")
print(f"{'='*70}\n")

from travel_agent import create_inline_tools, create_mcp_tools

try:
    inline_tools = create_inline_tools()
    print(f"✓ create_inline_tools(): {inline_tools}")
    for i, tool in enumerate(inline_tools):
        print(f"  [{i}] {type(tool).__name__}: {tool}")
except Exception as e:
    print(f"✗ create_inline_tools(): {e}")
    import traceback
    traceback.print_exc()

try:
    mcp_tools = create_mcp_tools()
    print(f"✓ create_mcp_tools(): {len(mcp_tools)} tools")
    for i, tool in enumerate(mcp_tools):
        print(f"  [{i}] {type(tool).__name__}: {tool}")
except Exception as e:
    print(f"✗ create_mcp_tools(): {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*70}")
print("Testing quick agent (convert currency only)...")
print(f"{'='*70}\n")

async def test_agent():
    """Run a quick agent test."""
    try:
        from openai import AsyncOpenAI
        from agent_framework.openai import OpenAIChatClient
        from travel_agent import AGENT_INSTRUCTIONS, MODEL_ID
        
        # Use a simplified prompt to test
        api_key = os.environ.get("GITHUB_TOKEN")
        if not api_key:
            print("✗ GITHUB_TOKEN not set - cannot test agent")
            return
            
        test_client = AsyncOpenAI(
            base_url="https://models.github.ai/inference",
            api_key=api_key,
            default_query={"api-version": "2024-08-01-preview"},
        )
        
        inline_tools = create_inline_tools()
        mcp_tools = create_mcp_tools()
        all_tools = [*inline_tools, *mcp_tools]
        
        print(f"Creating agent with {len(all_tools)} tools...")
        print(f"  - {len(inline_tools)} inline tools")
        print(f"  - {len(mcp_tools)} MCP tool servers")
        
        async with (
            OpenAIChatClient(
                async_client=test_client,
                model_id=MODEL_ID,
            ).create_agent(
                instructions="You are a currency converter. Convert 100 USD to EUR.",
                temperature=1,
                top_p=1,
                tools=all_tools,
            ) as agent
        ):
            print(f"\n✓ Agent created successfully!")
            print(f"  Testing with simple prompt...")
            
            text_parts = []
            tool_calls = []
            async for chunk in agent.run_stream(["Convert 100 USD to EUR"]):
                if chunk.text:
                    text_parts.append(chunk.text)
                from agent_framework import FunctionCallContent
                for content in chunk.contents:
                    if isinstance(content, FunctionCallContent):
                        tool_calls.append(content.name)
            
            response = "".join(text_parts)
            print(f"\n✓ Agent responded successfully!")
            print(f"  Response length: {len(response)} chars")
            print(f"  Tool calls: {tool_calls if tool_calls else 'none'}")
            print(f"\n  First 200 chars of response:")
            print(f"  {response[:200]}...")
            
    except Exception as e:
        print(f"✗ Agent test failed: {e}")
        import traceback
        traceback.print_exc()

if os.environ.get("GITHUB_TOKEN"):
    asyncio.run(test_agent())
else:
    print("⚠ Skipping agent test (GITHUB_TOKEN not set)")

print(f"\n{'='*70}")
print("Diagnostics Complete")
print(f"{'='*70}\n")
