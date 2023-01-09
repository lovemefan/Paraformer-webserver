#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName  :ASRPipeline.py
# @Time      :2023/1/9 20:15
# @Author    :lovemefan
# @email     :lovemefan@outlook.com
import logging
import time
# Copyright (c) Alibaba, Inc. and its affiliates.
from typing import Any, Dict, List, Sequence, Tuple, Union, Optional

import torch
import yaml
from funasr.bin.asr_inference_paraformer import Speech2Text
from funasr.fileio.datadir_writer import DatadirWriter
from funasr.modules.beam_search.beam_search import Hypothesis
from funasr.modules.subsampling import TooShortUttError
from funasr.torch_utils.set_all_random_seed import set_all_random_seed
from funasr.tasks.asr import ASRTaskParaformer as ASRTask
from funasr.utils import wav_utils, postprocess_utils, asr_utils

from modelscope.metainfo import Pipelines
from modelscope.models import Model
from modelscope.outputs import OutputKeys
from modelscope.pipelines.base import Pipeline
from modelscope.pipelines.builder import PIPELINES
from modelscope.preprocessors import WavToScp
from modelscope.utils.audio.audio_utils import (extract_pcm_from_wav,
                                                load_bytes_from_url)
from modelscope.utils.constant import Frameworks, Tasks
from modelscope.utils.logger import get_logger
from typeguard import check_argument_types
from funasr.utils import asr_utils

logger = get_logger()

__all__ = ['AutomaticSpeechRecognitionPipeline']


@PIPELINES.register_module(
    'asr-webservice', module_name=Pipelines.asr_inference)
