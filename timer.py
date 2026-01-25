#!/usr/bin/env python3

# type into terminal: python3 timer.py 8m

import argparse
import re
import subprocess
import sys
import time

def parse_time(time_str):
    """
    Parses a time string in formats like '1h30m10s', '90m', '180s', '1h'
    and returns the total duration in seconds.
    """
    # Regex to capture hours (h), minutes (m), and seconds (s)
    # Makes each part optional but requires at least one part
    match = re.match(r'^((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?$', time_str)

    if not match or not match.group(0): # Check if match is None or the matched string is empty
        raise ValueError(f"Invalid time format: '{time_str}'. Use formats like '1h30m', '90m', '180s'.")

    time_parts = match.groupdict()
    total_seconds = 0

    # Get integer value or 0 if the part is not present
    hours = int(time_parts.get('hours') or 0)
    minutes = int(time_parts.get('minutes') or 0)
    seconds = int(time_parts.get('seconds') or 0)

    # Calculate total seconds
    total_seconds += hours * 3600
    total_seconds += minutes * 60
    total_seconds += seconds

    if total_seconds <= 0:
        # Ensure at least one time component was provided and resulted in a positive duration
        if not hours and not minutes and not seconds:
             raise ValueError(f"Invalid time format: '{time_str}'. No time units (h, m, s) found.")
        raise ValueError("Total duration must be positive.")


    return total_seconds

def countdown(seconds):
    """Counts down from the specified number of seconds."""
    end_time = time.time() + seconds
    print(f"Timer set for {seconds} seconds.")

    try:
        while True:
            remaining = round(end_time - time.time())
            if remaining <= 0:
                print("\nTime's up!")
                break

            # Format remaining time (optional, for display)
            hours_rem = remaining // 3600
            mins_rem = (remaining % 3600) // 60
            secs_rem = remaining % 60
            time_str = f"{hours_rem:02d}:{mins_rem:02d}:{secs_rem:02d}"

            # Print remaining time, overwriting the previous line
            print(f"Time remaining: {time_str}", end='\r') # '\r' moves cursor to beginning of line
            sys.stdout.flush() # Ensure the output is displayed immediately

            # Sleep for a short interval to avoid busy-waiting
            # Use min to handle the last second accurately
            time.sleep(min(1, remaining))

    except KeyboardInterrupt:
        print("\nTimer cancelled by user.")
        sys.exit(0) # Exit gracefully if Ctrl+C is pressed

def play_sound_macos(repeat_count=10):
    """
    Plays the 'Ping' system sound on macOS repeat_count times using afplay.
    """
    # Set the sound file to Ping.aiff
    sound_file = '/System/Library/Sounds/Ping.aiff'
    print(f"Playing sound '{sound_file}' {repeat_count} times.")

    # Loop to play the sound multiple times
    for i in range(repeat_count):
        try:
            # Run the afplay command and wait for it to complete
            # capture_output=True prevents afplay's own messages from printing
            result = subprocess.run(['afplay', sound_file], check=True, capture_output=True)
            # Optional: Add a small delay between plays if needed
            # time.sleep(0.1) # e.g., 0.1 second delay
        except FileNotFoundError:
            print("Error: 'afplay' command not found. Is this a macOS system?")
            break # Stop trying if afplay is not found
        except subprocess.CalledProcessError as e:
            # This error occurs if afplay returns a non-zero exit code
            print(f"Error playing sound (iteration {i+1}): {e}")
            print(f"Stderr: {e.stderr.decode().strip()}")
            # Decide if you want to stop or continue on error
            break # Stop playing if one fails
        except KeyboardInterrupt:
             # Allow interruption during the sound loop
             print("\nSound playback interrupted by user.")
             sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred during sound playback (iteration {i+1}): {e}")
            break # Stop on unexpected errors

    print("Finished playing sound.")


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="A simple command-line timer for macOS.")
    parser.add_argument("duration", help="Duration for the timer (e.g., '1h30m', '90m', '180s', '2h')")

    # Parse arguments
    args = parser.parse_args()

    try:
        # Parse the time string provided by the user
        total_seconds = parse_time(args.duration)

        # Start the countdown
        countdown(total_seconds)

        # Play the 'Ping' sound 10 times when countdown finishes
        play_sound_macos(repeat_count=10)

    except ValueError as e:
        print(f"Error: {e}")
        parser.print_usage() # Show how to use the script correctly
        sys.exit(1) # Exit with an error code
    except KeyboardInterrupt:
        # Catch KeyboardInterrupt here as well in case it happens
        # exactly between countdown() ending and play_sound_macos() starting,
        # or during argument parsing/initial setup.
        print("\nTimer script interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
