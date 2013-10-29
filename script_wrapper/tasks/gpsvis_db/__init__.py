import os
import subprocess
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
import iso8601
from script_wrapper.tasks import MatlabTask
from script_wrapper.models import make_url

logger = get_task_logger(__name__)


class GpsVisDB(MatlabTask):
    name = 'gpsvis_db'
    label = "GPSvis_database"
    description = """Example script of Willem"""
    script = 'run_stefanoe.sh'

    def run(self, db_url, start, end, alt, trackers):
        # prepare arguments

        # Matlab script expects colortable identifier, so map color to id
        valid_colors = ['FFFF50',
                        'F7E8AA',
                        'FFA550',
                        '5A5AFF',
                        'BEFFFF',
                        '8CFF8C',
                        'FF8CFF',
                        'AADD96',
                        'FFD3AA',
                        'C6C699',
                        'E5BFC6',
                        'DADADA',
                        'C6B5C4',
                        'C1D1BF',
                        '000000'
                        ]
        tracker_ids = []
        speeds = []
        colors = []
        sizes = []
        for tracker in trackers:
            tracker_ids.append(tracker['id'])
            colorid = valid_colors.index(tracker['color']) + 1
            colors.append(colorid)
            sizes.append(tracker['size'])
            speeds.append(tracker['speed'])

        # TODO pass tracker_ids as '[1 2]' and in Matlab eval
        # See http://blogs.mathworks.com/loren/2011/01/06/matlab-data-types-as-arguments-to-standalone-applications/
        self.db_url = u = make_url(db_url)

        db_name = u.database
        if 'sslmode' in u.query and u.query['sslmode'] in ['require', 'verify', 'verify-full']:
            db_name += '?ssl=true&sslfactory=org.postgresql.ssl.NonValidatingFactory'

        # execute
        result = super(GpsVisDB, self).run(u.username,
                                           u.password,
                                           db_name,
                                           u.host,
                                           self.vectorize(tracker_ids),
                                           self.vectorize(colors),
                                           start.isoformat(),
                                           end.isoformat(),
                                           alt,
                                           self.cell_array(sizes),
                                           self.vectorize(speeds),
                                           )

        result['files'].update(self.outputFiles())
        return result

    def vectorize(self, mylist):
        return '[{}]'.format(",".join([str(i) for i in mylist]))

    def cell_array(self, mylist):
        return '{{}}'.format(",".join([str(i) for i in mylist]))

    def formfields2taskargs(self, fields, db_url):
        return {'db_url':  db_url,
                'start': iso8601.parse_date(fields['start']),
                'alt': fields['alt'],
                'end': iso8601.parse_date(fields['end']),
                'trackers': fields['trackers'],
                }
