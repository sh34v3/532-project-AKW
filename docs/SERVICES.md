## docs/SERVICES.md

The entire pipeline is orchestrated in docker compose, with endpoints programmed in Python using Flask.


[![](https://mermaid.ink/img/pako:eNqNkEtr4zAQgP-KmFMX8rBjOw8fFrZxult6a3uq3YOQxo6JLGVHcl8h_72ywaGFFKKD0Iy--WaYAwgjEVIolXkVW06OPWYFFZr58ye_x_8tWmef2Xj8m13nay7l-_PwP8T95_pqT0a2AmlskV5qgb_OctmF3OZn7kyrvuQmv-Pljp_myy7kNhdwAzvkeuBvfqNqvfsGDDkPSO44Ewq5ZlPmiGtbGmq6wn95VltXK3W9uX8cmn7TnCe81KJ2deMvZoUhtJ3u9swct4c-d_QlpeJVhbLfquLeKh6Qk9j-gGvj2JeSqcSXqW6V6lAYQUW1hLTkyuIIGqSGdzEcOk8BbosNFpD6J6Fs3_wSaDcWRhkqoNBHL9hz_WRMA6mj1ivItNX2JGz3fmuY1bwi3pyyhFoirU2rHaRRsAx7C6QHeIN0tkgmURQtw1UQh-FsvoxH8A5pGCeTxSwM4mgez6MwOY7go28bTBZREiSrZbKIPDxfzY6fEaz5Bw?type=png)](https://mermaid.live/edit#pako:eNqNkEtr4zAQgP-KmFMLefiVOvGhsI3T3dJbt6e1exDS2DGRpexI7ivkv69scNhCCtFBaGa--UbMAYSRCBlUyryJLSfHnvOSSs38-VE84d8OrbMvbDq9ZXfFmkv58TLWx3gorq_2ZGQnkKYW6bUReH2Wyy_kNt9zZ0YNLffFI692_PS__EJucwE3smNuAH4W96rRuy_AmPOA5I4zoZBrNmeOuLaVobZv_FXkjXWNUnebp-dx6BfNecJLLWrXtP5iVhhC2-sezvzj4TDkjr6lUryuUQ5bVdxbxW_kJLbf4No49l_LXOLrXHdK9ShMoKZGQlZxZXECLVLL-xgOvacEt8UWS8j8k1B2734JtJsKowyVUOqjF-y5_mNMC5mjzivIdPX2JOz2fmuYN7wm3p6yhFoirU2nHWRxsAwGC2QHeIcsShezOI6X4SpIwjC6WSYT-IAsTJJZGoVBkq6GUhodJ_A5DA5mabwIFqvlIo09frOKjv8AAqP5eA)

 - `caddy` : Caddy is an off the shelf load balancer that will divide incoming requests to our job producers

 - `producer-service`: these replicas maintain a connection to Kafka, plublishing jobs to it if it's healthy.

 - `Kafka`: Kafka mainly functions as a work queue in this pipeline.

 - `Flink`: Flink is the main data processesing pipeline that will clean incoming data, while also applying any transformations necessary to chat logs before passing them to DistillBERT. Flink will also be responsible, ultimately, for classifying conversations as "flagged" or not.

 - `DistillBERT` : sentiment analysis engine trained on GameTox

- `ElasticSearch` : DBMS and pipeline terminas. Flagged chats go into the DBMS so they may be reviewed by a moderator.