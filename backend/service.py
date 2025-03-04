from typing import Optional
from fastapi import HTTPException
import redis
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from io import BytesIO
from PIL import Image
import numpy as np
import mercantile
import time
import logging

logging.basicConfig(
    # debug level for dev
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# redis connection
try:
    r = redis.Redis(host='redis', port=6379, db=0)
except Exception as e:
    logger.error(f"Error: {e}, please make sure the redis server is running")
    exit(1)

try:
    dataset = rasterio.open("data/snowdepth.tiff")
except Exception as e:
    logger.error(f"Error: {e}, please make sure the tiff file is presented in the \"/data\" folder")
    exit(1)



# test debug case
logger.debug(f"Dataset: {dataset.bounds}")
# This dataset is:
# georeferenced using coordinate reference system (CRS) EPSG:4326
# - Longitude: roughly from the Pacific coast to the East Coast
# - Latitude: roughly from the mexico to canada.
# - Make sure the testing z, x, y values are within this range



def get_tile(z: int, x: int, y:int) -> Optional[bytes]:
    """
    Two cases
    1. return png file from cache directly
    2. generate new png file from tiff file
    params:
    x, y, z: tile coordinates
    return:
    png image or None

    """
    start = time.time()
    # Case 1
    cache_key = f"{z}:{x}:{y}"
    if r.exists(cache_key):

        end = time.time()
        logger.debug(f"time taken{end-start}")
        logger.info(f"Cache hit for {cache_key}")

        return r.get(cache_key)


    # Case 2
    try:
        bounds = mercantile.bounds(x, y, z)
        # For debug purpose
        logger.debug(f"Bounds: {bounds}")

        if dataset.crs != "EPSG:4326":
            logger.debug(f"Converting from EPSG:4326 to {dataset.crs}")
            bounds = transform_bounds("EPSG:4326", dataset.crs, *bounds)

        window = from_bounds(*bounds, transform=dataset.transform)
        if window.width <= 0 or window.height <= 0:
            logger.error("Given tile coordinates are out of the dataset bounds")
            raise HTTPException(status_code=404, detail="Tile out of bounds")
        
        data = dataset.read(window=window)

        # helper function see below
        img = numpy_to_png(data)
        end = time.time()
        logger.debug(f"time taken{end-start}")

        r.setex(cache_key, 3600, img)

        return img
    
    except Exception as e:
        logger.error(f"Error: {e} on tile {z}:{x}:{y}")
        return None

def numpy_to_png(data: np.ndarray) -> bytes:
    """
    Helper function to convert numpy array to png image

    params:
    data: numpy array
    return:
    png image
    """
    # 3 or more for colored image, else for grayscale
    if data.shape[0] >= 3:
        img_data = data[:3].transpose((1, 2, 0))
        img: Image = Image.fromarray(img_data)
    else:
        img: Image = Image.fromarray(data[0], mode='L')

    # Can also use Nearest for faster processing or bicubic for better quality
    img = img.resize((256, 256), Image.BILINEAR)
    # if the service requires a smaller image, use LANCZOS

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


