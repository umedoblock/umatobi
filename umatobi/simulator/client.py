import sys, os ,threading ,sqlite3 ,socket, multiprocessing

from umatobi.log import *
from umatobi.constants import *
from umatobi.simulator.darkness import Darkness
from umatobi.simulator import sql
from umatobi.lib import *

def make_darkness(d_config):
    '''darkness process を作成'''
    darkness_ = Darkness(**d_config)
    darkness_.start()

class Client(object):
    NODES_PER_DARKNESS = 4
    LETTER_SIZE = 1024

    def __init__(self, watson_office_addr, num_nodes):
        '''\
        Clientは各PCに付き一つ作成する。
        dir_name 以下に，Client が作成する一切合財を保存する。
        '''

        logger.info(f"Client(self={self}, watson_office_addr={watson_office_addr}, num_nodes={num_nodes})")

        if isinstance(num_nodes, int) and num_nodes > 0:
            pass
        else:
            raise RuntimeError('num_nodes must be positive integer.')

        self.watson_office_addr = watson_office_addr # (IP, PORT)
        self.num_nodes = num_nodes
        # Client set positive integer to id in self._init_attrs().
        self.id = -1
        self.nodes_per_darkness = self.NODES_PER_DARKNESS
        self.node_index = -1
        div, mod = divmod(self.num_nodes, self.nodes_per_darkness)
        if mod == 0:
            mod = self.nodes_per_darkness
        else:
            div += 1
        self.num_darkness = div
        self.last_darkness_make_nodes = mod
        self.total_created_nodes = 0
        self.darkness_processes = []

        self.leave_there = multiprocessing.Event()

        self.timeout_sec = 1
        socket.setdefaulttimeout(self.timeout_sec)

    ########################################################################
    # inside of client
    ########################################################################
    def start(self):
        '''\
        Darknessを、たくさん作成する。
        作成後は、watsonから終了通知("break down")を受信するまで待機する。
        '''
        logger.info(f"{self}.start()")

        self._consult_watson()

        self._has_a_lot_on_mind()

        self._confesses_darkness()

        self._waits_to_break_down()

        # time will tell

        self._run_a_way()

        self._come_to_a_bad_end()

    ########################################################################
    # client of action
    ########################################################################

    def _consult_watson(self):
        logger.info(f"{self}._consult_watson()")

        self._make_contact_with()

        _d_init_attrs = self._init_attrs()

    def _has_a_lot_on_mind(self):
        logger.info(f"{self}._makes_growings_table()")
        self.client_db = sql.SQL(db_path=self.client_db_path,
                                 schema_path=self.schema_path)
        self.client_db.create_db()
        self.client_db.create_table('growings')

    def _confesses_darkness(self):
        logger.info(f"{self}._confesses_darkness()")
        # Darkness が作成する node の数を設定する。
        nodes_per_darkness = self.nodes_per_darkness

        # for 内で darkness_process を作成し、
        # 順に darkness_processes に追加していく。
        for darkness_id in range(0, self.num_darkness):
            first_node_id = self.node_index + \
                            darkness_id * self.nodes_per_darkness
            if darkness_id == self.num_darkness - 1:
                # 最後に端数を作成？
                nodes_per_darkness = self.last_darkness_make_nodes
            logger.info(f"client_id={self.id}, darkness id={darkness_id}, num_darkness={self.num_darkness}, num_nodes={nodes_per_darkness}, first_node_id={first_node_id}")
            client_id = self.id

            # client と darkness process が DarknessConfig を介して通信する。
            darkness_d_config = {
                'id':  darkness_id,
                'client_id':  client_id,
                'start_up_orig':  self.start_up_orig,
                'dir_name':  self.dir_name,
                'log_level':  self.log_level,
                'num_nodes':  nodes_per_darkness,
                'first_node_id':  first_node_id,
                'num_darkness': self.num_darkness,
                # share with client and darkness
                'made_nodes':  multiprocessing.Value('i', 0),
                # share with client and another darkness
                'leave_there':  self.leave_there,
            }
            darkness_process = \
                multiprocessing.Process(
                    target=make_darkness,
                    args=(darkness_d_config,),
                )
            darkness_process.d_config = darkness_d_config
            self.darkness_processes.append(darkness_process)

        for darkness_process in self.darkness_processes:
            darkness_process.start()

    def _waits_to_break_down(self):
        logger.info(f"{self}._waits_to_break_down()")
        # watson から終了通知("break down")が届くまで待機し続ける。
        # TODO: #149 watson からの接続であると確認する。
        tries = 0
        recved_mail = b''
        while True:
            logger.debug(f"{self}._waits_to_break_down(), _tcp_sock={self._tcp_sock}, tries={tries}")
            recved_mail = self._watch_mailbox(self._tcp_sock)
            logger.info(f"{self}._waits_to_break_down(), got mail={recved_mail} from {self._tcp_sock}, tries={tries}.")
            if not recved_mail:
                continue

            if recved_mail == b'break down.':
                logger.info(f"{self}._waits_to_break_down(), got break down from {self._tcp_sock}, tries={tries}.")
                break
            logger.error(f"{self}._waits_to_break_down(), got unknown mail from {self._tcp_sock}, tries={tries}.")
            tries += 1

        return recved_mail

    def _run_a_way(self):
        '''\
        Client 終了処理。leave_thereにsignal を set することで、
        Clientの作成した Darkness達は一斉に終了処理を始める。
        '''
        logger.info(f"{self}._run_a_way()")
        self.leave_there.set()

        for darkness_p in self.darkness_processes:
            darkness_p.join()
            logger.info(f"{self}._run_a_way(), {darkness_p} process joind.")

        logger.debug(f"{self.client_db}.close()()")
        self.client_db.close()

        # host のみ比較、 compare only host
        # "on the same network endpoint" stands for otsne
        otsne = are_on_the_same_network_endpoint(self.watson_office_addr,
                                                     self._tcp_sock)
        if otsne:
            send_or_not = 'send'
        else:
            send_or_not = 'doesn\'t send'
        logger.info('{self} {send_or_not} client.{self.id}.db to watson(={self.watson_office_addr})')
        # send client.1.db

        for darkness_process in self.darkness_processes:
            self.total_created_nodes += \
                darkness_process.d_config['made_nodes'].value

        logger.info(f"{self} created num of nodes {self.total_created_nodes}")

    def _come_to_a_bad_end(self):
        logger.info(f"{self}._come_to_a_bad_end()")
        # You must call close() about socket.SOCK_STREAM
        # you wil come to a bad end
        self._tcp_sock.close()
        logger.info(f"{self} closed {self._tcp_sock}.")
        # if you call shutdown() about socket.SOCK_STREAM.
        # Happily, you don't get below ResourceWarning.
        # ResourceWarning: unclosed <socket.socket fd=7, ...

    ########################################################################
    # action of detail
    ########################################################################

    #   _consult_watson()
    def _make_contact_with(self):
        self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logger.info(f"{self}._make_contact_with(), {self._tcp_sock}.connect(={self.watson_office_addr})")
        self._tcp_sock.connect(self.watson_office_addr)

    def _say_good_bye(self):
        logger.info(f"{self}._say_good_bye(), {self._tcp_sock}.close(={self.watson_office_addr})")
        self._tcp_sock.close()

    #   _consult_watson()
    def _init_attrs(self):
        '''\
        watson に接続し、id, start_up_origを受信する。
        id は client.N.log として、log fileを作成するときに使用。
        start_up_orig は dir_nameを決定する際に使用する。
        '''
        logger.info(f"{self}._hello_watson()")
        reply = self._hello_watson()
        if not reply:
            self._tcp_sock.close()
            raise RuntimeError('client cannot say "I am Client." to watson where is {}'.format(self.watson_office_addr))

        self.id = reply['client_id']
        self.start_up_orig = isoformat_to_start_up_orig(reply['start_up_orig'])
        self.dir_name = reply['dir_name']
        self.client_db_path = os.path.join(self.dir_name,
                                     'client.{}.db'.format(self.id))
        self.node_index = reply['node_index']
        self.log_level = reply['log_level']
        self.schema_path = SCHEMA_PATH

        return reply

    #   _init_attrs()
    def _hello_watson(self):
        '''\
        watsonに "I am Client." をTCPで送信し、watson起動時刻(start_up_orig)、
        watsonへの接続順位(=id)をTCPで受信する。
        この時、受信するのはjson文字列。
        simulation 結果を格納する dir_name を作成するための情報を得る。
        dir_name 以下には、client.N.log, client.N.db 等を作成する。

        3 回 watson へ "I am Client." と伝えようとしても駄目だった場合、
        空の dictionary を返す。
        dictionary を受け取る _init_attrs() では、RuntimeError()を上げる。
        '''
        sheep = {
            'profess': 'I am Client.',
            'num_nodes': self.num_nodes,
        }
        mail = dict2bytes(sheep)

        logger.info(f"{self}._hello_watson(), sheep={sheep}, mail={mail}")

        insistent = 3
        self._franticalliy_tell(mail, insistent)
        got_mail = self._franticalliy_watch_mailbox(insistent)

        logger.debug(f"{self}._hello_watson(), got_mail={got_mail}.")

        return got_mail

    def _franticalliy_tell(self, mail, insistent):
        tries = 0
        while tries < insistent:
            logger.info(f"{self}._franticalliy_tell(), tries={tries}, insistent={insistent}.")
            told = self._tell_truth(mail)
            if told:
                break
            tries += 1

        if tries >= insistent:
            raise RuntimeError(f"cannot tell truth. {tries} times failed. cannot tell mail={mail} to {self.watson_office_addr}")

    def _franticalliy_watch_mailbox(self, insistent):
        tries = 0
        recved_mail = b'<empty>'
        while tries < insistent:
            logger.info(f"{self}._hello_watson(), {self._tcp_sock}.recv(1024), tries={tries}")
            recved_mail = self._watch_mailbox()
            if recved_mail:
                break

            tries += 1

        logger.debug(f"{self}._hello_watson(), recved_mail={recved_mail}, tries={tries}.")
        reply = bytes2dict(recved_mail)
        return reply

    def _tell_truth(self, truth):
        logger.debug(f"{self}._tell_truth(truth={truth})")
        told = sock_send(self._tcp_sock, truth)
        if told:
            logger.info(f"{self}._tell_truth(truth={truth}) success.")
        return told

    def _watch_mailbox(self, letter_size=LETTER_SIZE):
        logger.debug(f"{self}._watch_mailbox(letter_size={letter_size})")
        recved_mail = sock_recv(self._tcp_sock, letter_size)
        logger.info(f"{self}._watch_mailbox() returns {recved_mail.decode()}.")
        return recved_mail
