import os
import subprocess
from celery import Task
from celery import current_task
from celery.utils.log import get_task_logger
import iso8601
from script_wrapper.tasks import MatlabTask
from script_wrapper.models import make_url
from script_wrapper.models import getGPSCount
from script_wrapper.validation import validateRange

logger = get_task_logger(__name__)


class GpsVisDB(MatlabTask):
    name = 'gpsvis_db'
    label = "kmz-statplot"
    description = """kmz and statistics plot"""
    script = 'run_stefanoe.sh'
    matlab_version = '2009b'

    def run(self, db_url, start, end, alt, trackers):
        # prepare arguments

        tracker_ids = []
        speeds = []
        colors = []
        sizes = []
        for tracker in trackers:
            tracker_ids.append(tracker['id'])
            colors.append(tracker['color'])
            sizes.append(tracker['size'])
            speeds.append(tracker['speed'])

        # TODO pass tracker_ids as '[1 2]' and in Matlab eval
        # See http://blogs.mathworks.com/loren/2011/01/06/matlab-data-types-as-arguments-to-standalone-applications/
        db_url = make_url(db_url)
        db_name = self.sslify_dbname(db_url)

        # execute
        result = super(GpsVisDB, self).run(db_url.username,
                                           db_url.password,
                                           db_name,
                                           db_url.host,
                                           self.list2vector_string(tracker_ids),
                                           self.list2vector_string(colors),
                                           start.isoformat(),
                                           end.isoformat(),
                                           alt,
                                           self.list2cell_array_string(sizes),
                                           self.list2vector_string(speeds),
                                           )

        result['query'] = {'start': start,
                           'end':end,
                           'alt': alt,
                           'trackers': trackers,
                           }

        return result

    def convert_colors(self, tracker):
        """Matlab script expects colortable identifier, so map color to id"""
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
        colorid = valid_colors.index(tracker['color']) + 1
        return colorid

    def formfields2taskargs(self, fields, db_url):
        start = iso8601.parse_date(fields['start'])
        end = iso8601.parse_date(fields['end'])
        trackers = fields['trackers']
        for tracker in trackers:
            validateRange(getGPSCount(db_url, tracker['id'], start, end), 0, 50000)
            tracker['color'] = self.convert_colors(tracker)

        return {'db_url':  db_url,
                'start': start,
                'alt': fields['alt'],
                'end': end,
                'trackers': trackers,
                }
