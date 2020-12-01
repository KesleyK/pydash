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
from base.timer import Timer
from player.parser import *
from r2a.ir2a import IR2A


class R2AGrupo8(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []
        self.qualidade_cap = 0

        self.timer = Timer.get_instance()
        self.momento_requisicao = 0
        
        self.taxa_bits = 0
        self.throughput_mean = 0

        self.current_buffer = 0
        self.max_buffer = 0

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.momento_requisicao = self.timer.get_current_time()

        qualidade_selecionada = self.qi[0]
        for i in range(len(self.qi)):
            qualidade_selecionada = self.qi[i]
            if self.taxa_bits < qualidade_selecionada:
                if i == 0:
                    qualidade_selecionada = self.qi[0]
                else:
                    qualidade_selecionada = self.qi[i-1]
                break

        if self.whiteboard.get_playback_buffer_size():
            if self.current_buffer == 0:
                qualidade_selecionada = self.qi[0]
                # self.throughput_mean = 0

        msg.add_quality_id(qualidade_selecionada)

        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        tamanho_segmento = msg.get_bit_length()
        self.taxa_bits = tamanho_segmento/(self.timer.get_current_time() - self.momento_requisicao)
        if self.whiteboard.get_playback_buffer_size():
            self.current_buffer = self.whiteboard.get_playback_buffer_size()[-1][1]
        
        if self.throughput_mean == 0:
            self.throughput_mean = self.taxa_bits
        else:
            self.throughput_mean = (self.throughput_mean + self.taxa_bits)/2 # media de throughput
        
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
