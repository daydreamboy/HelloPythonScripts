import optparse
import shlex

def generateOptionParser():
    '''
    Gets the return register as a string for lldb
    base upon the hardware
    '''
    usage = "usage: %prog [options] breakpoint_query\n" + "Use 'bar -h' for option desc"

    parser = optparse.OptionParser(usage=usage, prog='bar')
    parser.add_option("-n", "--non_regex",
                      action="store_true",
                      default=False,
                      dest="non_regex",
                      help="Use a non-regex breakpoint instead"
                      )
    return parser


if __name__ == '__main__':
    parser = generateOptionParser()
    (options, args) = parser.parse_args()
    print options, args
