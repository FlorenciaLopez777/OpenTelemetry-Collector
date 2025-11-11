from fastapi import FastAPI
import time, random

# --- OpenTelemetry setup ---
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Identify this service
resource = Resource.create({"service.name": "fastapi-otel-demo"})

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Send traces to Collector (running on port 4317)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# --- FastAPI setup ---
app = FastAPI()

# Attach automatic instrumentation
FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

tracer = trace.get_tracer(__name__)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/work/{id}")
def work(id: int):
    with tracer.start_as_current_span("business_logic") as span:
        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)
        span.set_attribute("item_id", id)
        span.set_attribute("processing_time_ms", round(delay * 1000))
    return {"item": id, "processing_time_ms": round(delay * 1000)}
