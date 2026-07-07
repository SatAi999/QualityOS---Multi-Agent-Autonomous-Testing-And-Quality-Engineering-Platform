import time
import functools
import logging
from typing import Any, Callable, Dict, Optional
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from app.core.config import settings

# Setup standard logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(settings.APP_NAME)

# OpenTelemetry Tracer setup
provider = TracerProvider(resource=Resource.create({"service.name": settings.APP_NAME}))
# For development, export to stdout or local OTLP/Jaeger.
# In production, we'd use OTLPSpanExporter pointing to a collector.
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

def trace_agent_execution(agent_name: str):
    """
    Decorator to wrap LangGraph agent nodes with OTel tracing,
    recording agent metrics, duration, token estimations, and errors.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            with tracer.start_as_current_span(f"Agent:{agent_name}") as span:
                span.set_attribute("agent.name", agent_name)
                start_time = time.time()
                try:
                    logger.info(f"Starting agent: {agent_name}")
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    span.set_attribute("agent.duration_seconds", duration)
                    span.set_status(Status(StatusCode.OK))
                    logger.info(f"Agent {agent_name} finished in {duration:.2f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    span.set_attribute("agent.duration_seconds", duration)
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, description=str(e)))
                    logger.error(f"Agent {agent_name} failed: {str(e)}", exc_info=True)
                    raise e
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            with tracer.start_as_current_span(f"Agent:{agent_name}") as span:
                span.set_attribute("agent.name", agent_name)
                start_time = time.time()
                try:
                    logger.info(f"Starting agent: {agent_name}")
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    span.set_attribute("agent.duration_seconds", duration)
                    span.set_status(Status(StatusCode.OK))
                    logger.info(f"Agent {agent_name} finished in {duration:.2f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    span.set_attribute("agent.duration_seconds", duration)
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, description=str(e)))
                    logger.error(f"Agent {agent_name} failed: {str(e)}", exc_info=True)
                    raise e

        import inspect
        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
    return decorator
