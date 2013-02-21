import os
import subprocess
from celery import Task
from celery import current_task
from trackertask.tasks import MatlabTask

class GpsOverview(MatlabTask):
    name = 'gps_overview'
    label = "GPS Overview"
    description = """Perform something in a Matlab executable with postgresql query"""
    deploy_script = 'run_gps_overview.sh'

    def run(self, trackers):
            # prepare arguments
            tracker_ids = str([t['id'] for t in trackers])
            # TODO pass tracker_ids as '[1 2]' and in Matlab eval
            # See http://blogs.mathworks.com/loren/2011/01/06/matlab-data-types-as-arguments-to-standalone-applications/
            u = self.db_url
            username = u.username
            password = u.password
            instance = u.database
            jdbc_url = 'jdbc:{drivername}://{host}:{port}/{database}'.format(drivername=u.drivername,
                                                                             host=u.host,
                                                                             port=u.port or 5432,
                                                                             database=u.database)

            # execute
            result = super(GpsOverview, self).run(username,
                                                  password,
                                                  instance,
                                                  jdbc_url,
                                                  tracker_ids
                                                  )

            return result