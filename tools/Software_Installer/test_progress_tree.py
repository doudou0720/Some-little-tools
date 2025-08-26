import time
import os
import sys

# 将当前目录添加到Python路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from CLI import ProgressBar

def test_progress_tree():
    # 创建主进度条，设置刷新频率为0.05秒
    progress = ProgressBar(total=100, title="软件安装进度", refresh_rate=0.5)
    
    # 显示初始进度条
    print("\n" * 20)  # 留出足够的空白行用于显示进度条
    progress._draw_main_progress()
    
    # 添加有依赖关系的子进度条
    # 第一组任务：下载相关
    download_task = progress.add_sub_progress("下载主程序", 100, "下载软件的主要程序文件")
    download_dep1 = progress.add_sub_progress("下载依赖库A", 50, "下载第一个依赖库", depends_on=download_task)
    download_dep2 = progress.add_sub_progress("下载依赖库B", 30, "下载第二个依赖库", depends_on=download_task)
    
    # 第二组任务：安装相关
    install_task = progress.add_sub_progress("安装主程序", 100, "安装软件的主要程序文件", depends_on=download_task)
    install_dep1 = progress.add_sub_progress("配置依赖库A", 50, "配置第一个依赖库", depends_on=install_task)
    install_dep2 = progress.add_sub_progress("配置依赖库B", 30, "配置第二个依赖库", depends_on=install_task)
    
    # 启用交互模式
    progress.enable_interaction()
    
    # 模拟任务执行过程
    # 1. 执行下载主程序任务
    for i in range(101):
        download_task.update(value=i)
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
        install_task.update(value=i)
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
    time.sleep(1)  # 等待最后一帧绘制完成
    progress.disable_interaction()
    print("所有任务完成!")

def test_nested_progress():
    # 创建主进度条
    main_progress = ProgressBar(total=100, title="主任务进度", refresh_rate=0.5)
    
    # 显示初始进度条
    print("\n" * 10)
    main_progress._draw_main_progress()
    
    # 创建嵌套的子进度条
    phase1 = main_progress.add_sub_progress("阶段一", 100, "第一阶段任务")
    phase2 = main_progress.add_sub_progress("阶段二", 100, "第二阶段任务")
    
    # 阶段一的子任务
    subtask1_1 = phase1.add_sub_progress("子任务1.1", 50, "阶段一的第一个子任务")
    subtask1_2 = phase1.add_sub_progress("子任务1.2", 50, "阶段一的第二个子任务")
    
    # 阶段二的子任务
    subtask2_1 = phase2.add_sub_progress("子任务2.1", 30, "阶段二的第一个子任务")
    subtask2_2 = phase2.add_sub_progress("子任务2.2", 70, "阶段二的第二个子任务")
    
    # 启用交互模式
    main_progress.enable_interaction()
    
    # 执行阶段一任务
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
    main_progress.disable_interaction()
    print("嵌套进度条测试完成!")

def test_multiple_dependencies():
    # 创建主进度条
    progress = ProgressBar(total=100, title="多依赖任务测试", refresh_rate=0.5)
    
    # 显示初始进度条
    print("\n" * 15)
    progress._draw_main_progress()
    
    # 创建多个前置任务
    task_a = progress.add_sub_progress("任务A", 100, "第一个前置任务")
    task_b = progress.add_sub_progress("任务B", 100, "第二个前置任务")
    
    # 创建依赖于多个任务的后续任务
    task_c = progress.add_sub_progress("任务C", 100, "依赖于任务A和任务B", depends_on=[task_a, task_b])
    
    # 启用交互模式
    progress.enable_interaction()
    
    # 执行任务A和任务B（并行）
    for i in range(101):
        task_a.update(value=i)
        task_b.update(value=i)
        time.sleep(0.01)
    
    # 执行任务C
    for i in range(101):
        task_c.update(value=i)
        time.sleep(0.01)
    
    # 完成进度条
    progress.finish()
    time.sleep(1)
    progress.disable_interaction()
    print("多依赖任务测试完成!")

if __name__ == "__main__":
    print("=== 进度树测试 ===")
    test_progress_tree()
    
    print("\n=== 嵌套进度条测试 ===")
    test_nested_progress()
    
    print("\n=== 多依赖任务测试 ===")
    test_multiple_dependencies()