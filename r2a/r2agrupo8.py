# -*- coding: utf-8 -*-
"""  
Pedro Agnes -       180026305
Kesley Kenny -      180021231
Victor Carvalho -   160147140

@description: Projeto final de Redes de Computadores 2020/1

An implementation of a dynamic R2A Algorithm.

the quality list is obtained with the parameter of handle_xml_response() method and the choice
is made inside of handle_segment_size_request(), before sending the message down.

In this algorithm the quality choice should be dynamic according to the available bandwidth?
"""
import random
from player.parser import *
from r2a.ir2a import IR2A


class R2AGrupo8(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # getting qi list
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        #random choosing approach
        qi_id = random.randint(0, len(self.qi)-1)

        print(self.whiteboard.get_playback_history())

        #list = self.whiteboard.get_playback_history()
        #if len(list) > 0:
        #    print(f'>>>>>>>>>>> {list[0][1]}')

        # Hora de definir qual qualidade será escolhida
        msg.add_quality_id(self.qi[qi_id])

        self.send_down(msg)

    def handle_segment_size_response(self, msg):



        self.send_up(msg)

    def initialize(self):
        # self.send_up(Message(MessageKind.SEGMENT_REQUEST, 'Olá Mundo'))
        pass

    def finalization(self):
        pass
