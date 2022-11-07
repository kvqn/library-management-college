#!/bin/python
import argparse
import logging
import db

parser = argparse.ArgumentParser("library", description="A tool to manage library books and fees")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging", dest="verbose")
parser.add_argument("--user", help="MariaDB User", dest="user", default="root")
parser.add_argument("--password", help="MariaDB Password", dest="password", default="root")
parser.add_argument("--database", help="MariaDB Database", dest="database", default="library")
parser.add_argument("--server", help="MariaDB Server", dest="server", default="localhost")
subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)
commands = {}

commands["start"] = subparsers.add_parser("start", help="Start the camera")
commands["start"].add_argument("--show-fps", action="store_true", help="Show FPS on the screen", dest = "show_fps")
commands["start"].add_argument("--show-landmarks", action="store_true", help="Show hand landmarks on the screen", dest = "show_landmarks")
commands["start"].add_argument("--video-capture", "-vc", help="Video capture to use", dest = "video_capture", default=0)
commands["start"].add_argument("--n-processes", "-np", help="Number of processes to use", dest = "n_processes", default=4, type=int)

commands["version"] = subparsers.add_parser("version", help="Print version")

args = None

if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        db.CreateConnection(args.user, args.password, args.database, args.server)
    except Exception as e:
        logging.error("Failed to connect to database")
        raise e
    
    if args.command == "version":
        with open("version", 'r') as file:
            version = file.read()
        print(f"Library Management System v{version}")
    elif args.command == "start":
        from camera import vision
        vision.main(args.show_fps, args.show_landmarks, args.video_capture, args.n_processes)
