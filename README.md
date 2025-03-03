# Snowmap Submission

FastAPI server that serves GeoTIFF tiles

### Setup & Usage

**Prerequisites**

List any dependencies, software, or libraries required.

```
# Software:
Docker # (if you want to run everything in containers)
Python 3.9+
Node.js + npm
Redis
pip


# Dependencies:
1. Concurrently # Easier to run the backend and frontend simultaneously
2. Fastapi # Backend framework given that it is within the Python ecosystem
3. rasterio # Handling tiff files reading and retrieval
4. mercantile # Handling coordinates conversion
5. pillow # Handleing image type conversion
6. numpy
7. redis
```

**Installation**

Step-by-step guide on how to install and set up the project. (Only doing this for the first time)

```
git clone https://github.com/PoliteVincent/snowmap.git
# base - installing concurrently for later running
npm install

# Frontend
cd mapbox
npm install

# Backend - make sure to get back to project root using `cd ..`
# You only need to do this if you want to test my backend server locally
# Else you can skip to `Running the server` section

cd backend
pip install -r requirements.txt
```

**Running the Server**

Instructions to start and test the Slippy Map Server.

```
# If you want to test my backend server locally:
docker-compose up --build
curl http://localhost:5000/tile/8/48/96.png --output test_tile.png

# If you want to test as a whole, simply go back to the project root
npm run dev

```

Once started:

- The frontend typically runs on **`http://localhost:3000`**.
- The backend runs on **`http://localhost:5000`**.

**Troubleshooting**

1. Missing Redis: I strongly recommend using `docker-compose up` to run the backend even if you can also do `uvicorn main:app --host 0.0.0.0 --port 5000`. I intergrate the Redis and a early exit check if no redis client detected. Thus, if not having Redis running (at the specified port), the FastAPI server will fail.
2. CORS: This is unlikely to happen as I have explicitly specified it. But if things indeed happened (hopefully not), please go check `backend/main.py` where the `CORSMiddleware` is declared.
3. Token issue: The original `README.md` file does not mention about this point, however, I did encounter a 403 forbidden error when first testing with the frontend. I came to realize that it was due to the permission unmatched with the provided access_token. I went ahead replace it with my own. If you come with the same 403 error, please try to change the access_token to see if it will work.
4. Missing Tiff file. Notice that the tiff file should be stored inside the `backend/data/`, double check if it is appeared.
