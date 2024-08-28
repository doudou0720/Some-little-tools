# -*- coding:utf-8 -*-
import easygui
import ffmpeg
import numpy as np
import wave
# import spleeter
# import spleeter.separator

def get_wave(audio_path):
    # 打开WAV文档
    f = wave.open(audio_path, "rb")
    # 读取格式信息
    # (nchannels, sampwidth, framerate, nframes, comptype, compname)
    params = f.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    # 读取波形数据
    str_data = f.readframes(nframes)
    f.close()
    #将波形数据转换为数组
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, 2
    wave_data = wave_data.T
    return wave_data
if __name__ == '__main__':
    audio_path = '1.wav'
    
    ffmpeg.input(easygui.fileopenbox()).output(audio_path).run() 
    
    # sep = spleeter.separator.Separator('spleeter:2stems')
    # sep.separate_to_file(audio_path,"./")
