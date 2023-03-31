# -*- coding:utf-8 -*-
# Modified from RapidParaformer(https://github.com/RapidAI/RapidASR/blob/main/rapid_paraformer/rapid_paraformer.py)
# @FileName  :ParaformerAsrService.py
# @Time      :2023/1/8 17:01
# @Author    :lovemefan
# @email     :lovemefan@outlook.com
import asyncio
from typing import Union
from typing import List

from numpy import ndarray

from backend.service.utils import (CharTokenizer, Hypothesis, OrtInferSession,
                                   TokenIDConverter, WavFrontend, read_yaml)
from backend.decorator.singleton import singleton
from sanic.request import File
import numpy as np
from backend.config.Config import Config
from backend.utils.AudioHelper import AudioReader


@singleton
class ParaformerAsrService:

    def __init__(self, config_path: str = None) -> None:
        config_path = Config.get_instance().get('paraformer.config_path', None)
        if config_path is None:
            raise ValueError('please set path of config.yaml in backend/config/config.ini')

        config = read_yaml(config_path)

        self.converter = TokenIDConverter(**config['TokenIDConverter'])
        self.tokenizer = CharTokenizer(**config['CharTokenizer'])
        self.frontend_asr = WavFrontend(
            cmvn_file=config['WavFrontend']['cmvn_file'],
            **config['WavFrontend']['frontend_conf']
        )
        self.ort_infer = OrtInferSession(config['Model'])

    async def transcribe(self, audio: Union[File, ndarray]):

        if isinstance(audio, File):
            waveform, _ = AudioReader.read_wav_bytes(audio.body)
            waveform = waveform[None, ...]
        else:
            waveform = audio[None, ...]
        speech, _ = self.frontend_asr.forward_fbank(waveform)
        feats, feats_len = self.frontend_asr.forward_lfr_cmvn(speech)
        am_scores = self.ort_infer(input_content=[feats, feats_len])

        results = []
        for am_score in am_scores:
            pred_res = await self.infer_one_feat(am_score)
            results.append(pred_res)
        return results

    def infer_without_async(self, audio_data):
        def infer_one_feat_without_async(am_score):
            yseq = am_score.argmax(axis=-1)
            score = am_score.max(axis=-1)
            score = np.sum(score, axis=-1)

            # pad with mask tokens to ensure compatibility with sos/eos tokens
            # asr_model.sos:1  asr_model.eos:2
            yseq = np.array([1] + yseq.tolist() + [2])
            nbest_hyps = [Hypothesis(yseq=yseq, score=score)]
            infer_res = []
            for hyp in nbest_hyps:
                # remove sos/eos and get results
                last_pos = -1
                token_int = hyp.yseq[1:last_pos].tolist()

                # remove blank symbol id, which is assumed to be 0
                token_int = list(filter(lambda x: x not in (0, 2), token_int))

                # Change integer-ids to tokens
                token = self.converter.ids2tokens(token_int)

                text = self.tokenizer.tokens2text(token)
                infer_res.append(text)
            return infer_res

        waveform = audio_data[None, ...]
        speech, _ = self.frontend_asr.forward_fbank(waveform)
        feats, feats_len = self.frontend_asr.forward_lfr_cmvn(speech)
        am_scores = self.ort_infer(input_content=[feats, feats_len])

        results = []
        for am_score in am_scores:
            pred_res = infer_one_feat_without_async(am_score)
            results.append(pred_res)
        return results

    async def infer_one_feat(self, am_score: np.ndarray) -> List[str]:
        yseq = am_score.argmax(axis=-1)
        score = am_score.max(axis=-1)
        score = np.sum(score, axis=-1)

        # pad with mask tokens to ensure compatibility with sos/eos tokens
        # asr_model.sos:1  asr_model.eos:2
        yseq = np.array([1] + yseq.tolist() + [2])
        await asyncio.sleep(0)
        nbest_hyps = [Hypothesis(yseq=yseq, score=score)]
        await asyncio.sleep(0)
        infer_res = []
        for hyp in nbest_hyps:
            await asyncio.sleep(0)
            # remove sos/eos and get results
            last_pos = -1
            token_int = hyp.yseq[1:last_pos].tolist()

            # remove blank symbol id, which is assumed to be 0
            token_int = list(filter(lambda x: x not in (0, 2), token_int))

            # Change integer-ids to tokens
            token = self.converter.ids2tokens(token_int)

            text = self.tokenizer.tokens2text(token)
            infer_res.append(text)
        return infer_res
