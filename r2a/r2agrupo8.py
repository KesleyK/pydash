# -*- coding: utf-8 -*-
"""  
Pedro Agnes -       180026305
Kesley Kenny -      180021231
Victor Carvalho -   160147140

@description: Projeto final de Redes de Computadores 2020/1

An implementation of a dynamic R2A Algorithm.
This algorithm tries to deliver the best possible quality avoiding pauses the best it can...
"""

import random
import math
from base.timer import Timer
from player.parser import *
from r2a.ir2a import IR2A


class R2AGrupo8(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []
        self.current_quality = 0
        self.qualidade_cap = 0

        self.timer = Timer.get_instance()
        self.momento_requisicao = 0
        
        self.taxa_bits = 0
        self.historico_t = []

        self.current_buffer = 0

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.momento_requisicao = self.timer.get_current_time()

        self.current_quality = self.seleciona_qualidade()

        if self.whiteboard.get_playback_buffer_size():
            if self.current_buffer == 0:
                self.current_quality = self.qi[0] # sempre que for detectado buffer vazio, pegamos a pior qualidade

        msg.add_quality_id(self.current_quality)

        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        tamanho_segmento = msg.get_bit_length()
        self.taxa_bits = tamanho_segmento/(self.timer.get_current_time() - self.momento_requisicao)
        if self.whiteboard.get_playback_buffer_size():
            self.current_buffer = self.whiteboard.get_playback_buffer_size()[-1][1]
        
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass


    ############ metodos auxiliares ############

    def seleciona_qualidade(self):
        qualidade_atual_suportada = self.calcula_qualidade_maxima(self.taxa_bits)
        # qualidade_media_suportada = self.calcula_qualidade_maxima(self.avg_throughput())
        qualidade_selecionada = self.qi[math.floor(qualidade_atual_suportada*self.limite_porcento_qualidade())]
        return qualidade_selecionada

    def avg_throughput(self):
        return sum(self.historico_t)/self.historico_t.size()

    def calcula_qualidade_maxima(self, throughput):
        qualidade_index = 0
        for i in range(len(self.qi)):
            qualidade = self.qi[i]
            if throughput < qualidade:
                if i == 0:
                    qualidade_index = 0
                else:
                    qualidade_index = i-1
                break

        return qualidade_index

    def limite_porcento_qualidade(self):
        stable_buffer = 50
        limite = self.current_buffer/stable_buffer
        if(limite > 1):
            limite = 1

        return limite
