"""Day 1: detect and track vehicles in a video using YOLOv8.
Usage: python detect.py --source ../dataset/sample.mp4
"""
import argparse
import os
from collections import defaultdict

import cv2
from ultralytics import YOLO

# COCO class ids: 2=car, 3=motorcycle, 5=bus, 7=truck
VEHICLE_CLASSES = [2, 3, 5, 7]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="video file path")
    p.add_argument("--model", default="yolov8n.pt")
    p.add_argument("--conf", type=float, default=0.4)
    p.add_argument("--out", default="outputs/annotated.mp4")
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    model = YOLO(args.model)

    cap = cv2.VideoCapture(args.source)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    writer = cv2.VideoWriter(args.out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    seen = defaultdict(set)  # class name -> set of track ids

    for r in model.track(source=args.source, persist=True, stream=True,
                         classes=VEHICLE_CLASSES, conf=args.conf, verbose=False):
        if r.boxes is not None and r.boxes.id is not None:
            for cls, tid in zip(r.boxes.cls.int().tolist(), r.boxes.id.int().tolist()):
                seen[model.names[cls]].add(tid)
        writer.write(r.plot())

    writer.release()
    print("\nUnique vehicles tracked:")
    for name, ids in seen.items():
        print(f"  {name}: {len(ids)}")
    print(f"Annotated video saved to {args.out}")


if __name__ == "__main__":
    main()
