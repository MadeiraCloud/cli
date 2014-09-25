import logging

from cliff.command import Command
from visualops.utils import dockervisops,boot2docker,utils


class Stop(Command):
    "stop an Running app"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Stop, self).get_parser(prog_name)
        parser.add_argument('region_name', nargs='?', default='')
        parser.add_argument('app_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):
        self.app.stdout.write('app stop TO-DO!\n')


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

