# LangSmith Tracing Integration Guide

This documentation explains the comprehensive LangSmith tracing integration for the Inventra AI system.

## 🚀 Quick Setup

### 1. Environment Configuration

Update your `.env` file with LangSmith settings:

```bash
# LangSmith Configuration
LANGSMITH_API_KEY="your_langsmith_api_key_here"
LANGSMITH_PROJECT="inventra-ai"
LANGSMITH_ENVIRONMENT="development"  # or "staging", "production"
LANGSMITH_TRACING=true
```

### 2. Start the Application

The LangSmith tracing is automatically initialized when you start any component:

```bash
# CLI Mode
python main.py cli

# Web Interface
python main.py web

# API Server
python main.py api
```

## 📊 Tracing Coverage

### Multi-Agent Workflow Tracing

The entire LangGraph workflow is traced with detailed visibility:

1. **Main Flow**: `process_query()` - Entry point tracing
2. **Classification Node**: Intent recognition and parsing
3. **Data Gathering Node**: Database queries and data collection
4. **Decision Making Node**: AI-powered business analysis
5. **Response Formatting Node**: Response generation and formatting

### API Endpoint Tracing

- **POST /api/v1/assistant/chat**: Complete request/response cycle
- **Error Handling**: Automatic error capture and context
- **Request Metadata**: User agent, query length, session tracking

### Agent-Level Tracing

- **Inventory Analysis**: Stock status, reorder recommendations
- **Sales Analysis**: Pattern recognition, opportunity identification
- **Financial Analysis**: Profit/loss calculations, margin analysis
- **Vendor Analysis**: Performance optimization, selection criteria

## 🏷️ Tagging Strategy

### Common Tags Applied to All Traces

- `inventra-v1`: Version identifier
- `ai-assistant`: System type
- `env-{environment}`: Environment (dev/staging/prod)
- `multi-agent`: Architecture type

### Component-Specific Tags

- **API**: `api`, `chat`, `production`
- **Workflow**: `workflow`, `langgraph`
- **Nodes**: `node`, `{node_type}`, `ai_analysis`
- **Data**: `data`, `database`, `report`
- **Decision**: `decision`, `ai-analysis`

## 📋 Metadata Tracking

### Automatic Metadata Collection

- **Request Info**: User agent, query length, session ID
- **Processing Info**: Model used, node types, analysis types
- **Performance**: Execution times, data points processed
- **Error Context**: Error types, component information

### Custom Metadata Examples

```python
# Node metadata
metadata = {
    "node_type": "classification",
    "model": "gemini",
    "version": "1.0.0"
}

# Analysis metadata
metadata = {
    "analysis_type": "inventory_needs",
    "ai_powered": True,
    "data_source": "database"
}
```

## 🎯 Usage Examples

### 1. Testing Basic Tracing

```bash
# Start CLI and ask a question
python main.py cli
> "What's my inventory status?"

# Check LangSmith dashboard for traces
```

### 2. API Testing

```bash
# Start API server
python main.py api

# Make a request
curl -X POST "http://localhost:8000/api/v1/assistant/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me sales patterns for the north region"}'
```

### 3. Error Tracing

```bash
# Intentionally trigger an error to see error tracing
curl -X POST "http://localhost:8000/api/v1/assistant/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": ""}'  # Empty query
```

## 🔧 Advanced Configuration

### Environment-Specific Settings

```python
# Development
LANGSMITH_PROJECT="inventra-dev"
LANGSMITH_ENVIRONMENT="development"

# Staging
LANGSMITH_PROJECT="inventra-staging"
LANGSMITH_ENVIRONMENT="staging"

# Production
LANGSMITH_PROJECT="inventra-prod"
LANGSMITH_ENVIRONMENT="production"
```

### Custom Tracing in Your Code

```python
from config.langsmith_setup import enhanced_traceable, trace_error

@enhanced_traceable(
    name="Custom Function",
    tags=["custom", "business_logic"],
    metadata={"version": "1.0.0"}
)
def your_function():
    try:
        # Your business logic
        pass
    except Exception as e:
        trace_error(e, {"context": "custom_function"})
        raise
```

## 📈 Monitoring & Analytics

### Key Metrics to Monitor

1. **Response Times**: End-to-end workflow performance
2. **Error Rates**: Component failure tracking
3. **Usage Patterns**: Popular intents and queries
4. **Data Quality**: Database query performance
5. **AI Performance**: Model accuracy and relevance

### LangSmith Dashboard Views

- **Traces**: Individual request flows
- **Datasets**: Test cases and examples
- **Evaluations**: Model performance metrics
- **Playground**: Query testing and debugging

## 🛠️ Troubleshooting

### Common Issues

1. **No Traces Appearing**
   - Check LANGSMITH_API_KEY is set correctly
   - Verify LANGSMITH_TRACING=true
   - Check network connectivity to LangSmith

2. **Missing Metadata**
   - Ensure enhanced_traceable decorator is used
   - Check function parameters are being passed

3. **Performance Impact**
   - Tracing adds minimal overhead (~5-10ms per trace)
   - Disable in production if needed: LANGSMITH_TRACING=false

### Debug Mode

Set log level to DEBUG to see tracing initialization:

```bash
LOG_LEVEL=DEBUG python main.py api
```

## 🔒 Security & Privacy

- **API Keys**: Store in environment variables, never in code
- **Data Sanitization**: Query content is truncated in error traces
- **PII Handling**: Avoid logging sensitive customer data
- **Access Control**: Use LangSmith's project-based access controls

## 📚 Additional Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangGraph Tracing Guide](https://langchain-ai.github.io/langgraph/how-tos/tracing/)
- [Best Practices for Production Monitoring](https://docs.smith.langchain.com/how_to_guides/monitoring/best_practices)

---

**Next Steps**: After setup, visit your LangSmith dashboard to see real-time traces of your Inventra AI interactions!
