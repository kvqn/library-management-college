#!/bin/python
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

commands["register-student"] = subparsers.add_parser("register-student", help="Register a student")
commands["register-student"].add_argument("id", help="Student ID", type=int)
commands["register-student"].add_argument("name", help="Student name")
commands["register-student"].add_argument("phone", help="Student phone number")
commands["register-student"].add_argument("branch", help="Student branch")
commands["register-student"].add_argument("semester", help="Student semester", type=int)
commands["register-student"].add_argument("email", help="Student email")


args = None

if __name__ == "__main__":
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    if args.command == "start":
        from camera import vision
        vision.main(args.show_fps, args.show_landmarks, args.video_capture)
    elif args.command == "register-student":
        from db import student
        s = student.Student(args.id, args.name, args.phone, args.branch, args.semester, args.email)
        student.CreateTableIfNotExist()
        student.InsertIntoDatabase(s)
