from terra_sdk.client.lcd import LCDClient
from time import sleep
import requests
from dotenv import load_dotenv
import os

network = 'columbus-5'
networkRPC = "https://lcd.terra.dev"
pushURL = "https://push.techulus.com"

load_dotenv("credentials.env")
pushAPIKey = os.environ.get("API_key")
bot_address = os.environ.get("bot_address")

ANC_LIQ_QUE_CONTRACT = "terra1e25zllgag7j9xsun3me4stnye2pcg66234je3u"
BLUNA_CONTRACT = "terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp"

terra = LCDClient(networkRPC, network)

def getBidInfo(ID):
    bidInfo = terra.wasm.contract_query(ANC_LIQ_QUE_CONTRACT, {"bid": {"bid_idx": ID}})
    return bidInfo

def getBidsByUser(address):
    msg = {
    "bids_by_user": {
        "collateral_token": BLUNA_CONTRACT,
        "bidder": address, 
        "start_after": "123", 
        "limit": 30 
  }
}
    bidsByUser = terra.wasm.contract_query(ANC_LIQ_QUE_CONTRACT, msg)
    IDs = []
    for bid in bidsByUser["bids"]:
        IDs.append(bid["idx"])
    return IDs

if __name__ == "__main__":
    while True:
        bid_ids = getBidsByUser(bot_address)
        for bid in bid_ids:
                info = getBidInfo(bid)
                if not info["pending_liquidated_collateral"] == "0":
                    #notify that bid is filled
                    notificationString = f"Bid {info['idx']} filled for {int(info['pending_liquidated_collateral']) * 1000000} bLuna"
                    header = {"Content-type": "application/json"}
                    body = {
                        "title": "Liquidation bid filled!",
                        "body": notificationString
                        }
                    print("notified")
                    requests.post(f"{pushURL}/api/v1/notify/{pushAPIKey}", headers=header, json=body)

        sleep(1)
    