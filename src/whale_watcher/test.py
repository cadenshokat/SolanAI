import websockets
import asyncio
import json

WEBSOCKET = "wss://mainnet.helius-rpc.com/?api-key=d723896b-6ed8-4afe-a83e-cc8be2a5df93"

async def whale_listener():
    async with websockets.connect(WEBSOCKET) as ws:
        # Prepare a subscription message using programSubscribe
        subscription_message ={
                  "jsonrpc": "2.0",
                  "id": 1,
                  "method": "programSubscribe",
                  "params": [
                    "5quBtoiQqxF9Jv6KYKctB59NT3gtJD2Y65kdnB1Uev3h",
                    {
                      "encoding": "base64",
                      "filters": [
                        {
                          "dataSize": 80
                        }
                      ]
                    }
                  ]
                }
        await ws.send(json.dumps(subscription_message))
        print("Subscription request sent!")

        # Listen for incoming messages indefinitely
        while True:
            try:
                response = await ws.recv()
                data = json.loads(response)
                print("Received message:", data)
            except Exception as e:
                print("Error receiving data:", e)
                break

async def main():
    await whale_listener()

if __name__ == "__main__":
    asyncio.run(main())