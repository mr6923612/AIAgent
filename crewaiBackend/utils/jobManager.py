# Core functions:
# (1) Manage multiple jobs and their status, ensure thread safety through lock mechanism.
# (2) Define the structure of jobs and events, and provide a function to append events, while initializing new job instances when jobs start.


# Import Python standard library
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
from threading import Lock


# Create a lock to protect the jobs dictionary, ensuring safety during multi-threaded operations
jobs_lock = Lock()
# A dictionary to store Job instances with job_id as key
jobs: Dict[str, "Job"] = {}



# Use @dataclass to define an Event class, representing the structure of an event
# timestamp: Time when the event occurred
# data: Data related to the event
@dataclass
class Event:
    timestamp: datetime
    data: str


# Use @dataclass to define a Job class, representing the structure of a job
# status: Represents the status of the job (e.g., "STARTED", "COMPLETE", etc.)
# events: A list containing events related to this job
# result: Result after job completion
@dataclass
class Job:
    status: str
    events: List[Event]
    result: str


# Define function append_event, accepting job_id and event data event_data as parameters
def append_event(job_id: str, event_data: str):
    # Use context manager with to ensure code execution during lock period, avoiding multi-thread conflicts
    with jobs_lock:
        # Check if job_id exists in jobs dictionary
        # If not exists, create a new Job instance, set its status to STARTED, initialize event list as empty, result as empty string
        if job_id not in jobs:
            print("Job %s started", job_id)
            jobs[job_id] = Job(
                status='STARTED',
                events=[],
                result='')
        else:
            # If job_id already exists, print information indicating appending event for this job
            print("Appending event for job %s: %s", job_id, event_data)

        # Create a new Event instance, record current time and event data, then append it to the event list of the corresponding Job instance
        jobs[job_id].events.append(
            Event(timestamp=datetime.now(), data=event_data))
