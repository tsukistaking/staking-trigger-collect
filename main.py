import os
from substrateinterface import SubstrateInterface

import json
from google.auth import jwt
from google.cloud import pubsub_v1

rpc_url = os.environ["RPC_URL"]
gcloud_api_key = os.environ["GCLOUD_API_KEY"]
gcloud_service_json = os.environ["GCLOUD_SERVICE_JSON"]
gcloud_project_id = os.environ["GCLOUD_PROJECT_ID"]
gcloud_pubsub_topic_id = os.environ["GCLOUD_PUBSUB_TOPIC_ID"]

service_account_info = json.loads(gcloud_service_json)
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
credentials = jwt.Credentials.from_service_account_info(service_account_info, audience=audience)
credentials_pub = credentials.with_claims(audience=audience)
publisher = pubsub_v1.PublisherClient(credentials=credentials_pub)
topic_path = publisher.topic_path(gcloud_project_id, gcloud_pubsub_topic_id)


def main():
    substrate_connection = SubstrateInterface(url=rpc_url)
    substrate_connection.rpc_request("chain_subscribeNewHeads", [], result_handler)
    
def result_handler(result):
    if result.get("method", "") == "chain_newHead":
        number = result['params']['result']['number']
        substrate_connection = SubstrateInterface(url=rpc_url)
        block_hash = substrate_connection.get_block_hash(number)
        block_events = substrate_connection.get_runtime_events(block_hash=block_hash).get('result')
        print(int(number, 16), block_hash)
        for block_event in block_events:
            module_id = block_event['module_id']
            event_id = block_event['event_id']
            if module_id == "Staking" and event_id == "EraPayout":
                print(f"{module_id}.{event_id}")
                publisher.publish(topic_path, b' ')

if __name__ == "__main__":
    main()