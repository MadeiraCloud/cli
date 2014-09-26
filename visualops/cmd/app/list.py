import logging
from visualops.utils import rpc,utils,db
from cliff.lister import Lister

class List(Lister):
    "List your apps, locally or on AWS"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='list_app_local', help='get local app list')
        parser.add_argument('--filter', action='store', dest='filter_name', nargs='?', default='', help='filter by app name')
        parser.add_argument('--region', action='store', dest='region_name', nargs='?', default='', help='specified region')
        return parser

    def take_action(self, parsed_args):


        if parsed_args.list_app_local:
            print 'List local app....'
            rlt = db.get_app_list()
            return (( 'Name', 'Source Id', 'Region', 'State', 'Create At', 'Change At'), rlt)

        else:
            print 'List remote app....'

            (username, session_id) = utils.load_session()

            # get app list
            (err, result) = rpc.app_list(username, session_id, parsed_args.region_name)

            if err:
                raise RuntimeError('get app list failed:( ({0})'.format(err))
            else:
                self.app.stdout.write('get {0} app list succeed!\n'.format(len(result)))
                return (('Id', 'Name', 'Region', 'State'),
                    ((app["id"], app["name"], app["region"], app["state"]) for app in result if (parsed_args.filter_name.lower() in app['name'].lower() and app["state"] in ["Running"]) )
                )
