from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from service import get_tile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

# testing endpoint
@app.get("/")
async def root():
    return {"message": "Hello Snowmap"}

# endpoint to get a tile
@app.get("/tile/{z}/{x}/{y}.png")
async def tile_endpoint(z: int, x: int, y: int):


    """
    calling service method (get_tile) to get a tile in png format

    """
    tile_data = get_tile(z, x, y)
    if tile_data is None:
        raise HTTPException(status_code=404, detail="Tile not found")
    return Response(content=tile_data, media_type="image/png")
