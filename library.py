import argparse
import logging

parser = argparse.ArgumentParser("library", description="A tool to manage library books and fees")
parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging", dest="verbose")
subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)
commands = {}
commands["start"] = subparsers.add_parser("start", help="Start the camera")
commands["start"].add_argument("--show-fps", action="store_true", help="Show FPS on the screen", dest = "show_fps")
commands["start"].add_argument("--show-landmarks", action="store_true", help="Show hand landmarks on the screen", dest = "show_landmarks")
commands["start"].add_argument("--video-capture", "-vc", help="Video capture to use", dest = "video_capture", default=0)

args = None

if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    if args.command == "start":
        from camera import test
        test.main(args.show_fps, args.show_landmarks, args.video_capture)
