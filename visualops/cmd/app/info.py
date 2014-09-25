import logging
import json
from visualops.utils import rpc,utils,db
from cliff.lister import Lister

class Info(Lister):
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
            print json.dumps(app_info, indent=4)
            return (( 'Id', 'Name', 'App Id' ), container_info)

        else:
            print 'Show remote app info....'

            (username, session_id) = utils.load_session()

            # get app info
            (err, result) = rpc.app_info(username, session_id, parsed_args.region_name, [app_id])

            if err:
                raise RuntimeError('get app info failed:( ({0})'.format(err))
            else:
                self.app.stdout.write('get {0} app info succeed!\n'.format(len(result)))

                columns = ('Name',
                           'CloudType',
                           'Provider',
                           'Component',
                           )
                data = (result[0]["name"],
                        result[0]["cloud_type"],
                        result[0]["provider"],
                        len(result[0]["component"]),
                        )
                return (columns, data)
