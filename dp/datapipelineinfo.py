import ssl
import threading
import logging
from datetime import datetime
import subprocess
import json

class DataPipelineInfo:
    def __init__(self, server, username, password, disable_ssl_check=True):
        # Turn off SSL certificate checking. Bad!
        if disable_ssl_check:
            ssl._create_default_https_context = ssl._create_unverified_context

        self.response_fetched = datetime.min
        self.response_lock = threading.Lock()
        self.response = ""

        self.logger = logging.getLogger("TESTING")
        self.logger.setLevel("DEBUG")
        self.logger.addHandler(logging.StreamHandler())

    def fetch_build_status(self):
        result = []

        pipelines = json.loads(subprocess.check_output("aws datapipeline list-pipelines --region eu-west-1", shell=True))['pipelineIdList']

        for pipeline in pipelines:
          pipeline_id = pipeline['id']
          pipeline_name = pipeline['name']

          runs_count = int(subprocess.check_output("aws datapipeline list-runs --region eu-west-1 --pipeline-id " + pipeline_id + " | wc -l", shell=True))
          tasks = subprocess.check_output("./aws_cli_dp.sh " + pipeline_id, shell=True).replace('\n','').split(',')

          print pipeline_id + " " + pipeline_name + " runs count = " + str(runs_count)

          # Check for runs
          if runs_count > 3:
            for task in tasks:
              task_status = subprocess.check_output("./aws_cli_dp.sh " + pipeline_id + " "+task, shell=True).replace('\n','').split(',')
              print pipeline_id
              print pipeline_name
              print tasks
              print task
              print task_status
              status = task_status[2]

              result.append({
                "group": pipeline_name,
                "pipeline": task,
                "status": status,
                "paused": False
              })

          if runs_count == 0:
            print "Need to check for failed runs as run count is too large"
            failed_runs_count = int(subprocess.check_output("aws datapipeline list-runs --region eu-west-1 --pipeline-id " + pipeline_id + " --status failed | wc -l", shell=True))
            if failed_runs_count > 3:
              result.append({
                "group": pipeline_name,
                "pipeline": "all-tasks",
                "status": "FAILED",
                "paused": False
              })
            if failed_runs_count == 3:
              result.append({
                "group": pipeline_name,
                "pipeline": "all-tasks",
                "status": "FINISHED",
                "paused": False
              })
            if failed_runs_count == 0:
              result.append({
                "group": pipeline_name,
                "pipeline": "all-tasks",
                "status": "UNKNOWN",
                "paused": False
              })

          if runs_count == 3:
              result.append({
                "group": pipeline_name,
                "pipeline": "no-tasks",
                "status": "NEVER RUN",
                "paused": False
              })


        return result

    def get_status(self):
        with self.response_lock:
            if (datetime.utcnow() - self.response_fetched).total_seconds() > 30:
                self.logger.info("Fetching status from Go Server")
                self.response = self.fetch_build_status()
                self.response_fetched = datetime.utcnow()
            else:
                self.logger.info("Returning status from cache")
            return self.response
