#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import os
from PIL import Image, ImageTk
from feature_extral_comp import FeatureExtAndComp
from config import Config

class RetrieverGUI:
    def __init__(self, window):
        self.retriever = FeatureExtAndComp(
            Config.arch_name,
            Config.class_nums,
            Config.input_size,
            Config.batch_size,
            Config.feature_layers,
            Config.feature_index_in_module,
            Config.pretrained
        )
        self.parent = window
        self.parent.title("图像检索工具")
        # ...其余GUI代码保持不变...

    def choose_retrieved_dir(self):
        self.selectDirName = tkinter.filedialog.askdirectory(title='选择目录')
        if not self.selectDirName:
            tkinter.messagebox.showerror("错误！", "未选择任何目录！")
            return
        self.retrieved_entry.delete(0, END)
        self.retrieved_entry.insert(0, os.path.basename(self.selectDirName))
        print(f"选定的搜索目录：{self.selectDirName}")

    # ...其余方法保持不变...
    def choose_contrast_file(self):
        """处理选择目标图片的按钮点击事件"""
        # 弹出文件选择对话框，限制选择图片文件
        self.selectFileName = tkinter.filedialog.askopenfilename(
            title='选择文件',
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png")]
        )

        # 错误处理：未选择文件
        if not self.selectFileName:
            tkinter.messagebox.showerror("错误！", "未选择任何文件！")
            return

        # 错误处理：文件不存在
        if not os.path.exists(self.selectFileName):
            tkinter.messagebox.showerror("错误！", "指定的图片不存在！")
            return

        # 更新输入框显示
        self.contrast_entry.delete(0, END)
        self.contrast_entry.insert(0, os.path.basename(self.selectFileName))

        # 在画布上显示图片
        display_width = 256  # 显示区域的宽度
        display_height = 256  # 显示区域的高度

        # 使用PIL打开图片并调整大小
        self.img_png = Image.open(self.selectFileName)
        # 保持纵横比缩放到指定尺寸内
        self.img_png.thumbnail((display_width, display_height), Image.LANCZOS)

        # 转换为Tkinter可用的图片格式
        self.tkimg = ImageTk.PhotoImage(self.img_png)

        # 配置画布尺寸以适应图片
        self.contrast_panel.config(
            width=self.tkimg.width(),
            height=self.tkimg.height()
        )
        # 在画布上创建图片对象
        self.contrast_panel.create_image(
            0, 0,
            image=self.tkimg,
            anchor=NW  # 图片左上角对齐画布原点
        )

    def get_retriever_top(self):
        """执行检索并显示结果"""
        try:
            topN = 10  # 设置检索结果数量

            # 调用检索器获取相似图片
            result = self.retriever.get_topN(
                topN,
                self.selectFileName,  # 目标图片路径
                self.selectDirName  # 搜索目录路径
            )

            # 结果有效性检查
            if not result or not isinstance(result, list) or len(result) == 0:
                tkinter.messagebox.showinfo("结果", "未找到结果！")
                return

            # 清空之前的搜索结果
            for widget in self.result_panel1.winfo_children():
                widget.destroy()

            # 图片显示参数
            display_width = 256
            display_height = 256

            # 遍历结果并显示
            for i, image_name in enumerate(result):
                # 构建完整图片路径
                result_image_path = os.path.join(self.selectDirName, image_name)

                # 检查图片是否存在
                if not os.path.exists(result_image_path):
                    tkinter.messagebox.showerror("错误！", f"图片 {image_name} 不存在")
                    continue

                # 加载并调整图片大小
                img = Image.open(result_image_path)
                img.thumbnail((display_width, display_height), Image.LANCZOS)

                # 转换为Tkinter格式
                tk_img = ImageTk.PhotoImage(img)

                # 创建标签组件显示图片
                panel = Label(self.result_panel1, image=tk_img)
                panel.image = tk_img  # 保持引用，防止被垃圾回收

                # 网格布局：每行显示5张图片
                panel.grid(
                    row=i // 5,  # 行号（整除）
                    column=i % 5  # 列号（取余）
                )

        except Exception as e:
            # 异常处理：显示错误信息
            tkinter.messagebox.showerror("错误！", f"发生错误: {str(e)}")
            print(f"错误详情：{e}")  # 控制台输出便于调试


if __name__ == '__main__':
    # 创建主窗口并启动事件循环
    window = Tk()  # 实例化Tk主窗口
    retriever_gui = RetrieverGUI(window)  # 创建GUI实例
    window.resizable(width=True, height=True)  # 允许窗口调整大小
    window.mainloop()  # 进入Tk事件循环，等待用户交互