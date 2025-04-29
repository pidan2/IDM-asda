#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from tkinter import *  # 导入 tkinter 模块用于创建图形界面
import tkinter.filedialog  # 导入文件对话框模块，用于选择文件和目录
import tkinter.messagebox  # 导入消息框模块，用于显示对话框
import os  # 导入操作系统模块，用于路径操作
from PIL import Image, ImageTk  # 导入Pillow库，用于图像处理
from feature_extral_comp import FeatureExtAndComp  # 导入特征提取和比较模块
from config import Config  # 导入配置模块


# 定义图像检索工具界面类
class RetrieverGUI():
    def __init__(self, window):
        # 初始化图像检索器
        self.retriever = FeatureExtAndComp(
            Config.arch_name,  # 模型架构名称
            Config.class_nums,  # 类别数量
            Config.input_size,  # 输入图像的大小
            Config.batch_size,  # 批处理大小
            Config.feature_layers,  # 特征层
            Config.feature_index_in_module,  # 特征索引
            Config.pretrained  # 是否使用预训练模型
        )

        self.selectDirName = "test"
        self.parent = window  # 设置主窗口对象
        self.parent.title("图像检索工具")  # 设置窗口标题

        # 初始化 GUI 布局
        self.frame = Frame(self.parent)  # 创建一个框架，用于存放其他组件
        self.frame.grid(row=0, column=0, sticky=W)  # 将框架添加到窗口的网格中，位置在第0行第0列

        # 创建并设置目标图片标签
        self.contrast_label = Label(self.frame, text="目标图片:")
        self.contrast_label.grid(row=0, column=0, sticky=W)

        # 创建并设置目标图片输入框
        self.contrast_entry = Entry(self.frame)
        self.contrast_entry.grid(row=0, column=1, sticky=W)

        # 创建并设置加载按钮，点击后调用choose_contrast_file函数选择图片文件
        self.contrast_btn = Button(self.frame, text="加载", command=self.choose_contrast_file)
        self.contrast_btn.grid(row=0, column=2, sticky=W)

        # 创建并设置对比图像显示区域
        self.contrast_panel = Canvas(self.frame)
        self.contrast_panel.grid(row=1, column=0, rowspan=2, columnspan=2, sticky=W + E + N + S, padx=5, pady=5)

        # 创建并设置“搜索”按钮，点击后调用get_retriever_top函数进行检索
        self.btn = Button(self.frame, text="搜索", command=self.get_retriever_top)
        self.btn.grid(row=1, column=3, sticky=W + E)

        # 创建并设置搜索目录标签
        self.retrieved_label = Label(self.frame, text="搜索目录:")
        self.retrieved_label.grid(row=0, column=4, sticky=W)

        # 创建并设置搜索目录输入框
        self.retrieved_entry = Entry(self.frame)
        self.retrieved_entry.grid(row=0, column=5, sticky=W)

        # 创建并设置加载按钮，点击后调用choose_retrieved_dir函数选择目录
        self.retrieved_btn = Button(self.frame, text="加载", command=self.choose_retrieved_dir)
        self.retrieved_btn.grid(row=0, column=6, sticky=W + E)

        # 创建并设置检索结果显示区域
        self.result_panel1 = Canvas(self.frame)
        self.result_panel1.grid(row=1, column=4, rowspan=2, columnspan=2, sticky=W + E + N + S, padx=5, pady=5)

    def choose_retrieved_dir(self):  # 选择检索目录
        self.selectDirName = tkinter.filedialog.askdirectory(title='选择目录')
        if not self.selectDirName:
            tkinter.messagebox.askokcancel("错误！", message="未选择任何目录！")
            return
        if not os.path.exists(self.selectDirName):
            tkinter.messagebox.askokcancel("错误！", message="指定的目录不存在！")
            return
        self.retrieved_entry.delete(0, END)
        self.retrieved_entry.insert(0, os.path.basename(self.selectDirName))
        print(self.selectDirName)

    def choose_contrast_file(self):  # 选择对比图片
        self.selectFileName = tkinter.filedialog.askopenfilename(title='选择文件')
        if not self.selectFileName:
            tkinter.messagebox.askokcancel("错误！", message="未选择任何文件！")
            return
        if not os.path.exists(self.selectFileName):
            tkinter.messagebox.askokcancel("错误！", message="指定的图片不存在！")
            return
        self.set_contrast_file_path(self.selectFileName)

    def set_contrast_file_path(self, file_path):  # 直接设置目标图片路径
        if not os.path.exists(file_path):
            tkinter.messagebox.askokcancel("错误！", message="指定的图片路径不存在！")
            return

        self.contrast_entry.delete(0, END)
        file_name = os.path.basename(file_path)
        self.contrast_entry.insert(0, file_name)

        display_width = 256
        display_height = 256
        self.img_png = Image.open(file_path)
        self.img_png.thumbnail((display_width, display_height), Image.LANCZOS)
        self.tkimg = ImageTk.PhotoImage(self.img_png)
        self.contrast_panel.config(width=self.tkimg.width(), height=self.tkimg.height())
        self.contrast_panel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.selectFileName = file_path

    def get_retriever_top(self):  # 获取检索结果
        try:
            topN = 10
            result = self.retriever.get_topN(topN, self.selectFileName, self.selectDirName)
            if not result or not isinstance(result, list) or len(result) == 0:
                tkinter.messagebox.showinfo("结果", "未找到结果！")
                return
            for widget in self.result_panel1.winfo_children():
                widget.destroy()
            display_width = 256
            display_height = 256
            for i, image_name in enumerate(result):
                result_image_path = os.path.join(self.selectDirName, image_name)
                if not os.path.exists(result_image_path):
                    tkinter.messagebox.showerror("错误！", f"检索的图片文件 {image_name} 不存在。")
                    continue
                img = Image.open(result_image_path)
                img.thumbnail((display_width, display_height), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                panel = Label(self.result_panel1, image=tk_img)
                panel.image = tk_img
                panel.grid(row=i // 5, column=i % 5)
        except Exception as e:
            tkinter.messagebox.showerror("错误！", f"发生错误: {str(e)}")
            print(f"get_retriever_top 中的错误: {e}")
        self.get_top_image_paths()

    def get_top_image_paths(self):  # 输出10张结果图片的完整路径
        try:
            topN = 10  # 设置要返回的图片数量为10
            result = self.retriever.get_topN(topN, self.selectFileName, self.selectDirName)  # 获取检索结果

            # 如果没有检索到结果，返回空字符串
            if not result or not isinstance(result, list) or len(result) == 0:
                print("未找到结果！")
                return "未找到结果！"

            # 拼接图片路径
            full_paths = [os.path.join(self.selectDirName, image_name) for image_name in result]
            result_string = "\n".join(full_paths)  # 用换行符拼接成字符串
            #print(result_string)  # 输出结果字符串
            return result_string

        except Exception as e:
            print(f"发生错误: {str(e)}")  # 打印错误信息
            return ""


# 示例调用
if __name__ == '__main__':
    window = Tk()
    retriever_gui = RetrieverGUI(window)

    # 示例：直接传递待搜索图片的路径
    image_path = sys.argv[1]  # 替换为实际图片路径
    print(image_path)
    retriever_gui.set_contrast_file_path(image_path)
    result = retriever_gui.get_top_image_paths()
    print(result)
    window.resizable(width=True, height=True)
    window.mainloop()
