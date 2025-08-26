#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
urwid_CLI测试和使用示例
展示所有组件的使用方法
"""

import threading
import time
import os
import sys

# 将当前目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from urwid_CLI import SelectBox, FileOpenBox, ynBox, ProgressBar


def test_select_box():
    """测试SelectBox组件"""
    print("=== SelectBox 测试 ===")
    
    # 单选模式测试
    choices = [("选项1 - 文档", "doc"), ("选项2 - 图片", "img"), ("选项3 - 视频", "video"), ("选项4 - 音频", "audio")]
    selected = SelectBox("请选择文件类型", "使用上下键选择，回车确认", choices).start()
    if selected:
        print(f"你选择了: {selected[0]} ({selected[1]})")
    else:
        print("未选择任何选项")
    
    # 多选模式测试
    print("\n--- 多选模式 ---")
    multi_selected = SelectBox("请选择多个文件类型", "使用上下键选择，空格键选中，回车确认", choices, multi=True).start()
    if multi_selected:
        print(f"你选择了: {[item[0] for item in multi_selected]}")
    else:
        print("未选择任何选项")


def test_file_open_box():
    """测试FileOpenBox组件"""
    print("\n=== FileOpenBox 测试 ===")
    
    # 单选模式测试
    print("单选模式 - 选择一个文件:")
    selected_file = FileOpenBox(".", multi=False).start()
    if selected_file:
        print(f"你选择了文件: {selected_file}")
    else:
        print("未选择文件")
    
    # 多选模式测试
    print("\n多选模式 - 选择多个文件:")
    selected_files = FileOpenBox(".", multi=True).start()
    if selected_files:
        print(f"你选择了 {len(selected_files)} 个文件:")
        for f in selected_files:
            print(f"  - {f}")
    else:
        print("未选择任何文件")


def test_yn_box():
    """测试ynBox组件"""
    print("\n=== ynBox 测试 ===")
    
    # 确认框测试
    result = ynBox("确认执行操作吗？", "此操作将删除选中的文件，无法恢复").start()
    if result:
        print("用户选择了确认")
    else:
        print("用户选择了取消")


def test_progress_bar_basic():
    """测试基础ProgressBar功能"""
    print("\n=== ProgressBar 基础测试 ===")
    
    # 创建主进度条
    progress = ProgressBar(total=100, title="文件处理进度", refresh_rate=0.05)
    
    # 添加子任务
    download_task = progress.add_sub_progress("下载文件", 100, "从服务器下载文件")
    process_task = progress.add_sub_progress("处理文件", 100, "对下载的文件进行处理")
    
    # 在新线程中运行进度条界面
    progress_thread = threading.Thread(target=progress.start)
    progress_thread.daemon = True
    progress_thread.start()
    
    # 模拟任务执行
    try:
        for i in range(101):
            # 更新下载任务
            if i <= 50:
                download_task.update(value=i*2)
            else:
                download_task.finish()
                
            # 更新处理任务
            if i >= 50:
                process_task.update(value=(i-50)*2)
                
            # 更新主进度条
            progress.update(value=i)
            time.sleep(0.05)
        
        # 完成所有任务
        process_task.finish()
        progress.finish()
        time.sleep(1)
    finally:
        progress.stop()
    
    print("基础进度条测试完成")


def test_progress_bar_advanced():
    """测试高级ProgressBar功能（依赖关系和嵌套）"""
    print("\n=== ProgressBar 高级测试 ===")
    
    # 创建主进度条
    progress = ProgressBar(total=100, title="软件安装进度", refresh_rate=0.05)
    
    # 添加有依赖关系的子任务
    # 第一组任务：下载相关
    download_main = progress.add_sub_progress("下载主程序", 100, "下载软件的主要程序文件")
    download_dep1 = progress.add_sub_progress("下载依赖库A", 50, "下载第一个依赖库", depends_on=download_main)
    download_dep2 = progress.add_sub_progress("下载依赖库B", 30, "下载第二个依赖库", depends_on=download_main)
    
    # 第二组任务：安装相关（依赖下载完成）
    install_main = progress.add_sub_progress("安装主程序", 100, "安装软件的主要程序文件", depends_on=download_main)
    install_dep1 = progress.add_sub_progress("配置依赖库A", 50, "配置第一个依赖库", depends_on=install_main)
    install_dep2 = progress.add_sub_progress("配置依赖库B", 30, "配置第二个依赖库", depends_on=install_main)
    
    # 在新线程中运行进度条界面
    progress_thread = threading.Thread(target=progress.start)
    progress_thread.daemon = True
    progress_thread.start()
    
    # 模拟任务执行过程
    try:
        # 1. 执行下载主程序任务
        for i in range(101):
            download_main.update(value=i)
            time.sleep(0.02)
        
        # 2. 执行下载依赖任务（并行）
        for i in range(51):
            if i <= 50:
                download_dep1.update(value=i)
            if i <= 30:
                download_dep2.update(value=i)
            time.sleep(0.02)
        
        # 3. 执行安装主程序任务
        for i in range(101):
            install_main.update(value=i)
            time.sleep(0.02)
        
        # 4. 执行配置依赖任务（并行）
        for i in range(51):
            if i <= 50:
                install_dep1.update(value=i)
            if i <= 30:
                install_dep2.update(value=i)
            time.sleep(0.02)
        
        # 完成进度条
        progress.finish()
        time.sleep(1)
    finally:
        progress.stop()
    
    print("高级进度条测试完成")


def test_nested_progress():
    """测试嵌套进度条功能"""
    print("\n=== 嵌套进度条测试 ===")
    
    # 创建主进度条
    main_progress = ProgressBar(total=100, title="主任务进度", refresh_rate=0.05)
    
    # 创建嵌套的子进度条
    phase1 = main_progress.add_sub_progress("阶段一", 100, "第一阶段任务")
    phase2 = main_progress.add_sub_progress("阶段二", 100, "第二阶段任务")
    
    # 阶段一的子任务
    subtask1_1 = phase1.add_sub_progress("子任务1.1", 50, "阶段一的第一个子任务")
    subtask1_2 = phase1.add_sub_progress("子任务1.2", 50, "阶段一的第二个子任务")
    
    # 阶段二的子任务
    subtask2_1 = phase2.add_sub_progress("子任务2.1", 30, "阶段二的第一个子任务")
    subtask2_2 = phase2.add_sub_progress("子任务2.2", 70, "阶段二的第二个子任务")
    
    # 在新线程中运行进度条界面
    progress_thread = threading.Thread(target=main_progress.start)
    progress_thread.daemon = True
    progress_thread.start()
    
    # 执行阶段一任务
    try:
        for i in range(101):
            phase1.update(value=i)
            if i <= 50:
                subtask1_1.update(value=i * 2 // 2)  # 调整更新速度
            if i > 50:
                subtask1_2.update(value=(i - 50) * 2 // 2)  # 调整更新速度
            time.sleep(0.01)
        
        # 执行阶段二任务
        for i in range(101):
            phase2.update(value=i)
            if i <= 30:
                subtask2_1.update(value=i * 10 // 3)  # 调整更新速度
            if i > 30:
                subtask2_2.update(value=(i - 30) * 10 // 7)  # 调整更新速度
            time.sleep(0.01)
        
        # 完成进度条
        main_progress.finish()
        time.sleep(1)
    finally:
        main_progress.stop()
    
    print("嵌套进度条测试完成")


def main():
    """主测试函数"""
    print("urwid_CLI 组件测试")
    print("=" * 50)
    
    # 测试各个组件
    test_select_box()
    # test_file_open_box()  # 取消注释以测试文件选择器
    test_yn_box()
    test_progress_bar_basic()
    test_progress_bar_advanced()
    test_nested_progress()
    
    print("\n所有测试完成！")


if __name__ == "__main__":
    main()