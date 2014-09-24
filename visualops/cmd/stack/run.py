import logging
import os
import yaml
import json
from cliff.command import Command


class Run(Command):
    "Deploy the stack locally, or in the cloud"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        parser.add_argument('-l', '--local', action='store_true', dest='run_stack_local', help='deploy the stack locally')
        parser.add_argument('stack_id', nargs='?', default='')
        return parser

    def take_action(self, parsed_args):

        stack_id = parsed_args.stack_id

        stack_file = os.path.join(os.getcwd(), '%s.yaml' % stack_id)
        if not os.path.isfile(stack_file):
            print( '%s is not exist, please pull stack first!' % stack_file )
            return

        if parsed_args.run_stack_local:
            print 'Deploying %s.yaml ......' % stack_id
        else:
            print 'Deploying %s.yaml to remote (not support yet, please try -l)....' % stack_id
            return

        try:
            self.log.debug( ">Load data from %s" % stack_file )
            stream = open(stack_file, 'r')
            app = yaml.load(stream)
        except Exception:
            raise RuntimeError('Load yaml error!')

        if not app:
            raise RuntimeError('stack json is invalid!')

        self.log.debug( '==============================================================' )
        self.log.debug( json.dumps(app, indent=4) )
        self.log.debug( '==============================================================' )


        print 'TO-DO'

