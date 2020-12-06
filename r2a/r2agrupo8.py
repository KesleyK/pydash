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
        self.segmentos_baixados = 0

        self.timer = Timer.get_instance()
        self.momento_requisicao = 0
        
        self.taxa_bits = 0
        self.menor_taxa = math.inf
        self.maior_taxa = 0
        self.historico_t = []

        self.current_buffer = 0
        self.quedas_consecutivas = 0

        self.logger = None

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        self.momento_requisicao = self.timer.get_current_time()
        self.current_quality = self.seleciona_qualidade()

        msg.add_quality_id(self.current_quality)

        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.segmentos_baixados += 1
        tamanho_segmento = msg.get_bit_length()

        self.taxa_bits = tamanho_segmento/(self.timer.get_current_time() - self.momento_requisicao)
        if self.taxa_bits < self.menor_taxa:
            self.menor_taxa = self.taxa_bits
        if self.taxa_bits > self.maior_taxa:
            self.maior_taxa = self.taxa_bits

        self.historico_t.append(self.taxa_bits)

        if self.whiteboard.get_playback_buffer_size():
            self.current_buffer = self.whiteboard.get_playback_buffer_size()[-1][1]
        
        self.send_up(msg)

    def initialize(self):
        self.logger = open("results/estatisticasAdicionais.log", "w")

    def finalization(self):
        self.logger.close()
        print("avg throughput:", self.avg_throughput())
        print("avg qi:", self.avg_qi())


    ############ metodos auxiliares ############

    def seleciona_qualidade(self):
        qualidade_atual_suportada = self.calcula_qualidade_maxima(self.taxa_bits)
        
        qualidade_selecionada = math.floor(qualidade_atual_suportada * self.limite_porcento_qualidade(qualidade_atual_suportada) * self.estabilidade_rede())
        if qualidade_selecionada >= len(self.qi):
            qualidade_selecionada = len(self.qi)-1

        if qualidade_selecionada == 0 and self.current_buffer > 0:
            qualidade_selecionada = self.suavisa_queda_qualidade(qualidade_selecionada)
        else:
            self.quedas_consecutivas = 0

        return self.qi[qualidade_selecionada]

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
            elif i == len(self.qi)-1:
                qualidade_index = len(self.qi)-1

        return qualidade_index

    def limite_porcento_qualidade(self, qualidade):
        stable_buffer = self.qi[qualidade]/self.menor_taxa
        stable_buffer += 5

        self.logger.write(f"Tempo: {self.timer.get_current_time()}\nBuffer Estável: {stable_buffer}\nBuffer atual: {self.current_buffer}\nMenor taxa: {self.menor_taxa}\nQualidade selecionada: {qualidade}\n\n")

        limite = self.current_buffer/stable_buffer
        if limite > 1:
            limite = 1

        return limite

    def suavisa_queda_qualidade(self, qualidade):
        if len(self.whiteboard.get_playback_pauses()) != 0:
            return qualidade

        self.quedas_consecutivas += 1
        qualidade_corrigida = 0

        qualidade_atual = 0
        for q in self.qi:
            if q == self.current_quality:
                break
            qualidade_atual += 1

        media = self.avg_qi()

        if self.quedas_consecutivas == 1:
            qualidade_corrigida = (qualidade_atual + media)/2
        elif self.quedas_consecutivas == 2:
            qualidade_corrigida = media
        elif self.quedas_consecutivas == 3:
            qualidade_corrigida = media/2

        return math.floor(qualidade_corrigida)

    def estabilidade_rede(self):
        grau_escalabilidade = 3
        agora = self.timer.get_current_time()
        estabilidade = (len(self.qi)/grau_escalabilidade * math.log(agora, 10) + 10)/len(self.qi)

        if estabilidade > 1:
            estabilidade = 1
        elif estabilidade < 0:
            estabilidade = 0

        return estabilidade

    def avg_throughput(self):
        if len(self.historico_t) == 0:
            return self.qi[0]
        return sum(self.historico_t)/len(self.historico_t)

    def avg_qi(self):
        media = 0
        if len(self.whiteboard.get_playback_qi()) == 0:
            return media

        for q in self.whiteboard.get_playback_qi():
            media += q[1]
        
        return media/len(self.whiteboard.get_playback_qi())
