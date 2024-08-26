# -*- coding:utf-8 -*-
import easygui
import ffmpeg
import matplotlib.pyplot as plt
import numpy as np
import wave
from scipy.signal import savgol_filter,find_peaks

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
    wave_data = np.absolute(wave_data)
    p , _ = find_peaks
    time = np.arange(0, nframes) * (1.0 / framerate)
    # 绘制波形
    plt.subplot(211) 
    plt.plot(time[:1500:2], wave_data[0][:1500:2])
    plt.subplot(212) 
    plt.plot(time[:1500:2], wave_data[1][:1500:2], c="g")
    plt.xlabel("time (seconds)")
    plt.show()
    # savgol_filter(wave_data[0], 5, 3, mode= 'nearest')
    # 绘制波形
    plt.subplot(211) 
    plt.plot(time[:1500:2], savgol_filter(wave_data[0], 5, 3, mode= 'nearest')[:1500:2])
    plt.subplot(212) 
    plt.plot(time[:1500:2], savgol_filter(wave_data[1], 5, 3, mode= 'nearest')[:1500:2], c="g")
    plt.xlabel("time (seconds)")
    plt.show()
if __name__ == '__main__':
    audio_path = '1.wav'
    
    # ffmpeg.input(easygui.fileopenbox()).output(audio_path).run() 
    
    get_wave(audio_path=audio_path)
