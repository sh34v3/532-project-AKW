
import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import exec from 'k6/execution';

const conversations = new SharedArray(
  'conversations',
  () => JSON.parse(open('./conversations.json'))
);

const url = __ENV.TARGET_URL || 'http://localhost:8080/submit_job';
const delaySeconds = Number(__ENV.MESSAGE_DELAY_MS || 0) / 1000;

export const options = {
  scenarios: {
    chat_messages: {
      executor: 'shared-iterations',
      vus: Number(__ENV.VUS || 10),
      iterations: conversations.length,
      maxDuration: __ENV.MAX_DURATION || '30m',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const conversation = conversations[exec.scenario.iterationInTest];

  for (const message of conversation.messages) {
    const payload = {
      'from-user': message['from-user'],
      'to-user': message['to-user'],
      'times-stamp': new Date().toISOString(),
      message: message.message,
    };

    const response = http.post(url, JSON.stringify(payload), {
      headers: {
        'Content-Type': 'application/json',
      },
      tags: {
        endpoint: 'submit_job',
      },
    });

    check(response, {
      'POST accepted': (r) => r.status === 200,
    });

    if (response.status !== 200) {
      console.error(
        `HTTP ${response.status} sending ${conversation.conversation_id}`
      );
    }

    if (delaySeconds > 0) {
      sleep(delaySeconds);
    }
  }
}