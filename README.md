# 532-project-AKW

### Team name: modBERT

### Team Roster

| Email                | GitHub Username |
| :------------------- | :-------------- |
| jkaros@umass.edu     | sh34v3          |
| _____                | _______         |

### Project Documentation

- [Refined Project Description](docs/PROJECT.md)
- [Initial Service List](docs/SERVICES.md)
- [Service Level Objectives](docs/SLO.md)

MMORPGs ubiquitously come with accompanying chat features for players to communicate both in communal chat rooms and private ones. These chat rooms are typically moderated, although the volume of the chat logs are far too high to be done by humans alone. Instead, the logs are put through a pipeline that flags windows of logs for malicious–bullying, harassment, or threatening–behavior. 

This project aims to construct an orchestrated pipeline of services that is capable of ingesting a stream of 1-on-1 chat logs between players, window the logs based on conversation, enrich and format the logs for classification by an ML model, tag conversations with sentiment scores by said model, then record those conversations in a searchable DBMS.

The entire system will be orchestrated by Docker Compose, with service instances for each component of the pipeline: requests will be load balanced using Caddy to producer replicas which then push the jobs to Kafka as the work queue, Flink will consume jobs as the stream processor, DistillBERT will be used as the sentiment analyzer trained on the GameTox dataset, and Elastic Search will be used as the DBMS that Flink writes to when it classifies a chat as flagged.

The GameTox dataset will also be used to synthetically generate our testing data. This will be done by concatenating 3-5 random statements from the dataset to form a "conversation" before being sent to the pipeline.