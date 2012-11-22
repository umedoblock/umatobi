from xxx import args_xxx, get_xxx_path

def args_db():
    parser = args_xxx(description='select.py')
    parser.add_argument(# last argment, db file
                        metavar='f', dest='xxx_file',
                        nargs='?', default='',
                        help='simulation.db, watson.db, or client.1.db, ...')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # examples:
    # umatobi/select.py --help
    # umatobi/select.py --show-timestamps
    # umatobi/select.py watson.db clients
    # umatobi/select.py --index=1 client.1.db pickles id=1

    args = args_db()
    db_path = get_xxx_path(args, 'db')

    if db_path:
        print('db_path =', db_path)
