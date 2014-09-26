import logging
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
            (app_info, container_info) = db.get_app_info( app_id )

            if len(app_info) == 0:
                print 'Can not found local app %s ' % app_id
                return ((),())

            #format and output app info
            title  = ['Name','Source Id','Region','State','Create At','Change At']
            header = ['Field','Value']
            app_info = [ title, list(app_info) ] #insert title
            app_info = map(list, zip(*app_info))    #matrix transpose
            print utils.print_prettytable(header, app_info)

            if len(container_info) ==0:
                print 'No container'
                return ((),())

            #output container info
            return (( 'Id', 'Name', 'App Id' ), container_info)

        else:
            print 'Show remote app info....'

            (username, session_id) = utils.load_session()

            # get app info
            (err, result) = rpc.app_info(username, session_id, None, [app_id])

            if err:
                raise RuntimeError('get app info failed:( ({0})'.format(err))
            else:
                self.log.debug('>Get {0} app(s) info'.format(len(result)))

                if len(result) == 0:
                    return (),()

                app_json = result[0]

                del app_json['layout']
                del app_json['property']

                instance_with_state    = 0
                instance_without_state = 0
                for (uid,comp) in app_json['component'].items():
                    if unicode(comp['type']) == constant.RESTYPE['INSTANCE']:

                        log_str = '>Found instance {0}'.format(comp['name'])

                        if comp['state']:
                            log_str+=': has %s state(s)' % len(comp['state'])
                            instance_with_state+=1
                        else:
                            log_str+=': has no state'
                            instance_without_state+=1

                        self.log.debug(log_str)

                print "App Info:"
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
