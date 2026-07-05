#!/usr/bin/env python3
"""Test script for LangSmith tracing integration."""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.langsmith_setup import initialize_langsmith, enhanced_traceable, trace_error
from config.logger import get_logger
from agents.coordinator import process_query

logger = get_logger(__name__)


@enhanced_traceable(
    name="LangSmith Integration Test",
    tags=["test", "validation", "integration"],
    metadata={"test_type": "langsmith_validation", "version": "1.0.0"},
)
def test_langsmith_integration():
    """Test LangSmith integration with sample queries."""

    test_queries = [
        "What's my current inventory status?",
        "Show me sales patterns for the north region",
        "Generate a financial summary",
        "What are the pending tickets?",
        "Hello, how can you help me?",
    ]

    results = []

    print("🧪 Testing LangSmith Integration...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}/5: {query}")

        try:
            start_time = time.time()
            response = process_query(query, session_id=f"test-session-{i}")
            duration = time.time() - start_time

            # Truncate long responses for display
            display_response = (
                (response[:100] + "...") if len(response) > 100 else response
            )

            print(f"✅ Response: {display_response}")
            print(f"⏱️  Duration: {duration:.2f}s\n")

            results.append(
                {
                    "query": query,
                    "success": True,
                    "duration": duration,
                    "response_length": len(response),
                }
            )

        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
            trace_error(e, {"test_query": query, "test_number": i})
            results.append({"query": query, "success": False, "error": str(e)})

    return results


def print_test_summary(results):
    """Print test execution summary."""
    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print("=" * 70)
    print("  LANGSMITH INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"Tests completed: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")

    if successful == total:
        print("🎉 All tests passed! LangSmith tracing is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above and your configuration.")

    print("\n📊 Performance Summary:")
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        avg_duration = sum(r["duration"] for r in successful_results) / len(
            successful_results
        )
        avg_length = sum(r["response_length"] for r in successful_results) / len(
            successful_results
        )
        print(f"Average response time: {avg_duration:.2f}s")
        print(f"Average response length: {avg_length:.0f} characters")


def check_environment():
    """Check if LangSmith environment is properly configured."""
    print("🔍 Checking Environment Configuration...\n")

    try:
        from config.settings import get_settings

        settings = get_settings()

        # Check required settings
        missing_vars = []

        if not settings.gemini_api_key:
            missing_vars.append("GEMINI_API_KEY")
            print(f"❌ GEMINI_API_KEY: Not set")
        else:
            value = settings.gemini_api_key
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ GEMINI_API_KEY: {masked_value}")

        if not settings.langsmith_api_key:
            missing_vars.append("LANGSMITH_API_KEY")
            print(f"❌ LANGSMITH_API_KEY: Not set")
        else:
            value = settings.langsmith_api_key
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ LANGSMITH_API_KEY: {masked_value}")

        print("\n📝 Configuration:")
        print(f"   LANGSMITH_PROJECT: {settings.langsmith_project}")
        print(f"   LANGSMITH_ENVIRONMENT: {settings.langsmith_environment}")
        print(f"   LANGSMITH_TRACING: {settings.langsmith_tracing}")
        print(f"   LANGSMITH_ENDPOINT: {settings.langsmith_endpoint}")

        if missing_vars:
            print(f"\n⚠️  Missing required settings: {', '.join(missing_vars)}")
            print("Please check your .env file configuration.")
            return False

        print("\n✅ Configuration looks good!")
        return True

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False


def main():
    """Main test execution."""
    print("🚀 Inventra LangSmith Integration Test\n")

    # Check environment first
    if not check_environment():
        sys.exit(1)

    # Initialize LangSmith
    print("\n🔧 Initializing LangSmith...")
    client = initialize_langsmith()

    if not client:
        print("❌ Failed to initialize LangSmith. Check your configuration.")
        sys.exit(1)

    print("✅ LangSmith initialized successfully!")
    print("🌐 You can view traces at: https://smith.langchain.com")

    # Run tests
    print("\n" + "=" * 50)
    results = test_langsmith_integration()

    # Print summary
    print_test_summary(results)

    print("\n📋 Next Steps:")
    print("1. Check your LangSmith dashboard for detailed traces")
    print("2. Look for the 'inventra-ai' project in LangSmith")
    print("3. Explore individual trace details and metadata")
    print("4. Test with your own queries using the CLI or API")

    print(
        f"\n🔗 Direct link: https://smith.langchain.com/projects?projectName=inventra-ai"
    )


if __name__ == "__main__":
    main()
