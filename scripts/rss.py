#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch RSS feed from Google Apps Script URL and output JSON to stdout.
Downloads images to <output_dir>/images/ and rewrites image URLs to local paths.
Used by GitHub Actions to update docs/rss.json and docs/images for Pages deploy.
"""

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from html import unescape

import requests

RSS_URL = "https://script.google.com/macros/s/AKfycbxKygdEFZRz5BFzFOP52e-HkgLry-B6qrtNEcZvMXkF8CRzHGbpWCbQ6n5y6VD7dHB8/exec"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"


def text_or_empty(node):
    if node is None:
        return ""
    return (node.text or "").strip()


def download_image(url, images_dir, save_filename, image_index=0, timeout=30):
    """Download image from url to images_dir. save_filename: basename from RSS file element.
    Follows redirects (e.g. Google Drive shared URLs)."""
    try:
        save_filename = os.path.basename(save_filename).strip()
        save_filename = re.sub(r"[^\w.\-]", "_", save_filename) or f"file_{image_index}"
        path = os.path.join(images_dir, save_filename)
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })
        r = session.get(
            url,
            timeout=timeout,
            stream=True,
            allow_redirects=True,
        )
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return path
    except Exception:
        return None


def parse_item(item, out_dir=None, image_index=None):
    title_el = item.find("title")
    title = text_or_empty(title_el) if title_el is not None else ""

    desc_el = item.find("description")
    description = text_or_empty(desc_el) if desc_el is not None else ""

    duration_el = item.find("duration")
    duration_str = text_or_empty(duration_el) if duration_el is not None else "15"
    try:
        duration = int(duration_str)
    except ValueError:
        duration = 15
    duration = max(1, min(300, duration))  # clamp 1–300 seconds

    image_el = item.find("image")
    image_url = text_or_empty(image_el) if image_el is not None else ""

    file_el = item.find("file")
    file_name = text_or_empty(file_el) if file_el is not None else None

    content_encoded = item.find(f"{{{CONTENT_NS}}}encoded")
    content = ""
    if content_encoded is not None and content_encoded.text:
        content = unescape((content_encoded.text or "").strip())

    image = image_url
    if out_dir and image_url and file_name and image_index is not None:
        images_dir = os.path.join(out_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        path = download_image(
            image_url, images_dir, save_filename=file_name, image_index=image_index
        )
        if path:
            image = os.path.join("images", os.path.basename(path))

    return {
        "title": title,
        "description": description,
        "content": content,
        "duration": duration,
        "image": image,
        "file": file_name,
    }


def main():
    out_dir = (sys.argv[1] if len(sys.argv) > 1 else "docs").strip() or None

    r = requests.get(RSS_URL, timeout=30)
    r.raise_for_status()
    root = ET.fromstring(r.content)

    channel = root.find("channel")
    if channel is None:
        channel = root

    items = []
    image_counter = 0
    for item in channel.findall("item"):
        parsed = parse_item(item, out_dir, image_index=image_counter if out_dir else None)
        if out_dir and parsed.get("file"):
            image_counter += 1
        items.append(parsed)

    # Remove images in docs/images/ that are no longer referenced by the current feed
    if out_dir:
        images_dir = os.path.join(out_dir, "images")
        used_basenames = {
            os.path.basename(item["image"])
            for item in items
            if (item.get("image") or "").startswith("images/")
        }
        if os.path.isdir(images_dir):
            for name in os.listdir(images_dir):
                if name not in used_basenames:
                    path = os.path.join(images_dir, name)
                    if os.path.isfile(path):
                        try:
                            os.remove(path)
                        except OSError:
                            pass

    out = {"items": items}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
