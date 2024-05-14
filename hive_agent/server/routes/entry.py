import dateutil

from fastapi import APIRouter, HTTPException, Request, WebSocket, status


def setup_entry_routes(router: APIRouter, store):

    @router.post("/entry/{namespace}")
    async def create_entry(namespace: str, request: Request):
        data = await request.json()
        new_entry = await store.add(namespace, data)

        return {
            "status": "entry created",
            "data": {
                "namespace": namespace,
                "entry_id": new_entry.id
            }
        }

    @router.websocket("/entry/{namespace}/stream")
    async def stream_entry(websocket: WebSocket, namespace: str):
        await websocket.accept()

        try:
            while True:
                data = await websocket.receive_json()

                try:
                    new_entry = await store.add(namespace, data)
                    await websocket.send_json({
                        "status": "entry created",
                        "data": {
                            "namespace": namespace,
                            "entry_id": new_entry.id
                        }
                    })

                except Exception as e:
                    await websocket.send_json({"error": str(e)})

        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            await websocket.close()

    @router.get("/entry/{namespace}")
    async def get_entries(namespace: str):
        data_entries = await store.get(namespace)
        entries = [entry.to_dict() for entry in data_entries]

        return {
            "status": "entries retrieved successfully",
            "data": {
                "namespace": namespace,
                "entries": entries
            }
        }

    @router.get("/entry/{namespace}/{entry_id}")
    async def get_entry_by_id(namespace: str, entry_id: str):
        entry = await store.get_by_id(namespace, entry_id)

        if entry:
            return {
                "status": "entry retrieved successfully",
                "data": {
                    "namespace": namespace,
                    "entry": entry
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requested data entry not found",
            )

    @router.put("/entry/{namespace}/{entry_id}")
    async def update_entry(namespace: str, entry_id: str, request: Request):
        new_data = await request.json()
        if 'timestamp' in new_data and isinstance(new_data['timestamp'], str):
            new_data['timestamp'] = dateutil.parser.parse(new_data['timestamp'])

        await store.update(namespace, entry_id, new_data)

        return {
            "status": "entry updated",
            "data": {
                "namespace": namespace,
                "entry_id": entry_id
            }
        }

    @router.delete("/entry/{namespace}/{entry_id}")
    async def delete_entry(namespace: str, entry_id: str):
        await store.delete(namespace, entry_id)

        return {
            "status": "entry removed"
        }
