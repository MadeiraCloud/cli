import logging
import json

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils,db



class Stop(Command):
    "stop an Running app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Stop, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='stop_app_local', help='stop local app')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        app_id   = parsed_args.app_id

        #get app data from local db
        (appname,app) = db.get_app_data( app_id )
        if not (appname and app):
            raise RuntimeError('Can not find local app {0}'.format(app_id))

        self.log.debug( '==============================================================' )
        self.log.debug(">found app %s in local db" % appname)
        self.log.debug(">app_data")
        self.log.debug( json.dumps(app, indent=4) )
        self.log.debug( '==============================================================' )

        config = utils.gen_config(appname)
        if parsed_args.stop_app_local:
            self.stop_app(config, appname, app)
            print 'Stopping local app ...'
        else:
            print 'Stopping remote app ...(not support yet)'
            return

        #save app state
        db.stop_app(appname)


    # Stop app
    def stop_app(self, config, appname, app_dict):
        if boot2docker.has():
            config["docker_sock"] = "tcp://%s:2375"%(boot2docker.ip(config,appname))
        for hostname in app_dict.get("hosts",{}):
            for state in app_dict["hosts"][hostname]:
                if state == "linux.docker.deploy":
                    for container in app_dict["hosts"][hostname][state]:
                        if dockervisops.stop(config, container) is True:
                            print "Container %s stopped"%container
                        else:
                            utils.error("Unable to stop container %s"%container)
        if boot2docker.has():
            boot2docker.stop(config, appname)
        print "app %s stopped."%appname

