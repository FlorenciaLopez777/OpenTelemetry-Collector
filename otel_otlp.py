from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
trace.set_tracer_provider(provider)

otlp = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp))

tracer = trace.get_tracer("demo.e-level")

with tracer.start_as_current_span("e-parent") as parent:
    parent.set_attribute("app.user_id", 123)
    with tracer.start_as_current_span("e-child") as child:
        child.set_attribute("work.step", "otlp-export")
        child.add_event("child doing work")
    parent.add_event("parent finishing")

print("Spans sent via OTLP -> Collector")
