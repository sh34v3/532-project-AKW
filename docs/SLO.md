## docs/SLO.md

This document contains latency and reliability SLOs for any service with handwired endpoints. 


### `producer-service` : should be optimized for ingestion speed

- the `submit-job` endpoint should target $p99 < 15ms$. We anticipate many requests coming in constantly, so we'll need to ingest those requests and push them to Kafka as quickly as possible.
- the `submit-job` endpoint should succeed $99\%$ of the time. Failed incoming requests can be retried, and healthchecks can be used to avoid loadbalancing requests to downed replicas.


### `DistillBERT-service`

- the `get-score` endpoint should target $p99 < 25ms$
- the `get-score` endpoint should succeed $99\%$ of the time.