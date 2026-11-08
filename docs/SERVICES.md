## docs/SERVICES.md

The entire pipeline is orchestrated in docker compose, with endpoints programmed in Python using FastAPI.



[![](https://mermaid.ink/img/pako:eNqNkM1O6zAQRl_FmtVFatokbW_TLJCgKfeyYEFhRcLC2NM0wrHL2OGv6rvjBFohVKR6EXnmOz4TewPCSIQUlsq8iBUnx26zQjO_zvIFPjVonb1nQXDKzvMZl_Lt_jPdVV00-7MmIxuBFFik50rgyQEqO4qa_0YdGNIduMgX_OGhclfXX7-WHQvOjwE_0W-tDvmXX6hKP-7zXe1DyR1nQiHXbMAccW2Xhur20P88q6yrlDqfL253I_eKw6kXWtSuqv2HWWEIbau6_DH_ctPVW48vFS9LlN1bKu6N4gY5idUBVBvHvuEDic8D3ShVaOhBSZWEdMmVxR7USDVva9i0lgLcCmssIPVbQtm8-mvTYyCMMlRAobdesOb6zpgaUkeNV5BpytVe2Kz9O2FW8ZJ4ve8Saok0M412kEZJ3Ekg3cArpHE47A_jSTQaJkkUxRMfvkEa_E368TicTsMoCYdxkoy2PXjvxkb9cDSejiehb07a7fYDncLupA?type=png)](https://mermaid.live/edit#pako:eNqNkE2P2jAQhv-KNadWIpAPaEIOlboE2lXVQ-memuzBa09ChGPTsbPdLeK_14SCqopK-GB5_D5-xvYehJEIOdTK_BQbTo49FJVmfnwo1_ijR-vsIwuC9-yuXHApXx9P6bkaosWbHRnZC6TAIj23At9eoYqbqOX_qCtNhgOrcs2fnlr35eufqxW3gstbwBO6Kj_zestPV_xYrlSrt5fwXPtQcseZUMg1mzBHXNvaUHc89KksWutape6W64dzv4vieuqFFrVrOz8xKwyhParu_-l_vx_qg8drxZsG5fCRinuj-IacxOYKqo1jf-ETic8T3StVaRhBQ62EvObK4gg6pI4fa9gfLRW4DXZYQe6XhLJ_8c-mbSCMMlRBpQ9esOP6uzEd5I56ryDTN5uLsN_5f8Ki5Q3x7rJLqCXSwvTaQR6l2SCBfA8vkMdhMk7iNJomWRZFcRqP4BXy4F02jmfhfB5GWZjEWTY9jODX0DYah9PZfJaGaezzJJ7ODr8BiMDtwQ)

 - `caddy` : Caddy is an off the shelf load balancer that will divide incoming requests to our job producers

 - `producer-service`: these replicas maintain a connection to Kafka, plublishing jobs to it if it's healthy.

 - `RabbitMQ`: work queue for the pipeline

 - `Flink`: Flink is the main data processesing pipeline that will clean incoming data, while also applying any transformations necessary to chat logs before passing them to DistillBERT. Flink will also be responsible, ultimately, for classifying conversations as "flagged" or not.

 - `DistillBERT` : sentiment analysis engine trained on GameTox

- `ElasticSearch` : DBMS and pipeline terminas. Flagged chats go into the DBMS so they may be reviewed by a moderator.