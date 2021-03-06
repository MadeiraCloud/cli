# Copyright 2014 MadeiraCloud LTD.

import logging
import json
import base64
from visualops.utils import rpc,utils,db,constant
#from cliff.lister import Lister
from cliff.show import ShowOne

class Info(ShowOne):
    "Show summary information for specified app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Info, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='info_app_local', help='get local app info')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        app_id = parsed_args.app_id

        if parsed_args.info_app_local:
            print 'Show local app info ....'
            (app_info, app_data, container_info) = db.get_app_info( app_id )

            #1. format and output app info
            if not app_info or len(app_info) == 0:
                print "Can not found local app info '%s' " % app_id
                return ((),())
            title  = ['Name','Source Id','Region','State','Create At','Change At']
            header = ['Field','Value']
            app_info = [ title, list(app_info) ] #insert title
            app_info = map(list, zip(*app_info))    #matrix transpose
            print '\nApp info:'
            print utils.print_prettytable(header, app_info)

            #2. format and output app data
            if not app_data or len(app_data) == 0:
                print "Can not found local app data '%s' " % app_id
                return ((),())
            print '\nApp data:'
            print json.dumps(utils.str2dict(base64.b64decode(app_data[0])), indent=4)


            #3. output container info
            if not container_info or len(container_info) ==0:
                print 'No container'
                return ((),())
            print '\nContainer:'
            return (( 'Id', 'Name', 'App Id' ), container_info)

        else:
            print 'Show remote app info....'

            (username, session_id) = utils.load_session()
            if not(username and session_id):
                return (),()

            (project_name, project_id, key_id) = utils.load_current_project()
            if not key_id:
                return (),()

            # get app info
            (err, result) = rpc.app_info(username, session_id, key_id, None, [app_id])

            if err:
                print('Get app info failed')
                utils.hanlde_error(err,result)
            else:
                self.log.debug('> get {0} app(s) info'.format(len(result)))

                if len(result) == 0:
                    return (),()

                app_json = result[0]

                del app_json['layout']
                del app_json['property']

                instance_with_state    = 0
                instance_without_state = 0
                for (uid,comp) in app_json['component'].items():
                    if unicode(comp['type']) == constant.RESTYPE['INSTANCE']:

                        log_str = '> found instance {0}'.format(comp['name'])

                        if comp['state']:
                            log_str+=': has %s state(s)' % len(comp['state'])
                            instance_with_state+=1
                        else:
                            log_str+=': has no state'
                            instance_without_state+=1

                        self.log.debug(log_str)

                print "App Info in %s(%s):" % (project_name,project_id)
                columns = ( 'Id',
                            'Name',
                            'Region',
                            'Version',
                            'Module Tag',
                            'Component',
                            'Instance Total',
                            'Instance With State',
                            'Instance Without State',
                           )
                data = (
                        result[0]['id'],
                        result[0]['name'],
                        result[0]['region'],
                        result[0]['version'],
                        result[0]['agent']['module']['tag'],
                        len(result[0]['component']),
                        instance_with_state+instance_without_state,
                        instance_with_state,
                        instance_without_state,
                        )
                return (columns, data)
