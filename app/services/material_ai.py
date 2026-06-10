import hashlib
import json
import os
import time

import requests
from loguru import logger

from app.config import config
from app.utils import utils


def _cache_path(prompt_obj: dict, cfg: dict) -> str:
    key = (
        cfg.get("image_model", "fal-ai/flux-2-pro")
        + json.dumps(prompt_obj, sort_keys=True)
        + str(cfg.get("image_seed", 0))
    )
    h = hashlib.sha256(key.encode()).hexdigest()[:16]
    cache_dir = cfg.get("image_cache_dir", "storage/ai_cache")
    cache_dir = os.path.join(utils.root_dir(), cache_dir)
    ext = cfg.get("output_format", "png")
    return os.path.join(cache_dir, f"{h}.{ext}")


def generate_image(prompt_obj: dict, cfg: dict) -> str:
    """Generate one image from a Flux JSON prompt, return local path. Cached."""
    path = _cache_path(prompt_obj, cfg)
    if os.path.exists(path):
        logger.info(f"image cache hit: {path}")
        return path

    try:
        import fal_client
    except ImportError as exc:
        raise ImportError(
            "fal-client is not installed. Run: pip install fal-client"
        ) from exc

    fal_key = cfg.get("fal_api_key", "")
    if fal_key:
        os.environ["FAL_KEY"] = fal_key

    model = cfg.get("image_model", "fal-ai/flux-2-pro")
    max_retries = int(cfg.get("image_retry_max", 3))

    last_err = None
    for attempt in range(max_retries):
        try:
            result = fal_client.subscribe(
                model,
                arguments={
                    "prompt": json.dumps(prompt_obj),
                    "image_size": cfg.get("image_size", "portrait_16_9"),
                    "seed": cfg.get("image_seed", 0),
                    "safety_tolerance": cfg.get("safety_tolerance", "3"),
                    "output_format": cfg.get("output_format", "png"),
                },
                with_logs=True,
            )
            url = result["images"][0]["url"]
            img_data = requests.get(url, timeout=60).content
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(img_data)
            logger.success(f"image generated: {path}")
            return path
        except Exception as e:
            last_err = e
            logger.warning(f"image generation attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)

    raise RuntimeError(
        f"image generation failed after {max_retries} retries: {last_err}"
    )


def generate_scene_images(prompts: list[dict], cfg: dict) -> list[str]:
    """One image per scene prompt object, aligned 1:1 with prompts."""
    return [generate_image(p, cfg) for p in prompts]


def generate_fallback_card(width: int, height: int, output_path: str) -> str:
    """Create a brand-colored fallback card (deep navy with green accent)."""
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise ImportError("PIL is required for fallback cards") from exc

    img = Image.new("RGB", (width, height), "#0A1628")
    draw = ImageDraw.Draw(img)
    bar_height = max(int(height * 0.02), 4)
    draw.rectangle([0, height - bar_height, width, height], fill="#34D88A")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path)
    logger.info(f"fallback card created: {output_path}")
    return output_path
