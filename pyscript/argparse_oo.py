import os
import sys
import argparse


def Args(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator

class ClientShell(object):
    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='client',
            epilog='See "client help COMMAND" '
                   'for help on a specific command.',
            description=(__doc__ or '').strip(),
            add_help=False,
        )

        parser.add_argument('-h', '--help',
            action='store_true',
            help=argparse.SUPPRESS,
        )
        
        parser.add_argument('--os_username', metavar='<auth-user-name>',
            default=os.environ.get('OS_USERNAME', ''),
            help='Default to env[OS_USERNAME',
        )

        parser.add_argument('--os_password', metavar='<auth-user-password>',
            default=os.environ.get('OS_PASSWORD', ''),
            help='Default to env[OS_PASSWORD',
        )

        return parser

    def get_subcommand_parser(self):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        action_model = Test_Opts()

        self._find_actions(subparsers, action_model)
        self._find_actions(subparsers, self)
        return parser

    def _find_actions(self, subparsers, module):
        for attr in (a for a in dir(module) if a.startswith('do_')):
            command = attr[3:].replace('_', '-')
            callback = getattr(module, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(
                command,
                help=help,
                description=desc,
                add_help=False,
            )
            subparser.add_argument('-h', '--help',
                action='help',
                help=argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    @Args('command', metavar='<subcommand>', nargs='?',help='Display help for <subcommand>')
    def do_help(self, argv):
        '''
        Display help about this program
        '''
        if getattr(argv, 'command', None):
            if argv.command in self.subcommands:
                self.subcommands[argv.command].print_help()
            else:
                raise Exception("'%s' is not a valid subcommand" % argv.command)
        else:
            self.parser.print_help()

    def main(self, argv):
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)

        subcommand_parser = self.get_subcommand_parser()
        self.parser = subcommand_parser

        if not argv or options.help:
            self.do_help(options)
            return 0

        args = subcommand_parser.parse_args(argv)

        if args.func == self.do_help:
            self.do_help(args)
            return 0

        args.func(args)


class Test_Opts(object):
    @Args('--name', metavar='<user-name>', required=True, help='List page about user')
    @Args('--category', metavar='<page-category>', help='Page about category')
    def do_list_page(self, args):
        '''
        list an example
        '''
        print 'Call do_list_page'

    @Args('--name', metavar='<user-name>', required=True, help='Page author')
    @Args('--title', metavar='<page-title>', help='Page title')
    def do_create_page(self, args):
        '''
        create an example
        '''
        print 'Call do_create_page'


def main():
    try:
        ClientShell().main(sys.argv[1:])
    except Exception,e:
        print >> sys.stderr,e
        sys.exit(1)

if __name__ == '__main__':
    main()