class AutomaticSpeechRecognitionPipeline(Pipeline):
    """ASR Inference Pipeline
    """

    def __init__(self,
                 model: Union[Model, str] = None,
                 preprocessor: WavToScp = None,
                 **kwargs):
        """use `model` and `preprocessor` to create an asr pipeline for prediction
        """
        super().__init__(model=model, preprocessor=preprocessor, **kwargs)
        self.model_cfg = self.model.forward()
        self.speech2text = None

    def __call__(self,
                 audio_in: Union[str, bytes],
                 audio_fs: int = None,
                 recog_type: str = None,
                 audio_format: str = None) -> Dict[str, Any]:

        self.recog_type = recog_type
        self.audio_format = audio_format
        self.audio_fs = audio_fs

        if isinstance(audio_in, str):
            # load pcm data from url if audio_in is url str
            self.audio_in, checking_audio_fs = load_bytes_from_url(audio_in)
        elif isinstance(audio_in, bytes):
            # load pcm data from wav data if audio_in is wave format
            self.audio_in, checking_audio_fs = extract_pcm_from_wav(audio_in)
        else:
            self.audio_in = audio_in

        # set the sample_rate of audio_in if checking_audio_fs is valid
        if checking_audio_fs is not None:
            self.audio_fs = checking_audio_fs

        if recog_type is None or audio_format is None:
            self.recog_type, self.audio_format, self.audio_in = asr_utils.type_checking(
                audio_in=self.audio_in,
                recog_type=recog_type,
                audio_format=audio_format)

        if hasattr(asr_utils, 'sample_rate_checking'):
            checking_audio_fs = asr_utils.sample_rate_checking(
                self.audio_in, self.audio_format)
            if checking_audio_fs is not None:
                self.audio_fs = checking_audio_fs

        if self.preprocessor is None:
            self.preprocessor = WavToScp()

        output = self.preprocessor.forward(self.model_cfg, self.recog_type,
                                           self.audio_format, self.audio_in,
                                           self.audio_fs)
        output = self.forward(output)
        rst = self.postprocess(output)
        return rst

    def forward(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Decoding
        """

        logger.info(f"Decoding with {inputs['audio_format']} files ...")

        data_cmd: Sequence[Tuple[str, str, str]]
        if inputs['audio_format'] == 'wav' or inputs['audio_format'] == 'pcm':
            data_cmd = ['speech', 'sound']
        elif inputs['audio_format'] == 'kaldi_ark':
            data_cmd = ['speech', 'kaldi_ark']
        elif inputs['audio_format'] == 'tfrecord':
            data_cmd = ['speech', 'tfrecord']

        if inputs.__contains__('mvn_file'):
            data_cmd.append(inputs['mvn_file'])

        # generate asr inference command
        cmd = {
            'model_type': inputs['model_type'],
            'ngpu': 1,  # 0: only CPU, ngpu>=1: gpu number if cuda is available
            'log_level': 'ERROR',
            'audio_in': inputs['audio_lists'],
            'name_and_type': data_cmd,
            'asr_model_file': inputs['am_model_path'],
            'idx_text': '',
            'sampled_ids': 'seq2seq/sampled_ids',
            'sampled_lengths': 'seq2seq/sampled_lengths',
            'lang': 'zh-cn',
            'code_base': inputs['code_base'],
            'mode': inputs['mode'],
            'fs': {
                'audio_fs': inputs['audio_fs'],
                'model_fs': 16000
            }
        }

        config_file = open(inputs['asr_model_config'], encoding='utf-8')
        root = yaml.full_load(config_file)
        config_file.close()
        frontend_conf = None
        if 'frontend_conf' in root:
            frontend_conf = root['frontend_conf']
        token_num_relax = None
        if 'token_num_relax' in root:
            token_num_relax = root['token_num_relax']
        decoding_ind = None
        if 'decoding_ind' in root:
            decoding_ind = root['decoding_ind']
        decoding_mode = None
        if 'decoding_mode' in root:
            decoding_mode = root['decoding_mode']

        cmd['beam_size'] = root['beam_size']
        cmd['penalty'] = root['penalty']
        cmd['maxlenratio'] = root['maxlenratio']
        cmd['minlenratio'] = root['minlenratio']
        cmd['ctc_weight'] = root['ctc_weight']
        cmd['lm_weight'] = root['lm_weight']
        cmd['asr_train_config'] = inputs['am_model_config']
        cmd['lm_file'] = inputs['lm_model_path']
        cmd['lm_train_config'] = inputs['lm_model_config']
        cmd['batch_size'] = inputs['model_config']['batch_size']
        cmd['frontend_conf'] = frontend_conf
        if frontend_conf is not None and 'fs' in frontend_conf:
            cmd['fs']['model_fs'] = frontend_conf['fs']
        cmd['token_num_relax'] = token_num_relax
        cmd['decoding_ind'] = decoding_ind
        cmd['decoding_mode'] = decoding_mode
        cmd['num_workers'] = 0

        inputs['asr_result'] = self.run_inference(cmd)

        return inputs

    def postprocess(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """process the asr results
        """
        from funasr.utils import asr_utils

        logger.info('Computing the result of ASR ...')

        rst = {}

        # single wav or pcm task
        if inputs['recog_type'] == 'wav':
            if 'asr_result' in inputs and len(inputs['asr_result']) > 0:
                text = inputs['asr_result'][0]['value']
                if len(text) > 0:
                    rst[OutputKeys.TEXT] = text

        # run with datasets, and audio format is waveform or kaldi_ark or tfrecord
        elif inputs['recog_type'] != 'wav':
            inputs['reference_list'] = self.ref_list_tidy(inputs)

            if hasattr(asr_utils, 'set_parameters'):
                asr_utils.set_parameters(language=inputs['model_lang'])
            inputs['datasets_result'] = asr_utils.compute_wer(
                hyp_list=inputs['asr_result'],
                ref_list=inputs['reference_list'])

        else:
            raise ValueError('recog_type and audio_format are mismatching')

        if 'datasets_result' in inputs:
            rst[OutputKeys.TEXT] = inputs['datasets_result']

        return rst

    def ref_list_tidy(self, inputs: Dict[str, Any]) -> List[Any]:
        ref_list = []

        if inputs['audio_format'] == 'tfrecord':
            # should assemble idx + txt
            with open(inputs['reference_text'], 'r', encoding='utf-8') as r:
                text_lines = r.readlines()

            with open(inputs['idx_text'], 'r', encoding='utf-8') as i:
                idx_lines = i.readlines()

            j: int = 0
            while j < min(len(text_lines), len(idx_lines)):
                idx_str = idx_lines[j].strip()
                text_str = text_lines[j].strip().replace(' ', '')
                item = {'key': idx_str, 'value': text_str}
                ref_list.append(item)
                j += 1

        else:
            # text contain idx + sentence
            with open(inputs['reference_text'], 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line_item = line.split(None, 1)
                if len(line_item) > 1:
                    item = {
                        'key': line_item[0],
                        'value': line_item[1].strip('\n')
                    }
                    ref_list.append(item)

        return ref_list

    def inference(
            self,
            maxlenratio: float,
            minlenratio: float,
            batch_size: int,
            beam_size: int,
            ngpu: int,
            ctc_weight: float,
            lm_weight: float,
            penalty: float,
            log_level: Union[int, str],
            data_path_and_name_and_type,
            asr_train_config: Optional[str],
            asr_model_file: Optional[str],
            audio_lists: Union[List[Any], bytes] = None,
            lm_train_config: Optional[str] = None,
            lm_file: Optional[str] = None,
            token_type: Optional[str] = None,
            key_file: Optional[str] = None,
            word_lm_train_config: Optional[str] = None,
            bpemodel: Optional[str] = None,
            allow_variable_data_keys: bool = False,
            streaming: bool = False,
            output_dir: Optional[str] = None,
            dtype: str = "float32",
            seed: int = 0,
            ngram_weight: float = 0.9,
            nbest: int = 1,
            num_workers: int = 1,
            frontend_conf: dict = None,
            fs: Union[dict, int] = 16000,
            lang: Optional[str] = None,
            **kwargs,
    ):
        assert check_argument_types()
        if batch_size > 1:
            raise NotImplementedError("batch decoding is not implemented")
        if word_lm_train_config is not None:
            raise NotImplementedError("Word LM is not implemented")
        if ngpu > 1:
            raise NotImplementedError("only single GPU decoding is supported")

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s (%(module)s:%(lineno)d) %(levelname)s: %(message)s",
        )

        if ngpu >= 1 and torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        hop_length: int = 160
        sr: int = 16000
        if isinstance(fs, int):
            sr = fs
        else:
            if 'model_fs' in fs and fs['model_fs'] is not None:
                sr = fs['model_fs']
        # data_path_and_name_and_type for modelscope: (data from audio_lists)
        # ['speech', 'sound', 'am.mvn']
        # data_path_and_name_and_type for funasr:
        # [('/mnt/data/jiangyu.xzy/exp/maas/mvn.1.scp', 'speech', 'kaldi_ark')]
        if isinstance(data_path_and_name_and_type[0], Tuple):
            features_type: str = data_path_and_name_and_type[0][1]
        elif isinstance(data_path_and_name_and_type[0], str):
            features_type: str = data_path_and_name_and_type[1]
        else:
            raise NotImplementedError("unknown features type:{0}".format(data_path_and_name_and_type))
        if features_type != 'sound':
            frontend_conf = None
            flag_modelscope = False
        else:
            flag_modelscope = True
        if frontend_conf is not None:
            if 'hop_length' in frontend_conf:
                hop_length = frontend_conf['hop_length']

        finish_count = 0
        file_count = 1
        if flag_modelscope and not isinstance(data_path_and_name_and_type[0], Tuple):
            data_path_and_name_and_type_new = [
                audio_lists, data_path_and_name_and_type[0], data_path_and_name_and_type[1]
            ]
            if isinstance(audio_lists, bytes):
                file_count = 1
            else:
                file_count = len(audio_lists)
            if len(data_path_and_name_and_type) >= 3 and frontend_conf is not None:
                mvn_file = data_path_and_name_and_type[2]
                mvn_data = wav_utils.extract_CMVN_featrures(mvn_file)
                frontend_conf['mvn_data'] = mvn_data
        # 1. Set random-seed
        set_all_random_seed(seed)

        # 2. Build speech2text
        speech2text_kwargs = dict(
            asr_train_config=asr_train_config,
            asr_model_file=asr_model_file,
            lm_train_config=lm_train_config,
            lm_file=lm_file,
            token_type=token_type,
            bpemodel=bpemodel,
            device=device,
            maxlenratio=maxlenratio,
            minlenratio=minlenratio,
            dtype=dtype,
            beam_size=beam_size,
            ctc_weight=ctc_weight,
            lm_weight=lm_weight,
            ngram_weight=ngram_weight,
            penalty=penalty,
            nbest=nbest,
            frontend_conf=frontend_conf,
        )

        if self.speech2text is None:
            self.speech2text = Speech2Text(**speech2text_kwargs)

        # 3. Build data-iterator

        loader = ASRTask.build_streaming_iterator_modelscope(
            data_path_and_name_and_type_new,
            dtype=dtype,
            batch_size=batch_size,
            key_file=key_file,
            num_workers=num_workers,
            preprocess_fn=ASRTask.build_preprocess_fn(self.speech2text.asr_train_args, False),
            collate_fn=ASRTask.build_collate_fn(self.speech2text.asr_train_args, False),
            allow_variable_data_keys=allow_variable_data_keys,
            inference=True,
            sample_rate=fs
        )

        forward_time_total = 0.0
        length_total = 0.0
        # 7 .Start for-loop
        # FIXME(kamo): The output format should be discussed about
        asr_result_list = []
        if output_dir is not None:
            writer = DatadirWriter(output_dir)
        else:
            writer = None

        for keys, batch in loader:
            assert isinstance(batch, dict), type(batch)
            assert all(isinstance(s, str) for s in keys), keys
            _bs = len(next(iter(batch.values())))
            assert len(keys) == _bs, f"{len(keys)} != {_bs}"
            batch = {k: v[0] for k, v in batch.items() if not k.endswith("_lengths")}

            logging.info("decoding, utt_id: {}".format(keys))
            # N-best list of (text, token, token_int, hyp_object)

            try:
                time_beg = time.time()
                results = self.speech2text(**batch)
                time_end = time.time()
                forward_time = time_end - time_beg
                lfr_factor = results[0][-1]
                length = results[0][-2]
                results = [results[0][:-2]]
                forward_time_total += forward_time
                length_total += length
                logging.info(
                    "decoding, feature length: {}, forward_time: {:.4f}, rtf: {:.4f}".
                    format(length, forward_time, 100 * forward_time / (length * lfr_factor)))
            except TooShortUttError as e:
                logging.warning(f"Utterance {keys} {e}")
                hyp = Hypothesis(score=0.0, scores={}, states={}, yseq=[])
                results = [[" ", ["<space>"], [2], hyp]] * nbest

            # Only supporting batch_size==1
            key = keys[0]
            for n, (text, token, token_int, hyp) in zip(range(1, nbest + 1), results):
                # Create a directory: outdir/{n}best_recog
                if writer is not None:
                    ibest_writer = writer[f"{n}best_recog"]

                    # Write the result to each file
                    ibest_writer["token"][key] = " ".join(token)
                    ibest_writer["token_int"][key] = " ".join(map(str, token_int))
                    ibest_writer["score"][key] = str(hyp.score)

                if text is not None:
                    text_postprocessed = postprocess_utils.sentence_postprocess(token)
                    item = {'key': key, 'value': text_postprocessed}
                    asr_result_list.append(item)
                    finish_count += 1
                    asr_utils.print_progress(finish_count / file_count)
                    if writer is not None:
                        ibest_writer["text"][key] = text

                logging.info("decoding, predictions: {}".format(text))

        logging.info("decoding, feature length total: {}, forward_time total: {:.4f}, rtf avg: {:.4f}".
                     format(length_total, forward_time_total, 100 * forward_time_total / (length_total * lfr_factor)))
        return asr_result_list

    def run_inference(self, cmd):
        asr_result = self.inference(
            mode=cmd['mode'],
            batch_size=cmd['batch_size'],
            maxlenratio=cmd['maxlenratio'],
            minlenratio=cmd['minlenratio'],
            beam_size=cmd['beam_size'],
            ngpu=cmd['ngpu'],
            num_workers=cmd['num_workers'],
            ctc_weight=cmd['ctc_weight'],
            lm_weight=cmd['lm_weight'],
            penalty=cmd['penalty'],
            log_level=cmd['log_level'],
            data_path_and_name_and_type=cmd['name_and_type'],
            audio_lists=cmd['audio_in'],
            asr_train_config=cmd['asr_train_config'],
            asr_model_file=cmd['asr_model_file'],
            lm_file=cmd['lm_file'],
            lm_train_config=cmd['lm_train_config'],
            frontend_conf=cmd['frontend_conf'],
            token_num_relax=cmd['token_num_relax'],
            decoding_ind=cmd['decoding_ind'],
            decoding_mode=cmd['decoding_mode'])

        return asr_result
