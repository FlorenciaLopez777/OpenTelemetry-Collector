# otel_otlp.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import time

provider = TracerProvider()
trace.set_tracer_provider(provider)

# HTTP al collector (receiver http en :4318)
otlp = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
provider.add_span_processor(SimpleSpanProcessor(otlp))

tracer = trace.get_tracer("demo.e-level")

with tracer.start_as_current_span("e-parent") as parent:
    parent.set_attribute("app.user_id", 123)
    with tracer.start_as_current_span("e-child") as child:
        child.set_attribute("work.step", "otlp-export")
        child.add_event("child doing work")
    parent.add_event("parent finishing")

print("Spans sent via OTLP(HTTP) -> Collector")
time.sleep(1)  # da tiempo a que el exporter envíe en CI
